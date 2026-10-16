# Odysseus — Development Guide

## Purpose

This document defines the development workflow and repository conventions used
for Odysseus within the wider monorepo.

Odysseus lives under:

`apps/Odysseus/`

Application-specific code, tests, documentation, dependencies, version history,
and tooling configuration should remain within this directory wherever
practical.

Repository-level GitHub integration remains at the monorepo root.

---

# Development flow

Meaningful product work should follow this path:

`Requirement -> GitHub Issue -> Branch -> Pull Request -> CI -> Squash Merge`

The purpose of this flow is to keep product intent, implementation, testing, and
history traceable without introducing a separate traceability system.

Every stage should follow a consistent template or naming convention so the
history of Odysseus remains easy to understand.

---

## 1. Product requirements

Product requirements are defined in:

`apps/Odysseus/docs/product/requirements.md`

Requirements use stable identifiers such as:

- `AVAIL-01`
- `PLAN-03`
- `RUN-05`

Development work should reference the relevant requirement identifiers rather
than duplicating the requirement text.

One requirement may contribute to several development issues.

One development issue may satisfy several requirements.

A requirement does not map one-to-one with a branch or Pull Request.

---

## 2. GitHub Issues

A GitHub Issue represents a bounded piece of development work.

Issues should describe useful product behaviour rather than isolated technical
layers.

Good:

`[Odysseus] Manage recurring training availability`

Avoid:

`[Odysseus] Create availability repository`

Issues should use a consistent template containing:

- relevant product requirements;
- product outcome;
- expected behaviour;
- technical scope;
- acceptance criteria;
- architecture impact;
- testing expectations;
- documentation impact;
- explicit out-of-scope work.

Issues should use the GitHub label:

`app:odysseus`

The standard Odysseus Issue template should be used where applicable.

---

## 3. Branches

Branches should identify both the type of change and the application.

Format:

`<type>/odysseus/<issue-number>-<short-description>`

Supported types:

- `feat`
- `fix`
- `refactor`
- `spike`
- `docs`

Examples:

- `feat/odysseus/12-recurring-availability`
- `fix/odysseus/38-invalid-plan-validation`
- `spike/odysseus/44-local-model-evaluation`
- `docs/odysseus/51-planner-architecture`

Branch names should remain short and describe the issue rather than individual
implementation details.

---

## 4. Development

Implementation should follow the architectural principles defined in:

`apps/Odysseus/docs/architecture/principles.md`

Development should favour small end-to-end product capabilities rather than
building complete technical layers in isolation.

Introduce files, abstractions, dependencies, infrastructure, and adapters only
when the current feature requires them.

Do not create future-facing scaffolding simply because it appears in an
architecture diagram or is expected to be needed eventually.

Before implementation begins, the intended code shape and architectural impact
should be understood.

If implementation reveals a new architectural decision, pause the feature and
make that decision explicitly before continuing.

---

## 5. Development commits

Development commits on a feature branch may be small and practical.

They do not need to form the permanent public history of the application because
the Pull Request will normally be squash merged.

Development commit messages should still be clear enough to understand the
working history of the branch.

A simple imperative style is preferred:

- `Add recurring availability model`
- `Add availability update use case`
- `Render recurring availability form`
- `Fix PM availability parsing`

Avoid vague messages such as:

- `changes`
- `fix stuff`
- `wip`
- `updates`

---

## 6. Pull Requests

A Pull Request represents the reviewable implementation of a development issue.

PR titles should make the application explicit.

Example:

`[Odysseus] Manage recurring training availability`

The PR should reference and close the corresponding Issue where appropriate.

For example:

`Closes #12`

The standard repository Pull Request template should be used.

The PR should make clear:

- which application is affected;
- what changed;
- why the change was required;
- which requirements are affected;
- which Issue it implements;
- how the behaviour was verified;
- whether documentation changed;
- whether architecture changed.

A Pull Request should remain focused on the Issue it implements.

Unrelated cleanup should normally be handled separately.

---

## 7. Squash merge convention

Pull Requests should normally be squash merged so that `main` receives one
clear commit representing the completed Issue.

The squash commit is part of the permanent history of Odysseus and must be
sufficient to understand both:

- **what changed**;
- **why it changed**.

The squash commit should therefore contain a concise conventional subject and a
short explanatory body.

### Subject format

`<type>(odysseus): <product or engineering outcome>`

Examples:

- `feat(odysseus): manage recurring training availability`
- `fix(odysseus): reject plans scheduled on rest days`
- `docs(odysseus): document local LLM planning boundary`
- `refactor(odysseus): simplify planning context construction`

### Body format

The body should contain:

