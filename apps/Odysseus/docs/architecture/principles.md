# Odysseus — Architecture Principles

## Purpose

This document defines the architectural principles used to guide the design and
evolution of Odysseus.

These principles describe how architectural decisions should be made. They do
not prescribe a complete future implementation.

The architecture should grow in response to real product needs rather than from
speculation about what the finished system might eventually require.

---

## 1. Product behaviour comes first

Architecture exists to support Odysseus product behaviour.

New layers, abstractions, infrastructure, adapters, and dependencies should be
introduced because a concrete product capability requires them.

A future possibility is not, by itself, sufficient justification.

The preferred order is:

`Product need -> design need -> architectural change`

not:

`Possible future architecture -> implementation -> hoped-for use`

---

## 2. Use pragmatic ports and adapters

Odysseus uses ports and adapters to keep its core behaviour independent of
external technology.

The broad dependency structure is:

`Driving adapter -> Application -> Domain`

and:

`Application -> Outbound port <- Driven adapter`

External technologies should be replaceable without requiring the core product
model to understand them.

Ports and adapters are a boundary discipline, not a reason to create an
interface or wrapper for every class.

---

## 3. Dependencies point inward

The Odysseus core owns its behaviour and the contracts it requires.

The domain must not depend on:

- web frameworks;
- persistence frameworks;
- databases;
- Garmin;
- Hevy;
- Hyresult;
- planning runtimes;
- deployment infrastructure.

The application layer may depend on domain behaviour and Odysseus-owned
contracts.

Adapters may depend on the core.

The core must not depend on concrete adapters.

---

## 4. Use cases coordinate application behaviour

Application use cases represent meaningful product operations.

Examples may include:

- generating a weekly plan;
- changing training availability;
- viewing a weekly plan;
- recording a manual correction.

A use case may coordinate several domain concepts and outbound capabilities.

Use cases should contain application orchestration, not:

- HTTP behaviour;
- HTML rendering;
- SQL;
- Garmin or Hevy client logic;
- planning-runtime-specific code.

A use case's public interface may itself be the inbound port. Additional
interface abstractions should only be introduced when they solve a real
problem.

---

## 5. Keep the domain independent

The domain represents the concepts and rules that make Odysseus a training
system.

It should contain concepts such as:

- goals;
- availability and rest;
- training plans;
- planned sessions;
- training prescriptions;
- planning constraints;
- other training rules as they emerge.

Domain behaviour should be expressible and testable without starting a web
server, connecting to a database, or contacting an external service.

---

## 6. Odysseus owns its domain model

External systems provide data, execution capabilities, or specialised
services.

They do not define Odysseus concepts.

For example:

- Garmin may receive a representation of a planned workout;
- Hevy may provide completed strength data;
- Hyresult may provide an official HYROX result;
- a local or self-hosted LLM may provide the coaching judgement used to generate
  a weekly plan.

External intelligence does not become the source of truth for athlete state or
Odysseus behaviour.

The planning model may decide what training is appropriate, but Odysseus owns
the facts supplied to it, the structures it must produce, and the rules that
determine whether its output is acceptable.

Odysseus still owns the meaning and representation of:

- a weekly plan;
- a planned session;
- a completed activity;
- a goal;
- a training constraint.

External limitations should be handled at adapter boundaries rather than leaked
into the domain model.

---

## 7. Separate coaching judgement from product truth

The planning model is responsible for coaching judgement.

Odysseus is responsible for authoritative product truth.

Odysseus should determine and provide facts such as:

- effective availability;
- explicit rest;
- goals and target events;
- completed-training context;
- recovery and progression context;
- explicit and inferred athlete preferences;
- evidence context.

The local planning model may use that context to decide:

- weekly training structure;
- session selection and placement;
- volume and intensity;
- progression;
- recovery balance;
- exercise selection;
- interaction between training modalities;
- when prescribed training should differ from athlete preferences.

Athlete-stated preferences and Odysseus's coaching recommendations are distinct.
Training preferences are soft inputs; availability and explicit rest are hard
constraints.

Evidence-informed effectiveness takes priority over soft preferences where
there is a meaningful conflict. This does not imply one universally optimal
training method: recommendations should account for individual context,
feasibility, recovery, adherence, and evidence quality.

