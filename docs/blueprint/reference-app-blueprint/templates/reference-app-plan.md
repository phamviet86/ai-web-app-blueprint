---
template_id: REFAPP-TPL-REFERENCE-APP-PLAN
template_version: 1.0.0
produces: reference-app-plan
owner_guide: ../08-build-sequence-and-gates.md
use_when: Producing the final decision-complete plan and tracking implementation/showcase completion.
---

# Reference application plan: [name]

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: reference-app-plan`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `PLAN-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Goal/audience/target: local showcase / public showcase / production starter
- Selected tier and additive `CAP-*`:
- Operating mode: `AUTHOR_PRESET` / `INSTANTIATE_PRESET` / app-specific reference build
- Source `PRESET-*` / preset version / app preset-lock locator or `not-applicable`:

## Artifact registry

| Artifact ID or applicability row | Owner file | Status / `not-required` | Revision/currentness evidence or owner/rationale/revisit |
| --- | --- | --- | --- |
| `SYS-*` | Parent [system-profile](../../templates/system-profile.md) | | |
| `PRESET-*` | [preset-contract](preset-contract.md); required for author/instantiate modes | | |
| `STACK-*` | [stack-profile](stack-profile.md) | | |
| `COVERAGE-*` | [capability-coverage](capability-coverage.md) | | |
| `DATA-*` | [data-model](data-model.md) | | |
| `SHARED-*` | [shared-plan](shared-plan.md) | | |
| `PLATFORM-*` | [platform-plan](platform-plan.md) | | |
| `FEATURE-*` plans | [feature-plan](feature-plan.md) | | |
| `ROUTES-*` | [route-map](route-map.md) | | |
| `TEST-*` | Parent [test-strategy](../../templates/test-strategy.md) | | |
| `SLO-*` | Parent [slo-runbook](../../templates/slo-runbook.md) | | |
| `RELEASE-*` | Parent [release-recovery](../../templates/release-recovery.md) | | |
| `ACCESS-*` | Parent access matrix; required for `MULTI_TENANT_SAAS`, `REGULATED`, multi-tenant `FULL_SHOWCASE`, or when selected by system profile | | |
| Conditional `THREAT-*` | Parent threat model selected by system profile | | |

Do not consolidate until every required row is current and `accepted`; conditional rows may be `not-required` only with owner, rationale and revisit trigger. Link capability `NOT_SELECTED` decisions the same way. Parent artifacts may use their existing document shape but receive stable registry IDs here.

## End-to-end traceability

| `CAP-*` | Owner `MOD-*` / `FEATURE-*` | `DATA-*` / `PLATFORM-*` | `ROUTE-*` / job | `JRN-*` | `SLICE-*` | Planned/result `EVID-*` | Candidate `CTL-*` / `GATE-*` consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Control and readiness bridge

| `CTL-*` / `GATE-*` | Source `CAP-*` / artifact | Exact observed `EVID-*` or missing state | Assessment JSON row/result |
| --- | --- | --- | --- |

- Complete catalog/scorer input locator and digest:
- `PLAN-*` to readiness-assessment artifact/version:
- Controls with no selected capability owner and the artifact that owns them:
- Confirmation that `NOT_SELECTED` capabilities did not silently remove catalog controls:

## Architecture and structure

- Topology and executable roots:
- Module/public/dependency map:
- Shared/platform inventory:
- Data/migration/seed contract:
- Routes/journeys:
- Security/privacy/reliability decisions:

## Preset mode and compatibility

| Flow/layer | Preset capability status | Concrete paths/contracts | Clean-room or installed `EVID-*` | App deviation/owner |
| --- | --- | --- | --- | --- |
| Starter/materialization | | | | |
| Shared surface/input | | | | |
| Query/data/ORM | | | | |
| Identity/auth | | | | |
| Feature/action/service/repository | | | | |
| App route/composition | | | | |
| AI guide routing | | | | |

- Root framework files versus application `src` mapping:
- Undeclared target conflicts: none / owner and resolution
- Preset manifest/template/guides revision agreement:
- Installed preset lock and local customization policy:

## Implementation slices

| `SLICE-*` | User/operator outcome | Dependencies/artifact deltas | Schema/event/config compatibility | Tests/labs | Exit gate | Rollback/forward |
| --- | --- | --- | --- | --- | --- | --- |

## Demo and release

- Local start/check/reset commands:
- Public-demo isolation, limits, sandbox and reset:
- CI/artifact/deployment/migration order:
- Telemetry/SLO/alerts/runbooks:
- Backup/restore and operational labs:
- Exceptions/residual risk/owners:

## Completion evidence

| `CAP-*` / `JRN-*` | Implementation | `EVID-*` status/result/date | Owner | Pass/gap |
| --- | --- | --- | --- | --- |

- Blocking TODO/unknown count:
- Showcase-ready decision/reviewer:
- Parent production-readiness assessment: not assessed / link
- Fork-to-product removals/replacements:
