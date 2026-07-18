# Preset package contract

A preset is a coherent, executable reference implementation for one exact stack combination. It is not a snippet collection, a latest-version installer, or proof that arbitrary libraries compose safely.

## Required outputs

Every `docs/presets/<preset-id>` contains:

- a human README covering purpose, fit/non-fit, lifecycle, exact versions, and quick start;
- `preset.json`, valid against [`preset.schema.json`](preset.schema.json);
- a complete `template/` with framework-default root files and application source;
- seven canonical namespaced skill packages, plus any declared optional skills, defined by [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md);
- a pattern catalog with exemplars, deterministic verifiers, and positive/negative fixtures;
- a versioned UI design contract and reviewable evidence;
- a digested verification command registry with deterministic clean-room, architecture, contract, behavior, integrity, and eval lanes;
- at least one removable vertical walking slice proving declared layer contracts.

No real preset may be marked `candidate` or `verified` from documentation alone.

## Manifest minimum

Use JSON so a schema validator can reject incomplete or misspelled declarations before materialization. The following is an abbreviated structural sketch and is not valid until required arrays and digests are populated; the schema is authoritative for syntax, while blueprint guides own semantics.

```json
{
  "$schema": "../preset.schema.json",
  "schema_version": "1.1.0",
  "preset_id": "next-ts-example",
  "preset_version": "0.1.0",
  "blueprint_version": "0.12.0",
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
    "ui": { "name": "<namespaced-name>", "path": "<skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "audit-changes": { "name": "<optional-namespaced-name>", "path": "<optional-skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] },
    "publish": { "name": "<optional-namespaced-name>", "path": "<optional-skill-path>", "sha256": "<64-hex>", "invocation": "<trigger>", "targets": ["codex"] }
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
    "commands": {
      "path": "verification/commands.json",
      "sha256": "<64-hex>"
    },
    "skill_evals": "verification/skill-evals.json"
  }
}
```

The illustrative ID is not an available preset, placeholders are not valid digests, and the illustrated optional skill rows must be omitted when unsupported. Other narrow optional skills may use additional lowercase kebab-case capability keys. `sha256` values are raw lowercase 64-hex digests. A cross-file validator additionally proves that skill names begin with the exact `preset_id`, each namespaced folder/frontmatter name agrees, paths stay inside the preset, all seven canonical capabilities occur once, every declared optional skill is covered, referenced files exist, source IDs resolve, and digests match bytes. Optional `prerequisites`, `compatibility`, and `upgrade_policy` sections may make quality and lifecycle policy more explicit without replacing the canonical fields.

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

The pattern catalog is executable governance, not prose inventory. Each candidate/verified record identifies `id`, descriptive layer, intent, exactly one `primary_owner`, zero or more unique `support_skills`, allowed/forbidden dependencies, `applicability.use_when`/`avoid_when`, public input/output/state contracts, exemplars, verifier, authoritative `verifier_argv`, positive/negative fixtures, and digested dual-verdict evidence. Owner/support references resolve to declared skills, and the primary owner cannot also appear as support. Every exemplar path, whether a file or directory tree, contains at least one substantive regular file; empty, comment-only, symlink-only, or `.gitkeep`-only examples do not qualify a candidate/verified pattern. Positive fixtures prove supported shapes. Every negative fixture also has an exact catalog `expected_failures` entry with a stable lowercase kebab-case `code` and actionable `reason`; a parser crash or rejection for a different rule does not prove the intended guard.

Candidate/verified pattern evidence contains an `execution` object with `run_id`, actor, toolchain, environment, and timezone-aware `observed_at`. `pattern_contract_sha256` is SHA-256 over `preset-pattern-contract-v1\0` followed by compact, key-sorted, non-ASCII-preserving UTF-8 JSON for the complete catalog entry after removing only `evidence`; it binds intent, ownership, applicability, public contracts, dependencies, verifier invocation, and fixture declarations without circular evidence references. The execution map also binds the catalog verifier by exact path, current raw-file SHA-256, argv exactly equal to `verifier_argv`, and observed exit code `0`.

The same map binds every catalog fixture, with no missing or extra paths, by exact path and current SHA-256. Positive records say `observed: "accept"`; negative records say `observed: "reject"` and carry `observed_failure` exactly equal to the catalog's expected code/reason. The evidence timestamp equals the enclosing pattern-evidence timestamp. Empty or comment-only verifier/fixture resources do not qualify. The validator checks these recorded bindings and never executes arbitrary preset code; the evidence producer runs the declared command in the bounded clean-room workflow.

