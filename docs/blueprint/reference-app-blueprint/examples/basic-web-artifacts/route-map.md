---
artifact_id: ROUTES-READING-001
artifact_type: route-map
schema_version: "1.0"
artifact_version: 2
title: Reading List route and journey map
status: accepted
owner: example-presentation-team
created_at: 2026-07-12
updated_at: 2026-07-18
scope:
  - system:reading-list
  - journey:book-maintain
source_template: REFAPP-TPL-ROUTE-MAP@1.1.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List routes and journey

> Accepted route design for selected `CAP-CRUD`, `CAP-QUERY`, and `CAP-ACCESSIBILITY`; no route or browser behavior has been observed.

## Artifact control

- Upstream IDs: `STACK-READING-001`, `COVERAGE-READING-001`, `FEATURE-READING-BOOKS-001`.
- Stack/router: Django URL/view/template mapping with HTMX progressive enhancement.
- Exposure: localhost only; identity/access must be redesigned before hosted mutation.

## Routes and entrypoints

| Route ID | Path/method | Access | Runtime | Public contract | Query/freshness | States/a11y | Evidence/status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ROUTE-BOOK-LIST` | `GET /books?q=&status=&page=` | Local-only | Server full page or HTMX fragment | `listBooksV1` | Bounded current query | Empty/error/page controls; stable focus | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` |
| `ROUTE-BOOK-CREATE` | `GET/POST /books/new` | Local-only | Native form; optional HTMX swap | `createBookV1` | No cache | Validation/result focus; full redirect fallback | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` |
| `ROUTE-BOOK-EDIT` | `GET/POST /books/<id>/edit` | Local-only | Native form; optional HTMX swap | `updateBookV1` | Versioned detail | Not-found/conflict/errors | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` |
| `ROUTE-BOOK-ARCHIVE` | `POST /books/<id>/archive` | Local-only; CSRF proof | Server command | `archiveBookV1` | Versioned command | Confirmation/conflict/announced result | `EVID-WEB-001` `PLANNED` |
| `ROUTE-HEALTH-LIVE` | `GET /health/live` | Local-safe | Web root | Liveness only | No dependency detail | Plain semantic result | `EVID-STACK-001` `PLANNED` |

Request/result mapping keeps explicit `false`, `null`, `0`, empty and omitted/default states distinct. Planned fixtures use the persisted identifier shape selected by the data model and an explicit display timezone.

## Surface state and action evidence

| Route/surface | Loading / empty / error / stale / denied / success | Focus / keyboard / announcements | Responsive viewports/input | Pending / rapid repeat / double-submit / result behavior | Evidence status |
| --- | --- | --- | --- | --- | --- |
| `ROUTE-BOOK-LIST` | All six states specified; denied is a deployment-boundary result, not empty | Heading/result focus and keyboard paging planned | Narrow list and wide table; keyboard/pointer | Search refresh retains declared stale state; no mutation | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` |
| Create/edit form | Loading/error/denied/success plus validation/conflict states | First error then result focus; announced summary | Single-column narrow/wide; keyboard/pointer | Preserve submitted values; block rapid repeat; server conflict still authoritative | `EVID-WEB-001`, `EVID-A11Y-001` `PLANNED` |
| Archive action | Error/denied/success/conflict/ambiguous result | Confirmation and result focus planned | Native control at all viewports | One pending intent; second activation test and committed-success refresh planned | `EVID-WEB-001` `PLANNED` |

## Critical journeys

| Journey ID | Persona/start | Route/command sequence | Data effects | Failure/degraded/action-result path | Evidence/status |
| --- | --- | --- | --- | --- | --- |
| `JRN-BOOK-MAINTAIN` | Local operator at list | List -> create -> search -> edit -> archive -> active filter | One row created, versioned update, status archived | Validation, stale version, database unavailable, HTMX disabled | `EVID-APP-001`, `EVID-DB-001`, `EVID-WEB-001`, `EVID-A11Y-001` all `PLANNED` |

## Navigation and capability visibility

| Persona/capability | Destinations/actions | Server authorization | Denied/hidden policy |
| --- | --- | --- | --- |
| Local operator / selected `CAP-*` | Books list/create/edit/archive | Local-only deployment guard; application still validates intent | Hosted/public access blocked until identity/access artifacts exist |

## Framework mapping

- App shell renders full documents; named fragments render only for `HX-Request`.
- Direct URL and native form behavior remain functional without HTMX.
- Server presentation calls `MOD-BOOKS` public application contracts, never an internal HTTP route.
- History/focus/cache variation behavior is owned by `EVID-WEB-001` and `EVID-A11Y-001`.
