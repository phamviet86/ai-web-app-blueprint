---
guide_id: SKEL-ROUTER
title: Production Repository Blueprint Adoption Router
status: experimental
audience: human-and-ai
package_version: 0.13.0
control_catalog_version: 1.0.0
artifact_schema_version: "1.0"
purpose: Route humans and AI agents through a stack-neutral production blueprint with optional implementation profiles.
read_when:
  - Starting greenfield, architecture evolution, brownfield refactor, production-readiness, or repo-blueprint work.
skip_when:
  - A narrow task already has a proven owner, contract, and repo-local workflow.
depends_on: []
owns:
  - blueprint authority and source policy
  - operating-mode and task routing
  - package quality target and context budget
---

# Production repository blueprint adoption router

> Shared human/AI entrypoint. Select one operating mode and adoption stage, then load only the owners required for the current decision.

## What this package is

This package is an architecture core for:

- starting a production repository from zero;
- evolving a healthy repository without eroding its boundaries;
- incrementally refactoring a repository whose current structure is weak;
- auditing production readiness with evidence.

In the distributable repository it lives under `docs/blueprint` and remains the source of truth. The repository-level [README](../../README.md), [AI router](../../AGENTS.md), and [preset catalog](../presets/README.md) may route work into this package, but they do not override its architecture owners.

It is not a generalized copy of its host repository. Live repositories and current patterns are evidence, migration constraints, and possible anti-patterns—not the definition of the target architecture.

The core is stack-neutral. A file under `profiles/` maps core roles to a concrete stack. Templates and illustrative logical patterns are loaded only when the task produces those artifacts. Humans remain accountable for product constraints, risk acceptance, and release decisions; AI may discover evidence, draft artifacts, implement scoped changes, and run checks but may not invent those approvals.

## Package status and claims

| Contract | Current declaration |
| --- | --- |
| Package version/maturity | `0.13.0` / `experimental` |
| Control catalog | `1.0.0` in guide `08` |
| Artifact schema | `1.0` in [templates/README.md](templates/README.md) |
| Structural validation | `python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .` |
| Preset-package validation | `python3 docs/blueprint/scripts/validate_presets.py docs/presets` |
| Existing/custom app validation | `python3 docs/blueprint/scripts/validate_app_profile.py PATH --repo-root ROOT --expected-revision <current-source-revision> --expected-blueprint-revision <selected-blueprint-revision>` |
| Graduation policy/history | [MATURITY.md](MATURITY.md) / [CHANGELOG.md](CHANGELOG.md) |

The package is suitable for evaluation and governed pilots with human review. It has not yet established the multi-pilot evidence required for `stable`. A passing docs validator establishes structural conformance only; it does not make this package, a reference app, or an adopting implementation production-ready.

## Quality target

The documentation design target is **9.5/10 coverage** across architecture, security, data, reliability, testing, delivery, operations, evolution, governance, and human/AI usability. It is a target, not a self-awarded maturity score. Guide `08` scores an actual repository only from versioned controls and current implementation/operational evidence.

A conditional control may be `N/A` only with a named owner, rationale, and revisit trigger. “Not needed” without a risk decision is a gap.

## Authority order

For a greenfield repo:

1. user/product constraints and declared quality attributes;
2. this core blueprint;
3. accepted ADRs and system/risk profile;
4. selected stack profile and primary version-aware documentation;
5. implementation evidence.

For an existing repo, preserve observable behavior and data safety unless change is authorized. Use current code to discover contracts; do not copy its debt into the target. Repo-local canonical instructions remain authoritative until the blueprint is explicitly adopted for that concern. After adoption, app work resolves exactly one concrete authority: a verified preset lock, or a validated app profile that binds accepted repo-local artifacts, patterns, skills, commands, clean-room execution evidence, dual-verdict evaluations, revisions, and digests.

## Semantic labels

- **Invariant:** portable ownership, dependency, trust, or quality rule.
- **Risk control:** baseline or conditional control selected from the system profile.
- **Stack mapping:** concrete implementation of a core role; replaceable.
- **Transition rule:** temporary brownfield mechanism with owner and expiry.
- **Evidence:** executable check, artifact, measurement, or verified runtime observation.

## Guide map

