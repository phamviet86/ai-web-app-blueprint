---
guide_id: REFAPP-ROUTER
title: AI-Guided Reference Application Builder
status: experimental
audience: human-and-ai
purpose: Turn the stack-neutral repo blueprint into a verified stack preset or a runnable, extensible reference application.
read_when:
  - The user asks to plan, build, deploy, or adapt a showcase/reference application from the repo skeleton.
  - The user asks to author, review, select, or instantiate a stack preset.
skip_when:
  - The user is changing one established module in an existing application.
depends_on:
  - ../README.md
owns:
  - reference-application authority and task routing
  - stack-intake conversation and artifact sequence
  - default-domain routing and package context budget
  - preset-authoring and preset-instantiation routing
---

# AI-guided reference application builder

> Entry point for producing a live reference application. Select a risk-proportionate capability tier, verify the stack, generate traceable decision artifacts, then build executable vertical slices.

## What this package is

This package instantiates the parent [production repo blueprint](../README.md) as a coherent application that:

- demonstrates the architecture capabilities selected by the system/risk profile;
- is runnable locally and deployable through the selected stack;
- uses production-capable boundaries, security, data, tests, and operations;
- can be forked and evolved into a real product.

It does not redefine the core architecture rules, provide a universal source-code template, or require every optional vendor. Core rule owners remain in guides `01` through `17`; this package decides where a reference app demonstrates them. `FULL_SHOWCASE` is an explicit breadth goal, not the default for an ordinary application.

## Global modes and local phases

Declare one global root mode before changing files; guide [10-preset-authoring-and-instantiation.md](10-preset-authoring-and-instantiation.md) owns the boundary. `INSTANTIATE_PRESET` below is the local phase name inside global `APP_BOOTSTRAP`, not another primary mode.

| Mode | Outcome |
| --- | --- |
| `AUTHOR_PRESET` | Create or version a reusable exact-stack package under `docs/presets/<preset-id>/`; the distribution repository's root `src/` remains absent |
| `APP_BOOTSTRAP` / `INSTANTIATE_PRESET` phase | Select a compatible verified preset, materialize framework-default root files plus application `src/`, write an app preset lock and verify the clean start |
| `APP_BOOTSTRAP` or `APP_DEVELOPMENT` without a reusable preset | Use guides `01`–`09` directly and produce app-specific artifacts/evidence |

Preset authoring and application implementation may occur in one request only as ordered phases: verify/version the preset first, then instantiate that immutable revision. Never edit source preset files while satisfying an app-local code task.

## Capability tier and default domain

Guide `02` selects the smallest tier justified by the parent system/risk profile:

| Tier | Default domain slice when the user supplies none |
| --- | --- |
| `BASIC_WEB` | Single-organization catalog/customer records with bounded search and one accessible CRUD journey |
| `MULTI_TENANT_SAAS` | Workspaces + CRM with membership, tenant isolation, invitations and audit |
| `ASYNC_INTEGRATION` | Order intake + one durable job/integration with duplicate, outage and reconciliation paths |
| `REGULATED` | Workspaces + governed records with stronger identity, privacy, audit, retention and recovery evidence |
| `FULL_SHOWCASE` | **FulfillOps**, the complete multi-tenant order-to-fulfillment showcase |

Tiers are requirement presets, not maturity ranks. Select one primary tier and add individual capabilities only when another declared risk requires them. A custom domain is accepted when [02-capability-coverage-and-domain.md](02-capability-coverage-and-domain.md) maps every capability selected by that union to an equivalent feature and journey.

## AI conversation protocol

When the user asks to build a live demo/reference app:

1. Determine whether the request is preset authoring, preset instantiation, or an app-specific reference build.
2. Inspect any stack or deployment choices already provided; do not ask for them again.
3. Confirm a current parent [system/risk profile](../templates/system-profile.md), or create it before recommending a stack. Unknown blocking drivers must have an owner and resolution gate.
4. Select the smallest capability tier that covers the declared risks and record any additive capabilities or owned `N/A` decisions.
5. If the stack is incomplete, ask one grouped question covering the missing high-impact choices from guide `01`.
6. Recommend a maintained profile or verified preset revision only when it fits; otherwise create a project-local profile or enter `AUTHOR_PRESET`. Candidate mappings never bypass provenance and compatibility spikes.
7. Confirm whether the target is reusable preset, local showcase, public resettable demo, or production starter.
8. Fill the required decision artifacts below in owner order.
9. Present the decision-complete plan before generating a broad codebase.
10. Build one phase at a time and apply the parent guide owner for the current flow.

Do not conduct an open-ended technology interview. Resolve low-impact choices from the selected profile and record them as defaults.

## Required decision artifacts

