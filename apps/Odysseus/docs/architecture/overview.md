# Architecture overview

Odysseus uses a pragmatic **ports-and-adapters (hexagonal) architecture** inside a Python application.

The architecture is intentionally documented at two levels:

1. `architecture-overview.puml` shows the whole system at a **top level**.
2. Layer diagrams show the detail inside `web`, `application`, `domain`, and `adapters`.

The overview should stay readable as Odysseus grows. Detailed classes, functions, translations, and invariants belong in the layer diagrams rather than being pushed into the top-level view.

## Current implementation status

The current implementation establishes the first end-to-end vertical slice for recurring training availability.

Today, the implemented path is:

```text
Browser
  -> FastAPI/Jinja web adapter
  -> TrainingAvailabilityUseCases
  -> TrainingAvailabilityStore contract
  -> InMemoryTrainingAvailabilityStore
  -> RecurringTrainingAvailability
```

The web layer also translates domain/application output into a display-ready `TrainingAvailabilityView`, and translates submitted browser form values back into domain values.

Goals and target events have domain models, application CRUD operations, and a read-only future-target query through an application-owned storage contract, implemented by `InMemoryGoalsAndEventsStore`. This capability has no web flow yet.

PostgreSQL persistence, the local planning model, and Garmin / Hevy / Hyresult integrations remain planned architecture. They are shown in the top-level architecture only when clearly marked as planned rather than as completed implementation.

## Top-level architecture

Source: [`diagrams/architecture-overview.puml`](diagrams/architecture-overview.puml)

The top-level diagram answers:

> What are the main architectural areas, and how do they depend on one another?

Its main shape is:

```text
Athlete
  |
  v
Web adapter
  |
  v
Application use cases
  |   |  -> outbound ports <- driven adapters
  v
Domain
```

Driving adapters start interaction with Odysseus. Application use cases coordinate product behaviour. The domain owns training meaning and validity. Outbound ports describe capabilities the application needs from outside the core, and driven adapters provide concrete implementations.

## Layer diagrams

### Web layer

Source: [`diagrams/web-layer.svg`](diagrams/web-layer.svg)

The web layer is the current **driving adapter**. It contains:

- `app.py` — creates FastAPI and registers the availability router;
- `routes/availability.py` — handles `GET /availability` and `POST /availability`;
- `forms.py` — translates incoming browser form values;
- `presentation/availability.py` — builds display-ready Views;
- `templates/availability.html` — renders HTML.

A useful directional model is:

```text
Incoming:
Browser -> Route -> Forms -> Application / Domain

Outgoing:
Application / Domain -> Presentation -> Template -> Browser
```

Routes coordinate the HTTP flow. They do not own training rules or persistence decisions.

### Application layer

Source: [`diagrams/application-layer.puml`](diagrams/application-layer.puml)

The application layer exposes product operations independently of the web layer.

The current availability use case is:

```text
TrainingAvailabilityUseCases
```

with operations to:

- retrieve recurring availability;
- update recurring availability.

The application owns the outbound contract:

```text
TrainingAvailabilityStore
```

which defines `load()` and `save(...)`.

The application source depends on that contract rather than on a concrete storage implementation.

The Protocol is a **type-level contract**, not another runtime object inserted between the use case and adapter. At runtime, the use case holds the injected concrete store object and calls it directly.

`GoalsAndEventsUseCases` provides list, retrieve, create, update, and delete operations for goals and target events. Creation accepts explicit fields, assigns a UUID with `uuid4()`, and returns the new domain object. Updates accept a complete immutable domain object with an existing ID.

The application-owned `GoalsAndEventsStore` Protocol exposes synchronous `load()` and `save(snapshot)` operations. Its `GoalsAndEventsSnapshot` is a frozen dataclass containing `goals: tuple[Goal, ...]` and `target_events: tuple[TargetEvent, ...]`, both defaulting to empty tuples. Each mutation saves a replacement snapshot.

The use case validates non-None event references on goal creation and update. Multiple goals can reference one event. Missing records and missing referenced events raise `LookupError` without saving. Domain construction remains responsible for title and name validity.

`update_target_event(...)` coordinates explicit cancellation: setting an event to CANCELLED cancels only its ACTIVE linked goals, preserving their other fields and saving the event and all goal changes in one replacement snapshot. Other goal statuses, goals linked to other events, and standalone goals remain unchanged. Creating or updating an ACTIVE goal linked to a CANCELLED event raises `ValueError` without saving.

Cancelling a goal leaves its event and other goals untouched. Reactivating an event does not reactivate its goals; individual goals can be updated explicitly. Setting an event to COMPLETED or INACTIVE does not cancel goals, and passing dates do not change statuses.

Deleting a goal leaves its event intact. Deleting an event removes it and clears `target_event_id` on all linked goals in one snapshot save, preserving every other goal field, including status.

