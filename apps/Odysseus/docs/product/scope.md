# Odysseus — Product Scope

## Purpose

This document defines the scope of the current Odysseus application release.

The complete intended product behaviour is defined in `requirements.md`.

This is a living document. It should focus on the release currently being
developed and should be updated when development moves to a new application
version.

Release history belongs in `CHANGELOG.md`, while Git tags preserve the exact
state of the application and documentation at each release.

---

## Versioning

Odysseus uses semantic-style application versioning:

`MAJOR.MINOR.PATCH`

During pre-1.0 development:

- a **minor version** introduces a meaningful new product capability;
- a **patch version** fixes or refines behaviour within an existing capability.

For example:

- `v0.1.0` — first useful planning release;
- `v0.1.1` — planning fixes or refinements;
- `v0.2.0` — next substantial product capability.

---

# Current release — v0.1

## Product outcome

The first genuinely useful version of Odysseus must generate the athlete's
weekly training plan itself.

A product that only stores or displays manually created training plans is not
considered a complete `v0.1`.

The core product flow is:

`Athlete context -> Evidence-informed planning -> Weekly training plan`

Weekly planning must be performed using a local or self-hosted LLM.

A deterministic or manually authored planning system may be useful during
development, but does not by itself satisfy the `v0.1` planning capability.

---

## In scope

### Athlete planning context

Odysseus must have sufficient athlete context to generate a meaningful weekly
plan.

This includes:

- current goals;
- target races and events;
- recurring training availability;
- dated availability exceptions;
- explicit rest requirements;
- athlete training preferences;
- learned athlete preferences;
- representative recent completed training;
- relevant recovery and progression context.

Recent training history may initially be supplied manually or through
representative application data.

Automated Garmin, Hevy, and Hyresult ingestion is not required for `v0.1`.

Odysseus owns the athlete facts and constraints supplied to the planner.

The planner should receive structured Odysseus context rather than
source-specific Garmin, Hevy, Hyresult, web, or persistence representations.

---

### Weekly plan generation

Odysseus must generate a coherent Monday-to-Sunday training plan.

The week must be capable of coordinating:

- running;
- strength training;
- hybrid / HIIT / HYROX training;
- rest.

The planner should consider the training week as a whole rather than selecting
sessions independently for individual days.

Availability and explicit rest are hard constraints.

Odysseus resolves these constraints before planning and validates that the
generated plan obeys them.

---

### Planning responsibility

Odysseus and the local LLM have distinct responsibilities.

Odysseus owns:

- effective availability;
- explicit rest;
- goals and target events;
- completed-training context;
- recovery and progression context;
- learned athlete preferences;
- evidence context;
- structured planning inputs and outputs;
- validation of hard constraints and plan structure.

The local LLM owns the coaching judgement required to transform that context
into an appropriate weekly plan.

This includes decisions such as:

- weekly training structure;
- session selection;
- session placement;
- training frequency;
- volume and intensity;
- progression;
- recovery balance;
- interaction between running, strength, and hybrid training;
- exercise selection;
- race-specific preparation;
- when athlete preference should or should not be followed.

Odysseus should not attempt to reproduce this coaching judgement through a large
deterministic rules engine.

---

### Evidence-informed planning

Weekly planning should be based on credible contemporary training knowledge and
established best practice.

Planning should be capable of considering factors such as:

- training frequency;
- volume;
- intensity;
- progression;
- recovery;
- concurrent strength and endurance training;
- exercise selection;
- running-specific preparation;
- HYROX-specific preparation;
- fatigue management;
- periodisation.

Athlete preferences influence planning but do not dictate it.

Odysseus may prescribe a different weekly structure where that better supports
the athlete's goals, recovery, current context, and evidence-informed training
practice.

Meaningful departures from athlete preferences should have an understandable
training rationale.

Odysseus should provide explicit evidence-informed training context to the
planner rather than relying solely on the model's pretrained knowledge.

For `v0.1`, a curated and sourced set of training principles is sufficient.

Automated discovery or retrieval of current research, such as relevant
scientific papers or professional guidance, may be added if it proves useful and
sufficiently lightweight, but is not required for `v0.1`.

---

### Planner output

The planner must return structured output that can be represented as Odysseus
application data.

The output must include:

- the structured Monday-to-Sunday weekly plan;
- detailed structured session prescriptions;
- session purposes;
- a concise summary explaining the overarching aim of the week;
- relevant rationale for meaningful planning decisions or departures from
  athlete preference.

The structured plan is authoritative.