| Artifact | Required when | Required outcome |
| --- | --- | --- |
| Parent [system-profile](../templates/system-profile.md) | Always | Drivers, risk, quality targets, topology and applicable controls that constrain the stack |
| [preset-contract](templates/preset-contract.md) | Every `AUTHOR_PRESET`; referenced by every `INSTANTIATE_PRESET` | Exact stack/provenance, materialization map, capability/inter-layer contracts, manifest-routed skills/patterns and clean-room evidence |
| Application preset lock | Every `INSTANTIATE_PRESET` | Installed preset/blueprint/source revisions, selected options, install date and local deviations |
| [stack-profile](templates/stack-profile.md) | Always | Compatible runtime, UI, identity, data, services, testing, and deployment choices |
| [capability-coverage](templates/capability-coverage.md) | Always | Selected tier/additions map to owners, journeys, routes, data, and evidence; unselected rows have owned rationale |
| [data-model](templates/data-model.md) | Stored/projected data selected | Ownership, fields, constraints, isolation, lifecycle, and read models |
| [shared-plan](templates/shared-plan.md) | A shared contract is introduced/promoted | Real consumers, boundaries and removal/merge triggers |
| [platform-plan](templates/platform-plan.md) | Runtime/data/identity/provider mechanisms selected | Ports/adapters, environment mapping, composition roots and failure evidence |
| [feature-plan](templates/feature-plan.md) | Every selected module | Public contracts, use cases, ports, presentation, risks, and tests |
| [route-map](templates/route-map.md) | Every selected entrypoint/journey | Access, runtime, data owner, states, and telemetry |
| Parent [test-strategy](../templates/test-strategy.md) | Always, depth proportional to risk | Risk-to-evidence portfolio and architecture fitness registry |
| Parent [slo-runbook](../templates/slo-runbook.md) | Critical operated journey/SLO selected | SLI/SLO, alerts, ownership and mitigation |
| Parent [release-recovery](../templates/release-recovery.md) | Any deployed/public target; bounded local handoff otherwise | Artifact, migration, rollout, rollback/roll-forward and recovery gates |
| [reference-app-plan](templates/reference-app-plan.md) | Always | Ordered implementation slices, gates, demo policy, deploy, and extension path |

The parent [access matrix](../templates/access-matrix.md) and [threat model](../templates/threat-model.md) become required when the system profile selects their risks; the access matrix is required for any `MULTI_TENANT_SAAS`, `REGULATED`, or multi-tenant `FULL_SHOWCASE` build. Artifacts are planning interfaces. The implementation may use different filenames, but it may not leave their decisions implicit.

### Artifact lifecycle and traceability

Every created reference artifact follows schema `1.0` from the parent [artifact contract](../templates/README.md) and uses `draft -> in-review -> accepted -> superseded`; `rejected` is a terminal alternative. A conditional artifact may be recorded in the plan registry as `not-required` with owner, rationale and revisit trigger; that is an applicability decision, not an artifact status. Only `accepted` artifacts may feed the consolidated plan. Evidence uses the separate `PLANNED -> OBSERVED -> VERIFIED` lifecycle; a relevant change makes it `STALE`, and a disproving result makes it `INVALID`. `PLANNED` evidence is a test intention, never runtime proof.

Artifact IDs use `PRESET-*`, `STACK-*`, `COVERAGE-*`, `DATA-*`, `SHARED-*`, `PLATFORM-*`, `FEATURE-*`, `ROUTES-*`, and `PLAN-*`. Trace IDs use `CAP-*`, `MOD-*`, `ROUTE-*`, `JRN-*`, `SLICE-*`, and `EVID-*`. Each selected capability must trace through an owner module and route/job to evidence; data/platform IDs are added when that path depends on them.

Capability traceability does not replace the parent readiness universe. Each selected `CAP-*` records the `CTL-*` outcomes and `GATE-*` decisions its `EVID-*` may support. Before any readiness claim, generate all 40 catalog controls and four gates with `score_readiness.py`; a `NOT_SELECTED` capability never makes a baseline control `N/A`, and `PLANNED` evidence always leaves the linked readiness score at `0.00`. The consolidated `PLAN-*` owns the bridge while the readiness JSON remains the scoring authority.

## Guide map

