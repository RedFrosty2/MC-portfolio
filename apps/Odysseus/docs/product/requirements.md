# Odysseus — Product Requirements

## Purpose

This document defines the behaviour Odysseus is expected to support.

It describes product requirements rather than implementation choices.
Technology, architecture, database design, APIs, and package structure belong
elsewhere.

The product vision in [`vision.md`](vision.md) is the north star for these requirements.
The [product glossary](glossary.md) defines the shared terminology used here.

---

## 1. Athlete ownership and privacy

### ATH-01 — Athlete-owned data

All personal training data must belong to a specific athlete.

An athlete must only be able to access their own:

- plans;
- completed activities;
- availability;
- goals and races;
- body metrics;
- preferences;
- analytics.

### ATH-02 — Small multi-user support

Odysseus should support a small number of independent athletes.

The initial intended scale is fewer than five users.

### ATH-03 — Authentication

Access to Odysseus must require authentication.

### ATH-04 — Multi-factor authentication

The deployed system must support multi-factor authentication.

### ATH-05 — Login session persistence

After successful authentication, an athlete should remain signed in across
normal navigation, page refreshes, and reasonable browser or application
restarts without needing to authenticate repeatedly.

Authentication sessions must:

- expire appropriately;
- be invalidated when the athlete logs out;
- be revocable when required;
- no longer provide access when the associated athlete account is disabled or
  removed.

Persistent login must not weaken the privacy or security of athlete data.

### ATH-06 — Administrative access

Odysseus may support an administrative role for maintaining the service and
managing users.

Administrative access must not automatically grant access to another athlete's
personal training data.

### ATH-07 — User disablement

An athlete account must be capable of being disabled without immediately
deleting its historical data.

Disabling an athlete should prevent normal access and stop active integrations
or automated processing associated with that athlete.

### ATH-08 — User deletion

Where an athlete is deliberately deleted, Odysseus must support actual removal
of their personal data rather than merely hiding the account.

---

## 2. Goals and races

### GOAL-01 — Goals

An athlete must be able to define training goals that can influence planning.

### GOAL-02 — Races and events

An athlete must be able to record races or other target events with a relevant
date.

This may include:

- running races;
- HYROX events;
- other dated participation events relevant to planning.

### GOAL-03 — Time relevance

Goals and races must have time-bounded relevance.

Completed, expired, cancelled, or otherwise inactive goals should not continue
to drive future plans as though they were still active.

Future preparation targets are selected as of an explicitly supplied date:

- a standalone goal must be ACTIVE and have no target date or a target date on
  or after that date;
- an event must be ACTIVE and dated on or after that date;
- an event-linked goal must satisfy its own status/date conditions and reference
  an existing event that satisfies the event conditions.

The same-day boundary is inclusive. Missing, past, or non-active linked events
exclude their goals from this selection. Selection preserves stored order and
does not change statuses or remove historical records.

### GOAL-04 — Goal status

Odysseus must retain enough information to distinguish active, completed,
cancelled, and otherwise inactive goals or races.

Goals and target events are separate concepts, but an event-linked goal depends
on its referenced event. When an event is explicitly changed to CANCELLED:

- all ACTIVE goals linked to it become CANCELLED;
- COMPLETED, INACTIVE, and already CANCELLED linked goals keep their statuses;
- unrelated and standalone goals remain unchanged;
- the event change and affected goal changes take effect together.

Cancelling an individual goal leaves its event and other linked goals unchanged.
Reactivating a cancelled event does not reactivate its goals; the athlete may
explicitly update individual goals later. Creating or updating an ACTIVE goal
linked to a CANCELLED event must be rejected rather than silently changing the
goal's status.

Changing an event to COMPLETED or INACTIVE does not automatically cancel linked
goals. Dates passing do not by themselves change statuses. Deleting an event
unlinks its goals without deleting them or changing their statuses.

### GOAL-05 — Planning context

Active goals and races should be available as context when future training is
planned.

Future preparation targets are distinct from retained historical context.
Past and completed records remain accessible through ordinary list and retrieve
operations, even when excluded from the future-target query.

---

## 3. Training availability