Explicit and inferred preferences must remain distinguishable. When a
recommendation differs from an explicit preference, preserve the stated
preference and explain the relevant deviation rather than silently overwriting
it.

Odysseus must then validate the resulting structured plan before it becomes
active.

The application should not recreate the model's coaching judgement through a
large deterministic rules engine, and the model should not be trusted to define
or alter authoritative athlete facts.

---

## 8. Abstractions must be earned

An abstraction should exist because it provides a concrete benefit today.

Good reasons include:

- protecting the core from an external dependency;
- expressing a capability required by a use case;
- isolating technology-specific translation;
- simplifying testing at a meaningful boundary;
- representing a stable domain concept.

Poor reasons include:

- a framework commonly uses the pattern;
- the abstraction may be useful later;
- it makes the code look more enterprise-like;
- another project has one.

Prefer direct, understandable code until a real boundary or repeated concept
requires something more.

---

## 9. Prefer explicit composition

Dependencies should be assembled explicitly.

Application components should receive the collaborators they require rather than
discovering them through hidden global state or framework magic.

Composition belongs at the edge of the application.

This should make it possible to understand:

- which implementation satisfies each port;
- how the application is assembled;
- which dependencies a use case actually requires.

A dependency-injection framework should not be introduced unless ordinary
explicit composition becomes genuinely inadequate.

---

## 10. Introduce infrastructure when a capability needs it

Persistence, background processing, authentication, external integrations, and
other infrastructure should be introduced when they are required by active
product scope.

For example:

- do not introduce a database merely because one will eventually be needed;
- do not create Garmin adapters before Garmin behaviour enters scope;
- do not add a job queue before asynchronous work requires one.

When infrastructure is introduced, it should be production-appropriate for the
actual requirement rather than deliberately temporary or unnecessarily
elaborate.

---

## 11. Build vertically through useful behaviour

Development should prefer small end-to-end capabilities over completing
technical layers in isolation.

A useful increment may cross:

`Web -> Application -> Domain -> Port -> Adapter`

when that is what is required to deliver visible behaviour.

The aim is not to finish the domain layer, then the application layer, then the
web layer.

Architecture should support incremental product delivery rather than dictate a
layer-by-layer implementation sequence.

---

## 12. Preserve athlete ownership

Training data conceptually belongs to an athlete even before the complete
multi-user authentication capability exists.

Designs should therefore avoid assumptions that application data is permanently
global, anonymous, or ownerless.

Later authentication and authorisation should strengthen this boundary rather
than require the core data model to be fundamentally redesigned.

---

## 13. Make boundaries responsible for translation

Adapters should translate between Odysseus concepts and external
representations.

Examples include:

- web forms to application input;
- persistence records to Odysseus models;
- Odysseus workouts to Garmin-compatible structures;
- Hevy records to completed-strength representations;
- structured Odysseus planning context and evidence into model input;
- structured model responses back into Odysseus candidate plans.

Translation does not transfer ownership of validation or domain meaning to the
adapter.

External representations should not be allowed to spread through the core
simply because they are convenient.

---

## 14. Fail explicitly at important boundaries

Failures involving persistence, integrations, planning, or other important
external capabilities should be visible and understandable.

Odysseus should not silently:

- discard athlete data;
- invent missing data;
- guess unknown mappings;
- treat a failed integration as successful;
- hide a failed planning operation.

Failure behaviour should be designed as part of the relevant capability rather
than added as an afterthought.

---

## 15. Production-grade does not mean maximum complexity

Odysseus should be suitable for reliable long-term use.

Production quality means caring about:

- correctness;
- clear boundaries;
- safe configuration;
- secret handling;
- meaningful failures;
- useful observability;
- maintainability;
- recoverability where required.

It does not mean maximising:

- abstraction;
- infrastructure;
- framework usage;
- indirection;
- distributed components.

The simplest design that safely satisfies the real requirement is preferred.

---

## 16. Architecture is living documentation

Architecture documentation should describe the system that exists or is
actively being designed.

When meaningful architectural boundaries change, the relevant documentation and
diagrams should change with them.

Significant architectural decisions that need durable rationale should be
captured separately as Architecture Decision Records.

Git history records how the architecture evolved.

The living architecture documentation describes how it works now.

---

## Decision rule

When considering a new architectural element, ask:

> What current product or engineering need requires this?

If there is no clear answer, it probably does not need to exist yet.
