---
template_id: REFAPP-TPL-PRESET-CONTRACT
template_version: 1.1.0
produces: preset-contract
owner_guide: ../10-preset-authoring-and-instantiation.md
use_when: Authoring or revising one versioned stack preset and proving its materialization and inter-layer compatibility.
---

# Preset contract: [preset ID and version]

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: preset-contract`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `PRESET-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Preset ID / semantic version / maturity:
- Blueprint version / revision:
- `preset.json` path / schema version `1.1.0` / manifest digest:
- Verification command registry path / digest / schema version:
- Source stack profile / exact lockfile provenance:
- Pattern catalog / UI design contract / source ledger paths and digests:
- Target archetype and supported capability tiers:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:

## Filesystem and materialization map

| Template source | Target path | Create / merge / replace | Conflict/idempotency policy | Upgrade/removal owner |
| --- | --- | --- | --- | --- |

- Framework scaffold/version command:
- Application-code root and framework-default root exceptions:
- Paths deliberately not materialized:
- Application preset-lock target:

## Capability matrix

Use `provided`, `verified`, `conditional`, or `unsupported`. Only `verified` rows may claim exact-version compatibility.

| Capability ID | Layer | Status | Public contract/consumer | Constraint or unsupported rationale | Walking-slice `EVID-*` |
| --- | --- | --- | --- | --- | --- |

## Inter-layer contract matrix

| Flow ID | Producer/surface | Versioned request/input | Action/query + service | Repository/adapter/data or provider | Result/UI behavior | Negative-path `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- |

## Shared UI and input baseline

| Category/item | Required / conditional | Stable shared semantics | Feature-owned configuration | Input/output normalization | Accessibility/state evidence |
| --- | --- | --- | --- | --- | --- |

## Data, auth, feature, and app boundaries

| Boundary | Concrete path | Owns | May depend on | Must not own/import | Fitness evidence |
| --- | --- | --- | --- | --- | --- |

## AI skill routing

Guide [11](../11-preset-agent-skills-and-design-evidence.md) owns the skill contract. Resolve paths through `preset.json`; names are namespaced by preset ID.

| Manifest capability | Skill name / `SKILL.md` path | Distinct trigger branches | Freedom / allowed paths | Pattern/resource IDs | Verification/stop condition |
| --- | --- | --- | --- | --- | --- |
| Analyze request | | | | | |
| Add/modify lib | | | | | |
| Add/modify shared | | | | | |
| Add/modify feature | | | | | |
| Add/modify app | | | | | |
| Add/modify new pattern | | | | | |
| Design/review UI | | | | | |
| Audit immutable change range/checkpoint (optional) | | | | | |
| Publish validated final revision (optional) | | | | | |

For each coherent outcome, assign one vertical pattern and one evidence tier: `ESTABLISHED_PATTERN`, `PATTERN_EXTENSION`, or `CANDIDATE_GAP`. Give every task exactly one owner and exactly one data-access mode: `NONE`, `LIVE_READ`, `TEST_MUTATION`, or `PRODUCTION_HANDOFF`. Mark the semantic owner `primary`; mark lib/shared/UI/app tasks enabling the same flow `support` and inherit the same pattern. Treat `TASK_REROUTED` as analyzer continuation, not a verdict or outcome-level block.

## Pattern, source, design, and integrity synchronization

| Registry | Path / version | SHA-256 digest | Inputs/consumers | Freshness/invalidation trigger | Reviewer |
| --- | --- | --- | --- | --- | --- |
| Template/materialization | | | | | |
| Pattern catalog/exemplars/fixtures | | | | | |
| Skill packages/resources/scripts | | | | | |
| UI design contract/evidence index | | | | | |
| Official/advisory source ledger | | | | | |

## Source and API evidence

| Stack/design claim | Exact version/commit and license | Official URL | Context7 ID / scoped query / `retrieved_at` | Advisory use or fallback | Review deadline / invalidation |
| --- | --- | --- | --- | --- | --- |

Third-party output is untrusted advisory input. Record read-only/sandbox boundaries and accepted/rejected recommendations; do not install it globally or let it override official APIs, blueprint/preset rules, accessibility or product decisions.

For every pattern, record one declared primary owner, unique declared support skills, exact `verifier_argv`, negative expected failure code/reason, and candidate/verified execution evidence. The execution record binds run provenance/time, the `preset-pattern-contract-v1` digest of the whole catalog entry except evidence refs, current verifier/fixture path digests, exact argv/zero exit, all positive accepts, and all negative rejects with matching observed code/reason. Missing/extra, empty/comment-only, wrong-command, stale-contract, or wrong-reason evidence blocks qualification.

## Clean-room verification

The digested command registry uses structured argv and always declares `install`, `doctor`, `test`, `check`, `build`, and `start-smoke`. Every cwd is `.` or a preset-relative existing directory. Exact `publish`, `release`, and `deploy` lane keys are forbidden; use `*-simulate` only for a bounded non-mutating check against an isolated local target. The smoke lane has a positive timeout. Evidence must bind lane, exact argv/cwd, and exit code; every declared lane must execute, including optional additions, and `start-smoke` must record `readiness_observed: true` plus `termination_observed: true`.

| Gate | Command/lab | Environment | `EVID-*` status/result | Blocks acceptance? |
| --- | --- | --- | --- | --- |
| Scaffold/materialize | | | | Yes |
| `install` | | | | Yes |
| `doctor` | | | | Yes |
| `test` | | | | Yes |
| `check` | | | | Yes |
| `build` | | | | Yes |
| `start-smoke` | | | | Yes |
| Database/migration | | | | When selected |
| Identity/session | | | | When selected |
| Lint/typecheck/test/build | | | | Yes |
| Browser walking slice | | | | Yes for verified UI flow |
| Skill syntax/integrity | | | | Yes |
| Clean-context skill forward evaluation | | | | Yes |
| Pattern-conformance verdict | | | | Yes for affected flow |
| Requested-outcome verdict | | | | Yes for affected flow |

## Skill forward-evaluation matrix

| Case ID / kind | Skill / untouched task | Tier / owner / role / route result | Clean context + input digests | Pattern verdict | Outcome verdict | Failure/correction/rerun |
| --- | --- | --- | --- | --- | --- | --- |

Every declared skill has coverage. If present, `audit-changes` includes `audit-immutable-range` and `audit-checkpoint`; `publish` includes `publish-topology`, `publish-conflict`, and `publish-final-revision`. Each negative case references its corresponding optional skill and binds a substantive adversarial input digest, expected disposition, and failure code to matching observed values. Use only `PASS`, `FAIL`, `BLOCKED`, or `NOT_EXECUTED`; conformance and outcome use distinct evidence paths whose records bind one axis only. Both records carry the same `case_input_sha256`, computed under `preset-skill-eval-case-v1` from the case ID/kind/skills/prompt/route trace, authority digests, and optional adversarial expectation fields, excluding verdict/evidence refs.

## Versioning and handoff

- Local customization policy:
- Supported upgrade path / breaking changes:
- Deprecation/removal policy:
- Demo slice removal/replacement path:
- Unsupported capabilities and extension triggers:
- Accepted / gaps / reviewer:
