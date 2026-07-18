---
guide_id: REFAPP-BUILD
title: Plan Generation, Build Sequence, and Gates
status: experimental
audience: human-and-ai
read_when:
  - Producing the decision-complete implementation plan or building the reference app in vertical slices.
skip_when:
  - The request concerns one accepted slice with its own current plan and owner.
depends_on:
  - README.md
  - ../06-greenfield-bootstrap-and-portability.md
  - ../14-testing-and-architecture-fitness.md
owns:
  - reference-app plan-generation contract
  - dependency-ordered implementation phases
  - slice exit gates and checkpoint policy
  - preset authoring, clean-room verification, and instantiation gates
---

# Plan generation, build sequence, and gates

> Generate artifacts before broad source. Build a thin executable slice before shared abstractions, then expand capability by capability.

## Rule `REF-PLAN-COMPLETE-01`: the plan resolves implementation decisions

Before implementation, the consolidated plan links current versions of:

- current parent [system/risk profile](../templates/system-profile.md), accepted [stack profile](templates/stack-profile.md), and accepted risk-selected [capability coverage](templates/capability-coverage.md);
- [logical data model](templates/data-model.md), ownership and migrations/seed policy when stored/projected data is selected;
- [shared](templates/shared-plan.md) inventory only when shared contracts are introduced, and a [platform](templates/platform-plan.md) inventory for selected runtime/data/identity/provider mechanisms;
- [feature plans](templates/feature-plan.md), public contracts and [route/journey map](templates/route-map.md);
- current parent [test strategy](../templates/test-strategy.md), plus [SLO/runbook](../templates/slo-runbook.md) and [release/recovery plan](../templates/release-recovery.md) when the target/risk selects them;
- access matrix and threat model when selected by the system profile, including an access matrix for every multi-tenant public showcase;
- safe demo-operation and fork-to-product decisions from guide `09`.

Use artifact IDs `STACK-*`, `COVERAGE-*`, `DATA-*`, `SHARED-*`, `PLATFORM-*`, `FEATURE-*`, `ROUTES-*`, and `PLAN-*`. Use trace IDs `CAP-*`, `MOD-*`, `ROUTE-*`, `JRN-*`, `SLICE-*`, and `EVID-*`; bridge them to the parent catalog's `CTL-*` and `GATE-*` IDs.

A plan is implementation-ready only when every required artifact is current/`accepted`, every omitted conditional artifact has an owned `not-required` decision, no blocking `TBD` remains and every selected capability maps to a journey, owner module, data/platform dependency where applicable, route/job, evidence path, and candidate parent controls/gates. Artifact lifecycle is `draft -> in-review -> accepted -> superseded`, with `rejected` as an alternative under parent artifact schema `1.0`. Evidence lifecycle is `PLANNED -> OBSERVED -> VERIFIED -> STALE/INVALID`; planned evidence never satisfies a completion gate. The consolidated plan summarizes accepted decisions; it does not silently fill gaps.

Before a scored checkpoint, initialize the full catalog assessment, map each `EVID-*` to exact `CTL-*`/`GATE-*` rows, and run the parent scorer. Controls not owned by one feature remain owned by system, platform, delivery, operations, or governance artifacts. `CAP-* NOT_SELECTED` is never sufficient `N/A` evidence for a control.

## Planning flow

```text
STACK INTAKE
  -> COMPATIBILITY SPIKES / PROFILE
  -> CAPABILITY + DOMAIN MAP
  -> DATA + SHARED + PLATFORM DECISIONS
  -> FEATURE CONTRACTS + ROUTES/JOURNEYS
  -> DEPENDENCY-ORDERED SLICES
  -> TEST / RELEASE / DEMO / EXTENSION GATES
```

Reset AI context at artifact boundaries. The final plan consumes the filled artifacts; it does not require all design guides to remain loaded.

## Rule `REF-PRESET-BUILD-GATE-01`: author and install through separate gates

Guide [10](10-preset-authoring-and-instantiation.md) declares the operating mode. Apply these ordered flows before the application phases below.

### `AUTHOR_PRESET` phases