`get_future_planning_targets(as_of: date)` loads one snapshot and returns a frozen `FuturePlanningTargets` value defined in `application/goals_and_events.py`, containing goal and event tuples. It includes only ACTIVE goals whose optional target date has not passed and ACTIVE events dated on or after the explicitly supplied cutoff. Linked goals also require an existing qualifying event. Same-day dates qualify. The result preserves stored order and domain object identity; the query never saves or consults the system date. Ordinary list/get operations still expose historical and completed records. This selection does not introduce recovery windows, priority ranking, or planning algorithms.

### Domain layer

Source: [`diagrams/domain-layer.puml`](diagrams/domain-layer.puml)

The domain layer defines the meaning of recurring training availability, goals, and target events.

Current types are:

- `Weekday`;
- `DailyTrainingAvailability`;
- `RecurringTrainingAvailability`;
- `Goal` and `GoalStatus`;
- `TargetEvent`, `TargetEventType`, and `TargetEventStatus`.

The domain protects its own invariants.

A rest day cannot also contain AM or PM training availability. Ordinary unavailability remains valid and distinct from explicit rest.

A recurring week must contain exactly one entry for each weekday.

These rules belong in the domain because they must remain true regardless of whether availability is entered through FastAPI, a future API, a CLI, or another adapter.

Goals and target events are separate frozen dataclasses with caller-supplied UUID identifiers. A goal may exist without an event or target date, and may optionally reference one event by its UUID. A target event has a required date and can exist without linked goals. The domain does not check whether a referenced event exists.

Goal titles and target event names must not be empty or whitespace-only. Past dates are valid for historical records and do not automatically change status. Goals and events have separate status enums, each representing active, completed, cancelled, and inactive states. Event types are running, HYROX, strength, and other.

### Adapters layer

Source: [`diagrams/adapters-layer.puml`](diagrams/adapters-layer.puml)

The current concrete driven adapters are:

```text
InMemoryTrainingAvailabilityStore
InMemoryGoalsAndEventsStore
```

`InMemoryTrainingAvailabilityStore` satisfies the `TrainingAvailabilityStore` Protocol structurally.

It keeps one `RecurringTrainingAvailability` value in process memory:

- `load()` returns the current value;
- `save(...)` replaces it.

`InMemoryGoalsAndEventsStore` structurally satisfies `GoalsAndEventsStore`. It starts with an empty `GoalsAndEventsSnapshot` unless an initial snapshot is supplied. `load()` returns that exact current snapshot; `save(snapshot)` replaces it without merging or converting its `Goal` and `TargetEvent` objects. Each instance holds its own state.

Relationship validation and event-deletion unlinking remain in `GoalsAndEventsUseCases`. The adapter only stores the resulting snapshot.

Both adapters are deliberately small. They do not add serialization, generic repository abstractions, logging, thread-safety, or persistence machinery that the current features do not require.

Future storage and integration mechanisms should normally be added as new adapters that satisfy application-owned contracts, rather than changing the application to depend directly on a technology.

## Availability web flow

The executable walkthrough lives at:

[`../notebooks/web/availability-web-flow.ipynb`](../notebooks/web/availability-web-flow.ipynb)

The notebook focuses specifically on how the web boundary works.

For a read:

```text
GET /availability
  -> FastAPI route
  -> TrainingAvailabilityUseCases.get_recurring_availability()
  -> store.load()
  -> RecurringTrainingAvailability
  -> build_training_availability_view(...)
  -> availability.html
  -> HTML response
```

For an update:

```text
POST /availability
  -> FastAPI route
  -> form translation
  -> RecurringTrainingAvailability
  -> TrainingAvailabilityUseCases.update_recurring_availability(...)
  -> store.save(...)
  -> redirect
  -> GET /availability
```

This follows the POST / Redirect / GET pattern so refreshing the resulting page does not repeat the update.

## Dependency direction

The central dependency rule is:

> Dependencies should point inward toward Odysseus-owned abstractions and training concepts.

In practical terms:

| Layer | May depend on | Should not depend on |
| --- | --- | --- |
| `domain/` | standard library and domain code | application, adapters, web |
| `application/` | domain and application-owned contracts | concrete adapters, web |
| `adapters/` | domain and application contracts | web |
| `web/` | application and domain types needed for translation/presentation | concrete adapters |

The outer composition step is allowed to know concrete implementations so that it can connect them. A dedicated composition root has not yet been introduced in the current Issue #2 slice; the current application factory receives its application collaborator from outside.

## Why keep the diagrams separate?

The architecture overview should answer:

> How does the whole system fit together?

The layer diagrams should answer:

> What actually exists inside this layer, and what is each part responsible for?

This keeps the top-level diagram useful as the system grows while still providing enough detail to understand the concrete Python design.

The layer diagrams are living documentation. When a meaningful new component is added to a layer, its layer diagram should be reviewed. The top-level overview should change only when the system-level architecture changes.
