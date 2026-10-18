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

PostgreSQL persistence, the local planning model, and Garmin / Hevy / Hyresult integrations remain planned architecture. They are shown in the top-level architecture only when clearly marked as planned rather than as completed implementation.

## Top-level architecture

Source: [`diagrams/architecture-overview.svg`](diagrams/architecture-overview.svg)

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

Source: [`diagrams/application-layer.svg`](diagrams/application-layer.svg)

The application layer exposes the product operations needed by the web layer.

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

### Domain layer

Source: [`diagrams/domain-layer.svg`](diagrams/domain-layer.svg)

The domain layer defines the meaning of recurring training availability.

Current types are:

- `Weekday`;
- `DailyTrainingAvailability`;
- `RecurringTrainingAvailability`.

The domain protects its own invariants.

A rest day cannot also contain AM or PM training availability. Ordinary unavailability remains valid and distinct from explicit rest.

A recurring week must contain exactly one entry for each weekday.

These rules belong in the domain because they must remain true regardless of whether availability is entered through FastAPI, a future API, a CLI, or another adapter.

### Adapters layer

Source: [`diagrams/adapters-layer.puml`](diagrams/adapters-layer.puml)

The current concrete driven adapter is:

```text
InMemoryTrainingAvailabilityStore
```

It satisfies the `TrainingAvailabilityStore` Protocol structurally.

It keeps one `RecurringTrainingAvailability` value in process memory:

- `load()` returns the current value;
- `save(...)` replaces it.

The adapter is deliberately small. It does not add serialization, generic repository abstractions, logging, thread-safety, or persistence machinery that the current feature does not require.

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