```text
Why:
<reason this change was needed>

Changed:
- <important change>
- <important change>

Requirements:
<requirement IDs>

Issue:
#<issue-number>
```

Example:

```text
feat(odysseus): manage recurring training availability

Why:
Odysseus needs an authoritative recurring availability baseline before it can
generate weekly training plans.

Changed:
- added recurring AM / PM availability for all seven weekdays
- represented explicit rest separately from unavailability
- added application use cases and a web workflow for viewing and updating the week

Requirements:
AVAIL-01, AVAIL-02, AVAIL-03, UX-04

Issue:
#12
```

The squash commit should describe the meaningful outcome rather than listing
every file or low-level implementation detail.

This gives `main` a concise but useful application history without requiring
every development commit to be permanent documentation.

---

## 8. Dependency and environment management

Odysseus uses `uv` for Python version management, virtual environments,
dependency management, dependency locking, and project command execution.

The currently required uv version is:

`0.11.21`

The required version is declared in `pyproject.toml` so local development and CI
use the same uv release.

The Odysseus Python project is defined by:

- `pyproject.toml` — project metadata, direct dependencies, development
  dependencies, tool configuration, and the required uv version;
- `uv.lock` — the exact resolved dependency graph used for reproducible
  environments;
- `.python-version` — the Python version expected by the project.

`pyproject.toml`, `uv.lock`, and `.python-version` are committed to version
control.

The generated `.venv/` directory is local environment state and must not be
committed.

Odysseus uses a project-local uv environment rather than a shared Conda
environment.

Dependencies should normally be managed using uv commands rather than by
directly installing packages with pip or Conda.

Runtime dependencies are added with:

```bash
uv add <package>
```

Development-only dependencies are added with:

```bash
uv add --dev <package>
```

Dependencies are removed using the corresponding `uv remove` command.

The local project environment is created or synchronized with:

```bash
uv sync
```

Project commands should normally be run through uv:

```bash
uv run <command>
```

For example:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

GitHub Actions uses the same project definition, Python version, uv version, and
lockfile as local development.

CI synchronizes dependencies using:

```bash
uv sync --locked
```

The `--locked` option ensures CI fails if `pyproject.toml` and `uv.lock` are
inconsistent rather than modifying the committed dependency resolution.

Each application in the monorepo should manage its Python environment and
dependency resolution independently unless a demonstrated need for a shared
workspace emerges.

Odysseus is therefore not currently part of a monorepo-wide uv workspace.

---

## 9. Continuous integration

GitHub Actions workflows live at the monorepo level under:

`.github/workflows/`

Odysseus-specific workflow configuration should remain as small as practical
and should only run when relevant Odysseus paths change.

Application-specific tooling and quality configuration belongs within the
Odysseus application, primarily in:

`apps/Odysseus/pyproject.toml`

The GitHub Actions workflow should invoke that application-owned tooling rather
than duplicate configuration at repository level.

Odysseus quality checks should run when relevant files under
`apps/Odysseus/` change, while still allowing the repository-level required CI
gate to complete successfully when a Pull Request does not affect Odysseus.

The initial required quality gates are:

- Ruff lint checks;
- Ruff formatting checks;
- mypy static type checking for production source code;
- pytest.

The repository-level workflow may use a lightweight change-detection step to
avoid unnecessary Odysseus setup and test execution for unrelated monorepo
changes.

The required branch-protection check should remain stable regardless of whether
Odysseus-specific checks were needed for a particular Pull Request.

CI installs the uv version required by `pyproject.toml`, installs the pinned
Python version, and synchronizes the committed dependency environment before
running quality checks.

CI verifies submitted code.

It should not automatically modify source files.

Typical local commands are run through the Odysseus uv environment:

```bash
uv run ruff check --fix .
uv run ruff format .
uv run mypy src
uv run pytest
```

Equivalent CI checks should use non-mutating commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

The repository-level GitHub Actions workflow exposes a stable required status
check:

`Odysseus CI / Required gate`

This check must pass before an Odysseus Pull Request can be merged.

Additional quality gates should only be introduced when they protect against a
real project risk.

---

## 10. Repository protection and merge policy

The `main` branch is protected using GitHub repository rules.

Normal development changes must reach `main` through a Pull Request rather than
through direct development pushes.

The repository is configured so that:

- Pull Requests are required before changes reach `main`;
- required CI status checks must pass before merge;
- the `Odysseus CI / Required gate` check is used as the stable Odysseus CI gate;
- linear history is required;
- force pushes to `main` are blocked;
- squash merging is the standard merge method;
- merge commits and rebase merging are disabled;
- merged head branches are automatically deleted.