Prose exists to explain the plan rather than replace structured application
data.

---

### Plan validation

Generated plans must pass Odysseus validation before becoming active.

Validation should cover:

- structural correctness;
- required session information;
- scheduling within effective availability;
- compliance with explicit rest;
- supported session structures;
- completeness of the requested planning week.

A structurally valid model response may still be invalid as an Odysseus plan if
it violates a hard product constraint.

If validation fails, Odysseus should provide the validation failures back to
the planner and request a corrected plan.

A maximum of three generation attempts should be made.

If a valid plan cannot be produced within those attempts:

- generation fails visibly;
- no invalid plan becomes active;
- no partial plan is silently accepted.

---

### Running prescriptions

Odysseus must be capable of representing useful structured running sessions.

These may include:

- warm-up;
- steady running;
- intervals;
- recovery;
- repeated blocks;
- cool-down;
- distance or duration completion;
- heart-rate guidance;
- pace guidance;
- power guidance;
- other appropriate targets.

Garmin delivery is not required for `v0.1`.

---

### Strength prescriptions

Odysseus must be capable of representing useful strength sessions.

These may include:

- ordered exercises;
- sets;
- repetitions or repetition ranges;
- load where appropriate;
- RPE or RIR where useful;
- rest periods;
- supersets where appropriate.

Hevy execution or ingestion is not required for `v0.1`.

---

### Hybrid / HIIT / HYROX prescriptions

Odysseus must support hybrid training as a first-class training modality.

A hybrid session may contain ordered combinations of:

- running;
- SkiErg;
- rowing;
- sled work;
- burpees;
- carries;
- lunges;
- wall balls;
- other functional movements;
- rest or recovery.

Individual work elements should be capable of containing appropriate details
such as:

- distance;
- duration;
- repetitions;
- rounds;
- load;
- recovery;
- pace;
- heart-rate guidance;
- execution instructions.

The Odysseus prescription should describe the intended workout independently of
future Garmin workout-format limitations.

Garmin HIIT delivery and fallback behaviour for unsupported Garmin movements are
not required for `v0.1`.

---

### Weekly plan experience

The athlete must be able to inspect the generated week through the web
application.

The athlete should be able to understand:

- what is planned;
- when it is planned;
- what each session contains;
- the purpose of each session;
- the overarching aim of the week;
- how the week supports current goals;
- meaningful reasons for departures from stated preferences.

There is no separate approval step before the generated plan becomes active.

---

### Plan persistence

A generated weekly plan must persist beyond the immediate planning response.

The weekly plan should exist as application state rather than only as transient
generated text.

This establishes the foundation for later comparison with completed training
and future replanning.

---

## Requirement coverage

The principal product requirements targeted by `v0.1` are:

- `GOAL-01` through `GOAL-05`;
- `AVAIL-01` through `AVAIL-06`;
- `PLAN-01` through `PLAN-09`;
- `PLAN-12` through `PLAN-16`;
- `RUN-01` through `RUN-05`;
- `STR-01` through `STR-04`;
- `HYBRID-01` through `HYBRID-06`;
- `HYBRID-12`;
- `UX-01` through `UX-04`;
- `UX-08`;
- `UX-09`;
- relevant `OPS-05` behaviour concerning local or self-hosted AI.

Some requirements may only be partially realised where their full behaviour
depends on later integrations or completed-training data.

---

## Explicitly deferred

The following are deliberately outside `v0.1`:

- automated Garmin activity ingestion;
- Garmin structured running workout delivery;
- Garmin hybrid / HIIT workout delivery;
- Hevy workout ingestion;
- Hyresult race result ingestion;
- automatic planned-to-completed matching;
- completed-training reconciliation;
- midweek goal-aware replanning;
- analytics dashboards;
- automated preference learning from real integrated training behaviour;
- multi-source HYROX race reconciliation;
- production multi-user authentication and administration;
- email plan notification;
- production deployment hardening;
- a full RAG system;
- mandatory live scientific-research retrieval during every planning cycle.

These remain valid product requirements.

They are deferred so `v0.1` can focus on proving the central product value:

> Odysseus can generate a genuinely useful, evidence-informed training week
> using a private local planning model.

---

## Future releases

Future releases should be added to this document when they become relevant to
active planning.

Their scope should be determined from:

- the remaining product requirements;
- lessons learned from the current release;
- integration feasibility;
- newly discovered product or technical constraints.

Unreleased scope may change as understanding improves.

Once a release has shipped, its scope should not be rewritten retrospectively
except to correct documentation errors.