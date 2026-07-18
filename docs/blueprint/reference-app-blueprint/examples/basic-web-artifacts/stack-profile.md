---
artifact_id: STACK-READING-001
artifact_type: stack-profile
schema_version: "1.0"
artifact_version: 2
title: Django PostgreSQL HTMX stack plan for Reading List
status: in-review
owner: example-web-team
created_at: 2026-07-12
updated_at: 2026-07-18
scope:
  - system:reading-list
  - tier:basic-web
source_template: REFAPP-TPL-STACK-PROFILE@1.1.0
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

## Application authority binding

- Authority route: not selected; this is a planning bundle, not a preset-instantiated or app-profile-adopted repository.
- Blueprint/preset/source revisions and integrity digests: unresolved.
- Artifact registry/system-profile bindings: `REGISTRY-READING-001` and `SYS-READING-001`; digests not produced.
- Pattern/skill registries: planned below; no package or verifier exists.
- Verification command registry/clean-room evidence: planned below; no command was executed.
- Drift/authority refresh owner: example web team before stack acceptance.

## Acceptance gate

- System/risk and coverage decisions are filled but remain example planning records.
- Blocking spike `EVID-STACK-001` is `PLANNED`; therefore status remains `in-review`.
- Exact Python, PostgreSQL driver, WSGI server, and lockfile versions are unresolved.
- Neither authority route, its registries/digests, nor required clean-room command evidence exists; acceptance is blocked.

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

## Planned analyzer outcome

| Outcome | Task-time classification | Candidate pattern ID | Primary owner skill | Support skills/controls | Missing promotion evidence |
| --- | --- | --- | --- | --- | --- |
| Maintain one reading-list record through create/query/update/archive | `CANDIDATE_GAP` | `PAT-BOOK-MAINTAIN` | Books feature skill planned | Platform DB, shared form, UI and route support planned | Exemplar plus positive/negative verifier |

This is a planning-time analyzer result, not an established pattern-catalog entry. It cannot become `ESTABLISHED_PATTERN` until the missing evidence exists and the selected authority accepts it.

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

## Verification command registry

| Lane | Required / capability-selected | Declared argv/cwd | Environment / approval / side-effect boundary | Clean-room evidence/result |
| --- | --- | --- | --- | --- | --- |
| `install` | Required | Unresolved | Dependency-only; no secrets | `NOT_EXECUTED` |
| `doctor` | Required | Unresolved | Read-only | `NOT_EXECUTED` |
| `test` | Required | Unresolved | Synthetic data; guarded test target when integration is selected | `NOT_EXECUTED` |
| `check` | Required | Unresolved | Read-only/static plus deterministic tests | `NOT_EXECUTED` |
| `build` | Required | Unresolved | No production secret | `NOT_EXECUTED` |
| `start-smoke` | Required | Unresolved | Bounded local startup/readiness/termination | `NOT_EXECUTED` |

## Data-access policy

| Mode | Allowed interface/target | Guard and negative proof | Stop condition/owner |
| --- | --- | --- | --- |
| `NONE` | Current planning and static checks | No connection opens | Default until an executable task selects another mode |
| `LIVE_READ` | Not selected | No live interface exists | Stop if current data is requested |
| `TEST_MUTATION` | Future isolated PostgreSQL target through repo wrapper | Target collision/in-process guard planned | Data owner must accept before integration proof |
| `PRODUCTION_HANDOFF` | Not selected | No production target or operator | Hosted scope requires a new profile/task |

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
