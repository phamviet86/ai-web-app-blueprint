---
artifact_id: SYS-READING-001
artifact_type: system-profile
schema_version: "1.0"
artifact_version: 1
title: Planning profile for the BASIC_WEB Reading List example
status: draft
owner: example-product-owner
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - tier:basic-web
source_template: SKEL-TPL-SYSTEM-PROFILE@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List system and risk profile

> Fictional planning artifact. It contains accepted-looking decisions for review, but its `draft` status grants no authority and it contains no runtime evidence.

## Ownership

- System/product: local Reading List showcase.
- Decision owner: example product owner.
- Technical owner: example web team lead.
- Operations/security/data owners: example web team lead / security reviewer / product owner.
- Support/incident communication owners: example product owner during local evaluation.
- Date, approval state, and revisit trigger: 2026-07-12, draft; revisit before implementation or any non-local exposure.

## Primary architecture profile

- Primary profile and why it dominates: content/interaction plus simple transactional CRUD; one bounded record lifecycle dominates.
- Secondary profiles and bounded concerns: read-heavy only for bounded search/page; no async, integration, tenancy, file, or regulated profile selected.

## Critical journeys

| Journey | Users/actors | Success | Unacceptable failure | Peak/load shape |
| --- | --- | --- | --- | --- |
| `JRN-BOOK-MAINTAIN` | One local operator | Create, search, edit, and archive one book through full-page and enhanced paths | Lost committed change, duplicate effect, unbounded list, inaccessible form result | Local evaluation; 1 concurrent operator; fewer than 10,000 synthetic records |

## Risk classification

| Dimension | Decision | Evidence/unknown owner |
| --- | --- | --- |
| Exposure | localhost only | Planning decision; product owner revisits before network exposure |
| Data sensitivity | public synthetic book metadata | Field inventory in `DATA-READING-001`; data owner reviews additions |
| Tenancy | single local dataset | `COVERAGE-READING-001`; revisit before organization/user scope |
| Identity assurance | no identity boundary for localhost | Security owner blocks public mutation until identity/access artifacts exist |
| Availability | best effort local showcase | No SLO; operations owner revisits for an operated target |
| Regulation/contract | none known for synthetic metadata | Product owner reviews any user-supplied or personal field |
| Scale | 1 operator, fewer than 10,000 records | Representative query evidence is still planned |
| Cost envelope | local developer resources only | Product owner approves any hosted service |

## Data lifecycle and retention

| Data/store/cache/log/backup/vendor | Classification and tenant scope | Purpose/source of truth | Retention/deletion/legal hold | Backup/log/vendor propagation | Owner/evidence |
| --- | --- | --- | --- | --- | --- |
| PostgreSQL `books` | public synthetic; single scope | Authoritative book records | Archived records retained for local demo; database is resettable | No backup/vendor copy; safe structured logs exclude record payloads | Books owner; `DATA-READING-001`; evidence planned |

- Data residency and cross-border/vendor constraints: none for local-only execution.
- Erasure versus legal-hold decision authority: product owner; legal hold is not selected.
- Derived/search/analytics data deletion propagation: no derived store or analytics selected.
- Unknown classification/retention questions, owner, and resolve-by trigger: any new field is blocked until the data owner classifies it.

## Service and recovery objectives

| Critical journey/capability | SLI and SLO/window | RPO | RTO | Capacity/degradation objective | Measurement/restore evidence | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Local maintain-book journey | No operated SLO; command success and bounded query are planned checks | Recreate-only; no production data | One local setup session | 25 rows/page; fail visibly on database loss | `EVID-MIG-001`, `EVID-DB-002`, both `PLANNED` | Example web team |

- SLO exclusion and error-budget decision policy: no operated service; revisit before public deployment.
- Backup frequency/retention/immutability and restore environment: no backup; deterministic migrations and seed recreate local state.
- Dependency objectives and behavior when weaker: database unavailable returns a safe dependency error.
- Recovery decision authority and data-correction limit: local operator may reset only the guarded example database.