| Guide | Owns |
| --- | --- |
| [01-stack-intake-and-compatibility.md](01-stack-intake-and-compatibility.md) | Minimal stack questions, defaults, compatibility and source verification |
| [02-capability-coverage-and-domain.md](02-capability-coverage-and-domain.md) | Default domain, archetype coverage, critical journeys and substitution gate |
| [03-database-blueprint.md](03-database-blueprint.md) | Logical tables, relationships, constraints, ownership, seed and read models |
| [04-shared-foundation.md](04-shared-foundation.md) | Shared kernel, UI, hooks and testing primitives |
| [05-platform-and-integrations.md](05-platform-and-integrations.md) | Config, auth, database, storage, email, jobs, cache, telemetry and composition |
| [06-features-and-public-contracts.md](06-features-and-public-contracts.md) | Reference modules, use cases, public APIs, patterns and cross-module flows |
| [07-app-routes-and-journeys.md](07-app-routes-and-journeys.md) | Logical route tree, access/runtime policy and end-to-end journeys |
| [08-build-sequence-and-gates.md](08-build-sequence-and-gates.md) | Artifact-first planning, vertical slices and evidence gates |
| [09-demo-operations-and-extension.md](09-demo-operations-and-extension.md) | Safe demo mode, seed/reset, testing, observability, release and product evolution |
| [10-preset-authoring-and-instantiation.md](10-preset-authoring-and-instantiation.md) | Preset modes, package/skill registry contract, clean-room authoring and conflict-safe installation |
| [11-preset-agent-skills-and-design-evidence.md](11-preset-agent-skills-and-design-evidence.md) | Real preset skill packages, triggers/disclosure/completion, pattern forward-evaluation, source trust and UI design evidence |
| [../profiles/nextjs-prisma-antd.md](../profiles/nextjs-prisma-antd.md) | Candidate Next.js/Prisma/Ant Design mapping; not acceptance evidence until project-local verification |
| [../profiles/django-postgresql-htmx.md](../profiles/django-postgresql-htmx.md) | Maintained Django/PostgreSQL/HTMX builder profile |
| [examples/nextjs-typescript-shadcn-drizzle.md](examples/nextjs-typescript-shadcn-drizzle.md) | Non-authoritative worked Next.js/TypeScript/shadcn/TanStack/Better Auth/PostgreSQL/Drizzle stack decision |
| [examples/basic-web-golden-path.md](examples/basic-web-golden-path.md) | Filled `BASIC_WEB` planning artifacts with trace IDs; explicitly not runtime proof |

## Task router

Read only the required row, plus the next unresolved owner.

| Task | Required reads | Add only when needed |
| --- | --- | --- |
| Author or revise a preset | README, 01, 10, 11 | Guides `02`–`09` only for the layer/capability being authored; preset-contract template |
| Author or forward-test preset skills/UI | README, 11 | Guide 04 for shared UI, guide 08 for gates, selected pattern/source records |
| Select or install a preset | README, 01, 10 | Selected preset contract/manifest/skills/patterns and app system profile |
| Ask for/select a stack | README, 01 | Maintained Django profile, candidate Next mapping with mandatory verification, worked example, or newly generated project-local profile |
| Start a reference-app plan from scratch | README, 01, 02, 08 | Complete system/stack first, then route through artifact owners `03`–`07` |
| Consolidate already-filled artifacts | README, 08 | `reference-app-plan` template; do not invent missing decisions |
| Design the database | 03 | Parent `09` for read models; parent `12` for lifecycle/migrations |
| Design shared or platform | 04 or 05 | Matching structured template; this package's guide 11 for preset UI/skills; parent `03` and parent `11` for trust boundaries |
| Design features and contracts | 06 | Parent `02`, `04`, or `05` according to the selected flow |
| Design routes and journeys | 07 | Selected stack profile; parent `10` for runtime/UI budgets |
| Build one vertical slice | 08 | Selected feature skill/plan plus exactly one parent flow owner |
| Publish or evolve the demo | 09 | Parent `14`, `15`, or `16` according to the decision |

`depends_on` is lookup metadata, not a request to preload every parent guide. After a decision artifact is complete, start the next workstream with that artifact and its current owner instead of retaining the full planning context.

## Completion contract

An authored web preset is complete only when its manifest, template, contract, pattern catalog, source ledger, seven canonical namespaced skill packages and every declared optional package agree by digest; clean-room materialization and clean-context forward evaluations for every declared skill pass both pattern-conformance and requested-outcome gates; and every `verified` capability closes its exact-version inter-layer walking slice. `provided`, `conditional` and `unsupported` remain explicit. Preset acceptance is not application production readiness.

A reference application is complete only when:

- every capability selected by the tier plus additive risk decisions has implementation and evidence;
- the stack profile is compatible, version-aware, and reproducible;
- selected critical journeys work with deterministic seed data;
- access and isolation appropriate to the tier are tested, including tenant allow/deny only when tenancy is selected;
- duplicate, concurrent, failed, and degraded paths are demonstrated when their capability is selected;
- architecture, test, build, migration, telemetry, release, and recovery gates pass;
- showcase-only behavior is explicit and removable.

The phrase “demo complete” must not mean “screens render.” Use [09-demo-operations-and-extension.md](09-demo-operations-and-extension.md) to prove safe operation and a credible path to a real product.

## Stop conditions

Stop and resolve the plan when the operating mode is ambiguous, preset installation would overwrite undeclared local work, the stack is internally incompatible, the domain is a disconnected kitchen sink, a selected capability has no owner/journey/evidence, provider SDKs leak into business policy, public demo data can cause real side effects, or the generated plan relies on UI testing to prove server/data correctness.
