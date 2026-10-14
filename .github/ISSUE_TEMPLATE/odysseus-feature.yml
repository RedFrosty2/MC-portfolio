name: Odysseus feature
description: Plan a bounded Odysseus product capability
title: "[Odysseus] "
labels:
  - "app:odysseus"
body:
  - type: markdown
    attributes:
      value: |
        Use this form for bounded Odysseus product work.

        Keep the issue focused on useful behaviour rather than isolated technical layers.

  - type: input
    id: requirements
    attributes:
      label: Product requirements
      description: List the relevant Odysseus requirement IDs.
      placeholder: "e.g. AVAIL-01, AVAIL-02, UX-04"
    validations:
      required: true

  - type: textarea
    id: product-outcome
    attributes:
      label: Product outcome
      description: What useful behaviour should exist when this issue is complete?
      placeholder: "An athlete can..."
    validations:
      required: true

  - type: textarea
    id: behaviour
    attributes:
      label: Behaviour
      description: Describe the expected product behaviour without prescribing unnecessary implementation detail.
    validations:
      required: true

  - type: textarea
    id: technical-scope
    attributes:
      label: Technical scope
      description: Describe the boundaries and responsibilities expected for this change.
      placeholder: |
        Domain:
        Application:
        Adapter(s):
        Web / presentation:
    validations:
      required: true

  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance criteria
      description: Define observable conditions that must be true for the issue to be complete.
      placeholder: |
        - [ ] ...
        - [ ] ...
    validations:
      required: true

  - type: textarea
    id: architecture-impact
    attributes:
      label: Architecture impact
      description: What architectural boundaries does this feature exercise or change? Write "None" if unchanged.
      placeholder: "Existing boundary used: Web adapter -> Use case -> Domain -> Port <- Adapter"
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: What meaningful behaviours need automated coverage?
      placeholder: |
        - Domain behaviour:
        - Application behaviour:
        - Adapter behaviour:
        - Web / integration path:
    validations:
      required: true

  - type: textarea
    id: documentation-impact
    attributes:
      label: Documentation impact
      description: Which living docs, diagrams, ADRs, or notebooks need updating? Write "None" if no change is required.
    validations:
      required: true

  - type: textarea
    id: out-of-scope
    attributes:
      label: Out of scope
      description: Explicitly state related work that is not part of this issue.
    validations:
      required: true
