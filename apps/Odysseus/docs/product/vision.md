# Odysseus — Product Vision

## Purpose

Odysseus is a personal training, planning and analytics system designed to bring
running, strength training, recovery, availability, goals, and completed
training into one coherent workflow







Garmin and Hevy remain the recoding and execution tools - Odysseus sits above them. It plans training, understands the athlete's wider context, brings completed
activity data together, compares planned and completed work, learns from
training behaviour over time, and uses that understanding to improve future
plans.


## The problem Odysseus solves

Training information is naturally fragmented.

Running data and body metrics lives in Garmin.
Strength work lives in Hevy.
Goals and races exist separately from either.
Availability changes from week to week.
Completed training rarely matches the an intended training plan perfectly.

Each specialist application can perform its own job well, but none has the full
picture.

That makes it difficult to answer questions such as:

- What should I train this week?
- How should running and strength fit together?
- Does this week's plan reflect my current availability?
- What did I actually complete compared with what was planned?
- Am I progressing toward my goals?
- Should next week's plan change because of what happened this week?
- Which substitutions or training patterns do I repeatedly prefer?

Odysseus exists to provide that wider context.


## Product philosophy

Odysseus should coordinate specialist tools rather than compete with them.

The system should use the best execution surface for each activity while
providing the planning, context, comparison, and learning that those individual
tools cannot provide alone.

The core training loop is:

Plan
-> Execute
-> Capture
-> Compare
-> Learn
-> Replan



 - A plan should be informed by goals, availability, training history, and current
context.

- Execution should happen through familiar specialist tools.

- Completed activity should flow back into Odysseus.

- Odysseus should then compare intention with reality, understand meaningful
differences, and use that information when future plans are produced.


## The intended experience

Odysseus should be low-friction, an athlete should not need to spend significant time maintaining the system.

A normal week should eventually feel approximately like this:

- On Sunday, Odysseus prepares the next week's training using appropriate context (previous data, goals and athlete availability) and the athlete can see the complete week in one place, including running, strength, rest and unavailablity

- Planned running sessions are sent through to the linked Garmin device and completed during the week.

- Strength sessions are carried out using Hevy during the week.

- Odysseus gathers those results, compares them with the plan, and keeps the
history needed to understand progress.

- Over time, the system should become increasingly useful because it understands
the athlete's training history, preferences, goals, and behaviour.

## Planning philosophy

Each planned session should have a clear purpose and should fit into the wider
week and longer-term objective.

Availability and explicit rest requirements are hard constraints.

The system should distinguish between meaningful deviations and harmless
variation. For example, completing slightly less distance than planned may still represent
the intended session.

Completing a fundamentally different workout than planned should not be silently treated as
the same session but should still be preserved as part of the athlete's real training history.

Odysseus should adapt to reality rather than force reality to fit the plan.

## Learning over time

Odysseus should become more useful over time. Learning should come from real behaviour rather than requiring constant manual
configuration.

Repeated substitutions, training preferences, successful progressions, missed
sessions, completed workloads, and changing performance can all provide useful
context for future planning.

However, learning must not blindly optimise for preference.

Training effectiveness and the athlete's goals remain more important than
simply repeating what is most comfortable or familiar.

The system should therefore balance:

- athlete preference
- training effectiveness
- current context
- long-term goals

## Trust and transparency

The athlete should be able to understand why the system behaves as it does.

Important recommendations and training decisions should have an understandable
reason. The system should avoid unexplained automation where the consequence matters.

Training history should remain inspectable.

Planned and completed activity should remain distinguishable.

Automatic matching or planning decisions should be correctable where
appropriate.

## Privacy and ownership

Odysseus is intended to operate as a private personal system.

Training history, body metrics, goals, preferences, and related personal data
should remain under the user's control.

The long-term system may support a small number of users, but each person's
training data must remain private to them.

The product should favour local or self-hosted processing where practical,
particularly for personalised AI functionality.

External services should be used deliberately rather than becoming unnecessary
dependencies.

## What success looks like

A successful Odysseus should make training feel more connected.

The athlete should be able to understand:

- what they are doing
- why they are doing it
- what they actually completed
- how they are progressing

The system should reduce planning effort rather than create administrative
work.

It should integrate naturally with the tools already used for training.

It should preserve useful history without becoming a data warehouse for its
own sake.

Most importantly, it should become increasingly valuable over time as it builds
a coherent understanding of the athlete and their training.

Odysseus should eventually feel less like a collection of fitness features and
more like a single, continuously informed training system.