### AVAIL-01 — Weekly baseline

An athlete must be able to describe their normal recurring availability across
a Monday-to-Sunday week.

### AVAIL-02 — Day periods

Availability should distinguish between morning and afternoon/evening training
opportunities without requiring exact clock times.

### AVAIL-03 — Explicit rest

An athlete must be able to mark a day as an explicit rest day.

Rest must remain distinct from simply being unavailable to train.

### AVAIL-04 — Dated exceptions

An athlete must be able to override their normal availability for specific
dates.

Examples include:

- holidays;
- illness;
- work commitments;
- travel;
- temporary additional availability;
- explicit additional rest.

### AVAIL-05 — Effective availability

For any relevant date, Odysseus must be able to determine the athlete's
effective availability from their recurring baseline and any dated exception.

### AVAIL-06 — Hard constraint

Availability and explicit rest requirements are hard planning constraints.

Odysseus must not deliberately schedule training into a period in which the
athlete is unavailable.

### AVAIL-07 — Availability impact

If an athlete's availability changes after a weekly plan has been created,
Odysseus must identify where the existing plan is no longer compatible with the
new availability.

The impact should be considered across the remaining uncompleted week rather
than treating each conflicting session in isolation.

### AVAIL-08 — Goal-aware replanning

When changed availability affects an active weekly plan, Odysseus should adapt
the remaining week so that it still provides appropriate progression toward the
athlete's longer-term goals.

Replanning should consider:

- the purpose of affected sessions;
- training already completed that week;
- remaining available training opportunities;
- recovery and training balance;
- current goals and races;
- the intended overall training stimulus of the week.

Existing future sessions may be moved, modified, replaced, or removed where
that produces a better coherent plan.

Unnecessary changes should still be avoided, but preserving an existing session
is secondary to maintaining the quality and purpose of the training plan.

### AVAIL-09 — Preserve completed history

Changes to availability or replanning must not rewrite past or completed
training.

The historical record must continue to show what was originally planned and
what was actually completed.

---

## 4. Weekly training planning

### PLAN-01 — Weekly plan

Odysseus must be able to produce a coherent Monday-to-Sunday training plan.

### PLAN-02 — Planning cadence

The normal planning cycle should prepare the following week's training on
Sunday.

### PLAN-03 — Planning context

Planning should consider relevant context including:

- current goals and races;
- athlete availability;
- recent completed training;
- longer-term training history;
- current progression;
- athlete preferences;
- appropriate recovery.

### PLAN-04 — Mixed training

A weekly plan must be able to coordinate:

- running;
- strength training;
- hybrid / HIIT / HYROX training;
- rest.

These activities should be considered together rather than planned as unrelated
training streams.

### PLAN-05 — Session purpose

Every planned training session should have a clear purpose explaining why it is
included.

### PLAN-06 — Concrete prescription

Where appropriate, a planned session should contain concrete training targets
rather than only descriptive text.

### PLAN-07 — Period placement

A planned session may be associated with:

- morning;
- afternoon/evening;
- no specific period.

Exact clock times are not required.

### PLAN-08 — Whole-week visibility

The athlete must be able to view the complete planned week in one coherent
place.

### PLAN-09 — No approval gate

Normal weekly planning must not require a separate review or approval workflow
before the plan becomes active.

The athlete should be able to inspect the plan without creating unnecessary
administrative steps.

### PLAN-10 — Historical planning integrity

Later replanning must not erase the historical record of what was originally
planned.

Past and completed training should remain intact even when future sessions are
changed.

### PLAN-11 — Coherent replanning

When a plan changes during the week, Odysseus should consider the remaining
week as a whole.

The objective is to preserve useful progression, recovery, training balance,
and longer-term intent rather than simply moving an individual conflicting
session to the nearest available slot.

### PLAN-12 — Evidence-informed planning

Odysseus should use credible contemporary training knowledge and established
best practice when determining how an athlete should train toward their goals.

Planning should not be limited to reproducing the athlete's existing habits or
preferred training structure.

Relevant training knowledge may include principles relating to:

