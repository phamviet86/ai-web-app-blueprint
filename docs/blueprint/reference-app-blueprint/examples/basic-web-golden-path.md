---
example_id: REFAPP-EXAMPLE-BASIC-WEB-GOLDEN
title: BASIC_WEB Golden Path Artifact Bundle Index
status: example
audience: human-and-ai
verified_on: 2026-07-12
depends_on:
  - ../README.md
  - ../02-capability-coverage-and-domain.md
  - ../../profiles/django-postgresql-htmx.md
---

# `BASIC_WEB` golden path: Reading List artifact index

> This is a fictional **planning bundle**, not source code or runtime proof. All `EVID-*` entries are `PLANNED`; no install, build, test, migration, browser, deployment, recovery, or production observation is claimed.

The bundle demonstrates parent artifact schema `1.0`, reference lifecycle/statuses, capability-to-control traceability, and a fail-closed readiness calculation for a local Reading List example.

## Schema-conformant artifacts

| Artifact | Type/status | Purpose |
| --- | --- | --- |
| [Artifact registry](basic-web-artifacts/artifact-registry.md) | `artifact-registry` / `draft` | Stable IDs, versions, statuses, paths, and review dates |
| [System profile](basic-web-artifacts/system-profile.md) | `system-profile` / `draft` | Local-only risks, topology, data, objectives, and control universe |
| [Stack profile](basic-web-artifacts/stack-profile.md) | `stack-profile` / `in-review` | Django/PostgreSQL/HTMX mapping with unresolved compatibility spike |
| [Capability coverage](basic-web-artifacts/capability-coverage.md) | `capability-coverage` / `accepted` | `BASIC_WEB` selection and `CAP/EVID -> CTL/GATE` bridge |
| [Data model](basic-web-artifacts/data-model.md) | `data-model` / `accepted` | One authoritative `DATA-BOOKS` record model |
| [Platform plan](basic-web-artifacts/platform-plan.md) | `platform-plan` / `in-review` | Config, PostgreSQL, telemetry, and executable roots only |
| [Books feature plan](basic-web-artifacts/feature-books.md) | `feature-plan` / `accepted` | Public commands/query and planned failure evidence |
| [Route map](basic-web-artifacts/route-map.md) | `route-map` / `accepted` | Full/partial/fallback routes and `JRN-BOOK-MAINTAIN` |
| [Test strategy](basic-web-artifacts/test-strategy.md) | `test-strategy` / `draft` | Risk-routed planned checks and fitness evidence |
| [Local release plan](basic-web-artifacts/release-plan.md) | `release-plan` / `draft` | No-go gates and bounded recreate-only recovery |
| [Reference application plan](basic-web-artifacts/reference-app-plan.md) | `reference-app-plan` / `draft` | Artifact registry, end-to-end trace, control bridge, slices, and completion gaps |
| [Readiness assessment](basic-web-artifacts/readiness-assessment.md) | `readiness-assessment` / `draft` | Human-readable fail-closed assessment |

Shared-plan, SLO/runbook, access-matrix, and threat-model artifacts are not created because the selected local scope records explicit `not-required` applicability decisions with owners and revisit triggers. That does not remove any baseline catalog control.

## Machine-readable readiness closure

- Input: [readiness.json](basic-web-artifacts/readiness.json).
- Catalog/scorer: `1.0.0` / `1.0.0`.
- Coverage: all 40 `CTL-*` controls and four `GATE-*` rows.
- Honest evidence posture: every control has an empty observed-evidence list and effective score `0.00`; the applicable greenfield gate has a planning reference and `passed: false`.
- Expected result: `not-ready`, total `0.00/10`, eight named critical gaps, failed `GATE-GREENFIELD-01`, and no structural scorer errors.

Reproduce from the package root:

```text
python3 docs/blueprint/scripts/score_readiness.py docs/blueprint/reference-app-blueprint/examples/basic-web-artifacts/readiness.json --json --expect not-ready
```

The artifact bundle may guide a real project only after copying it to project-local governance paths, replacing fictional owners/scope, resolving the stack, implementing slices, recording exact observed evidence, and re-running the scorer. Its accepted design artifacts do not make the draft system, stack, plan, implementation, or deployment ready.
