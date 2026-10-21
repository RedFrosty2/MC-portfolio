# Odysseus — Product Glossary

## Purpose

This is the living dictionary of agreed Odysseus product and domain terminology.
Definitions describe product meaning, not a list of implemented Python types.
Product behaviour belongs in [requirements.md](requirements.md), and current
release commitments belong in [scope.md](scope.md).

## Athlete

The person whose training Odysseus supports. Their goals, availability,
preferences, plans, and training history belong to them.

## Goal

An outcome the athlete wants to achieve, such as bench pressing 120 kg. A goal
describes the desired result rather than a training method or programme
milestone.

A goal can exist independently of an event and may have a target date. It may
optionally link to one target event; multiple goals may reference the same event.

An event-linked goal depends on its referenced event. The one-way cancellation
lifecycle is defined under [GOAL-04](requirements.md#goal-04--goal-status).

## Target Event

A dated real-world participation target, such as the Manchester Half Marathon.
The event identifies what the athlete intends to participate in and when; a
linked goal can describe the outcome they want to achieve there.

An event can exist without any goals. An event and an objective are separate
concepts, even when both concern the same race.

## Availability

The periods when the athlete can train, expressed through recurring availability
and dated exceptions. Availability is a hard planning constraint, not a training
preference.

## Rest Day

A day explicitly reserved for rest, with no AM or PM training availability.
Explicit rest is a hard planning constraint. It differs from ordinary
unavailability, where the athlete cannot train but has not designated rest.

## Training Preference

How the athlete would like to train. Examples include two upper-body and two
lower-body strength sessions per week, or 16 weeks of preparation for an event.
The preparation period is an event-specific training preference, not itself a
goal or event.

Preferences are soft planning inputs. The actual plan may differ where there is
a meaningful training reason.

## Explicit Preference

A training preference deliberately stated or set by the athlete. It remains
their stated preference even when Odysseus recommends a different approach.

## Inferred Preference

A possible training preference inferred from observed behaviour, such as
repeated exercise substitutions. It remains distinguishable from an explicit
preference; repetition alone does not make it a hard constraint or a deliberate
athlete instruction.

## Coaching Recommendation

Odysseus's evidence-informed judgement about how best to pursue the athlete's
goals in their individual context. Prescribing three strength sessions instead
of a preferred four is a coaching decision, not a change to the preference.

Recommendations account for feasibility, recovery, adherence, and evidence
quality. They may differ from preferences, but must respect hard availability
and rest constraints and explain meaningful deviations.

## Training Plan

The structured training Odysseus prescribes: sessions, their timing, purpose,
and execution details. A plan applies coaching recommendations to the athlete's
context and may differ from their preferred training structure. Planned work
remains distinct from what the athlete actually completes.

## Planning Context

The relevant athlete facts, constraints, goals, events, preferences, training
history, recovery information, and training evidence supplied to inform a plan.
It describes the situation the planner must consider, rather than prescribing
the answer in advance.

## Training Evidence

Credible research, established practice, and well-supported coaching knowledge
used to inform recommendations. Evidence is considered for its quality and
relevance to the athlete; it does not imply one universally optimal method.

## Future Planning Target

A goal or target event relevant to upcoming training decisions. Storing a goal
or event does not by itself make it a current planning target.

A completed or past event is no longer an upcoming target, but may remain
important historical or recovery context. Passing dates alone do not change
statuses; explicit cancellation follows the
[goal and event lifecycle](requirements.md#goal-04--goal-status).

## Historical Training Context

Past training, completed activities, goals, and events that help explain the
athlete's current situation. Historical information can inform progression,
recovery, and future decisions without being treated as an upcoming target.
