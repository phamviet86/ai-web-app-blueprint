# App governance artifacts

This directory is reserved for repository-local application-governance state. It is documentation today; this blueprint distribution selects neither an app profile nor a preset.

A governed app selects exactly one current authority route:

- `preset-lock.json` for an app materialized from a verified preset: preset ID/version, immutable source revision, blueprint version/revision, manifest/template/skill/pattern/source/design/command/evaluation/integrity digests, qualification evidence references, materialization timestamp, and verification result; or
- `app-profile.json` for an existing/custom app: blueprint and source content revisions plus digest-bound references to the active artifact registry, its complete effective-artifact closure, active system profile, accepted stack profile, seven canonical skills, pattern catalog, verification-command registry, `clean_room_evidence`, current guidance evidence, and its `skill_evals` record. The clean-room record binds the source revision and command-registry digest, execution provenance, all six baseline lanes plus every declared additional lane, and zero exit results; `start-smoke` also proves readiness and bounded termination. Every declared skill is covered; conformance and outcome are distinct `PASS` verdicts/evidence for an effective profile, with additional adversarial cases when `audit-changes` or `publish` is declared.

Both routes also require:

- a local decision/override record for deliberate deviations;
- registered architecture exceptions and verification evidence when those artifacts apply.

`artifact_closure` contains every non-registry row whose registry status is effective: `active`, `accepted`, `final`, `approved`, or `in-progress`. Each entry locks stable ID, status, repository-relative path and current file SHA-256; its frontmatter and registry row must agree. The separately named `system_profile` and `stack_profile` records must exactly match their closure entries. Missing, extra, stale or ineffective entries fail qualification, so an accepted route, UI/design contract, test strategy, runbook or release/readiness artifact cannot change behind an unchanged registry.

An app-profile pattern catalog contains established records only. Each entry binds `id`, semantic `intent`, one declared `primary_owner`, unique declared `support_skills`, `applicability.use_when/avoid_when`, public input/output/state contracts, disjoint allowed/forbidden dependencies, digest-locked exemplar/verifier/fixtures, authoritative exact `verifier_argv`, expected code/reason for every negative, and a digest-locked verification-evidence record. The evidence records provenance/time, exact verifier argv and zero exit, complete positive/negative fixture results, and rejection for the declared reason. Its `pattern_contract` digest uses domain `app-profile-pattern-contract-v1` and excludes only the circular `verification_evidence` reference. The validator verifies the recorded map; it never executes arbitrary verifier code. `PATTERN_EXTENSION` and `CANDIDATE_GAP` are task-time analyzer classifications, not catalog statuses. The exact referenced-document shapes live under `patternCatalogDocument` and `patternVerificationEvidenceDocument` in the [app-profile schema](../blueprint/schemas/app-profile.schema.json).

## Evidence identity and freshness

`blueprint_revision`, `source_revision`, guidance `current_revision`, and both CLI expectations use a full 40/64-hex content identity or `sha256:<64-hex>`; branch, tag, release and `latest`-style selectors never qualify. `--expected-revision` must equal the source revision, `--expected-blueprint-revision` must equal the selected blueprint revision, and `blueprint_version` is exactly `0.13.0`. A required `freshness_policy.stale_after_days` from 1 through 365 applies to clean-room, pattern, guidance and skill-axis evidence; expired or future evidence fails.

Canonical app-profile digests hash `ASCII domain + NUL + compact key-sorted, non-ASCII-preserving UTF-8 JSON`:

- `app-profile-inputs-v1` binds profile/schema identity, blueprint/source revisions, artifact registry/closure, system/stack profiles, every skill, pattern-catalog locator, verification commands and freshness policy while excluding circular evidence references;
- `app-profile-freshness-policy-v1` binds the freshness policy;
- `app-profile-pattern-contract-v1` binds one complete pattern contract except its evidence reference;
- `app-profile-skill-eval-case-v1` binds case ID/kind, ordered skills, untouched prompt, route trace, authority input digests, and optional adversarial fixture/disposition/failure fields; absent optional values serialize as JSON `null`.

Clean-room evidence records exact lane/argv/cwd/exit observations for every declared command. Exact `publish`, `release`, and `deploy` lane keys are forbidden; only a separately named non-mutating isolated simulation belongs here. This naming guard cannot infer arbitrary argv semantics, so the runner/reviewer still proves isolation and absence of external production effects. Skill evaluation uses separate claim-bound conformance/outcome paths. Standardized audit/publish negative cases also bind a substantive adversarial fixture and expected disposition/failure code; both axis records must report the matching observed disposition/failure. A happy-path prompt with a negative case label provides no coverage.

Validate an app profile from the adopting repository root with:

```text
python3 docs/blueprint/scripts/validate_app_profile.py docs/governance/app-profile.json --repo-root . --expected-revision <current-source-revision> --expected-blueprint-revision <selected-blueprint-revision>
```

These files describe one application, not a reusable preset. They must not be written during `AUTHOR_PRESET`; an adoption or upgrade reconciles them instead of silently replacing local decisions. If both authority files are active, or either route is stale or internally inconsistent, app work stops until one complete authority is selected and revalidated.