- training frequency;
- training volume;
- intensity;
- progression;
- recovery;
- concurrent strength and endurance training;
- exercise selection;
- race-specific preparation;
- hybrid / HYROX training;
- fatigue management;
- periodisation.

The system should favour credible evidence and established practice over novelty
for its own sake.

### PLAN-13 — Preferences are soft constraints

Athlete preferences should influence planning but should normally be treated as
soft constraints rather than mandatory instructions.

For example, an athlete may prefer:

- two upper-body strength sessions;
- two lower-body strength sessions;
- three runs;
- one HYROX session.

Odysseus may prescribe a different weekly structure where there is a meaningful
training reason to do so.

Any alternative plan must remain consistent with:

- hard availability and rest constraints;
- current goals and races;
- appropriate recovery;
- recent completed training;
- current progression;
- the athlete's wider context.

### PLAN-14 — Goal effectiveness over template adherence

The planner should prioritise useful progression toward the athlete's goals over
strict adherence to a preferred weekly template.

A preferred split or session frequency should not be repeated automatically
when a different training structure would provide a more appropriate stimulus.

For example, an athlete's preferred week may contain two upper-body sessions,
two lower-body sessions, three runs, and one HYROX session.

Odysseus may prescribe a different distribution if that better supports the
athlete's goals, recovery, current training phase, and available training time.

### PLAN-15 — Explain meaningful deviations from preference

Where Odysseus deliberately departs from an athlete's stated or learned
preference in a meaningful way, the athlete should be able to understand why.

For example, Odysseus may explain that a preferred second lower-body strength
session was omitted because the week's HYROX-specific work already creates
substantial lower-body load and additional recovery would better support the
athlete's key running and hybrid sessions.

The explanation should communicate the training rationale without requiring the
athlete to understand the planner's internal implementation.

### PLAN-16 — Planning priority

When planning decisions compete, Odysseus should broadly prioritise:

1. hard constraints, including availability and explicit rest;
2. athlete goals and target events;
3. effective and appropriate training principles;
4. the athlete's current training context and progression;
5. athlete preferences;
6. avoiding unnecessary disruption.

Preferences should matter, but they should not override stronger training
reasons.

---

## 5. Running

### RUN-01 — Structured sessions

Odysseus must support structured running sessions rather than only simple
distance descriptions.

A run may contain ordered work such as:

- warm-up;
- steady running;
- intervals;
- recovery;
- repeated blocks;
- cool-down.

### RUN-02 — Completion conditions

Running steps should be capable of using appropriate completion conditions such
as:

- duration;
- distance;
- manual completion.

### RUN-03 — Training targets

Running steps should support useful training targets where appropriate,
including:

- heart-rate guidance;
- pace guidance;
- power guidance;
- unrestricted/easy execution.

### RUN-04 — Session categories

Runs should be distinguishable by their training purpose, such as:

- easy;
- recovery;
- long;
- interval;
- threshold;
- race;
- other.

### RUN-05 — Heart-rate zones

Where heart-rate zones are used, Garmin should remain the athlete-facing
authority for those zones.

Odysseus must preserve the relevant numeric target values used when a session
was planned so historical analysis remains meaningful if the athlete's zones
later change.

### RUN-06 — Garmin execution

Planned structured running sessions should be capable of being delivered to
Garmin so they can be executed on the athlete's watch.

### RUN-07 — Garmin completion data

Completed Garmin running activity should flow back into Odysseus for comparison
and analysis.

### RUN-08 — Meaningful tolerance

Small execution differences should not automatically make a run different from
its intended session.

For example, completing 9.6 km of an intended 10 km session may still represent
the planned workout.

A fundamentally different workout should not be silently treated as the same
session.

---

## 6. Strength training

### STR-01 — Strength sessions

Odysseus must support planned strength sessions containing ordered exercises.

### STR-02 — Set prescription

A strength exercise should support practical prescriptions based primarily on
load and repetitions.

Where useful, prescriptions may also include:

- repetition ranges;
- RPE;
- RIR;
- rest between sets.

### STR-03 — Supersets

Strength planning should be capable of representing supersets where they are
useful.

### STR-04 — Warm-up sets

Odysseus does not need to prescribe strength warm-up sets.