The binding-specific catalog and evidence fields have this shape; omitted semantic catalog fields remain required as described above:

```json
{
  "primary_owner": "feature",
  "support_skills": ["ui"],
  "verifier": "patterns/verifiers/example.py",
  "verifier_argv": ["python3", "patterns/verifiers/example.py"],
  "fixtures": {
    "positive": ["patterns/fixtures/example/positive/valid.json"],
    "negative": ["patterns/fixtures/example/negative/forbidden.json"],
    "expected_failures": {
      "patterns/fixtures/example/negative/forbidden.json": {
        "code": "forbidden-dependency",
        "reason": "Rejects the declared forbidden dependency."
      }
    }
  },
  "evidence": [{ "path": "verification/evidence/example.json", "sha256": "<64-hex>" }]
}
```

```json
{
  "conformance": "PASS",
  "outcome": "PASS",
  "qualification": "candidate",
  "claim_type": "pattern",
  "claim_id": "example",
  "observed_at": "<RFC-3339>",
  "input_digests": { "<authority>": "<64-hex>" },
  "execution": {
    "run_id": "pattern-example-run",
    "actor": "<actor>",
    "toolchain": "<toolchain>",
    "environment": "<environment>",
    "observed_at": "<same-RFC-3339>",
    "pattern_contract_sha256": "<64-hex>",
    "verifier": {
      "path": "patterns/verifiers/example.py",
      "sha256": "<64-hex>",
      "argv": ["python3", "patterns/verifiers/example.py"],
      "exit_code": 0
    },
    "fixtures": {
      "positive": [{ "path": "patterns/fixtures/example/positive/valid.json", "sha256": "<64-hex>", "observed": "accept" }],
      "negative": [{ "path": "patterns/fixtures/example/negative/forbidden.json", "sha256": "<64-hex>", "observed": "reject", "observed_failure": { "code": "forbidden-dependency", "reason": "Rejects the declared forbidden dependency." } }]
    }
  }
}
```

A typical feature may require public contracts, schemas, client orchestration, server actions/queries, application services, repositories, policies, and views; do not create empty layers. Evidence must show that presentation consumes typed public/feature contracts, actions validate untrusted input and establish context, services sequence use cases and transaction intent, repositories map persistence and enforce scope, UI adapters handle typed outcomes, and `app` stays composition-only.

The catalog-qualification envelope records independent `conformance` and `outcome` fields beside one shared verifier-execution map; neither field implies the other. Task and skill forward-evaluation evidence is stricter and uses distinct claim-bound files for the two axes. A build or snapshot cannot stand in for either review.

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

## Verification command registry

`verification.commands` is a digested file reference to a registry conforming to [`verification-command-registry.schema.json`](../blueprint/schemas/verification-command-registry.schema.json). The registry always declares `install`, `doctor`, `test`, `check`, `build`, and `start-smoke`; it may add capability-selected lanes such as `generate`, guarded `data-reset`, `auth-smoke`, `browser-smoke`, or an isolated `restore-drill`. Exact lane keys `publish`, `release`, and `deploy` are forbidden because real external mutation never belongs in clean-room qualification; only a separately named `*-simulate` lane for a non-mutating check against an isolated local target may be declared. This name check is defense in depth, not semantic proof: the runner/reviewer must inspect argv and prove the target is isolated and no external production effect occurred. A lane stores argv as an array, an optional portable working directory, required environment-variable names, and an optional timeout. The working directory defaults to `.`; any other value resolves inside the preset and must already be a real directory, not a missing path, file, or symlink traversal. `start-smoke` must declare a positive `timeout_seconds` so a successful start cannot leave an unbounded process. A lane does not replace argv with a free-form command field or store secret values.

Clean-room evidence records the lane, exact argv/cwd observed, and exit code. The `start-smoke` record additionally requires `readiness_observed: true` and `termination_observed: true`; exit zero without both observations is not a smoke proof. Candidate/verified acceptance requires successful evidence for every declared lane, including capability-selected additions beyond the six schema-required lanes. The validator compares evidence to the locked registry, so checking that a script exists, running a different command, leaving an optional lane unexecuted, changing the registry without refreshing evidence, or relabeling a real mutation as clean-room proof cannot qualify the preset.

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

