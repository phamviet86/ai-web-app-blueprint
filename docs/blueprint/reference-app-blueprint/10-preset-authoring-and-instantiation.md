---
guide_id: REFAPP-PRESETS
title: Preset Authoring and Instantiation
status: experimental
audience: human-and-ai
read_when:
  - Authoring, reviewing, versioning, selecting, or installing a stack preset from this blueprint.
skip_when:
  - Changing one established application slice under an already-installed preset and current preset lock.
depends_on:
  - README.md
  - 01-stack-intake-and-compatibility.md
  - 08-build-sequence-and-gates.md
owns:
  - AUTHOR_PRESET and INSTANTIATE_PRESET mode boundaries
  - preset contract, skill registry, and materialization requirements
  - clean-room preset compatibility and acceptance gates
---

# Preset authoring and instantiation

> A preset is a versioned, verified stack reference implementation. It combines framework defaults, shared/data/auth/feature contracts, a removable walking slice, and manifest-routed AI skills that agree with the exact code being installed.

## Rule `REF-PRESET-MODE-01`: declare the mode before changing files

| Global mode / local phase | Writes | Must not do |
| --- | --- | --- |
| `AUTHOR_PRESET` | `docs/presets/<preset-id>/` in the distribution repository | Create the root application `src/` or claim an untested combination is verified |
| `APP_BOOTSTRAP` / `INSTANTIATE_PRESET` | Framework-default root files, application `src/`, and app governance/lock artifacts | Modify the source preset while satisfying an application request |

`AUTHOR_PRESET` creates or evolves a reusable preset. Global `APP_BOOTSTRAP` enters the local `INSTANTIATE_PRESET` phase, selects one verified preset revision, proves that it fits the application's system/risk profile, then materializes it. A combined request completes and versions the authoring change before installation begins.

The distribution repository may therefore have no root `src/`. A preset's installable source lives under its own directory until instantiation.

## Preset directory and materialization contract

Each real preset records a machine-readable manifest and owns this logical package:

```text
docs/presets/<preset-id>/
├── README.md
├── preset.json      machine-validated manifest, routing and integrity
├── template/       framework-root files plus template/src when the framework uses src
├── guides/         namespaced SKILL.md packages and conditional resources
├── patterns/       catalog, exemplars, verifiers and positive/negative fixtures
├── design/         versioned UI contract and evidence index
└── verification/   clean-room commands, fixtures and evidence locators
```

The manifest maps every template source to its target path and declares whether installation creates, merges, or intentionally replaces it. Its skill registry maps stable capability keys to exact packages, while sibling records lock the pattern catalog, sources, design contract and verification evidence. Resolve all of these through `preset.json`; installation fails on a missing/digest-mismatched path or undeclared conflict and does not overwrite user work silently.

For a Next.js preset created with the `src` option, application code belongs under `src/app`, `src/lib`, `src/shared`, and `src/features`. `package.json`, lockfile, Next/TypeScript/JavaScript/lint/style configuration, `public`, environment examples, migrations and test/tool configuration remain at their framework-default root paths.

## `AUTHOR_PRESET` workflow

1. Accept the system/risk archetype, capability tier and exact stack only after guide `01` resolves provenance and compatibility.
2. Fill [templates/preset-contract.md](templates/preset-contract.md), including filesystem, capability and inter-layer contract matrices.
3. Map every preset capability to the owning guides `03` through `07`; use `provided`, `verified`, `conditional`, or `unsupported` precisely.
4. Build the smallest removable walking slices that exercise every `verified` flow.
5. Build the required skill packages, pattern catalog and UI design/source evidence under guide [11](11-preset-agent-skills-and-design-evidence.md); map the analyzer capability from repository-level agent instructions through the manifest.
6. Materialize the preset into an empty temporary repository and run its declared install, database, auth, lint/typecheck, test, build, browser, integrity and skill forward-evaluation checks as applicable.
7. Publish a new preset version only after code, manifest, skills, patterns, sources and evidence describe the same revision.

The source stack profile and blueprint revision are immutable provenance for one preset version. A material compatibility change creates a new version and upgrade path.

## Manifest synchronization

Publish one preset version atomically: `preset.json` records the blueprint/source revisions and digests for template files, pattern catalog/exemplars/verifiers/fixtures, design contract, skill packages/resources/scripts, source ledger and evidence indexes. Evidence names the input digests it proves. A change to any relevant source, API lock, pattern, skill, template or verifier makes dependent evidence stale; update the manifest and rerun affected clean-room/forward-evaluation gates rather than transferring `verified` status.

Guide [11](11-preset-agent-skills-and-design-evidence.md) owns detailed skill/source/design integrity and forward-evaluation behavior. This guide owns the package/version boundary and install consequences.