1. **Freeze:** accept the exact stack/provenance, archetype, filesystem topology and supported/unsupported capability matrix.
2. **Contract:** complete `PRESET-*` plus data/shared/platform/feature/route mappings for every provided flow.
3. **Foundation:** author framework-root template files, `template/src` roles and only the shared/data/auth/app mechanics selected by the contract.
4. **Walking slices:** implement the smallest removable feature path proving each capability labeled `verified`.
5. **Agent skills:** complete the seven canonical manifest-routed skill packages plus every declared optional package from guide [11](11-preset-agent-skills-and-design-evidence.md); validate triggers, paths, resources, pattern references, commands, forward evaluations and integrity against code.
6. **Clean room:** materialize into an empty temporary repository, install the exact lock set and run selected database/auth/lint/typecheck/test/build/browser gates plus clean-context skill forward evaluations.
7. **Publish:** capture evidence/source digests, version manifest/template/skills/patterns together and supersede the prior contract explicitly.

Authoring writes only the preset package; it does not create the distribution repository's root `src/`.

### `INSTANTIATE_PRESET` phases

1. Check the app system profile against the verified preset revision and reject unsupported blocking needs.
2. Inventory target paths and stop on an undeclared conflict.
3. Run the versioned scaffold/materialization map, preserving framework-default root locations and the preset's application `src` layout.
4. Install exact dependencies and write the application preset lock before feature customization.
5. Run clean-start, migration/auth and declared verification commands in the target repository.
6. Create app-specific governance artifacts, then route subsequent user work through the locked preset skills.

Instantiation is complete only when template provenance, installed paths, dependency lock, preset lock and verification results agree. A later upstream blueprint/preset change becomes an explicit upgrade slice; it never silently rewrites the application.

### Preset skill forward-evaluation gate

Before preset publication, run the real manifest-resolved skills in fresh, minimally primed agent contexts. Provide the skill package, raw task and ordinary repository authority—not an expected patch or the author's diagnosis. Cover direct/misdirected triggers, an established pattern, a cross-layer outcome, hard/quality prerequisite behavior, a forbidden boundary or untrusted-source attempt, a real/false new-pattern gap and UI async/responsive/accessibility states.

Store the untouched input, preset/skill/model/toolchain IDs, input digests, route/read trace, patch or artifact, command log and observed failure. A skill change invalidates affected cases. Publication fails when the agent reaches the right output only because expected answers leaked into context, skips a required conditional reference, crosses an allowed-path boundary, or claims completion beyond evidence.

### Standards and requested-outcome gates

Review every walking slice on two independent axes:

| Gate | Passes only when |
| --- | --- |
| Pattern/standards conformance | Locked ownership, dependency, API, payload/result, security, accessibility and framework-native contracts plus positive/negative fixtures pass |
| Requested outcome | The actual acceptance behavior, user flow, responsive interaction, failure recovery and business result work for representative users/data |

A visually polished or pattern-conformant screen can still fail its user outcome. A working happy path can still violate authorization, accessibility or preset architecture. Store separate verdicts and block the slice if either required axis fails.

## Tier-aware implementation phases

### Phase 0: freeze the executable foundation

Deliver:

- repository/tooling/typed-config skeleton;
- dependency and runtime compatibility proof;
- web, migration and test composition roots; worker/CLI roots only when selected capabilities require them;
- database connection plus one reviewed migration;
- telemetry bootstrap, structured error boundary and health semantics;
- architecture import/cycle/runtime fitness checks;
- reproducible local dependencies and CI commands.

Gate: clone-to-check/build works; invalid config fails safely; no business feature yet depends on a speculative shared framework.

### Phase 1: `BASIC_WEB` walking slice

Deliver one real path:

```text
enter selected route -> validate/access decision -> create/list/view one owned record
  -> database -> safe error/telemetry -> deterministic integration + browser smoke
```

Add application shell, minimal form/list/async states and provider wiring only as required.

Gate: `JRN-CUSTOMER-CATALOG` or the mapped equivalent passes; access policy is explicit; app route remains thin; no framework/ORM type escapes public contracts. A `BASIC_WEB` plan may proceed directly to hardening after this phase.

### Phase 2A: `MULTI_TENANT_SAAS` branch

Add identity/session lifecycle, organization membership, invitations, tenant-scoped records and direct-call allow/deny evidence.

Gate: wrong-tenant IDs, stale roles, disabled members and last-owner/concurrent membership rules are denied without relying on navigation visibility.

