# ADR-001 — Local LLM Planning Boundary

**Status:** Accepted  
**Date:** 2026-10-14

## Context

Odysseus must generate an athlete's weekly training plan itself.

The planner is expected to make contextual coaching decisions across:

- athlete goals and target events;
- effective availability and explicit rest;
- recent completed training;
- recovery and progression context;
- learned athlete preferences;
- running, strength, and hybrid / HYROX demands;
- evidence-informed training principles.

These decisions require judgement rather than simple scheduling.

For example, Odysseus may need to decide whether:

- a preferred training split remains appropriate;
- running or strength volume should change;
- a HYROX-specific session is valuable in the current week;
- an athlete preference should be overridden;
- session intensity should be reduced because of recent training;
- several individually reasonable sessions form a coherent week when considered
  together.

Implementing this behaviour primarily through a deterministic rules engine would
require Odysseus to encode a large and continually evolving body of coaching
judgement.

At the same time, allowing a language model to own athlete state, hard
constraints, or the Odysseus domain model would make core product behaviour
unreliable and difficult to control.

Odysseus therefore needs a clear boundary between:

- facts and constraints owned by the application;
- coaching judgement performed by an intelligent planning capability.

Privacy is also a core product concern. Personal athlete information should not
need to be sent to an external hosted AI service merely to generate a training
plan.

---

## Decision

Odysseus will use a **local or self-hosted large language model** to provide the
coaching judgement required to generate weekly training plans.

The LLM will operate behind an Odysseus-owned planning port.

Odysseus will own:

- authoritative athlete facts;
- hard constraints;
- learned athlete preferences;
- completed-training context;
- recovery and progression context;
- evidence context;
- structured planner input;
- structured planner output;
- domain meaning;
- validation of generated plans;
- persistence and activation of valid plans.

The LLM will own the coaching judgement used to transform that context into a
candidate weekly plan.

The boundary can be summarised as:

`Odysseus owns truth; the LLM owns coaching judgement.`

---

## Planning flow

The planning flow is:

`Odysseus context -> Local LLM -> Candidate plan -> Odysseus validation -> Active plan`

Odysseus first resolves the authoritative context required for planning.

This includes effective availability rather than requiring the LLM to reconcile
recurring availability and dated exceptions itself.

The resulting planning context is supplied to the LLM through the planning
adapter.

The LLM produces a structured candidate weekly plan together with concise
planning rationale.

Odysseus validates the candidate before it can become active.

If validation fails, the validation failures are supplied back to the planning
capability and a corrected plan may be requested.

A maximum of three generation attempts is allowed.

If no valid plan is produced within those attempts, the planning operation fails
visibly and no invalid or partial plan becomes active.

---

## Odysseus responsibilities

Odysseus is responsible for determining what is true about the athlete and the
application.

This includes:

- resolving effective availability;
- preserving explicit rest;
- providing goals and target events;
- providing completed-training history;
- providing recovery and progression context;
- storing and supplying learned preferences;
- constructing evidence context;
- defining supported training and session structures;
- validating generated output;
- preserving historical and persisted application state.

The LLM must not be relied upon to establish or alter these authoritative facts.

---

## LLM responsibilities

The local LLM is responsible for coaching decisions such as:

- the overall structure of the training week;
- training frequency;
- session selection;
- session placement within available periods;
- running volume and intensity;
- strength volume and exercise selection;
- hybrid / HYROX programming;
- progression;
- recovery balance;
- interaction between training modalities;
- race-specific preparation;
- whether an athlete preference should be followed or overridden;
- meaningful explanation of planning decisions.

Odysseus should not duplicate this behaviour through a large deterministic
coaching rules engine.

Deterministic logic should be used where the application needs certainty, not
where contextual coaching judgement is required.

---

## Planner input

The planning capability receives structured Odysseus-owned context.

Conceptually, this includes:

```text
PlanningContext
├── planning week
├── goals
├── target events
├── effective availability
├── explicit rest
├── completed training
├── progression context
├── recovery context
├── learned preferences
└── evidence context
```

The exact production types are deliberately not defined by this ADR.

The planner should not receive external-system representations such as:

- Garmin activity responses;
- Hevy workout responses;
- Hyresult responses;
- HTTP form data;
- database records.

Those representations must be translated into Odysseus-owned context before
planning.

---

## Planner output

The planning capability must produce structured output representing a candidate
Odysseus weekly plan.

The output includes:

```text
Candidate Weekly Plan
├── Monday to Sunday structure
├── planned sessions
├── detailed prescriptions
├── session purposes
├── weekly summary
└── relevant planning rationale
```

The structured plan is authoritative.