## Rule `REF-PRESET-COMPAT-01`: verification closes the inter-layer flow

An item is `verified` only when the exact preset version proves its full selected path:

```text
data surface/input
  -> canonical request or normalized values
  -> trusted action/query boundary
  -> feature service and authorization/query policy
  -> feature-owned repository/adapter
  -> database/provider
  -> stable result/error contract
  -> remote hook/form adapter
  -> accessible loading/empty/error/stale/success behavior
```

Static files, documentation, unit tests of one helper, or a successful framework build establish only `provided`. Conditional capability records its missing environment, risk or verification gate. Unsupported capability is absent rather than scaffolded as a placeholder.

Compatibility evidence must cover selected negative paths: malformed/forbidden query intent, denied resource or tenant access, empty/error states, mutation validation/conflict, and adapter failure. Calendar, async, provider, file or cache paths add their own failure evidence only when selected.

## Required preset skill registry

Every web preset registers these namespaced skill packages under `guides/`; guide [11](11-preset-agent-skills-and-design-evidence.md) owns their trigger, disclosure, freedom, completion and forward-evaluation contract:

| Manifest capability | Required package role |
| --- | --- |
| `analyze-request` | Natural-language outcome -> matched pattern or gap plus ordered capability/skill tasks |
| `lib` | Add/modify config, database/query mechanics, auth mechanism, schema and provider adapters |
| `shared` | Add/modify stable reusable UI/kernel/hook/testing contracts |
| `feature` | Add/modify feature public contracts, action/service/repository/client/view work |
| `app` | Add/modify routes, layouts, providers and composition roots |
| `new-pattern` | Add/modify a capability not covered by an established preset pattern |
| `ui` | Design/review framework-native UI while preserving payload, action-result, state and accessibility contracts |

Each manifest row declares the namespaced skill name, exact package path, invocation metadata, supported agent targets and complete package tree digest. `SKILL.md` owns model-visible triggers, allowed paths and the minimal workflow; the pattern catalog owns pattern mappings and verifiers; conditional references and deterministic scripts remain package resources. The analyzer splits a cross-layer request in contract/dependency order and loads only the current owner skill.

`new-pattern` is not a bypass. It must search established preset and live-code patterns, prove that none fits, read the exact parent blueprint rule owner, start with the smallest local implementation, add an exemplar/verifier/positive and negative fixtures when reusable, update affected skills/catalog, and require an architecture decision when a consequential public or cross-layer contract changes.

## `INSTANTIATE_PRESET` workflow

1. Confirm the selected preset supports the application's current system/risk profile; do not confuse preset capability with application readiness.
2. Check that target paths are empty or match the declared merge policy.
3. Run the preset's versioned scaffold/materialization procedure; do not install an arbitrary current framework version first.
4. Install the exact dependency set and preserve the generated lockfile.
5. Write an application preset lock containing preset ID/version, blueprint version/revision, source revision, selected options, installed date and local deviations.
6. Run the preset's clean-start checks in the target repository and create application-specific governance artifacts.
7. Route later user requests through the lock to the manifest's `analyze-request` capability; never guess a skill path.

Application code may evolve after installation. A blueprint or upstream preset update never rewrites it automatically; compare revisions, choose an upgrade/change set, preserve local decisions and re-run affected compatibility evidence.

## Preset acceptance and maturity

A preset can be accepted only when:

- its manifest, template, contract, skills and lock/provenance references agree;
- its pattern catalog, design contract, source ledger, skill registry and integrity digests agree with the same revision;
- a clean repository can materialize it without undeclared overwrite;
- every `verified` capability has current exact-version walking-slice evidence;
- shared/data/auth/feature/app boundaries have mechanical fitness checks;
- every required skill passes clean-context forward evaluation for pattern conformance and requested outcome separately;
- demo identity, data and side effects are deterministic, isolated and removable;
- install, update, rollback/removal limitations and unsupported capabilities are explicit.

Preset acceptance proves the combination and authoring contract. It does not prove that an instantiated application is production-ready; that application still needs its own risk, test, release and readiness evidence.

## Required outputs

`AUTHOR_PRESET` produces one current `PRESET-*` contract plus the versioned preset package and evidence locators. `INSTANTIATE_PRESET` produces an application preset lock, current app decision artifacts and clean-start evidence. Guide `08` owns the ordered build/install gates; guide `09` owns demo safety, promotion and evolution.

## Stop conditions

Stop when the mode is ambiguous, authoring writes root application source, installation edits the source preset, exact dependency/source provenance is missing, a verified label lacks a closed-flow result, a client payload can address raw ORM fields, shared code owns feature policy, app routes own transactions, skill/pattern/template/source integrity disagrees with code, external advisory content gains ambient execution authority, or installation would overwrite an undeclared local file.