### Phase 2B: `ASYNC_INTEGRATION` branch

Add one stateful command, durable job/outbox/inbox or equivalent, one owned external adapter, idempotency and reconciliation.

Gate: duplicate/crash/outage/ambiguous-result paths create one business effect, remain inspectable and have a bounded repair/replay path.

### Phase 2C: `REGULATED` branch

Add selected assurance/reauthentication, field/resource authorization, data classification/retention/privacy lifecycle, append-only audit and recovery evidence.

Gate: threat/access decisions, negative authorization/privacy tests, migration/recovery limits and residual-risk acceptance are current for the selected scope.

### Phases 3–6: `FULL_SHOWCASE` expansion

After the relevant Phase 2 branches, add only dependency-ready FulfillOps slices:

- catalog/files/inventory and contested stock evidence;
- order workflow, idempotent submit and durable allocation;
- invoice/payment sandbox, authenticated webhook and reconciliation;
- fulfillment/notifications with bounded retry and recovery;
- data exchange/read model with checkpoint, compare, rebuild and freshness evidence.

Gate each slice independently using its selected `CAP-*`; completing one archetype cannot compensate for another selected capability.

### Final phase: tier-appropriate hardening and release

Deliver deterministic seed/reset, exposure-appropriate demo guardrails, accessibility/responsive pass, selected telemetry/alerts/runbooks, dependency/supply-chain evidence, migration/recovery proof and deployment when requested.

Gate: guide `09` declares the selected tier showcase-ready from verified evidence; production-ready remains a separate parent guide `08` assessment.

## Rule `REF-SLICE-GATE-01`: each slice is independently releasable

Every `SLICE-*` records:

- observable user/operator outcome;
- owner modules and allowed dependency delta;
- schema/config/event/API changes and compatibility;
- transaction/idempotency/concurrency/failure behavior;
- tests at the lowest sufficient layers;
- route/demo evidence only for observable behavior;
- telemetry/alert/runbook delta;
- rollback or roll-forward decision;
- documentation/artifact updates;
- exit gate and residual risk owner.

Every slice also updates the `PLAN-*` trace row from `CAP-*` through `MOD-*`, data/platform dependencies, route/job and `JRN-*` to `EVID-*` status and the `CTL-*`/`GATE-*` rows that will consume observed evidence.

Do not mix unrelated layers merely to maximize parallel work.

## Verification routing

| Changed contract | Minimum useful evidence |
| --- | --- |
| Pure invariant/state transition | Unit/property tests with fixed clock/IDs |
| Application authorization/use case | Port-controlled application tests including deny/conflict |
| Database constraint/query/transaction | Real PostgreSQL integration and concurrency tests |
| Public DTO/error/event | Contract/schema compatibility tests |
| Webhook/provider | Adapter contract plus failure/authenticity fixtures |
| Job/outbox/inbox/import | Real persistence, duplicate/crash/replay tests |
| Shared UI/route journey | Component accessibility/interaction; critical browser smoke |
| Preset skill or router | Syntax/integrity checks plus clean-context trigger, conformance, stop and outcome forward-evaluation cases |
| UI design contract | Token/state/API checks, representative responsive renders and a real payload/action-result walking slice |
| Performance/capacity | Representative data/load/query/bundle evidence |
| Release/recovery | Deploy/migration/restore/failover or bounded lab evidence |

UI automation is not a substitute for server/data determinism. Conversely, unit tests do not prove route wiring or accessibility.

## Agent checkpoint

After each phase report:

```text
Completed slices and artifact IDs:
Public/data/event/config deltas:
Evidence and commands:
Coverage newly satisfied:
Active transitions/exceptions:
Residual risk and owner:
Next dependency-ready slice:
```

Do not report completion from code volume, green build alone, or planned-but-unexecuted evidence.

## Stop conditions

Stop when authoring creates root app source, installation would overwrite undeclared work, manifest/template/skills/patterns disagree, implementation begins with an incompatible/unknown blocking stack slot, plan artifacts disagree, a slice cannot state its user outcome and owner, migrations/events cannot coexist across deploy, UI testing becomes the main proof of server behavior, or later phases are used to postpone security/data/recovery decisions required by the current slice.
