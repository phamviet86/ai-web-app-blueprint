---
guide_id: SKEL-BOOTSTRAP
title: Greenfield Bootstrap, Developer Experience, and Portability
status: experimental
audience: human-and-ai
read_when:
  - Bootstrapping a production repository or mapping the core architecture to a stack.
skip_when:
  - Refactoring an existing repository; use guide 16.
depends_on:
  - README.md
  - 01-foundations.md
owns:
  - system-profile-first bootstrap
  - application authority and command-lane bootstrap
  - walking vertical slice sequence
  - developer onboarding command contract
  - progressive human and AI adoption stages
  - production capability phases
  - stack portability procedure
---

# Greenfield bootstrap, developer experience, and portability

> Bootstrap a production feedback loop, not an empty folder tree or an internal framework.

## Rule `ADOPTION-STAGE-01`: adopt evidence and enforcement progressively

Adoption is an explicit, reversible decision. Copying guides or generating folders does not adopt the blueprint.

| Stage | Human accountability | AI contribution | Required artifact/evidence | Exit condition |
| --- | --- | --- | --- | --- |
| `0 EVALUATE` | Name intended system/change and decide whether this package fits | Route minimum guides; identify conflicts, missing setup, and estimated ceremony | Fit/gap note with package version; no repo mutation | Human chooses stop, pilot, or another workflow |
| `1 PROFILE` | Accept drivers, risk/applicability, unknown owners, objectives, support/team limits | Draft from discovered evidence; mark unknowns instead of inferring | System profile + artifact registry using schema `1.0` | Accountable owners accept profile or block named actions |
| `2 PROVE` | Accept observable contract and risk of one slice | Implement/characterize one real slice; collect falsifiable checks | Walking-slice evidence and selected test/threat/data artifacts | Relevant greenfield/evolution gate passes for the slice |
| `3 ENFORCE` | Approve repo-local rules, review map, and bounded exceptions | Install only selected checks/routing; register artifacts and ratchets | Stable commands, CI enforcement, exception ledger | New work cannot bypass adopted boundaries cheaply |
| `4 RELEASE-GOVERN` | Own go/no-go and residual-risk acceptance | Build assessment input, execute checks/scorer, report gaps | Final assessment for named revision/deployment and applicable gate evidence | Human release owner approves or records `not-ready` |

Stage numbers express adoption depth, not implementation maturity. A team may remain at stage `1` while exploring. Record package/control/schema versions and next trigger at every hand-off.

The minimum adoption workspace is repo-native:

```text
small entry guide -> task router -> canonical rule owner
docs/governance/artifact-registry -> current accepted artifacts and tombstones
stable local/CI commands -> executable evidence
```

Do not replace existing canonical repo instructions silently. Map overlap and conflicts, choose the owner, migrate references, and remove stale duplicates. A human must accept product, risk, exception, and release decisions; an agent may not self-approve its draft.

## Rule `APP-AUTHORITY-01`: application work follows one verified authority chain

An instantiated application declares one current authority route before code work:

- a preset-created app uses a `preset-lock` under the [preset contract](../presets/PRESET-CONTRACT.md), bound to the exact verified manifest revision, registries, source/design/evaluation evidence, and integrity digests; or
- a customized or existing app uses an `app-profile` under the [app-profile schema](schemas/app-profile.schema.json), binding its accepted system/stack profiles, artifact registry, pattern and skill registries, [verification command registry](schemas/verification-command-registry.schema.json), revision-bound clean-room execution record, dual-verdict skill evaluations, source revision, and integrity digests.

The selected route may record the other route's historical provenance, but it must not activate a second authority file. Source without either complete route is ungoverned; stale, missing, mismatched, or conflicting locks stop app work. Re-resolve paths through the locked registry rather than guessing from filenames, and record every accepted authority change as an explicit profile/lock update.

Validate an app-profile fail-closed with `python3 docs/blueprint/scripts/validate_app_profile.py PATH --repo-root ROOT --expected-revision <current-source-revision> --expected-blueprint-revision <selected-blueprint-revision>`. Qualification never accepts a movable or unbound source/blueprint revision. Validator behavior and fixtures are owned by `DOCS-VALIDATION-01` in guide `07`.

## Phase 0: declare the system profile

