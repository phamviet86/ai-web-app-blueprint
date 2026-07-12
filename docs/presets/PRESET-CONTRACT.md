# Preset package contract

A preset is a coherent, executable reference implementation for one exact stack combination. It is not a snippet collection, a latest-version installer, or proof that arbitrary libraries compose safely.

## Required outputs

Every `docs/presets/<preset-id>` contains:

- a human README covering purpose, fit/non-fit, lifecycle, exact versions, and quick start;
- `preset.json`, valid against [`preset.schema.json`](preset.schema.json);
- a complete `template/` with framework-default root files and application source;
- seven namespaced skill packages defined by [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md);
- a pattern catalog with exemplars, deterministic verifiers, and positive/negative fixtures;
- a versioned UI design contract and reviewable evidence;
- deterministic clean-room, architecture, contract, behavior, integrity, and eval commands;
- at least one removable vertical walking slice proving declared layer contracts.

No real preset may be marked `candidate` or `verified` from documentation alone.

## Manifest minimum

Use JSON so a schema validator can reject incomplete or misspelled declarations before materialization. The following is an abbreviated structural sketch and is not valid until required arrays and digests are populated; the schema is authoritative for syntax, while blueprint guides own semantics.

```json
{
  "$schema": "../preset.schema.json",
  "schema_version": "1.0.0",
  "preset_id": "next-ts-example",
  "preset_version": "0.1.0",
  "blueprint_version": "0.11.0",
  "blueprint_revision": "<immutable-revision>",
  "status": "experimental",
  "archetype": "full-stack-web",
  "stack": [
    { "package": "<framework>", "version": "<exact-version>", "source_id": "framework-docs" }
  ],
  "capabilities": ["read-surface"],
  "verified_flows": [],
  "materialization": { "root": "template" },
  "skills": {
    "analyze-request": {
      "name": "next-ts-example-analyze-request",
      "path": "guides/next-ts-example-analyze-request",
      "sha256": "<64-hex>",
      "invocation": { "implicit": "Use for outcome-level and cross-layer requests" },
      "targets": ["codex"]
    },
    "lib": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "shared": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "feature": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "app": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "new-pattern": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "ui": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] }
  },
  "patterns": {
    "catalog": "patterns/catalog.json",
    "sha256": "<64-hex>"
  },
  "sources": {
    "ledger": "verification/sources.json",
    "sha256": "<64-hex>"
  },
  "design": {
    "contract": "design/ui-contract.json",
    "sha256": "<64-hex>",
    "evidence": ["design/evidence/<evidence-file>"]
  },
  "verification": {
    "skill_evals": "verification/skill-evals.json"
  }
}
```

The illustrative ID is not an available preset, and placeholders are not valid digests. `sha256` values are raw lowercase 64-hex digests. A cross-file validator additionally proves that skill names begin with the exact `preset_id`, each namespaced folder/frontmatter name agrees, paths stay inside the preset, all seven capabilities occur once, referenced files exist, source IDs resolve, and digests match bytes. Optional `prerequisites`, `compatibility`, and `upgrade_policy` sections may make quality and lifecycle policy more explicit without replacing the canonical fields.

## Capability and inter-layer matrix

Declare each capability as `provided`, `verified`, `conditional`, or `unsupported`. Only `verified` means an exact-version closed flow passed. Every capability names providers, consumers, public payloads/results, states/failures, constraints, and immutable evidence.

Baseline flows are:

```text
surface -> validated request -> feature query policy -> repository -> ORM/database
        <- typed result       <- safe mapped result    <-

input -> normalized values -> action -> service/transaction -> repository
      <- field/action result <- typed outcome           <-

session adapter -> trusted subject -> guard -> feature resource policy
                                          -> mandatory repository scope
```

Browser inputs never become raw ORM filters. `lib/db` may provide parsing, pagination, operator mechanics, transactions, and adapters; a feature owns public aliases, field/operator/sort/join/projection allowlists, authorization scope, and query cost/index constraints.

## Pattern and feature evidence

The pattern catalog is executable governance, not prose inventory. Each candidate/verified record identifies `id`, layer, intent, skill owners, allowed/forbidden dependencies, `applicability.use_when`/`avoid_when`, public input/output/state contracts, exemplars, verifier, positive/negative fixtures, and digested dual-verdict evidence. Positive fixtures prove supported shapes; negative fixtures prove forbidden ownership, dependency, raw payload, authorization, and state failures are detected.

A typical feature may require public contracts, schemas, client orchestration, server actions/queries, application services, repositories, policies, and views; do not create empty layers. Evidence must show that presentation consumes typed public/feature contracts, actions validate untrusted input and establish context, services sequence use cases and transaction intent, repositories map persistence and enforce scope, UI adapters handle typed outcomes, and `app` stays composition-only.

Pattern-conformance evidence and user-outcome evidence are separate required records. A build or snapshot cannot stand in for either.

## UI design contract

Every full-stack web preset declares a UI contract covering:

- tokens, typography, spacing, density, focus, motion, and theming;
- app/page layout and responsive breakpoints;
- normalized fields, form/action results, overlays, menus, feedback, and remote interaction;
- table/list search, filter, sort, pagination/range payloads;
- loading, empty, error, stale/success, denied, disabled, accessibility, and responsive states;
- the boundary between shared mechanics and feature-owned labels, columns, fields, filters, permissions, and actions.

The machine-readable contract records exact `version`, product `brief`, `tokens` split into `primitive`/`semantic`/`component_state`, representative `surfaces`, required remote `states`, `responsive` and `accessibility` rules, exact `framework_bindings`, and source-ledger `source_ids`. Candidate/verified contracts must include loading, empty, error, stale, denied, and success states plus at least one official-docs or Context7 source.