Required status checks do not currently require a branch to be fully up to date
with `main` before merging.

This avoids unnecessary rebuilds while still requiring the submitted change to
pass the configured quality checks.

Reviewer approval is not currently mandatory because Odysseus is being developed
as a personal project.

The protection policy should become stricter only when repository ownership or
collaboration needs justify it.

---

## 11. Testing

Tests should verify meaningful behaviour at the appropriate boundary.

Prefer:

- real domain values for domain behaviour;
- real lightweight adapters where they improve confidence;
- dependency injection for application boundaries;
- mocks where isolation provides a clear benefit.

Tests should describe behaviour rather than requirement identifiers.

For example:

`test_rest_day_cannot_be_scheduled_for_training`

is preferable to:

`test_avail_03`

Requirement traceability belongs in the Issue and Pull Request rather than in
test names.

Production source code is statically type checked with mypy.

Tests are not required to pass mypy unless a future project need justifies
extending static type checking to the test suite.

---

## 12. Documentation impact

Every meaningful development Issue should consider whether existing
documentation needs to change.

Possible impacts include:

- product requirements;
- current release scope;
- workflows;
- architecture overview;
- architecture principles;
- PlantUML diagrams;
- ADRs;
- engineering guidance;
- explanatory notebooks.

Documentation should be updated when the implemented behaviour or architecture
would otherwise make the current documentation inaccurate.

Do not create documentation purely to record implementation chronology.

Git history, Issues, and Pull Requests already provide that history.

---

## 13. Architecture Decision Records

Significant architectural decisions should be recorded under:

`apps/Odysseus/docs/architecture/decisions/`

An ADR is appropriate when a decision:

- materially affects system structure;
- establishes an important dependency boundary;
- selects between meaningful architectural alternatives;
- is likely to be questioned or revisited later.

ADRs should not be created for routine implementation choices.

Once accepted, an ADR records the reasoning at the time of the decision.

If the decision later changes, prefer a new ADR that supersedes the earlier one
rather than rewriting historical reasoning.

---

## 14. Application versioning

Odysseus is versioned independently from other applications in the monorepo.

Application versions use:

`MAJOR.MINOR.PATCH`

Examples:

- `v0.1.0`
- `v0.1.1`
- `v0.2.0`

Repository Git tags should namespace the application:

- `odysseus-v0.1.0`
- `odysseus-v0.1.1`
- `odysseus-v0.2.0`

The current release scope is defined in:

`apps/Odysseus/docs/product/scope.md`

Released changes are recorded in:

`apps/Odysseus/CHANGELOG.md`

`scope.md` moves forward with the active release.

`CHANGELOG.md` preserves the human-readable release history.

Git tags preserve the exact repository state for each release.

Notable changes should be added to the `Unreleased` section of
`apps/Odysseus/CHANGELOG.md` as part of the Pull Request that introduces them.

Internal implementation details, routine refactors, test-only changes, and
development-process changes should not be recorded unless they materially affect
the application or its operation.

---

## 15. Monorepo boundary

Odysseus should remain self-contained within `apps/Odysseus/` unless something
is genuinely shared across applications.

Do not move code into shared monorepo packages merely because another
application might theoretically use it later.

Shared code should be created only when there is a demonstrated
cross-application need and an appropriate ownership boundary is understood.

Changes outside `apps/Odysseus/` should be deliberate and should be called out
in the relevant Issue and Pull Request.

---

## 16. Convention summary

The standard conventions are:

### Issue title

`[Odysseus] <product outcome>`

### Issue label

`app:odysseus`

### Branch

`<type>/odysseus/<issue-number>-<short-description>`

### Pull Request title

`[Odysseus] <product outcome>`

### Development commit

Short imperative description of the working change.

### Squash commit subject

`<type>(odysseus): <product or engineering outcome>`

### Squash commit body

```text
Why:
...

Changed:
- ...
- ...

Requirements:
...

Issue:
#...
```

### Python environment

Odysseus uses uv `0.11.21` with a project-local environment.

`pyproject.toml`, `uv.lock`, and `.python-version` define the reproducible
project environment.

`.venv/` is generated locally and is not committed.

### Main branch

Protected by GitHub rules. Changes normally arrive through a Pull Request,
required CI must pass, and Pull Requests are squash merged.

### Required CI gate

`Odysseus CI / Required gate`

### Release tag

`odysseus-v<major>.<minor>.<patch>`

These conventions should remain stable unless a real repository need justifies
changing them.

---

# Working principle

The development process should preserve a clear chain:

`Product intent -> Development work -> Verified behaviour -> Clean history`

The workflow exists to make development easier to understand and maintain.

It should not become ceremony for its own sake.
