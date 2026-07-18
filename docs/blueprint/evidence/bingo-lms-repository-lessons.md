---
document_id: SKEL-EVID-BINGO-REPO-01
title: Bingo LMS repository-derived lessons
status: experimental
audience: human-and-ai
---

# Bingo LMS repository-derived lessons

> This record is evidence input for portable blueprint rules. It is not an accepted stack profile, reusable preset, package-graduation decision, or production-readiness assessment.

## Source identity and current observation

- Repository: `https://github.com/phamviet86/bingo-lms.git`.
- Observed revision: `3ce223c9fd94c0cf8da69c5e4ecc393b7e5b539d` on 2026-07-18.
- Acquisition: owner-provided local checkout, read-only inspection and focused repository commands.
- License: no repository license file was present at the observed revision. No source code or app documentation is redistributed here; only observed failures, portable outcomes and non-authoritative locators are recorded.
- Live environment: not accessed. No database, provider, deployment, migration, seed, reset, retention or production operation ran.

Current focused evidence at the observed revision:

| Evidence | Result | Claim limit |
| --- | --- | --- |
| `npm run check:skills` | Passed: seven canonical, one release, one audit and one support package | Skill/governance structural contract only |
| Five focused script suites | 57/57 tests passed for skill routing, publish topology, audit state, disposable-database guard and schema history | Repository-local deterministic behavior only |

The focused suite command was:

```text
npm test -- tests/scripts/check-skills.test.js tests/scripts/publish-topology.test.js tests/scripts/audit-state.test.js tests/scripts/disposable-database.test.js tests/scripts/schema-sql.test.js
```

## Promoted lessons

| Observed failure or hardening | Portable invariant promoted to core | Owning concern and falsifying evidence | Source-specific material retained outside core |
| --- | --- | --- | --- |
| At the observed revision, `AGENTS.md` and `docs/governance` routed the working application through accepted repo-local artifacts and skill/pattern guidance without reusable preset-materialization provenance | Governed apps have two explicit authority routes: preset-created apps use a preset lock; existing/custom apps use a revision- and digest-bound app profile, never both at once | Guides `06`, `07` and the app-profile validator; simultaneous authority, movable revision, stale digest/status and incomplete registry negatives | Bingo governance paths, artifact IDs, skill names and current manual registry shape; Bingo was not adopted through the new validator in this run |
| Build referenced a nonexistent generator before `83fac4472766dd7154cbd189c87c1697ca076c37` | A bootstrap contract declares stable command lanes, and clean-room evidence runs the exact declared commands | Guide `06`; missing lane, wrong command and nonzero start-smoke fixtures | Package-manager script names and generator implementation |
| Disabled pagination was lost as a falsy value before `eee9f031fe57ea45baf462114e148d161b85384c` | Boundary tests preserve meaningful `false`, `null`, zero and omission semantics end to end | Guides `09` and `14`; sentinel normalization fixtures | Table library, query client and ORM pagination syntax |
| Identifier validation rejected values produced by the real store before `e55dc2d3fe803332f7e84ea6b0ea829e00c5551c` | Contract fixtures use representative persisted identifier, timezone and default shapes rather than convenient placeholders | Guides `12` and `14`; real-shape positive and malformed negative fixtures | Database-specific identifier validator and schema type |
| A green aggregate baseline still missed duplicate external effects, unauthorized-route runtime behavior and ineffective double-submit proof before `fc07a18c253a913555d095d79a2afa986968bd30` | Static/build evidence cannot substitute for concurrency, authenticated runtime or real interaction proof; skipped/unparsed scope is `NOT_EXECUTED` | Guides `10`, `13` and `14`; duplicate, ambiguous-result, second-submit and scoped runtime negatives | Product routes, vendor status vocabulary and UI component implementation |
| Test mutation and schema operations needed target-collision and schema-history hardening | The mutation wrapper itself proves a disposable target; schema history has a fixed authority, integrity record, clean replay and recovery path | Guide `12`; guard-bypass, alias-collision, checksum/order, transaction and lock-ownership negatives | PostgreSQL endpoint normalization, SQL-first policy and database tooling |
| Skill forward evaluation exposed ownership, false-gap, support-skill and completion ambiguity around checkpoint `66c48665e163b2b6cb96b595fe104501f89d5af9` | One vertical outcome has one task owner, support roles inherit its pattern, `TASK_REROUTED` continues, and outcome/conformance verdicts remain separate | Guide `07` and preset guide `11`; adversarial clean-context routing cases | Bingo skill names, pattern IDs and feature path policy |
| Audit and publication workflows required immutable revision/checkpoint and fail-closed checkout topology | Optional operational skills bind exact source/target revisions, never promote unproved checkpoints, stop before destructive conflict handling and verify final destination identity | Guides `07` and `15`; disconnected range, rename/symlink, ambiguous target, remote movement and conflict fixtures | Direct-main policy, worktree choreography, remote name and indexing tool |

## Portability check

Every promoted invariant above has a semantic mapping in both documented profile families:

| Portable concern | Next.js profile mapping | Django profile mapping |
| --- | --- | --- |
| Current authority and vertical analyzer/skill ownership | Selected preset/app-profile authority, one primary owner and support tasks | Same authority choice and ownership semantics across app/template boundaries |
| Exact command lanes and clean execution | Lockfile-compatible install through bounded start smoke | Environment/lock-compatible install through bounded start smoke |
| Data modes, mutation guard and schema history | Profile-selected data tools, disposable-target wrapper and accepted migration mechanism | Profile-selected data tools, isolated-target wrapper and accepted migration mechanism |
| Boundary values, public wire shapes and import safety | Server/client contracts and runtime-client initialization boundary | Full/fragment contracts and settings/client initialization boundary |
| UI state/action and architecture fitness evidence | Browser interaction plus negative import/runtime/architecture fixtures | Browser interaction plus negative public/import/architecture fixtures |
| External effects, operations and optional audit/publish | Stack-selected claim/finalize/reconciliation and project topology | Stack-selected claim/finalize/reconciliation and project topology |

The detailed mappings live in the [Next.js family profile](../profiles/nextjs-prisma-antd.md#portable-qualification-mapping) and [Django family profile](../profiles/django-postgresql-htmx.md#portable-qualification-mapping). This is an editorial portability check, not execution evidence for either profile. A rule that later requires different semantics in one family must move to a profile/preset or be removed from core.

## Evidence limitations and invalidation

- The focused run does not prove the full application, production build, authenticated journeys, backup, restore, SLO, alerts, security posture or live-data correctness at the observed revision.
- Historical change records indicate the failure and its repository-local repair; this comparison did not execute pre-repair revisions, and the records do not prove every future stack needs the same mechanism.
- One JavaScript web stack cannot prove portability or package stability. Every promoted invariant must map without semantic change to both documented profile families and later pass independent adoption evidence.
- Any change to the observed revision, relevant skill/guard tests, or promoted core contract invalidates the corresponding current-evidence claim until re-run.