| Guide | Owns |
| --- | --- |
| [01-foundations.md](01-foundations.md) | Drivers, quality attributes, risk profile, topology, cohesion, root capability map |
| [02-module-anatomy-and-public-contracts.md](02-module-anatomy-and-public-contracts.md) | Module anatomy, public API, domain/application/ports/adapters/presentation |
| [03-shared-kernel-and-platform.md](03-shared-kernel-and-platform.md) | Shared kernel/UI, platform capabilities, composition and configuration boundaries |
| [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md) | Dependency inversion, cross-module sync flows, commands/queries, transactions, error contracts |
| [05-semantic-pattern-selection.md](05-semantic-pattern-selection.md) | Semantic module/use-case archetypes and abstraction decisions |
| [06-greenfield-bootstrap-and-portability.md](06-greenfield-bootstrap-and-portability.md) | Greenfield walking skeleton, production bootstrap phases, stack portability |
| [07-ai-operating-system-and-governance.md](07-ai-operating-system-and-governance.md) | AI operating system, ADRs, rule ownership, context routing, exception governance |
| [08-scorecard-and-readiness-gates.md](08-scorecard-and-readiness-gates.md) | Ten-dimension scorecard, readiness gates, risk-proportionate evidence |
| [MATURITY.md](MATURITY.md) | Package version, maturity, compatibility, graduation, downgrade and claim policy |
| [09-query-cache-and-read-models.md](09-query-cache-and-read-models.md) | Query DSL, allowlists, pagination/cache identity, read-model decisions |
| [10-runtime-accessibility-and-performance.md](10-runtime-accessibility-and-performance.md) | Runtime selection, native-first UI, accessibility, performance and capacity budgets |
| [11-security-identity-and-privacy.md](11-security-identity-and-privacy.md) | Threats, identity/session/authz, privacy, secrets, abuse and audit controls |
| [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md) | Data inventory, isolation, retention, schema/data migration, RPO/RTO and restore |
| [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md) | Deadlines, retries, idempotency, concurrency, events, queues, webhooks and degradation |
| [14-testing-and-architecture-fitness.md](14-testing-and-architecture-fitness.md) | Test portfolio, deterministic data, contract/nonfunctional tests, architecture fitness |
| [15-delivery-observability-and-operations.md](15-delivery-observability-and-operations.md) | Environments, CI/CD, supply chain, telemetry, SLOs, incidents and runbooks |
| [16-refactor-and-evolution.md](16-refactor-and-evolution.md) | Characterization, seams, strangler/cutover, compatibility and decommissioning |
| [17-reference-patterns.md](17-reference-patterns.md) | Illustrative, non-compile-ready logical contracts loaded only while generating implementation |
| [profiles/nextjs-prisma-antd.md](profiles/nextjs-prisma-antd.md) | Candidate Next.js/React/Ant Design/TanStack Query/Prisma mapping; project-local provenance and compatibility proof required |
| [profiles/django-postgresql-htmx.md](profiles/django-postgresql-htmx.md) | Django/PostgreSQL/HTMX server-rendered mapping and second-stack portability evidence |

### Companion packages

| Package | Use for |
| --- | --- |
| [reference-app-blueprint/README.md](reference-app-blueprint/README.md) | Select a stack and risk-proportionate capability tier, then plan/build a traceable reference application without redefining core rules |
| [../presets/README.md](../presets/README.md) | Catalog contract for exact-version presets authored and instantiated through the reference-app companion; no runnable preset is currently included |

### Load-on-demand decision artifacts

| Template | Use for |
| --- | --- |
| [templates/system-profile.md](templates/system-profile.md) | Drivers, risk, quality targets, topology, applicable controls |
| [templates/README.md](templates/README.md) | Canonical artifact-instance schema, statuses, catalog, and filled examples |
| [templates/artifact-registry.md](templates/artifact-registry.md) | Stable artifact IDs, current locations, supersession, and tombstones |
| [templates/architecture-exception.md](templates/architecture-exception.md) | One bounded deviation with risk owner, ratchet, expiry, and removal proof |
| [templates/exception-ledger.md](templates/exception-ledger.md) | Active/historical exception index and expiry enforcement |
| [templates/readiness-assessment.md](templates/readiness-assessment.md) | Reproducible control-level scoring, evidence freshness and readiness cap |
| [controls/README.md](controls/README.md) | Machine control catalog, scorer input, hash-resolved evidence manifest, and CI result semantics |
| [templates/adr.md](templates/adr.md) | Consequential architecture decision and fitness/revisit policy |
| [templates/threat-model.md](templates/threat-model.md) | Trust-boundary data flow, abuse cases, controls and residual risk |
| [templates/access-matrix.md](templates/access-matrix.md) | Subject/action/resource/tenant authorization and lifecycle |
| [templates/data-migration.md](templates/data-migration.md) | Expand/backfill/compare/switch/contract and recovery plan |
| [templates/test-strategy.md](templates/test-strategy.md) | Risk-to-test mapping and architecture fitness registry |
| [templates/slo-runbook.md](templates/slo-runbook.md) | Critical-journey SLI/SLO, alerts and mitigation |
| [templates/release-recovery.md](templates/release-recovery.md) | Artifact, rollout, compatibility and recovery gates |
| [templates/refactor-slice.md](templates/refactor-slice.md) | One frozen and characterized brownfield seam with candidate/checker closure through decommission |

