---
template_id: REFAPP-TPL-STACK-PROFILE
template_version: 1.1.0
produces: stack-profile
owner_guide: ../01-stack-intake-and-compatibility.md
use_when: Selecting or validating the concrete stack before reference-app planning.
---

# Reference application stack profile

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: stack-profile`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `STACK-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: `SYS-*`, `COVERAGE-*`
- Source mapping: maintained/candidate profile path or `CUSTOM`, authority/provenance, plus deviations:
- Target: local showcase / public showcase / production starter

## Application authority binding

- Authority route at instantiation/adoption: `preset-lock` under the [preset contract](../../../presets/PRESET-CONTRACT.md) / `app-profile` under the [app-profile schema](../../schemas/app-profile.schema.json):
- Locked blueprint / preset (when applicable) / source revisions and integrity digests:
- Artifact registry and accepted system-profile IDs/digests; selected authority binds this stack-profile path/digest:
- Pattern catalog / skill registry IDs, paths and digests:
- Verification command registry path/digest under its [schema](../../schemas/verification-command-registry.schema.json):
- Conflict, drift and authority-refresh owner/trigger:

## Acceptance gate

- [ ] System/risk profile is current and blocking drivers are resolved.
- [ ] Coverage tier and additive capabilities are current; unselected runtimes/providers are not scaffolded.
- [ ] Every blocking compatibility concern is `PASS`.
- [ ] Every `CONDITIONAL` result is an explicit constraint with owner/expiry.
- [ ] Exact compatible versions and lockfile policy are selected.
- [ ] API claims link exact-version official sources; Context7 lookups record library ID, scope, source URL and retrieval date.
- [ ] Third-party advisory inputs are commit-pinned, license-reviewed and excluded from ambient/global execution.
- [ ] Every blocking spike passes.
- [ ] The selected authority route, registries, revisions and digests agree; no second route claims a conflicting code shape.
- [ ] Every selected vertical pattern has one primary owner, optional support skills and positive/negative evidence.
- [ ] Required command lanes execute in clean-room evidence; existence-only checks do not count.
- [ ] Data-access modes, mutation guards and production-handoff boundaries are explicit.

Only then set status to `accepted`; an unresolved contradiction makes it `rejected`, otherwise use `draft` or `in-review`. An accepted artifact replaced by a newer accepted revision becomes `superseded`.

## Stack card

| Role | Selection/version | Runtime | Owner path | Primary `EVID-*` / status | Replacement seam |
| --- | --- | --- | --- | --- | --- |
| Web/runtime | | | | | |
| Language/tooling | | | | | |
| UI/styling | | | | | |
| Browser server-state | | | | | |
| Identity/session | | | | | |
| Authorization/tenancy | | | | | |
| SQL/ORM/driver | | | | | |
| Validation | | | | | |
| Storage | | | | | |
| Email | | | | | |
| Jobs/queue/scheduler | | | | | |
| Cache/rate limit | | | | | |
| Telemetry/errors | | | | | |
| Testing/fitness | | | | | |
| CI/deployment | | | | | |

## Pattern and skill registry

| Pattern ID | Outcome semantics | Primary owner skill | Support skills/controls | Current exemplar | Positive/negative verifier |
| --- | --- | --- | --- | --- | --- |

This registry contains established patterns only. An analyzer classifies each requested outcome at task time as `ESTABLISHED_PATTERN`, `PATTERN_EXTENSION`, or `CANDIDATE_GAP`; those classifications are not catalog status. Supporting layer work inherits the selected vertical pattern and never creates a second task owner.

## Executable topology

| Root | Selected by `CAP-*` | Runtime/deploy unit | Dependencies | Startup/shutdown | Health/owner |
| --- | --- | --- | --- | --- | --- |
| Web | Baseline | | | | |
| Worker | Conditional | | | | |
| Migration | Stored data | | | | |
| CLI/labs | Conditional | | | | |

## Environment adapters

| Capability | Local | Test | Preview/public demo | Production starter |
| --- | --- | --- | --- | --- |

## Verification command registry

| Lane | Required / capability-selected | Declared argv/cwd | Environment / approval / side-effect boundary | Clean-room `EVID-*` / result |
| --- | --- | --- | --- | --- |
| `install` | Required | | | |
| `doctor` | Required | | | |
| `test` | Required | | | |
| `check` | Required | | | |
| `build` | Required | | | |
| `start-smoke` | Required; positive timeout, readiness and bounded termination | | | |
| `generate`, guarded `data-reset`, `auth-smoke`, `browser-smoke`, isolated `restore-drill` | Select when applicable; no external publish/release lane | | | |

## Data-access policy

| Mode | Allowed interface/target | Guard and negative proof | Stop condition / owner |
| --- | --- | --- | --- |
| `NONE` | No data access | No connection is opened | |
| `LIVE_READ` | Approved least-privilege read-only interface | Read-only proof; no direct fallback | |
| `TEST_MUTATION` | Disposable isolated target through guarded wrapper | In-process normalized target/live-collision check | |
| `PRODUCTION_HANDOFF` | Operator-applied reviewed artifact | Pre/postchecks and recovery; no task mutation | |

## Compatibility decisions

| Concern | PASS / CONDITIONAL / REJECT | Evidence | Constraint/exception owner and expiry |
| --- | --- | --- | --- |

## API and source provenance

| Role/claim | Exact package version / lock | Official source URL/version | Context7 library ID / scoped query / `retrieved_at` | Compatibility conclusion / `EVID-*` | Review deadline / invalidation |
| --- | --- | --- | --- | --- | --- |

| Advisory source | Role | Commit/version | License | Read-only/sandbox policy | Accepted/rejected guidance | Refresh trigger |
| --- | --- | --- | --- | --- | --- | --- |

Official exact-version documentation owns API behavior. Context7 retrieves documentation; advisory skills/datasets propose candidates only. Record missing hard source evidence as blocking and a missing quality source with its declared fallback and narrowed claim.

## Configuration inventory

| Variable/class | Server/public/secret | Environments | Owner | Validation/rotation |
| --- | --- | --- | --- | --- |

## Required spikes

| Spike | Command / `EVID-*` | Evidence status | Result | Blocks implementation? |
| --- | --- | --- | --- | --- |

## Rejected alternatives

| Alternative | Reason rejected | Revisit trigger |
| --- | --- | --- |