Generated prose exists to explain the plan and its overarching intent rather
than acting as the plan itself.

The exact production schema is deliberately not defined by this ADR.

---

## Evidence-informed planning

The LLM should not rely solely on knowledge contained in its pretrained model.

Odysseus will provide an explicit evidence context containing relevant,
credible training principles.

For the initial planning capability, this may be a curated and sourced body of
training guidance.

The architecture should allow this context to evolve later.

For example, Odysseus may eventually retrieve current scientific literature,
reviews, consensus statements, position stands, or other credible sources when
they are relevant to a planning decision.

A full retrieval-augmented generation system is not required by this decision.

Any future external evidence retrieval should avoid sending personal athlete
information where generic research queries are sufficient.

---

## Validation boundary

Structured-output validation and product validation are distinct.

A model response may be structurally valid while still violating Odysseus
product rules.

For example, a correctly structured session scheduled during an unavailable
period remains an invalid Odysseus plan.

Validation therefore includes both:

**Structural validation**

- expected output structure;
- required fields;
- supported session types;
- valid prescription structures;
- complete planning week.

**Product validation**

- effective availability;
- explicit rest;
- other hard planning constraints;
- consistency with authoritative Odysseus context.

Validation belongs to Odysseus rather than to the LLM or its adapter.

---

## Planning adapter responsibility

The planning adapter sits between the Odysseus planning port and the selected
local model/runtime.

It is responsible for translating:

`Odysseus planning context -> model-compatible input`

and:

`structured model output -> Odysseus candidate-plan representation`

The adapter may also contain model-specific instructions and structured-output
configuration.

It does not own:

- athlete facts;
- coaching policy outside the supplied planning instruction;
- domain concepts;
- validation rules;
- retry policy;
- activation of generated plans.

Those responsibilities remain inside the Odysseus core.

---

## Model and runtime selection

This ADR does not select a specific:

- LLM;
- parameter size;
- quantisation;
- inference engine;
- serving runtime;
- hardware configuration.

The chosen implementation should favour a relatively small, resource-efficient
model that remains sufficiently capable of the required planning judgement.

Model and runtime choices remain replaceable behind the planning adapter.

They may therefore evolve without changing the fundamental planning
architecture described by this decision.

---

## Alternatives considered

### Deterministic planning engine

A rule-based planner could provide predictable behaviour and straightforward
constraint enforcement.

It was rejected as the primary planning mechanism because the central planning
problem requires substantial contextual coaching judgement across goals,
modalities, progression, recovery, evidence, and athlete preferences.

Encoding that judgement comprehensively as deterministic application logic
would create a large and difficult-to-maintain coaching rules engine.

Deterministic rules remain appropriate for hard constraints and validation.

### Hosted external LLM

A hosted model could provide strong planning capability and reduce local
inference requirements.

It was rejected as the default architecture because Odysseus is intended to
remain private and self-hostable, and personal athlete context should not need
to leave the user's environment merely for planning convenience.

This decision does not require support for an external hosted fallback.

### LLM owns the complete planning process

The application could provide raw athlete information and trust the LLM to
resolve constraints, structure the plan, and decide whether its own output is
valid.

This was rejected because authoritative athlete state, hard constraints, domain
meaning, and validation are application responsibilities.

The model should exercise coaching judgement inside boundaries owned by
Odysseus.

### Model knowledge only

The planner could rely entirely on knowledge learned during model training.

This was rejected because evidence-informed planning is an important product
characteristic and the relevant knowledge should be capable of being made
explicit, sourced, and updated independently of the model itself.

---

## Consequences

The application requires a clear planning port separating Odysseus from the
chosen model and runtime.

Planning context must be represented independently of Garmin, Hevy, Hyresult,
web, persistence, and model-specific formats.

Weekly plans and their session prescriptions must have structured Odysseus-owned
representations.

A validation boundary is required between model generation and plan activation.

Planning failures must be capable of producing useful validation feedback for a
subsequent generation attempt.

The planning adapter will contain model-specific translation and prompting
concerns.

Evidence context becomes a first-class input to planning even if its initial
implementation remains deliberately simple.

The specific local model and runtime may be replaced without redesigning the
domain or application layers.

The quality of the planning capability will depend partly on model capability,
so model evaluation remains an engineering concern even though model selection
is not fixed by this ADR.

---

## Future decisions

Separate decisions may later be required for:

- selection of the initial local LLM;
- selection of the local inference/runtime technology;
- representation and maintenance of curated training evidence;
- whether live research retrieval is worthwhile;
- model versioning and reproducibility;
- how learned athlete preferences are derived;
- detailed planner input and output schemas.

These decisions should be made when implementation requires them rather than
being fixed by this ADR.