## Support and incident model

- Support hours, timezone, holidays, and promised response: none; local evaluation only in `Asia/Ho_Chi_Minh`.
- On-call/escalation coverage and vendor escalation: none.
- Incident severity owner, customer/status communication owner, and channels: example product owner if exposure changes.
- Maintenance/change window and emergency-change authority: local operator stops and recreates the example.
- Runbook/alert/restore exercise cadence: not required for local scope; reconsider before deployment.

## Team and release capability

- Team size, relevant skills, ownership boundaries, and bus factor: example two-person web team; one backup reviewer required before implementation.
- Release cadence, change approval, and separation-of-duty constraints: local manual review; no deployed release.
- Environment/CI/artifact-promotion capability: planned clean install/check/test sequence; no promoted artifact yet.
- Operational capacity: local developer ownership; no managed service or 24x7 support.
- Training, access, hand-off, or recovery gaps with owner and deadline: stack compatibility and clean-setup evidence owned by tech lead before code generation.
- Capability gaps that block a topology/control or require an exception: identity, hosted recovery, and SLO capability block public deployment.

## Quality targets

| Quality scenario | Stimulus and source | Environment/load | Expected response and measure | Accepted trade-off | Owner | Revisit trigger |
| --- | --- | --- | --- | --- | --- | --- |
| Bounded query | Search/list request | Representative local dataset | 25 rows/page, stable order, query plan reviewed | No cache | Books owner | Dataset or latency target changes |
| Progressive access | HTMX unavailable | Supported browser | Full create/search/edit/archive journey remains usable | Less dynamic interaction | Presentation owner | JavaScript-only capability proposed |
| Reproducibility | Clean checkout | Supported local runtime | Setup, migrate, seed, check and test are one documented path | No production deployment | Tech lead | Stack version changes |

- Baseline qualities that cannot be traded away: correctness, safe errors, accessibility, deterministic setup, and maintainability.
- Differentiating quality priorities: simple progressive interaction and low setup cost.

## Topology

- Repository topology and rationale: one application repository.
- Deployment topology and rationale: one synchronous Django web root plus separate migration/test commands; local PostgreSQL.
- Data ownership boundaries: `MOD-BOOKS` owns `DATA-BOOKS`.
- External dependencies/trust boundaries: browser request and PostgreSQL only; no provider/worker/file/email.
- Conditions that trigger extraction or redesign: public exposure, identity, tenancy, durable work, external integration, sensitive data, or operated SLO.

## Selected controls

| Control/guide | baseline / conditional / N/A | Owner | Evidence or N/A rationale | Revisit trigger |
| --- | --- | --- | --- | --- |
| Catalog `1.0.0` all 40 `CTL-*` rows | Baseline universe; no row removed by capability tier | Example architecture reviewer | [Planning readiness input](readiness.json) scores every row `0.00` because no runtime evidence exists | Any implementation or evidence change |
| `GATE-GREENFIELD-01` | Applicable and failing | Example architecture reviewer | Planning record only; walking slice not implemented | First executable slice |
| Evolution/refactor/release gates | N/A for current mode/target | Example product owner | Greenfield local planning; see owned decisions in readiness JSON | Existing system, refactor, or deployed release appears |

## Unknowns and adoption decision

| Unknown/assumption | Decision owner | Resolve by or discovery trigger | Safe default / blocked action |
| --- | --- | --- | --- |
| Compatible Python/driver/server versions | Tech lead | Before stack acceptance | Stack remains `in-review` |
| Public exposure or real users | Product owner | Before any hosted target | Public mutation blocked |
| Runtime/query behavior | Quality owner | First implementation slice | All readiness controls remain score `0.00` |

- Adoption decision: useful as a planning example only; not implementation-ready or production-ready.
- Required human approvers before status `active`: product, technical, security/data, and operations owners for the actual target.