Frontmatter `depends_on` identifies rule owners for just-in-time lookup; it does not trigger transitive preload. The task router's **Required reads** column is the only automatic bundle.

## Select operating mode

| Mode | Use when | Default posture |
| --- | --- | --- |
| `GREENFIELD` | No production contract exists yet | Define drivers and walking skeleton before abstractions |
| `EVOLUTION` | Existing architecture is sound enough | Preserve contract, change one coherent owner, prevent regression |
| `REFACTOR` | Target structure differs materially from legacy | Characterize, create seam, migrate/cut over incrementally |
| `RELEASE` | Preparing/deploying/operating a change | Prove compatibility, observability, recovery and ownership |
| `AUDIT` | Scoring gaps or drift | Require evidence; do not infer implementation from docs |

## Progressive adoption for humans and AI

Do not copy the entire package into a repository and call it adopted. Use guide `06`'s staged contract:

1. **Evaluate:** a human names the decision/system; AI routes the smallest owner set and reports fit/gaps. No repo rule changes.
2. **Profile:** jointly instantiate a system profile and artifact registry; humans accept drivers, unknowns, owners, and control applicability.
3. **Prove:** implement or characterize one real vertical slice and collect falsifiable evidence. AI may draft; owners accept observable contract and residual risk.
4. **Enforce:** adopt only applicable rules in repo-local guidance/checks; register ADRs and bounded exceptions instead of copying prose.
5. **Release-govern:** score the named revision/deployment, pass applicable gate IDs, and obtain human release/risk acceptance.

At every stage record package/catalog/schema versions, source revision, decisions, evidence, and the next trigger. Teams may stop after evaluation or profile without pretending later stages passed.

## Task router

Read required guides in order. Add at most the owner of the next unresolved concern.

| Task | Required reads | Add only when needed |
| --- | --- | --- |
| Evaluate/adopt this package | README, 06, MATURITY | 07 when installing artifact governance; template `system-profile` |
| Define a new system or topology | 01, 08 | 02 for module shape; template `system-profile` |
| Design or reshape a module | 02, 04, 05 | Selected profile only when translating the accepted design |
| Implement an accepted synchronous slice | 17, 04 | Selected profile |
| Implement an accepted query/read slice | 17, 09 | Selected profile |
| Implement an accepted async/integration slice | 17, 13 | Selected profile |
| Add shared/platform capability | 03, 01 | 11 for trust; 15 for runtime/operations |
| Add synchronous use case/transaction | 04, 02 | 05 for archetype; 13 for concurrency/idempotency |
| Add query/search/read model | 09, 04 | 12 for schema/data; 10 for measured cost |
| Add event/job/webhook/vendor flow | 13, 04 | 11 for external trust; 12 for data consistency |
| Add identity/security/privacy control | 11, 04 | 14 for verification; threat/access templates |
| Evolve schema or data contract | 12, 09 | 16 only for brownfield/cutover; 13 for concurrent delivery |
| Define testing or fitness checks | 14, 08 | Owning architecture/security/data guide |
| Optimize runtime/UI/database | 10, 14 | 09 for query cost; selected profile |
| Bootstrap a greenfield walking slice | 01, 06, 14 | Selected profile during implementation; 08 at readiness assessment |
| Prepare CI, release, telemetry, SLO or incident flow | 15, 08 | 11/12 for their risk controls |
| Refactor a weak/legacy module | 16, 14 | Owner of the target boundary; 08 at scored checkpoints |
| Cut over or decommission a refactor | 16, 15, 08 | 12/13 for data or async recovery |
| Add ADR, AI guide, skill, or exception | 07, 08 | 01 for system-level decision |
| Maintain/release this docs package | README, 07, 08, MATURITY | Templates/examples only when their contract changes |
| Plan or build a stack-selected reference application | Companion `reference-app-blueprint` router | Load core owners only as that router requests |
| Author, verify, or instantiate a reusable preset | Companion `reference-app-blueprint` guide `10` | Preset catalog contract; load core owners only for unresolved contracts |
| Author preset skills or UI/design evidence | Companion `reference-app-blueprint` guide `11` | 07 for portable skill/source rules; 01 or 04 for stack/design owners |
| Govern an existing/custom application without preset provenance | README, 06, 07, 14 | Accepted system/stack artifacts, app-profile schema, repo-local command registry, and dual-verdict skill evaluations |

