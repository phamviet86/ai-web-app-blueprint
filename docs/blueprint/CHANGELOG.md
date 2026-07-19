---
document_id: SKEL-CHANGELOG
title: Package Changelog
status: experimental
audience: human-and-ai
package_version: 0.13.0
---

# Changelog

All notable package-contract changes are recorded here. Versions follow [MATURITY.md](MATURITY.md); dates use ISO `YYYY-MM-DD`.

## Unreleased

- None.

## 0.13.0 - 2026-07-19

### Added

- Frozen structural-refactor baseline contract with immutable revision identity, declared artifact groups, authorized deltas, and fail-closed drift coverage.
- Candidate-disposition contract distinguishing confirmed refactor action, intentional owner-local behavior, false positives, and unresolved record-only findings.
- Runtime-initialization contract and negative build/import proof for checks that claim independence from runtime-only secrets and external services.
- Revision-bound Bingo LMS repository-wide refactor evidence that separates current focused checks from broader historical source-reported closure.
- Executable positive and adversarial regressions for effective refactor-plan sections, populated tables, and draft/effective status boundaries.

### Changed

- Module public contracts now support narrow consumer/capability/runtime sub-surfaces while treating broad facades as composition or bounded compatibility seams.
- Shared promotion, query normalization, characterization, and architecture fitness now preserve lifecycle/effect ordering, declare checker coverage, and measure dependency/effect improvement instead of line reduction.
- The refactor-slice template advances to `1.1.0` with frozen-boundary, candidate-disposition, behavior-equivalence, and checker-coverage sections.

### Migration

- Effective refactor-plan artifacts adopting this package line rebind `source_template` to template `1.1.0` (`SKEL-TPL-REFACTOR-SLICE@1.1.0`, or the current canonical path when path-qualified), increment `artifact_version`, update `updated_at`, refresh the artifact-registry digest, and add populated `Frozen boundary and authorized delta`, `Candidate disposition`, `Behavior-equivalence matrix`, and `Checker coverage` sections. Draft plans may remain incomplete until approval; a non-applicable checker still records rationale, owner, and manual evidence.
- Existing/custom app profiles and future preset manifests adopt `blueprint_version` `0.13.0` only when intentionally upgrading and must refresh the selected blueprint revision, affected digests, and qualification evidence; no authority path or artifact-schema migration is introduced.

### Maturity

- Package remains `experimental`; control catalog remains `1.0.0` and artifact schema remains `1.0`. A second observation of the same application repository is not an independent pilot or cross-stack runtime proof.

## 0.12.0 - 2026-07-18

### Added

- Stack-neutral app-profile authority contract and validator for existing/custom applications that cannot claim preset materialization provenance.
- Versioned verification-command registry with required install, doctor, test, check, build and start-smoke lanes bound to clean-room evidence.
- Portable data-access task modes for no access, bounded live read, guarded test mutation and production handoff.
- Optional `audit-changes` and `publish` skill contracts with adversarial checkpoint/topology evaluations.
- Revision-bound Bingo LMS repository-learning evidence that separates promoted invariants, source-specific exclusions and evidence limits.

### Changed

- Analyzer/skill routing now uses vertical pattern ownership, primary/support roles, explicit evidence tiers, task re-routing and separate requested-outcome/pattern-conformance verdicts.
- Bootstrap, query/UI, data, integration, testing and operations owners now require edge-value, negative-fixture, wire-shape, interaction and evidence-completeness checks learned from revision-bound real-app repository evidence.
- Preset and app-profile qualification now binds declared command lanes, all declared skills and current integrity/evaluation evidence instead of accepting file presence or a generic build.
- Stack-profile, route-map, test-strategy, SLO/runbook and preset-contract templates advance to `1.1.0`; artifact-instance schema remains `1.0`.

### Migration

- Existing/custom apps adopting this release create and validate `docs/governance/app-profile.json`; apps already governed by a preset retain `preset-lock.json` and must not enable both authority paths.
- Future candidate/verified presets add the command-registry reference and forward-evaluate every declared optional skill. The catalog remains empty, so no existing preset instance requires migration.

### Maturity

- Package remains `experimental`. One repository-derived stack source improves the rule set but does not establish clean-room preset usability, second-stack portability or production readiness.

## 0.11.0 - 2026-07-12

### Added

- Portable preset skill-package contract with model-facing triggers, progressive disclosure, checkable completion criteria, execution-freedom levels, deterministic helpers, and clean-context forward evaluations.
- Versioned pattern catalog, external-source ledger, skill/source/template integrity digests, and separate pattern-conformance versus requested-outcome evidence.
- Exact-version official-documentation and Context7 lookup protocol with recorded library IDs, scoped queries, source URLs, freshness, and fallback behavior.
- UI design-evidence workflow covering product brief, primitive/semantic/component tokens, framework-native component states, responsive/accessibility/performance checks, and closed action/result flows.
- Load-on-demand research provenance for `mattpocock/skills` and `nextlevelbuilder/ui-ux-pro-max-skill`, including immutable revisions, licenses, adopted ideas, and rejected authority claims.
- Standard-library preset-package validator, JSON schema, regression tests, cross-platform LF policy, domain-separated tree digests, status/input-bound evidence, and CI gate that accepts an empty catalog but fails closed when a real preset appears.

### Changed

- Future preset guidance is now a set of namespaced `SKILL.md` packages resolved through `preset.json`, rather than six loose `guides/*.md` files.
- Web presets add a `ui` skill capability alongside analyze-request, lib, shared, feature, app, and new-pattern.
- Third-party UI/UX search output is advisory and read-only; exact framework/library API behavior comes from pinned official sources, located through Context7 when useful, then verified in the preset.
- `preset.yaml` became standard-library-validated `preset.json` before any real preset existed.

### Migration

- Future preset authors must use the new namespaced skill directory and manifest registry; no existing preset requires migration because the catalog is still empty.
- Any draft external-tool automation must pin a reviewed revision, inventory licenses, avoid global installation, and regenerate evidence when source or framework claims become stale.

### Maturity

- Package remains `experimental`; structural skill/preset checks are implemented, but no independent real-preset forward-test has qualified as graduation evidence.

## 0.10.0 - 2026-07-12

### Added

- Repository distribution contract with a minimal root router, `docs/blueprint` source of truth, empty `docs/presets` catalog contract, and app-local governance location.
- Preset authoring/instantiation mode, exact-version preset contract, inter-layer capability matrix, and required AI guide routing.
- Closed read, write, and identity/authorization flow requirements connecting shared surfaces, feature policy, services, repositories, data adapters, and UI result states.
- Preset requirements for normalized inputs, dynamic query payloads, feature-owned allowlists, clean-room walking slices, materialization conflict policy, and lock/upgrade evidence.

### Changed

- The documentation package moved from repository root into `docs/blueprint`; root commands, CI filters, and validator repository lookup now reflect that boundary.
- The reference-application companion can author a reusable preset or instantiate one in addition to planning a single app.
- Next.js preset topology keeps application code under `src/` while retaining framework-default package, configuration, environment, public, and tool-owned paths at repository root.

### Migration

- Existing package-root links remain relative inside `docs/blueprint`; callers must prefix validator/scorer paths with `docs/blueprint`.
- Future apps must select a verified preset and record its immutable revision before treating preset guides as code-shape authority.

### Maturity

- Package remains `experimental`; the new distribution and preset contracts have structural validation but no completed independent preset pilot yet.

## 0.9.0 - 2026-07-12

### Added

- Human and AI progressive-adoption route.
- Versioned package maturity and graduation policy.
- Versioned control catalog with stable control and gate IDs.
- Machine-readable control catalog, fail-closed readiness scorer, input initializer, and regression tests.
- Versioned evidence-manifest JSON schema with repository-contained artifact hashes and explicit trusted-producer/acceptor policy.
- Baseline-versus-conditional applicability, auditable N/A decisions, scored repo-owned extensions, mode-selected gates, evidence-date/freshness checks, stale-gate failure semantics, and hash-resolved evidence manifests that prevent locator-only readiness claims.
- Canonical artifact-instance metadata, status lifecycle, registry, exception ledger, and architecture-exception template.
- Reproducible readiness-calculation contract and filled governance examples.
- Automated documentation-validation contract and CI command.
- Negative validation for empty/incomplete effective artifacts, unchecked gates, blank effective fields, and source-template produced-type mismatches.
- Second stack profile for Django/PostgreSQL/HTMX and a schema-conformant `BASIC_WEB` artifact bundle with a fail-closed `0.00/not-ready` assessment to test portability, traceability, and proportionality.
- Complete system-profile prompts for retention, service objectives, recovery, support, and team/release capability.
- Risk-selected reference-app tiers so a small web app does not inherit full-showcase ceremony by default.
- Explicit production contracts for cache/HTTP-cache failure, browser hardening and detection, multi-store disaster recovery, worker shutdown/scheduling, test lanes/flaky policy, and public-contract deprecation.

### Changed

- Root router now distinguishes documentation-package conformance from implementation production readiness.
- Governance templates now declare their produced artifact type and template version.
- Reference-app artifacts now use the same schema `1.0`, lowercase lifecycle, template version, and produced-type contract as root governance artifacts.
- Documentation CI uses read-only permissions, non-persisted checkout credentials, commit-pinned actions, and catalog-aware path filters.
- The non-reproducible Next.js source snapshot is labeled a candidate mapping; the source-backed Django mapping remains the maintained portability profile.

### Migration

- Existing artifact files should retain their current IDs when known; otherwise assign a new stable ID and record prior paths/identifiers in the artifact registry.
- Existing exceptions require an expiry/removal trigger and ledger entry before they can be treated as active waivers.
- Existing readiness assessments must declare control-catalog version `1.0.0` and recalculate from stable control IDs.

### Maturity

- Package remains `experimental`; candidate/stable evidence in [MATURITY.md](MATURITY.md) has not yet been established.