Every forward-eval case at every status supplies its untouched prompt, current input digests, route trace, separate verdict objects, and distinct claim-bound evidence paths. Only two `PASS` axes count as skill/kind coverage; stubs, stale/misbound records, shared paths, and non-pass results do not. `candidate` and `verified` additionally require `upgrade_policy`, object-form capability/flow matrices, digested references for commands, skill evals, integrity, design evidence, and clean-room evidence. Each verified capability names nonempty providers, consumers, payloads, states, constraints, and catalog pattern IDs; each verified flow carries `capability_id`, and every verified capability has at least one mapped flow. Each forward-eval case binds the current template, command, pattern, source, design, and every declared skill digest. A verdict-specific record contains one `result`, `claim_type`, `claim_id`, and `case_input_sha256`; use only `PASS`, `FAIL`, `BLOCKED`, or `NOT_EXECUTED`. The suite covers every declared skill. Optional `audit-changes` requires `audit-immutable-range` and `audit-checkpoint` negative cases; optional `publish` requires `publish-topology`, `publish-conflict`, and `publish-final-revision` negative cases. Each such case must reference the corresponding skill.

`case_input_sha256` is SHA-256 over the UTF-8 bytes `preset-skill-eval-case-v1\0` followed by compact, key-sorted, non-ASCII-preserving JSON containing exactly `id`, `kind`, `skills`, `prompt`, `route_trace`, authority `input_digests`, and the optional `adversarial_input`, `expected_disposition`, and `expected_failure_code` keys (`null` when absent). It excludes conformance/outcome objects and all verdict evidence references, so there is no self-reference. Both axis records bind this same digest. Mutating a prompt, skill route, case kind/ID, authority input, or adversarial expectation invalidates both records even when their file references and global input maps still exist.

Every standardized `audit-changes` or `publish` negative case must supply a substantive adversarial input as a `{path, sha256}` reference, an expected disposition from `BLOCKED`, `REFUSED`, or `TASK_REROUTED`, and a lowercase kebab-case expected failure code. Both axis evidence records report matching `observed_disposition` and `observed_failure_code`. A happy-path input carrying only the required kind label, a drifted fixture digest, or a mismatched observed failure does not count as negative coverage.

Status evidence contains `result: "pass"`, `qualification` equal to the exact status, an explicit context (`ui-review`, `clean-room`, or `independent-use`), `run_id`, actor, toolchain, environment, timezone-aware RFC 3339 `observed_at` within `stale_after_days`, and the exact current `input_digests` map. Clean-room and independent-use evidence also contain nonempty zero-exit records bound by lane and exact argv/cwd to the command registry. `verified` requires a distinct independent-use path and run ID whose `independent_from_run_id` names a clean-room run, so candidate evidence cannot be relabeled or self-declared independent without a new run.

The status-evidence input map binds `manifest_inputs`, `template`, `commands`, `patterns`, `sources`, `design`, `skill_evals`, and `skill:<capability>` for every declared skill. `manifest_inputs` is SHA-256 over compact, key-sorted UTF-8 JSON for `preset.json` after removing only design/status-evidence references; this binds status, preset/blueprint identity, stack, capabilities, materialization, command registry and freshness policy without a self-reference. `template` uses the length-prefixed tree record format from the skill contract under domain `preset-template-tree-v1`.

`verification/integrity.json` declares a passing `sha256` result, timezone-aware `generated_at`, and POSIX byte-sorted `{path, sha256}` records. It covers every regular preset file except `preset.json` and itself, rejects symbolic links, stale bytes, duplicates, and missing/extra records, and is itself locked from the manifest. This graph proves package closure; the named input map proves that the recorded tests apply to the exact manifest identity and inputs.

## Freshness and upgrades

Manifest schema `1.1.0` adds the required digested command registry and standardized optional skill/eval contracts. A `1.0.0` manifest must add the six baseline command lanes, refresh its input/integrity graph, and rerun affected clean-room and forward-evaluation evidence before it can be accepted under this contract.

Skill records lock their complete directories with the deterministic tree-digest algorithm defined by [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md). `patterns.sha256` applies the same record format to the complete pattern directory under domain `preset-pattern-tree-v1`; `sources` and `design` lock their declared files with raw SHA-256. Evidence is stale when its exact input map changes, its freshness window expires, an invalidation trigger fires, an exact dependency/source changes, or a verifier gains relevant coverage.

Upgrades compare the instantiated lock, local changes, source preset, and target preset. They re-run only safely reusable evidence plus every gate invalidated by the digest graph; they never transfer `verified` status automatically or overwrite local work merely because upstream changed.