Warm-up work recorded during the real workout should still be preserved when
completed Hevy data is ingested.

### STR-05 — Hevy execution

Hevy remains the primary tool for recording completed strength training.

### STR-06 — Athlete flexibility

The athlete may perform more weight or repetitions than prescribed without the
system treating that behaviour as invalid.

### STR-07 — Exercise substitutions

Exercise substitutions made during real training should be preserved.

Repeated substitution behaviour may later inform athlete preferences.

---

## 7. Hybrid / HIIT / HYROX training

### HYBRID-01 — Structured hybrid sessions

Odysseus must support structured hybrid or HIIT training sessions.

A session may combine different forms of work within one ordered workout,
including:

- running;
- conditioning;
- functional movements;
- recovery periods.

### HYBRID-02 — HYROX support

HYROX training must be treated as a first-class training modality rather than
being forced into either the running or strength model.

HYROX races and HYROX-specific training should be capable of influencing both
weekly planning and longer-term progression.

### HYBRID-03 — Ordered workout structure

A hybrid session should be capable of describing the complete intended workout
in execution order.

This may include work such as:

- running;
- SkiErg;
- rowing;
- sled push;
- sled pull;
- burpee broad jumps;
- farmer's carries;
- lunges;
- wall balls;
- other relevant conditioning or functional movements;
- recovery or rest periods.

The model should not assume that every hybrid session contains the same set of
activities.

### HYBRID-04 — Detailed work prescription

Each part of a hybrid or HIIT session should be capable of carrying the details
required to execute it correctly.

Depending on the work being prescribed, this may include:

- duration;
- distance;
- repetitions;
- rounds;
- load;
- recovery duration;
- heart-rate target;
- pace target;
- other appropriate execution guidance.

Not every field applies to every type of work.

### HYBRID-05 — Repeated work

Hybrid sessions should support repeated structures where appropriate.

For example, a session may prescribe repeated rounds containing multiple pieces
of work rather than requiring every round to be expanded manually.

### HYBRID-06 — Session purpose

Every planned hybrid session should have a clear training purpose and fit into
the wider weekly plan and longer-term objective.

### HYBRID-07 — Garmin workout delivery

Odysseus must be capable of converting a compatible planned hybrid or HIIT
session into a structured Garmin workout and delivering it for execution on the
athlete's watch.

The intended experience should be similar to structured running:

Odysseus creates the workout
-> Garmin receives the workout
-> the watch guides the athlete through the session

The workout sent to Garmin should preserve as much of the planned structure and
guidance as the Garmin execution format supports.

### HYBRID-08 — Watch-guided execution

Where supported by Garmin, the athlete should be able to follow the ordered
parts of a hybrid or HIIT workout directly from the watch rather than relying on
Odysseus as a second execution screen during training.

### HYBRID-09 — Execution fidelity and graceful degradation

Odysseus must preserve the complete intended hybrid session even when Garmin
cannot represent every part of the prescription exactly.

When a hybrid or HIIT workout is prepared for Garmin, each planned element
should be represented as faithfully as the Garmin workout format allows.

Where an exact representation is not available, Odysseus should fall back to
the closest representation that still preserves the athlete's understanding of
what they are expected to perform.

This may include:

- using a more generic work step;
- preserving the intended movement name as guidance;
- preserving useful instructions;
- requiring manual progression between workout steps where appropriate.

The underlying Odysseus session remains the authoritative planned workout.

### HYBRID-10 — Unsupported movement handling

If a prescribed hybrid movement cannot be represented faithfully enough by the
Garmin workout format, Odysseus must not silently remove it or substitute a
different exercise merely to make the workout compatible.

The system should:

1. preserve the original movement in the Odysseus plan;
2. use the most faithful watch-compatible representation available;
3. make any meaningful loss of execution detail understandable to the athlete;
4. avoid sending a watch workout that materially misrepresents the intended
   session.

For example, the running portions of a HYROX session may map directly to
structured Garmin steps while a functional movement may need to be represented
as a generic manually completed work step with clear instructions.

### HYBRID-11 — Safe execution fallback

