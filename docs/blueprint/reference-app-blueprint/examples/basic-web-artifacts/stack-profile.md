---
artifact_id: STACK-READING-001
artifact_type: stack-profile
schema_version: "1.0"
artifact_version: 1
title: Django PostgreSQL HTMX stack plan for Reading List
status: in-review
owner: example-web-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - tier:basic-web
source_template: REFAPP-TPL-STACK-PROFILE@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List stack profile

> Planning artifact sourced from the [Django/PostgreSQL/HTMX profile](../../../profiles/django-postgresql-htmx.md). No package was installed and no command result was observed.

## Artifact control

- Upstream IDs: `SYS-READING-001`, `COVERAGE-READING-001`.
- Source mapping: `../../../profiles/django-postgresql-htmx.md`; no architecture deviation.
- Target: local showcase.
- Refresh trigger: any version, deployment, capability, or exposure change.

## Acceptance gate

- System/risk and coverage decisions are filled but remain example planning records.
- Blocking spike `EVID-STACK-001` is `PLANNED`; therefore status remains `in-review`.
- Exact Python, PostgreSQL driver, WSGI server, and lockfile versions are unresolved.

## Stack card

| Role | Selection/version | Runtime | Owner path | Primary evidence/status | Replacement seam |
| --- | --- | --- | --- | --- | --- |
| Web/runtime | Django `6.0`; WSGI posture | Server | `config`, thin views | `EVID-STACK-001` `PLANNED` | ASGI selected only by a new runtime need |
| Language/tooling | Python version from supported matrix; exact lock unresolved | Server/tooling | Repository root | `EVID-STACK-001` `PLANNED` | Lockfile/tool contract |
| UI/styling | Django templates + HTMX `2.0.4` + minimal owned CSS | Browser/server HTML | Books presentation | `EVID-WEB-001` `PLANNED` | Native full-page fallback |
| Browser server-state | Not selected | Browser | None | Coverage decision | Add only for proven lifecycle need |
| Identity/session | Not selected for localhost | Server | None | `SYS-READING-001` | Identity port before exposure |
| Authorization/tenancy | Local-only boundary; no tenant | Application | `MOD-BOOKS` | Planning review | Access matrix before exposure |
| SQL/ORM/driver | PostgreSQL `17` target + Django ORM; driver unresolved | Server | Platform DB + Books adapter | `EVID-DB-001` `PLANNED` | `BookStore` port |
| Validation | Django form/request parsing plus application validation | Server | Presentation/application | `EVID-APP-001` `PLANNED` | Public command DTO |
| Storage/email/jobs/cache | Not selected | None | None | `COVERAGE-READING-001` | Add only with selected capability |
| Telemetry/errors | Structured local logs + correlation ID | Server | Platform telemetry | `EVID-OBS-001` `PLANNED` | Exporter seam |
| Testing/fitness | Python/Django tests, PostgreSQL integration, browser accessibility, import check | Test | Repository tooling | `TEST-READING-001` draft | Tool substitutions preserve evidence layers |
| CI/deployment | Clean local command path; no hosted target | Tooling | Repository scripts | `EVID-CI-001` `PLANNED` | Deployment profile required before hosting |

## Executable topology

| Root | Selected by capability | Runtime/deploy unit | Dependencies | Startup/shutdown | Health/owner |
| --- | --- | --- | --- | --- | --- |
| Web | Baseline | One synchronous Django process | Config, logs, PostgreSQL, Books | Validate/start; drain request process | Local liveness; web team |
| Migration | Stored data | Separate management command | Config, PostgreSQL, migrations | Apply and exit | Exit status; data owner |
| Test | `CAP-TEST-FITNESS` | Isolated test process | Test DB and deterministic fixtures | Create/reset/close | Test result; quality owner |
| Worker/CLI labs | Not selected | Absent | None | None | Revisit with async/ops capability |

## Environment adapters

| Capability | Local | Test | Preview/public demo | Production starter |
| --- | --- | --- | --- | --- |
| Database | Guarded Reading List database | Isolated PostgreSQL database | Not selected | Not selected |
| Telemetry | Safe console logs | Captured structured logs | Not selected | Not selected |
| Identity/providers | None | Controlled absence | Not selected | Not selected |

## Compatibility decisions and spikes

| Concern | Result | Evidence | Constraint/owner |
| --- | --- | --- | --- |
| Django/HTMX full and partial response | Conditional | `EVID-STACK-001`, `EVID-WEB-001` planned | Tech lead; direct URLs must render full pages |
| Python/driver/PostgreSQL compatibility | Conditional | `EVID-STACK-001` planned | Tech lead resolves before acceptance |
| Local-only exposure | Pass as planning decision | `SYS-READING-001` | Product owner blocks hosted mutation |

## Configuration inventory

| Variable/class | Server/public/secret | Environments | Owner | Validation/rotation |
| --- | --- | --- | --- | --- |
| Database URL/parts | Server secret | Local/test | Platform DB owner | Required schema; example value only; no production credential |
| Debug/host mode | Server config | Local/test | Web owner | Explicit local-safe values |
| Public config | None selected | None | Web owner | No server config serialized to browser |

## Rejected alternatives

| Alternative | Reason rejected | Revisit trigger |
| --- | --- | --- |
| Full showcase Next/worker/provider stack | No selected async, provider, tenant, or rich-client need | Capability tier changes |
| ASGI/async views | No long-lived/async runtime requirement | Measured async need appears |
