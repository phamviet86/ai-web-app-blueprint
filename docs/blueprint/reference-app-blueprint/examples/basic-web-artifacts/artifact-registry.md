---
artifact_id: REGISTRY-READING-001
artifact_type: artifact-registry
schema_version: "1.0"
artifact_version: 2
title: Artifact registry for the BASIC_WEB Reading List example
status: draft
owner: example-governance-owner
created_at: 2026-07-12
updated_at: 2026-07-18
scope:
  - system:reading-list
  - tier:basic-web
source_template: SKEL-TPL-ARTIFACT-REGISTRY@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List artifact registry

> Draft registry for fictional planning artifacts. Paths are live package examples; statuses grant no implementation or readiness claim.

| Artifact ID | Type | Version | Status | Scope | Owner | Path/evidence locator | Updated | Review | Supersession | Note |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| `REGISTRY-READING-001` | artifact-registry | 2 | draft | system | example-governance-owner | This file | 2026-07-18 | 2026-08-12 | none | Example registry |
| `SYS-READING-001` | system-profile | 1 | draft | system/tier | example-product-owner | [system profile](system-profile.md) | 2026-07-12 | 2026-08-12 | none | Human acceptance absent |
| `STACK-READING-001` | stack-profile | 2 | in-review | system/tier | example-web-team | [stack profile](stack-profile.md) | 2026-07-18 | 2026-08-12 | none | Compatibility spike planned |
| `COVERAGE-READING-001` | capability-coverage | 1 | accepted | system/tier | example-product-owner | [coverage](capability-coverage.md) | 2026-07-12 | 2026-08-12 | none | Planning decision only |
| `DATA-READING-001` | data-model | 1 | accepted | module | example-books-team | [data model](data-model.md) | 2026-07-12 | 2026-08-12 | none | Logical design only |
| `PLATFORM-READING-001` | platform-plan | 1 | in-review | system/tier | example-web-team | [platform plan](platform-plan.md) | 2026-07-12 | 2026-08-12 | none | Runtime unresolved |
| `FEATURE-READING-BOOKS-001` | feature-plan | 1 | accepted | module | example-books-team | [feature plan](feature-books.md) | 2026-07-12 | 2026-08-12 | none | Contract design only |
| `ROUTES-READING-001` | route-map | 2 | accepted | journey | example-presentation-team | [route map](route-map.md) | 2026-07-18 | 2026-08-12 | none | Route design only |
| `TEST-READING-001` | test-strategy | 2 | draft | journey | example-quality-owner | [test strategy](test-strategy.md) | 2026-07-18 | 2026-08-12 | none | All evidence planned |
| `RELEASE-READING-001` | release-plan | 1 | draft | local target | example-operations-owner | [release plan](release-plan.md) | 2026-07-12 | 2026-08-12 | none | No release evidence |
| `PLAN-READING-001` | reference-app-plan | 1 | draft | system/tier | example-web-team | [reference plan](reference-app-plan.md) | 2026-07-12 | 2026-08-12 | none | Blocked by upstream plans |
| `ASSESSMENT-READING-001` | readiness-assessment | 1 | draft | planning target | example-review-owner | [assessment](readiness-assessment.md), [JSON](readiness.json) | 2026-07-12 | 2026-08-12 | none | `0.00`, not-ready |

## Registry invariants

- Every artifact metadata ID/status/version above matches its file.
- No supersession, exception, or tombstone exists in this first fictional version.
- Shared plan, SLO/runbook, access matrix, and threat model are `not-required` applicability decisions in `PLAN-READING-001`, not artifact statuses.
- Any implementation or evidence change increments the affected artifact version and updates this registry.