Where Garmin cannot represent a planned hybrid session accurately enough to
provide useful watch guidance, Odysseus should prefer an explicit fallback over
an incorrect structured workout.

The athlete should still be able to inspect the complete prescribed session in
Odysseus and understand which parts can and cannot be represented faithfully on
the watch.

External execution limitations must not alter the intended training
prescription simply to make the session fit the Garmin format.

### HYBRID-12 — Interaction with other training

Hybrid workload must be considered alongside standalone running and strength
training when planning:

- fatigue;
- recovery;
- weekly training balance;
- progression.

The running and strength demands of a hybrid session must not be ignored when
planning the surrounding week.

### HYBRID-13 — Completed hybrid training

Completed hybrid or HIIT training must be preserved as part of the athlete's
actual training history.

Odysseus should retain enough completed-session information to understand how
the athlete performed relative to the planned workout.

### HYBRID-14 — Planned vs completed comparison

Where a hybrid session was planned, Odysseus should be able to compare the
planned structure and purpose with the athlete's completed session.

Small execution differences should be treated appropriately, while a
substantially different workout should remain distinguishable from the planned
session.

---

## 8. Completed training

### COMPLETE-01 — Preserve reality

Odysseus must preserve what the athlete actually completed rather than forcing
completed data to match the original plan.

### COMPLETE-02 — Garmin activities

Relevant completed activity information from Garmin must be available for
Odysseus analysis.

This should include sufficient information for meaningful analysis of running,
hybrid training, and training execution.

### COMPLETE-03 — Strength activities

Completed strength workouts from Hevy must be available to Odysseus.

### COMPLETE-04 — Hybrid activities

Completed hybrid or HYROX training must be available to Odysseus regardless of
whether the underlying activity originated from one or multiple recording
sources.

### COMPLETE-05 — Body metrics

Relevant body metrics available from the athlete's Garmin ecosystem should be
capable of contributing to the athlete's history and planning context.

### COMPLETE-06 — Off-plan training

Training completed without a matching planned session must still be retained as
real training history.

### COMPLETE-07 — Historical integrity

Completed training must remain distinguishable from planned training.

### COMPLETE-08 — Source fidelity

Where completed training originates from an external specialist tool, Odysseus
should preserve enough source identity and detail to understand where the
activity came from and reconcile later source changes where required.

### COMPLETE-09 — Multiple records for one real activity

A single real-world training session or race may be described by complementary
records from more than one external source.

Odysseus must be capable of associating those records with one coherent
completed activity or event rather than automatically treating every external
record as a separate training session.

The information contributed by each source should remain distinguishable where
that distinction is useful.

### COMPLETE-10 — No double-counting

Complementary external records describing the same real-world activity must not
cause training volume, race completion, analytics, or goal progress to be
counted more than once.

---

## 9. Planned-to-completed matching

### MATCH-01 — Automatic matching

Odysseus should automatically attempt to associate completed training with the
appropriate planned session.

### MATCH-02 — One-to-one constraint

A completed real-world activity may match at most one planned session.

A planned session may match at most one completed real-world activity.

Odysseus must not silently use the same completed activity to satisfy multiple
planned sessions.

Multiple external records may contribute to one completed activity without
violating this constraint.

### MATCH-03 — Tolerant matching

Matching should tolerate small harmless differences between the prescription
and execution.

### MATCH-04 — Structural difference

A substantially different session should remain distinguishable from the
planned workout even when some basic measurements are similar.

### MATCH-05 — Manual correction

The athlete must be able to correct an automatic match.

### MATCH-06 — Manual precedence

A manually corrected match should take precedence over automatic matching until
the athlete deliberately changes it again.

### MATCH-07 — Match provenance

Odysseus should retain whether a match was made automatically or manually.

### MATCH-08 — Missed and additional training

Odysseus should be able to distinguish:

- planned sessions that were not completed;
- completed sessions that were not planned.

### MATCH-09 — Modality-aware matching

Matching should consider the intended structure and modality of a session.

Running, strength, and hybrid sessions should not be considered equivalent
simply because they occurred at a similar time or have superficially similar
summary values.

### MATCH-10 — Race result reconciliation

