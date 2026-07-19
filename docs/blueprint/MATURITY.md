---
guide_id: SKEL-MATURITY
title: Documentation Package Version and Maturity Policy
status: experimental
audience: human-and-ai
package_version: 0.13.0
control_catalog_version: 1.0.0
artifact_schema_version: "1.0"
read_when:
  - Adopting, releasing, grading, or changing this documentation package.
skip_when:
  - Implementing a narrow application change under already-adopted repo-local rules.
depends_on:
  - README.md
  - 07-ai-operating-system-and-governance.md
  - 08-scorecard-and-readiness-gates.md
owns:
  - package version and maturity claims
  - graduation and deprecation policy
  - compatibility policy for guides controls and templates
---

# Documentation package version and maturity policy

> This policy grades the blueprint package, not applications built from it. No package maturity label proves that an implementation is secure, reliable, or production-ready.

## Current declaration

| Field | Value |
| --- | --- |
| Package version | `0.13.0` |
| Package maturity | `experimental` |
| Control catalog | `1.0.0` in guide `08` |
| Artifact schema | `1.0` in [templates/README.md](templates/README.md) |
| Required validators | Unit/fixtures: `PYTHONPATH=docs/blueprint python3 -m unittest discover -s docs/blueprint/scripts -p 'test_*.py'`; docs: `python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .`; presets: `python3 docs/blueprint/scripts/validate_presets.py docs/presets`; adopting app: `python3 docs/blueprint/scripts/validate_app_profile.py PATH --repo-root ROOT --expected-revision <current-source-revision> --expected-blueprint-revision <selected-blueprint-revision>` |
| Declaration date | 2026-07-19 |

`9.5/10` is the design coverage target. It is not the current package maturity label and is never inherited by a repository. An implementation earns a readiness claim only through guide `08` against current evidence.

## Current graduation evidence register

| Requirement | Current evidence | Accountable owner / next trigger |
| --- | --- | --- |
| Package owner | Unassigned; blocker | A human maintainer must accept ownership before candidate declaration |
| Support/security/compatibility channel | None; blocker | Owner publishes a reachable channel and response policy |
| Human dry run | Missing | Run from system profile through scorer without author guidance |
| AI-assisted dry run | Bingo LMS supplies two revision-bound repository-derived observations with focused checks current only for each named source revision; neither is a clean-room adoption of this package | Run an independent app-profile or preset adoption from unprimed context against the current package revision |
| Independent defect review | In-session editing/auditing is not a published independent acceptance | Named reviewer records scope, date, result, and evidence locator |
| Pilot repositories | No qualifying package pilot; two records from one same-stack repository are recorded in `evidence/bingo-lms-repository-lessons.md` and `evidence/bingo-lms-refactor-lessons-2026-07-19.md` | Complete two materially different governed pilots; at least one must use another effective stack architecture |
| Reassessment trigger | Package/content change or continued evaluation by 2026-08-18 | Prospective owner; no automatic maturity promotion |

These missing rows are intentionally explicit. Do not replace them with invented names, approvals, repositories, or command results. Structural CI and the fictional reference bundle demonstrate mechanics only.

## Rule `PKG-VERSION-01`: version the public documentation contract

Use semantic versioning for the package:

- **major:** a rule is removed/redefined incompatibly, a stable ID changes meaning, an artifact schema requires migration, or scoring changes an existing result materially;
- **minor:** a backward-compatible guide/control/template/profile is added, or optional metadata becomes available;
- **patch:** wording, link, example, or validator correction that does not change obligations or scores.

The public documentation contract includes guide/rule/control/template IDs, required artifact fields, controlled statuses, scoring formula, and required validation command. Never reuse a retired ID for another meaning. Keep a tombstone or supersession link when an ID is retired.

Every release updates:

1. `package_version` here and in the root router;
2. [CHANGELOG.md](CHANGELOG.md), including migrations and removed/deprecated IDs;
3. validator fixtures when a machine-checkable contract changes;
4. affected examples and registry entries;
5. the control-catalog or artifact-schema version when its contract changes.

## Maturity lifecycle

```text
experimental -> candidate -> stable -> deprecated -> retired
                    |           |
                    +-----------+-> experimental when a major redesign invalidates evidence
```

| State | Permitted claim | Minimum meaning |
| --- | --- | --- |
| `experimental` | Safe to evaluate and pilot with human review | Structure may change; gaps and portability assumptions are still being tested |
| `candidate` | Suitable for governed pilots | Structural validation passes; artifacts and scoring are reproducible; remaining graduation evidence is named |
| `stable` | Supported package contract | Graduation evidence below is current; compatibility and release policy are operational |
| `deprecated` | Existing use only | Replacement, migration path, owner, and removal date are published |
| `retired` | Historical evidence only | No new adoption; links remain only for audit/migration history |

Guide/profile/example maturity cannot exceed package maturity unless it is versioned and supported as an explicitly independent package.

## Rule `PKG-GRADUATION-01`: graduation requires evidence, not editorial confidence

### Experimental to candidate

All are required:

- the canonical docs validator and its negative fixtures pass in CI;
- all guides remain within the declared context budget and have unique owners/IDs;
- control catalog and artifact schema are versioned and demonstrated by filled examples;
- one human and one AI-assisted dry run can route from system profile to a scored assessment without undocumented interpretation;
- at least one stack profile is checked against current primary documentation;
- an independent reviewer records no unresolved critical documentation defect;
- known gaps, package owner, support channel, and next review date are published.

### Candidate to stable

All candidate evidence remains current, plus:

- at least two completed pilot repositories with materially different risk or stack profiles record adoption friction and assessment evidence;
- at least one pilot exercises release/recovery and one exercises an exception through resolution or expiry;
- a second stack mapping demonstrates that core rules are not framework-specific;
- two consecutive package releases complete without an unplanned breaking change;
- deprecated IDs and artifact migrations have been exercised from the previous minor line;
- maintainers accept a documented review cadence and security/compatibility response policy.

Pilot evidence may be private, but the package declaration must name the reviewer, date, scope, result, and a non-sensitive evidence locator. A sample app, passing build, or docs validator alone is insufficient.

## Review, downgrade, and deprecation

- Review package maturity at every minor/major release and at least every 90 days while `candidate` or `stable`.
- Downgrade the declaration when required evidence is invalidated, primary references materially change, the validator no longer represents the contract, or a critical ambiguity causes unsafe adoption.
- Deprecation must name replacement, migration steps, compatibility window, owner, and removal release/date.
- A security correction may break compatibility immediately; document impact and safe migration in the changelog.
- Historical claims retain their original package version, catalog version, artifact schema, source revision, and assessment date.

## Claim vocabulary

Use only claims supported by evidence:

- **design target:** intended coverage, not assessed;
- **structurally conformant:** the required docs validator passed for a named revision;
- **pilot-ready:** package is at least `candidate` and adoption prerequisites are satisfied;
- **implementation ready / 9.5-ready:** guide `08` passed against the named deployed system and evidence window.

Never shorten “structurally conformant documentation” to “production-ready.”