Do not combine every optional concern into one context. Context cost is cumulative: finish design with a decision artifact, then start implementation from `17` + the selected profile + exactly one flow owner instead of retaining all design guides. Split architecture, safety, implementation, and release into coherent workstreams.

## Mode-aware execution protocol

```text
SELECT MODE + RISK CLASS
  -> FREEZE OR DEFINE OBSERVABLE CONTRACT
  -> LOAD CURRENT RULE OWNER
  -> CHOOSE TARGET SEAM + DEPENDENCY DELTA
  -> IMPLEMENT ONE COHERENT VERTICAL CHANGE
  -> PROVE WITH THE LOWEST SUFFICIENT EVIDENCE
  -> RECORD DECISION, EXCEPTION, AND RESIDUAL RISK
```

Mode additions:

- `GREENFIELD`: establish system profile -> topology -> walking slice -> production gates.
- `EVOLUTION`: inspect live contract -> change owner -> enforce no new violations.
- `REFACTOR`: characterize -> seam -> shadow/compare; reclassify cutover/decommission as `RELEASE` and load guide `15`.
- `RELEASE`: verify compatibility -> promote the reviewed artifact, or its reproducible platform build -> observe -> rollback/roll forward.
- `AUDIT`: collect evidence -> score -> prioritize highest risk-adjusted gap.

## Package guardrails

- Core files contain no product-specific feature catalog or remembered library API.
- Exact framework/library behavior belongs in a dated profile and primary references.
- One detailed rule has one owning guide; other guides link to the rule ID.
- Illustrative implementation-shape pseudocode belongs in `17`; compile-ready stack code belongs in a verified profile or adopting repository, never in conceptual owners.
- Templates capture decisions; they do not become mandatory ceremony for unrelated tasks.
- Each guide stays independently loadable and near 300 lines or fewer.
- A default task bundle stays at four guides or fewer and roughly 900 lines or fewer.
- Architecture controls should become lint/tests/pipeline gates where mechanically enforceable.
- Transition mechanisms must have owner, success metric, expiry, and deletion trigger.
- Governance artifact instances use schema `1.0`, stable IDs, controlled status transitions, and the artifact registry.
- Application source uses one validated authority path at a time. A preset lock proves reusable materialization provenance; an app profile proves only the named existing repository's accepted local authority and evidence.
- Package releases follow `MATURITY.md` and cannot promote their own maturity without named graduation evidence.
- `python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .` is the local/CI structural gate from the repository root; semantic and runtime claims still require review/evidence.
- `python3 docs/blueprint/scripts/validate_presets.py docs/presets` additionally fails closed on any future preset manifest, skill, pattern, source, or evaluation package; an empty catalog remains valid.
- `python3 docs/blueprint/scripts/validate_app_profile.py PATH --repo-root ROOT --expected-revision <current-source-revision> --expected-blueprint-revision <selected-blueprint-revision>` fails closed on stale or contradictory authority references for an adopting existing/custom app; it does not make that app a reusable preset.

## Evidence basis

The quality model is informed by current primary sources including [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/), [NIST SSDF 1.1](https://csrc.nist.gov/projects/ssdf), [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [SLSA 1.2](https://slsa.dev/spec/v1.2/), [OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/), and official framework/library documentation. The revision-bound [Bingo LMS repository lesson record](evidence/bingo-lms-repository-lessons.md) and [repository-wide refactor lesson record](evidence/bingo-lms-refactor-lessons-2026-07-19.md) supply two observations from one real-app repository for portable rules, not stack authority, an independent pilot, or readiness proof. These sources define verification baselines, not a universal enterprise ceremony; the system profile selects proportionate controls.

## When not to use this package

Skip it for a one-line change, a local bug with a known contract, or work already fully governed by a narrower repo skill. Do not use “9.5/10” as permission for speculative platforms, microservices, generic factories, or exhaustive UI testing.