Where Garmin activity data and an official Hyresult result refer to the same
HYROX race, Odysseus should reconcile them as complementary evidence of one
completed race.

They must not be treated as separate completed sessions or independently satisfy
multiple planned activities.

---

## 10. Progress and analytics

### ANALYTICS-01 — Planned vs completed

The athlete must be able to compare planned training with completed training.

### ANALYTICS-02 — Running progression

Odysseus should support useful running trends over time, including measures such
as:

- weekly running distance;
- pace;
- heart rate;
- Zone 2 pace;
- fastest kilometre;
- VO2 max where available.

### ANALYTICS-03 — Strength progression

Odysseus should support analysis of strength progression using completed load,
repetitions, exercises, and other useful training information.

### ANALYTICS-04 — Hybrid and HYROX progression

Odysseus should support meaningful analysis of hybrid / HIIT / HYROX training
and racing where the available data makes this useful.

The system should be capable of considering:

- running performance;
- functional work;
- station performance;
- recovery between work;
- overall hybrid performance.

For HYROX races, official Hyresult performance data should be capable of being
analysed alongside relevant Garmin-recorded telemetry.

### ANALYTICS-05 — Goal progress

Where meaningful, analytics should help the athlete understand progress toward
active goals and races.

### ANALYTICS-06 — Historical comparison

Analysis should remain meaningful when contextual values change over time.

For example, later changes to heart-rate zones should not rewrite the targets
that were used for historical sessions.

### ANALYTICS-07 — Useful rather than exhaustive storage

Odysseus should retain the data needed for planning, comparison, progress, and
learning without collecting data merely for the sake of having it.

---

## 11. Learning and adaptation

### LEARN-01 — Behavioural learning

Odysseus should be capable of learning useful patterns from the athlete's real
training behaviour over time.

### LEARN-02 — Preference learning

Repeated choices such as exercise substitutions or recurring training changes
may contribute to an understanding of athlete preferences.

### LEARN-03 — Effectiveness over convenience

Athlete preference must not automatically override training effectiveness,
recovery needs, or the athlete's goals.

### LEARN-04 — Planning feedback loop

Completed training and meaningful deviations from the plan should be capable of
influencing future planning.

### LEARN-05 — Explainable planning

Important planning recommendations should have an understandable reason.

The athlete should be able to understand the purpose of a session and the
context that contributed to important planning decisions.

### LEARN-06 — Changing context

Learned behaviour should remain contextual rather than being treated as a
permanent rule.

A preference or pattern observed historically should not automatically override
new goals, availability, progression, recovery needs, or other relevant
training context.

### LEARN-07 — Preference confidence

Odysseus should distinguish between an athlete's repeated preferences and hard
requirements.

A behaviour occurring repeatedly should not automatically become a permanent
planning rule.

### LEARN-08 — Evidence may challenge preference

Learned or explicitly stated athlete preferences should be considered alongside
credible contemporary training knowledge.

Where a preference conflicts with a better-supported approach for the athlete's
current goals or context, Odysseus should be capable of recommending and
prescribing the better-supported approach.

### LEARN-09 — Evolving training knowledge

The training knowledge used to guide planning should be capable of evolving as
credible evidence, established best practice, or well-supported coaching
consensus develops.

Odysseus should not permanently encode one fixed interpretation of effective
training if stronger evidence later supports a better approach.

### LEARN-10 — Avoid trend chasing

New or fashionable training ideas should not influence planning merely because
they are recent or popular.

Changes in planning guidance should favour:

- credible evidence;
- established practice;
- strong expert consensus;
- demonstrated relevance to the athlete's goals and context

over unsupported novelty.

---

## 12. Garmin integration

### GARMIN-01 — Running activity ingestion

Odysseus must be capable of importing relevant completed running activities
from Garmin.

### GARMIN-02 — Structured running workout delivery

Odysseus must be capable of creating structured Garmin running workouts from
compatible planned run prescriptions.

### GARMIN-03 — Structured hybrid workout delivery

Odysseus must be capable of creating structured Garmin hybrid or HIIT workouts
from compatible planned hybrid prescriptions.