Before choosing structure or vendors, instantiate [templates/system-profile.md](templates/system-profile.md) and [templates/artifact-registry.md](templates/artifact-registry.md). Use the [filled profile example](templates/examples/system-profile-small-web-app.md) only to understand completeness. Capture:

- critical user journeys and unacceptable failures;
- internet/internal exposure and trust boundaries;
- data sensitivity, tenancy, retention, and regulatory needs;
- identity assurance and privileged operations;
- expected traffic, dataset, concurrency, latency, and cost envelope;
- availability target, SLO, RPO, RTO, and support ownership;
- repository and deployment topology;
- support hours, incident/customer communication, restore and runbook exercise cadence;
- team size/skills/bus factor, release cadence/approval, environment/CI capability, and operational capacity;
- unknowns with owner, resolve-by trigger, safe default, and actions blocked meanwhile.

Unknowns are allowed when named with owner and discovery trigger. High-risk unresolved unknowns block the affected gate. Do not silently choose high-complexity controls “just in case” or optimistic objectives the support model cannot operate.

## Rule `DEVEX-ONBOARD-01`: one documented path from clone to evidence

A new contributor or agent should be able to:

1. install deterministic dependencies from the lockfile;
2. create sanitized local configuration without receiving production secrets;
3. run a doctor/preflight check for runtime, services, config, generated artifacts, and ports;
4. start required local dependencies and the application;
5. load deterministic non-sensitive development data;
6. run fast checks, focused tests, full CI-equivalent checks, and production build;
7. find architecture, troubleshooting, and release documentation.

The onboarding path must state supported human prerequisites and non-interactive agent behavior. A setup step requiring secrets, destructive data changes, external messages, elevated access, or production mutation has an explicit approval/sandbox boundary.

The concrete commands may differ, but the selected authority binds a machine-readable command registry exposing these required lanes:

```text
install       deterministic dependency installation
doctor        read-only environment/config/dependency diagnosis
test          focused/default deterministic tests
check         formatting/lint/types/architecture/unit/integration gates
build         production artifact build
start-smoke   bounded startup plus readiness/termination proof
```

Add `generate`, guarded `data-reset`, `auth-smoke`, `browser-smoke`, or an isolated `restore-drill` only when the selected capability needs them. Real externally mutating publish/release commands never belong in this clean-room registry; only a separately named, non-mutating simulation against an isolated local target may be declared. Validators reject conventional `publish`, `release`, and `deploy` lane keys as defense in depth, but cannot infer arbitrary argv semantics: renaming an unsafe command does not make it safe, so the runner/reviewer still proves the target is isolated and no external production effect occurred. Registry entries use an unambiguous executable/argument/environment contract; the accepted profile identifies destructive or secret-bearing approval boundaries and the evidence owner. Clean-room verification executes every declared lane against the locked source; checking that scripts or files exist is not evidence that onboarding works. CI remains authoritative. Local hooks improve feedback but must not be the only enforcement point.

## Phase 1: architecture foundation

1. Select the simplest topology satisfying guide `01`; normally one modular deployable.
2. Establish composition roots, module public APIs, platform boundary, and shared-kernel limits.
3. Enable a strict language/static-analysis mode appropriate to the stack.
4. Add import/cycle/runtime-boundary fitness checks before feature count grows.
5. Centralize typed configuration and fail-fast validation.
6. Establish structured error codes, correlation context, and redaction policy.
7. Create a minimal test harness and isolated development/test data path.
8. Add CI that runs the same deterministic checks as local `check`.

Create directories only when the first selected capability needs them. The architecture is defined by contracts and dependency checks, not by empty folders.

## Rule `GREENFIELD-SLICE-01`: first slice crosses every real boundary

Implement one small, production-shaped use case:

```text
entrypoint/presentation
  -> application command or query
  -> domain policy when needed
  -> owned port
  -> real adapter and persistence/external dependency
  -> safe result/error mapping
  -> telemetry + deterministic verification
```

The first slice should include only capabilities required by that journey, but none may be faked by crossing the intended boundary. For example, do not bypass the application contract merely because there is one module.

Acceptance:

- module public API is the only external import path;
- expected and unexpected failures are distinguishable;
- authorization and input validation occur at trusted boundaries;
- persistence migration and local test data are reproducible;
- one representative trace/log correlation can be followed;
- transport and persistence boundaries preserve meaningful `false`, `null`, `0`, and omitted values, real identifier shapes, timezone behavior, and declared defaults;
- modules intended for analysis/test discovery satisfy [`RUNTIME-INITIALIZATION-01`](03-shared-kernel-and-platform.md#rule-runtime-initialization-01-importing-code-does-not-start-the-runtime); when build/check claims no external dependency, evidence runs with runtime-only secrets absent and relevant endpoints unreachable and proves no eager connection attempt;
- unit/integration/contract checks cover the actual failure risks;
- required command lanes, production build, bounded startup smoke, and CI pass in a clean environment.

## Phase 2: safety and data baseline

Before sensitive or externally callable behavior expands:

- complete the threat/access artifacts routed by guide `11`;
- inventory data and define retention/deletion/isolation with guide `12`;
- define deadlines, retries, concurrency, and idempotency with guide `13`;
- prove negative authorization and tenant-isolation paths;
- prove migration compatibility and a non-production restore path.

Load only the guide whose control applies to the current slice.

## Phase 3: production delivery loop

Before the first production release, guide `15` must establish:

- environment and secret boundaries;
- immutable artifact build and promotion;
- deploy/migration compatibility and rollback or roll-forward plan;
- telemetry, health/readiness, SLI/SLO, alerts, and runbook ownership;
- dependency/supply-chain gates proportional to risk;
- backup/restore evidence against declared RPO/RTO.

A preview deployment is not production readiness by itself.

## Rule `BOOTSTRAP-PRODUCTION-01`: multiply only after the second slice

Use a second real module/use case to test the architecture before promoting abstractions:

1. compare semantic contracts and volatility;
2. keep unrelated domain policy vertical;
3. promote only stable shared/platform capability;
4. add a fitness check for the new invariant;
5. record an ADR only when the decision is costly to reverse or cross-cutting;
6. update illustrative reference patterns only after the implementation stabilizes and the adaptation evidence is known.

Two consumers are evidence, not sufficient proof. A shared abstraction must also have one owner and the same reason to change.

## Capability-oriented root map

```text
repo/
├── app-or-entrypoints/       composition roots and delivery adapters
├── modules/                  business capabilities and public contracts
├── platform/                 config, telemetry, DB/queue/vendor bootstrap
├── shared/                   tiny kernel and reusable presentation primitives
├── tests/                    cross-module/contract/E2E/nonfunctional suites when needed
├── migrations/              reviewed schema/data evolution artifacts
├── scripts/                 guarded operational/developer workflows
├── infra/                   deploy/runtime definitions when repo-owned
└── docs/                    architecture, ADRs, runbooks, templates
```

A stack may colocate tests or migrations. Preserve capability ownership rather than the spelling.

## Porting procedure

Map logical roles before choosing libraries:

| Core role | Possible implementation |
| --- | --- |
| Entrypoint/presenter | Route, controller, resolver, CLI, worker, UI screen |
| Application command/query | Use case, interactor, handler, service method |
| Domain | Entity/value object/policy/state machine or simple pure rules |
| Port | Repository/gateway/clock/ID/event/file contract owned by the caller |
| Adapter | ORM repository, SDK client, HTTP gateway, queue publisher |
| Composition root | Factory, framework container, provider, startup module |
| Client server-state | Optional cache/synchronization layer |
| Platform | Config, auth primitives, DB/queue clients, telemetry, runtime hooks |

Then:

1. choose a dated stack profile or create one from primary docs;
2. map each core role without changing dependency direction;
3. define public/runtime boundaries and fitness checks;
4. implement the first slice;
5. prove production gates before adding broad abstractions.

### Portability acceptance

A stack mapping is credible only when it records:

- stack/runtime/database/deployment versions and primary-source verification date;
- every required core role, or a reason the role is inapplicable;
- exact enforcement for public imports, cycles, runtime boundaries, config, migrations, tests, and build;
- local/CI/release command mapping and unsupported capability gaps;
- one end-to-end slice proving the mapped roles without changing core dependency direction.

A written table alone is a hypothesis. Mark the mapping `experimental` until the slice and checks pass; do not claim the core is portable from two profiles that share the same effective framework/runtime architecture.

## Stop conditions

Stop and simplify when bootstrap creates unused layers, a DI container before a real volatile dependency, microservices without independent operational need, a test matrix unrelated to risk, production secrets for local setup, or an abstraction before the second semantic consumer.
