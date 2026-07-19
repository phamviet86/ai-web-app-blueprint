---
document_id: SKEL-EVID-BINGO-REFACTOR-01
title: Bingo LMS repository-wide refactor lessons
status: experimental
audience: human-and-ai
---

# Bingo LMS repository-wide refactor lessons

> This is revision-bound evidence input for portable blueprint rules. It is not an app profile, preset, stack authority, second pilot, package-graduation decision, runtime-performance benchmark, or production-readiness assessment.

## Source identity and safety boundary

- Repository: `https://github.com/phamviet86/bingo-lms.git`.
- Frozen pre-refactor baseline: `fe08bff014cdd18354cf6cc76680df851626d9bf`.
- Refactor branch content target: `3fd5a8c5232eaecd5ed1f6a6ced90881df8e5e61`.
- Observed merged revision: `98c2faf05c17a55fc4fded80f38119e6f93a7d2f` on 2026-07-19; local `main` and `origin/main` agreed and the worktree was clean before and after the audit.
- Content identity: refactor target and merged revision both resolve to tree `ab767d965b34aeb2fbbd4a077f680e9031223e58`; the merge adds no refactor-content delta. Baseline-to-target changes 116 files with 4,235 insertions and 1,908 deletions.
- Acquisition: owner-provided local checkout, read-only code/docs/tests/history/graph inspection, plus focused non-database commands.
- License: no repository license file was present. No source code or app documentation is redistributed here; only observed outcomes, portable invariants, immutable identities, and non-authoritative locators are recorded.
- Data mode: `NONE`. No database, provider, deployment, migration, seed, reset, external message, production credential, or live environment was accessed.

## Current focused evidence

These checks were executed against observed revision `98c2faf05c17a55fc4fded80f38119e6f93a7d2f` during the core audit:

| Evidence | Current result | Claim limit |
| --- | --- | --- |
| `npm run check:skills` | Passed: seven canonical, one release, one audit, and one support package | Repository-local skill/governance structure only |
| `npm run check:architecture` | Passed: zero covered runtime import cycles and zero covered cross-feature broad-browser imports | Only the checker's declared static import/re-export syntax and paths |
| `npm run check:contracts` | Passed: 84 public surfaces | Export identity/compatibility inventory, not wire or behavioral equivalence |
| Eight focused characterization suites | 92/92 tests passed | Query, shared mechanics, attendance workflow, integration policy/delivery, responsive layout source contract, and architecture checker behavior only |

The focused test command was:

```text
npm test -- tests/scripts/check-architecture.test.js tests/platform/query-contract.test.js tests/shared/form-submit.test.js tests/shared/filter-value.test.js tests/features/attendances/attendance-notification-form-workflow.test.js tests/features/zalo/zalo-token.application.test.js tests/integrations/zalo-message-delivery.test.js tests/shared/layout-responsive-contract.test.js
```

No build, database suite, browser E2E, deployment, or external I/O was run as part of this current audit.

## Historical source-reported closure

The source repository's revision-bound record at `docs/governance/evidence/repo-wide-refactor-2026-07-19.md` reports broader closure against the same refactor content: guarded disposable-database verification, 28 files/99 database tests, focused E2E, a fail-closed build with database endpoints made unreachable, a full check with 679 passed and 28 skipped tests, documentation/preset validators, graph indexing, clone classification, and frozen-boundary diffs. That record also states no live database access.

Those broader results were not independently re-executed during this core audit. They are historical source-reported evidence, not current command evidence merely because the observed merge has the same tree.

## Observed refactor outcomes and promoted invariants