Calendar, masonry, transfer, upload, editor, and similar surfaces are capability-selected. A supported surface declares emitted request, consumed result, keyboard/screen-reader behavior, narrow/wide layouts, failure recovery, exemplar, and outcome evidence.

Visual evidence should include representative viewport/state captures plus objective checks where possible; it must not rely only on an agent saying the result looks good. Link design evidence to the exact UI contract, template, source, and integrity digests.

## Source provenance

`sources.ledger` points to the preset's source ledger and `sources.sha256` locks its bytes. Every ledger record declares `id`, `kind`, URL, requested ref, resolved immutable revision, retrieval time, license, claims used, and invalidation triggers.

- Official documentation for every pinned framework/library API is mandatory. Query it through Context7 when available and record `library_id`, concept-scoped `queries`, and `official_urls`; reconcile retrieved guidance with the exact pinned version.
- Each stack item's source record uses `requested_ref` equal to that exact stack version. Every UI `framework_binding` is an exact `<package>@<version>` tuple present in the stack; evidence cannot silently combine documentation or design bindings from another version.
- Context7 is a retrieval mechanism, not a replacement for source authority or version evidence.
- `ui-ux-pro-max` may be a commit-pinned, license-reviewed `ux-heuristic` source only when `acquisition_mode` is `read-only`. It cannot override official APIs, the blueprint, preset contracts, accessibility requirements, or user decisions.
- Do not copy third-party text, code, or assets unless the license and preset provenance record allow it. Prefer independently authored rules and evidence.

Missing hard sources block affected implementation. Missing quality sources use the manifest fallback and lower the confidence/status claim.

## Materialization and verification

`materialization` identifies the complete template root or explicit entries. Detailed entries declare source, target, `create`/`merge`/`replace`, conflict policy, and SHA-256. Instantiation must:

1. confirm capability fit, hard prerequisites, exact toolchain, source freshness, and integrity;
2. inventory conflicts before writing;
3. materialize framework root files and `src/` at declared paths;
4. install locked dependencies without opportunistic upgrades;
5. map selected preset skills and write the preset lock/local decisions;
6. run clean-room build, pattern fixtures, walking slices, UI checks, and forward-eval gates;
7. store conformance and outcome evidence separately;
8. leave failure diagnosable and resumable without recording success.

Deterministic scripts must use explicit inputs, stable ordering, non-zero failure exits, machine-readable output where useful, and no undeclared network or destructive side effects. Reasoning-heavy design and product choices remain agent work bounded by contracts, not encoded as brittle scripts.

Manifest paths are canonical cross-platform POSIX-relative paths: no backslashes, colons/drive prefixes, empty/`.`/`..` components, trailing dot/space, Windows device names, case-fold collisions, duplicate targets, or ancestor/descendant target overlap. Text files are normalized to LF by `.gitattributes`; binary assets retain raw bytes. Invoke scripts through their declared interpreter so executable-mode differences do not change behavior across clones.

## Candidate and verified evidence envelope

`candidate` and `verified` require `upgrade_policy`, object-form capability/flow matrices, digested references for skill evals, integrity, design evidence, and clean-room evidence. Each verified capability names nonempty providers, consumers, payloads, states, constraints, and catalog pattern IDs; each verified flow carries `capability_id`, and every verified capability has at least one mapped flow. Each forward-eval case binds the current template, pattern, source, design, and seven skill digests, records its route trace, and stores distinct `conformance` and `outcome` evidence; the suite must cover all seven canonical skills. Every dual-verdict record binds `claim_type`, `claim_id`, exact non-circular input digests, qualification, and freshness, so one generic result cannot prove unrelated patterns, capabilities, flows, or eval cases.

Status evidence contains `result: "pass"`, `qualification` equal to the exact status, an explicit context (`ui-review`, `clean-room`, or `independent-use`), `run_id`, actor, toolchain, environment, timezone-aware RFC 3339 `observed_at` within `stale_after_days`, and the exact current `input_digests` map. Clean-room and independent-use evidence also contain nonempty zero-exit command records. `verified` requires a distinct independent-use path and run ID whose `independent_from_run_id` names a clean-room run, so candidate evidence cannot be relabeled or self-declared independent without a new run.

The status-evidence input map binds `manifest_inputs`, `template`, `patterns`, `sources`, `design`, `skill_evals`, and `skill:<capability>` for all seven canonical skills. `manifest_inputs` is SHA-256 over compact, key-sorted UTF-8 JSON for `preset.json` after removing only design/status-evidence references; this binds status, preset/blueprint identity, stack, capabilities, materialization, and freshness policy without a self-reference. `template` uses the length-prefixed tree record format from the skill contract under domain `preset-template-tree-v1`.

`verification/integrity.json` declares a passing `sha256` result, timezone-aware `generated_at`, and POSIX byte-sorted `{path, sha256}` records. It covers every regular preset file except `preset.json` and itself, rejects symbolic links, stale bytes, duplicates, and missing/extra records, and is itself locked from the manifest. This graph proves package closure; the named input map proves that the recorded tests apply to the exact manifest identity and inputs.

## Freshness and upgrades

Skill records lock their complete directories with the deterministic tree-digest algorithm defined by [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md). `patterns.sha256` applies the same record format to the complete pattern directory under domain `preset-pattern-tree-v1`; `sources` and `design` lock their declared files with raw SHA-256. Evidence is stale when its exact input map changes, its freshness window expires, an invalidation trigger fires, an exact dependency/source changes, or a verifier gains relevant coverage.

Upgrades compare the instantiated lock, local changes, source preset, and target preset. They re-run only safely reusable evidence plus every gate invalidated by the digest graph; they never transfer `verified` status automatically or overwrite local work merely because upstream changed.