The Garmin representation should preserve the planned:

- workout order;
- work structure;
- recovery structure;
- supported targets;
- useful execution instructions

as faithfully as the Garmin workout format allows.

When a planned movement has no sufficiently accurate Garmin representation,
Odysseus must use an explicit fallback rather than silently dropping,
misclassifying, or replacing the movement.

The original Odysseus session remains the authoritative planned workout.

### GARMIN-04 — Scheduling

Planned Garmin workouts should be capable of being associated with their
intended training date so that normal Garmin/watch synchronisation can deliver
them to the athlete.

### GARMIN-05 — Watch-guided execution

Compatible planned running and hybrid workouts should be executable directly
from the athlete's Garmin watch with useful structured guidance.

### GARMIN-06 — Garmin representation limitations

A limitation in Garmin's workout model must not constrain what Odysseus is able
to prescribe.

Where Garmin cannot represent a planned step exactly, Odysseus should use the
closest sufficiently faithful representation available.

Where no sufficiently faithful representation exists, the limitation should be
surfaced rather than hidden.

### GARMIN-07 — Activity detail

Odysseus should retain the level of Garmin activity detail required for useful
analysis, including summary and relevant lap or split information.

Higher-frequency samples should only be retained where they provide useful
planning or analytics value.

### GARMIN-08 — Heart-rate zones

Odysseus must be capable of using the athlete's Garmin heart-rate zones as
training context.

### GARMIN-09 — Historical zone context

Where zone-based targets influence a planned session, Odysseus should preserve
the numeric values used at that time so later Garmin zone changes do not rewrite
historical meaning.

### GARMIN-10 — Body metrics

Odysseus should be capable of ingesting relevant body metrics available through
the athlete's Garmin-connected scale.

---

## 13. Hevy integration

### HEVY-01 — Strength workout ingestion

Odysseus must be capable of importing completed strength workouts from Hevy.

### HEVY-02 — Exercise identity

Odysseus must be able to associate known Hevy exercises with its own exercise
understanding without relying only on display names.

### HEVY-03 — Unknown exercises

If a Hevy exercise cannot be mapped confidently, Odysseus must preserve it as
unmapped rather than guessing an identity.

### HEVY-04 — Completed detail

Relevant completed sets, repetitions, loads, warm-up work, and substitutions
should be retained where available.

### HEVY-05 — Source changes

Odysseus should be capable of reflecting meaningful edits or deletions made to
completed Hevy workouts rather than assuming imported data can never change.

### HEVY-06 — Athlete-led execution

The athlete remains free to make practical changes during a strength workout in
Hevy.

Odysseus should use the completed workout as the record of what actually
happened rather than requiring exact adherence to the original prescription.

---

## 14. Hyresult integration

### HYRESULT-01 — HYROX race-specific source

Odysseus must support Hyresult as a source of completed HYROX race data.

This integration is specifically for official HYROX race results and should not
be treated as a general source of training or workout data.

### HYRESULT-02 — Official race result ingestion

Odysseus must be capable of importing an athlete's official HYROX race result
from Hyresult.

The imported result should retain the useful official performance information
made available by the source.

### HYRESULT-03 — Race performance detail

Where available from Hyresult, Odysseus should preserve useful race information
such as:

- overall finishing time;
- event and race category;
- official splits;
- running splits;
- station performance;
- transition or Roxzone information;
- penalties;
- official placing or ranking;
- other relevant official race metrics.

Odysseus should retain only information that is useful for race analysis,
progress tracking, goal evaluation, or future planning.

### HYRESULT-04 — Planned race association

An imported HYROX result should be capable of being associated with the
corresponding HYROX race or target event already known to Odysseus.

The official result should therefore contribute to both completed training
history and evaluation of the athlete's race goal.

### HYRESULT-05 — Complementary Garmin data

A HYROX race may be represented by both:

- a Garmin-recorded activity;
- an official Hyresult race result.

Odysseus must recognise that these records can describe the same real-world
race.

They should be treated as complementary data rather than separate completed
events.

### HYRESULT-06 — Source authority

Where Garmin and Hyresult both describe the same HYROX race, each source should
remain authoritative for the information it measures best.