| Observed outcome | Portable invariant promoted or strengthened | Core owner and falsifying evidence | Source-specific material retained outside core |
| --- | --- | --- | --- |
| The structural slice pinned its baseline and froze routes, authorization, DTO/ordering/pagination/error behavior, provider effects, schema/history, dependency manifests, and compatibility facades | A structural-only refactor binds an immutable baseline, declared frozen artifact groups, authorized deltas, and fail-closed final diff/check evidence; omitted or unreadable scope is not passing | `REFACTOR-BASELINE-01`; wrong revision, missing group, unauthorized drift, stale digest/query, or snapshot-only behavior claim | Exact repository paths, product contracts, package manager, schema tool, and Git worktree topology |
| Covered architecture fitness moved from two runtime strongly connected components and 87 broad cross-feature facade imports to zero/zero while retaining 67 prior surfaces and adding 17 narrow public leaves | A compatibility/composition facade may remain, but new cross-module consumers use the narrowest intentional public sub-surface; graph evidence resolves supported imports/re-exports and limits zero claims to declared coverage | `MODULE-PUBLIC-01`, `FITNESS-REGISTRY-01`, `FITNESS-CHECK-PROOF-01`; direct/self/re-export cycle, broad surface, deep import, ignored path, unsupported syntax, or parser failure negatives | Client/runtime filenames, language-specific parser implementation, exact surface counts, and application module names |
| A pinned clone scan classified all 55 groups as 37 intentionally local, eight false positives, and ten record-only; none was automatically extracted, while three separately proved mechanics were shared | Clone/line/complexity tools nominate candidates. Every finding receives `REFACTOR_CONFIRMED`, `INTENTIONAL_OWNER_LOCAL`, `FALSE_POSITIVE`, or `RECORD_ONLY`; record-only is not completion and shared extraction requires semantic equivalence | `REFACTOR-CANDIDATE-01` and `SHARED-PROMOTION-01`; unclassified finding, syntax-only refactor, divergent authorization/labels/lifecycle, missing owner, or record-only completion claim | Clone tool/version/threshold, exact findings, feature labels, and project-local duplication percentage |
| Shared form/filter mechanics and query normalization were decomposed only after presence, failure, callback, alias/coercion, group/error precedence, limit, ordering, and pagination behavior was characterized | Shared and query refactors use a behavior-equivalence matrix; logical pure stages preserve defaults, meaningful values, error precedence, effect timing, and absence of downstream I/O after rejection | `SHARED-PROMOTION-01`, `QUERY-BOUNDARY-01`, `TEST-CHARACTERIZATION-01`; `false`/`null`/zero/empty/omitted drift, reordered error/callback, broadened allowlist, new adapter call, or consumer-specific policy leak | UI library lifecycle, field/operator names, query adapter syntax, and project-specific error text |
| Complex entrypoints and integration facades became smaller seams while feature-owned coordinators, pure decisions, and explicit I/O modules retained behavior and public facades | Optional orchestration decomposition is selected by cohesion, dependency direction, effect isolation, change cadence, and testability—not file length. Refactor equivalence covers public shape, call cardinality/order, transaction span, retry, idempotency, fencing, and ambiguous outcomes | `MODULE-PRESENTATION-01`, `REFACTOR-CHARACTERIZE-01`, `PUBLIC-CONTRACT-PROOF-01`; extra/missing/reordered I/O, network inside a transaction, changed ambiguous retry, weakened claim/fencing, or public method drift | Framework component/hook structure, vendor protocol/statuses, exact complexity threshold, and product workflow |
| The historical source closure ran artifact build with dependency endpoints made unreachable | Import, analysis, test discovery, check, and build do not eagerly start runtime-only clients or demand runtime-only secrets when independence is claimed; legitimate build-time dependencies have a separate isolated contract | `RUNTIME-INITIALIZATION-01` and `TEST-SEAM-01`; absent secret or unreachable endpoint causes eager access, hidden external work, or undeclared build dependency | Exact environment names, endpoint poison value, client library, and build command |

## Portability check without profile mutation

The promoted rules map semantically to both existing profile families without changing either profile:

| Portable concern | Client-heavy modular stack mapping | Server-rendered modular stack mapping |
| --- | --- | --- |
| Frozen structural baseline | Pin routes/entrypoints, public contracts, schema/history, dependency locks, build/runtime configuration, and allowed source groups | Pin URL/view/template/form contracts, application services, schema/history, dependency locks, settings, and allowed source groups |
| Narrow public surfaces | Intentional module sub-surfaces separate composition compatibility from cross-module consumer contracts | Intentional package/application/facade modules expose only the capability needed by another app/module |
| Candidate disposition | Component, query, state, and integration candidates require semantic/lifecycle equivalence before extraction | View, form, template, service, and query candidates require semantic/lifecycle equivalence before extraction |
| Behavior/effect equivalence | Characterize serialization, interaction states, callbacks, adapter calls, transactions, and external effects | Characterize full/fragment responses, form/error precedence, service calls, transactions, and external effects |
| Import/build isolation | Static analysis/build runs without runtime-only services when the selected build contract claims independence | Import/check/static-asset or artifact build runs without runtime-only services when the selected build contract claims independence |

The concrete mappings remain owned by the [Next.js family profile](../profiles/nextjs-prisma-antd.md) and [Django family profile](../profiles/django-postgresql-htmx.md). This table is editorial semantic mapping only; it creates no profile, app-profile authority, preset, or runtime portability proof.

## Evidence limitations and invalidation

- The source architecture parser deliberately ignores dynamic imports. Core checker claims therefore require explicit dynamic/conditional/generated coverage accounting and report uncovered branches as `NOT_EXECUTED`; the source's zero result is not generalized beyond its static coverage.
- Graph node/edge totals varied across fresh tool runs. Portable claims use the deterministic repository checker results, not absolute graph totals.
- Clone similarity, line count, and complexity are discovery signals. They do not prove an abstraction or runtime optimization.
- No representative before/after latency, memory, bundle, query-cost, throughput, or external-cost benchmark was available. The evidence supports structural fitness, dependency control, and testability improvement—not faster runtime performance.
- One application stack and a second observation of the same repository cannot prove cross-stack portability, package stability, preset usability, or an independent pilot.
- Any source revision/tree change, checker-coverage change, relevant test change, or promoted core-contract change invalidates the corresponding current claim until evidence is re-run and re-bound.
