---
artifact_id: FEATURE-READING-BOOKS-001
artifact_type: feature-plan
schema_version: "1.0"
artifact_version: 1
title: Books module public-contract plan
status: accepted
owner: example-books-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - module:books
source_template: REFAPP-TPL-FEATURE-PLAN@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: `MOD-BOOKS` feature plan

> Accepted contract design for `CAP-CRUD` and `CAP-QUERY`. Implementation and every `EVID-*` result remain absent.

## Artifact control

- Upstream IDs: `COVERAGE-READING-001`, `DATA-READING-001`, `PLATFORM-READING-001`.
- Trace scope: `CAP-CRUD`, `CAP-QUERY`; `MOD-BOOKS`; `ROUTE-BOOK-*`; `JRN-BOOK-MAINTAIN`.
- In scope: create, list/search, edit with version, archive.
- Out of scope: identity, tenancy, restore command, files, import, event, worker, provider, cache.
- Allowed dependencies: shared pure result/error concepts and application-owned `BookStore`; no ORM type crosses the public surface.

## Public contracts

| Kind | Name/version | Input/output/error | Access | Idempotency/concurrency/freshness |
| --- | --- | --- | --- | --- |
| Command | `createBookV1` | Title/author -> `BookDetail`; validation/conflict/dependency error | Local-only entry boundary | One committed result; duplicate browser submit remains an observed-risk test |
| Command | `updateBookV1` | ID/version/title/author -> `BookDetail`; not-found/conflict/domain error | Local-only entry boundary | Expected version prevents lost update |
| Command | `archiveBookV1` | ID/version -> archived result; not-found/conflict/domain error | Local-only entry boundary | Expected version; repeat returns stable domain result |
| Query | `listBooksV1` | `q`, status, page -> bounded `Page<BookSummary>` | Local-only entry boundary | 25 rows/page; stable title then ID order; current database state |
| Event | Not selected | No public event contract | — | New capability decision required |

## Application and domain

- Use cases/invariants: normalize and require title/author; archived records cannot be edited; list operators are allowlisted.
- Transaction policy: one bounded command transaction; no remote I/O; version conflict is typed.
- Application-owned ports: `BookStore`, `Clock`, `IdGenerator` where deterministic inputs are needed.
- Degraded behavior: database unavailable returns safe dependency failure; no false empty success.

## Adapters and entrypoints

| Port/entrypoint | Adapter | Runtime | Failure/recovery |
| --- | --- | --- | --- |
| `BookStore` | Django ORM/PostgreSQL adapter | Server | Translate database conflict/dependency failures; rollback command |
| Full/partial web view | Django view + template/fragment | WSGI posture | Same application contract; full redirect/page fallback |
| Test root | Controlled port + real PostgreSQL adapter tests | Test | Deterministic reset |

## Presentation

| Route/job | User outcome | States | Accessibility |
| --- | --- | --- | --- |
| `ROUTE-BOOK-LIST` | Search/page records | Loading, empty, validation, dependency error | Semantic list/form, keyboard access, stable focus target |
| `ROUTE-BOOK-CREATE` | Create record | Form errors and successful redirect/swap | Labels, error association, focus first error/result heading |
| `ROUTE-BOOK-EDIT` | Edit current version | Not-found/conflict/domain/dependency | Conflict explanation and recoverable navigation |
| `ROUTE-BOOK-ARCHIVE` | Archive record | Confirmation, conflict, result | Native POST fallback and announced result |

## Evidence

| Failure mode/invariant | Lowest sufficient layer | Evidence ID/status | Exit gate | Parent consumers |
| --- | --- | --- | --- | --- |
| Validation/archive rule/version conflict | Application tests | `EVID-APP-001` `PLANNED` | Focused behavior passes | `CTL-CONTRACT-OWNERSHIP-01`, `CTL-TEST-RISK-01` |
| Constraint/transaction/concurrent update | PostgreSQL integration | `EVID-DB-001` `PLANNED` | One effect or typed conflict | `CTL-DATA-INTEGRITY-01`, `GATE-GREENFIELD-01` |
| Bounded query/order/plan | PostgreSQL integration/measurement | `EVID-DB-002` `PLANNED` | Page and representative plan meet target | `CTL-UX-CAPACITY-01` |
| Full/partial/fallback mapping | HTTP/browser | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` | Same contract and accessible journey | `CTL-UX-NATIVE-01`, `CTL-UX-BUDGET-01` |