Hyresult should be treated as the authoritative source for official race
outcomes such as:

- official finishing time;
- official splits;
- penalties;
- placing or ranking.

Garmin should remain the source for relevant device-recorded information such
as:

- heart rate;
- GPS;
- watch-recorded timing;
- other available device telemetry.

Odysseus should combine the useful information from both without unnecessarily
discarding either source.

### HYRESULT-07 — No double-counting

Importing both Garmin and Hyresult information for the same race must not cause
that race to be counted as two completed activities.

Training history, analytics, workload, race completion, and goal progress should
continue to represent one real-world race.

### HYRESULT-08 — Result corrections

Where an official HYROX result changes after initial ingestion, Odysseus should
be capable of reflecting the corrected source data.

Historical race analysis should not remain permanently tied to an official
result that has subsequently been amended.

---

## 15. Athlete interaction and delivery

### UX-01 — Web application

Odysseus must provide a web interface through which the athlete can inspect and
interact with their training information.

### UX-02 — Weekly plan access

The athlete must be able to inspect the current weekly training plan from the
web application.

### UX-03 — Session detail

The athlete must be able to inspect the useful details and purpose of an
individual planned session.

This includes running, strength, and hybrid sessions.

### UX-04 — Availability management

The athlete must be able to manage recurring availability and dated
availability changes.

### UX-05 — Replanning visibility

When availability or another significant change causes the remaining weekly
plan to be adapted, the athlete should be able to understand the resulting
updated plan.

### UX-06 — Matching correction

The athlete must have a practical way to correct planned-to-completed matching
when automatic matching is wrong.

### UX-07 — Weekly notification

Odysseus should be capable of notifying the athlete when the new weekly plan is
ready.

Email may be used as a delivery mechanism, while the web application remains
the primary place to inspect the complete plan.

### UX-08 — Low-friction interaction

Routine use of Odysseus should require minimal administrative effort from the
athlete.

### UX-09 — Understandable decisions

Where Odysseus makes a meaningful automated planning, replanning, or matching
decision, the result should be understandable enough that the athlete can
inspect what happened and, where appropriate, correct it.

### UX-10 — Execution limitation visibility

Where an external execution tool cannot faithfully represent part of a planned
workout, the athlete should be able to understand that limitation.

The athlete should not be left believing that the watch representation is the
complete prescription when meaningful detail exists only in Odysseus.

---

## 16. Privacy, deployment and operational constraints

### OPS-01 — Private deployment

Odysseus is intended to operate as a private system rather than a public
fitness platform.

### OPS-02 — Self-hosting

The system should be capable of being self-hosted on modest personal hardware.

### OPS-03 — Low-resource operation

Normal operation should not require expensive or high-power infrastructure.

### OPS-04 — No mandatory paid cloud

Core Odysseus functionality should not require a paid cloud platform.

### OPS-05 — Local personalised AI

Personalised AI processing should favour local or self-hosted models where
practical.

Athlete data should not be sent to external AI services merely for
convenience.

### OPS-06 — Secrets

Credentials for Garmin, Hevy, Hyresult, authentication, databases, and other
services must not be exposed through the application interface, logs, or
committed source code.

### OPS-07 — Data preservation

The system must retain sufficient historical information to support planning,
analytics, matching, and learning.

It should avoid unnecessary permanent storage of transient implementation
details.

### OPS-08 — Recoverability

The deployed system should support recovery of important athlete data after a
host or storage failure.

### OPS-09 — Observable operation

The running system should provide sufficient operational information to
understand important application behaviour and diagnose failures.

Operational visibility must not expose credentials or unnecessary personal
training data.

### OPS-10 — Reliable automation

Automated processes such as planning, integration synchronisation, result
ingestion, or other background work should fail visibly rather than silently
losing or inventing athlete data.

---

## Requirement principles

These requirements describe product behaviour and product-level constraints.

A technical implementation should be judged by whether it satisfies these
requirements while remaining consistent with the product vision.

Where the requirements leave implementation choices open, the preferred
solution should be the simplest design that satisfies the real product need and
preserves the agreed architectural principles.
