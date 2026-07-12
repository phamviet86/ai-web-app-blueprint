---
template_id: REFAPP-TPL-CAPABILITY-COVERAGE
template_version: 1.0.0
produces: capability-coverage
owner_guide: ../02-capability-coverage-and-domain.md
use_when: Selecting a risk-proportionate capability tier and proving every selected capability has a traceable owner and evidence path.
---

# Reference application capability coverage

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: capability-coverage`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `COVERAGE-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: `SYS-*`
- Domain and substitution rationale:
- Primary tier: `BASIC_WEB` / `MULTI_TENANT_SAAS` / `ASYNC_INTEGRATION` / `REGULATED` / `FULL_SHOWCASE`
- Additive capability IDs and risk rationale:

## Selection gate

- [ ] The primary tier is the smallest preset covering current system risks.
- [ ] Every tier-required and additive row is `SELECTED` with a real owner, journey and planned evidence.
- [ ] Every other row is `NOT_SELECTED` with owner, rationale and revisit trigger; no empty placeholder is generated.
- [ ] `PLANNED` evidence is labeled as planning and is not counted as observed/verified proof.

| Capability ID | `SELECTED` / `NOT_SELECTED` | Tier/addition rationale | Owner `MOD-*` | `DATA-*` / `PLATFORM-*` dependency | `ROUTE-*` / job | `JRN-*` | `EVID-*` / status | Parent `CTL-*` / `GATE-*` bridge | N/A owner/revisit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CAP-CRUD` | | | | | | | | | |
| `CAP-WORKFLOW` | | | | | | | | | |
| `CAP-READMODEL` | | | | | | | | | |
| `CAP-ASYNC` | | | | | | | | | |
| `CAP-INTEGRATION` | | | | | | | | | |
| `CAP-BATCH` | | | | | | | | | |
| `CAP-RECONCILIATION` | | | | | | | | | |
| `CAP-IDENTITY` | | | | | | | | | |
| `CAP-TENANCY` | | | | | | | | | |
| `CAP-QUERY` | | | | | | | | | |
| `CAP-FILES` | | | | | | | | | |
| `CAP-TRANSACTION` | | | | | | | | | |
| `CAP-IDEMPOTENCY` | | | | | | | | | |
| `CAP-AUDIT-PRIVACY` | | | | | | | | | |
| `CAP-ACCESSIBILITY` | | | | | | | | | |
| `CAP-TEST-FITNESS` | | | | | | | | | |
| `CAP-OBSERVABILITY` | | | | | | | | | |
| `CAP-DELIVERY-RECOVERY` | | | | | | | | | |
| `CAP-EMAIL-PROVIDER` | | | | | | | | | |
| `CAP-CARRIER-PROVIDER` | | | | | | | | | |
| `CAP-CACHE` | | | | | | | | | |
| `CAP-ADVANCED-IDENTITY` | | | | | | | | | |
| `CAP-PRODUCTION-READINESS` | | | | | | | | | |

`CTL-*` and `GATE-*` cells identify possible evidence consumers, not scores. A capability decision cannot omit a catalog row, make a baseline control inapplicable, or turn planned evidence into an observed result.

## Coverage reconciliation

- Missing selected capability:
- Selected row represented only by UI/docs/planned evidence and therefore incomplete:
- Duplicate implementation with no added contract:
- Blocking `NOT_SELECTED` rationale or stale revisit trigger:
- Final coverage decision / reviewer:
