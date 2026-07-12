---
document_id: SKEL-CHANGELOG
title: Package Changelog
status: experimental
audience: human-and-ai
package_version: 0.10.0
---

# Changelog

All notable package-contract changes are recorded here. Versions follow [MATURITY.md](MATURITY.md); dates use ISO `YYYY-MM-DD`.

## Unreleased

- None.

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
