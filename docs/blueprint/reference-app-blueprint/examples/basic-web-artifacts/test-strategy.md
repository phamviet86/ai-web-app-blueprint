---
artifact_id: TEST-READING-001
artifact_type: test-strategy
schema_version: "1.0"
artifact_version: 2
title: Planning test strategy for Reading List
status: draft
owner: example-quality-owner
created_at: 2026-07-12
updated_at: 2026-07-18
scope:
  - system:reading-list
  - journey:book-maintain
source_template: SKEL-TPL-TEST-STRATEGY@1.1.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List test strategy

> Planning portfolio only. No test file, command, environment, or result exists; every `EVID-*` remains `PLANNED` and every linked control remains score `0.00`.

- Observable contracts: Books commands/query, full/partial/fallback route behavior, deterministic local setup.
- Risks: validation, lost update, query bounds, accessibility/focus, migration reproducibility, unsafe logging.
- Out of scope: identity/tenant, async, providers, files, cache, hosted performance, backup restore.

| Failure mode/invariant | Cheapest sufficient layer | Test/data/environment | Negative/concurrency | Cadence/owner |
| --- | --- | --- | --- | --- |
| Validation/archive/version rules | Application test | Fixed clock/ID, controlled store | Invalid input, archived edit, stale version | Default check; Books owner |
| Database constraint/rollback | PostgreSQL integration | Isolated real database | Concurrent stale update, dependency failure | CI-equivalent; data owner |
| Bounded query/order | PostgreSQL integration/plan | Representative synthetic cardinality | Invalid filter/page | Measured checkpoint; data owner |
| Full/partial/fallback/CSRF | Django client + browser | Normal and `HX-Request`, HTMX disabled | Invalid CSRF, server error | Focused route check; presentation owner |
| Keyboard/focus/semantics | Browser accessibility | Critical journey | Validation/conflict focus | Critical smoke; accessibility reviewer |
| Imports/runtime separation | Static architecture check | Repository graph | ORM import from public/presentation | Every check; architecture owner |

## Public contract evidence

| Boundary/consumer | Callable signature and serialized wire shape | `false` / `null` / `0` / empty / omitted/default cases | Compatibility/error/authorization cases | Evidence/result |
| --- | --- | --- | --- | --- |
| Browser -> route -> Books application | `listBooksV1` query and full/fragment result shapes | Explicit filter absence versus false/zero/null where allowed | Malformed query, denied hosted access, full/fragment drift | `EVID-WEB-001` `NOT_EXECUTED` |
| Form -> command -> repository | Create/update/archive input/result/error shapes | Omitted optional fields and declared defaults | Validation, stale version, not found, conflict | `EVID-APP-001`, `EVID-DB-001` `NOT_EXECUTED` |

## Determinism

- Clock/timezone/locale: fixed UTC application time; display timezone explicitly selected.
- ID/randomness: injected deterministic IDs matching the selected persisted identifier shape.
- Import/startup discovery: planned negative fixture imports analysis/test modules without production-only secrets or eager data/network clients.
- Database: `TEST_MUTATION` only, through an in-process guarded isolated target; no production data. Static/planning tasks use `NONE`.
- External protocols: none selected.
- Sensitive data: synthetic book metadata only.

## Architecture fitness

| Check ID | Invariant/scope | Planned command | Positive/negative fixtures and excluded/parser cases | Threshold/baseline | Ratchet/exception | Owner/cadence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `EVID-ARCH-001` | Public/presentation cannot import ORM model/adapter internals | Command unresolved until repo exists | Conforming import plus forbidden import, ignored path and unparsed syntax fixtures | Zero violations/no baseline | No exception planned | Architecture owner/every check |
| `EVID-DB-002` | Query operators/page size are allowlisted/bounded | Test/measurement unresolved | Allowed query plus denied operator, omission/default and over-limit fixtures | 25 rows/page/no baseline | No exception planned | Data owner/scored checkpoint |

- Required command lanes / clean-room environment: unresolved; all six baseline lanes are `NOT_EXECUTED`.
- Passed / failed / skipped / unparsed accounting: no command exists, so no passing evidence is claimed.

## Completion evidence

Planned IDs: `EVID-APP-001`, `EVID-DB-001`, `EVID-DB-002`, `EVID-WEB-001`, `EVID-A11Y-001`, `EVID-ARCH-001`, `EVID-OBS-001`, `EVID-CI-001`, `EVID-MIG-001`. Requested-outcome and pattern-conformance verdicts are both `NOT_EXECUTED`; completion is blocked until exact commands and observed, axis-specific results exist.
