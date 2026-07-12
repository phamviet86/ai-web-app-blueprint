---
guide_id: SKEL-ARTIFACT-SCHEMA
title: Governance Artifact Schema and Template Catalog
status: experimental
audience: human-and-ai
schema_version: "1.0"
depends_on:
  - ../07-ai-operating-system-and-governance.md
owns:
  - artifact instance field schema
  - artifact status vocabulary
  - root template catalog
---

# Governance artifact schema and template catalog

> Templates are prompts; instantiated artifacts are governed records. An instance is valid only when its frontmatter and lifecycle follow this schema and its decision fields are complete.

## Template-definition contract

Every template file declares:

```yaml
template_id: SKEL-TPL-SYSTEM-PROFILE
template_version: 1.0.0
produces: system-profile
owner_guide: ../01-foundations.md
use_when: Starting a greenfield blueprint or materially changing topology/risk.
```

`template_id` is immutable. Increment `template_version` using the compatibility policy in [MATURITY.md](../MATURITY.md). A template definition is not itself evidence that the produced artifact exists.

## Artifact-instance frontmatter schema `1.0`

Replace template-definition frontmatter with this block when creating an artifact instance; keep the template body and fill it with evidence-backed decisions.

```yaml
artifact_id: ADR-2026-0001
artifact_type: adr
schema_version: "1.0"
artifact_version: 1
title: Keep one modular deployable until extraction triggers are measured
status: proposed
owner: architecture-group
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:example-web
source_template: SKEL-TPL-ADR@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-10-12
expires_at: null
```

| Field | Contract |
| --- | --- |
| `artifact_id` | Immutable, repo-unique `^[A-Z][A-Z0-9]*(-[A-Z0-9]+){2,}$`; use type + stable scope/sequence, never a mutable title/path |
| `artifact_type` | One controlled type from the status table below |
| `schema_version` | Exact schema used to parse the artifact |
| `artifact_version` | Positive integer; increment for every approved material revision |
| `title` | Human-readable description; may change without changing ID |
| `status` | Controlled by artifact type; only an effective status grants authority |
| `owner` | One accountable role/team; active artifacts cannot use `TBD` |
| `created_at`, `updated_at` | ISO dates; `updated_at` cannot precede `created_at` |
| `scope` | Non-empty list of stable `kind:value` tokens such as `system:billing` or `capability:checkout` |
| `source_template` | `template_id@template_version`, or `null` only for an imported record whose body has a `## Migration note` section |
| `supersedes` | Artifact IDs replaced by this record; never paths |
| `superseded_by` | Replacing artifact ID, otherwise `null` |
| `review_by` | ISO date or `null`; required for active risk/profile/runbook/control artifacts |
| `expires_at` | ISO date or `null`; required for active exceptions and time-bound transitions |

Use `[]` and `null`, not empty strings. Store prior paths/legacy IDs in the registry note rather than changing `artifact_id`. Accepted material edits increment `artifact_version`, `updated_at`, and the registry entry. Supersession updates both records atomically where possible.

## Controlled types and statuses

| Artifact type | Lifecycle | Effective status |
| --- | --- | --- |
| `system-profile`, `access-matrix`, `threat-model`, `test-strategy`, `slo-runbook` | `draft -> active -> superseded -> retired` | `active` |
| `adr` | `proposed -> accepted / rejected -> superseded` | `accepted` |
| `architecture-exception` | `proposed -> active -> resolved / expired / rejected / superseded` | `active` before `expires_at` only |
| `readiness-assessment` | `draft -> final -> superseded` | `final` for its named revision/date only |
| `migration-plan`, `release-plan`, `refactor-plan` | `draft -> approved -> in-progress -> completed / cancelled / superseded` | `approved` or `in-progress` within scope/window |
| `artifact-registry`, `exception-ledger` | `draft -> active -> superseded -> retired` | `active` |
| `stack-profile`, `capability-coverage`, `data-model`, `shared-plan`, `platform-plan`, `feature-plan`, `route-map`, `reference-app-plan`, `preset-contract` | `draft -> in-review -> accepted / rejected -> superseded` | `accepted` |

Status values are lowercase in artifact frontmatter. Reference-plan `not-required` is an applicability decision with owner/rationale/revisit, not an artifact status. Status transitions require owner, date, and evidence in the body or registry. `expired`, `rejected`, `resolved`, `retired`, and `superseded` records remain discoverable as audit tombstones. An overdue review invalidates authority/evidence as defined by its owner; it never silently extends an exception.

## Registry layout in an adopting repo

Recommended, not path-dependent:

```text
docs/governance/artifact-registry.md
docs/governance/exception-ledger.md
docs/governance/profiles/
docs/governance/adrs/
docs/governance/exceptions/
docs/governance/assessments/
docs/governance/runbooks-and-plans/
```

The stable ID, not the directory, is identity. Register every active/superseded decision, assessment, exception, plan, and operational artifact. Retain tombstones after moves or deletion.

## Template catalog

| Template | Produces |
| --- | --- |
| [system-profile.md](system-profile.md) | System drivers, risks, objectives, support/team capability, and selected controls |
| [adr.md](adr.md) | Consequential architecture decision |
| [architecture-exception.md](architecture-exception.md) | One bounded deviation with expiry/removal proof |
| [artifact-registry.md](artifact-registry.md) | Canonical artifact inventory and tombstones |
| [exception-ledger.md](exception-ledger.md) | Active and historical exception index |
| [readiness-assessment.md](readiness-assessment.md) | Reproducible control score and gate decision |
| [threat-model.md](threat-model.md) | Trust-boundary threats, controls, and residual risk |
| [access-matrix.md](access-matrix.md) | Resource/action/tenant authorization lifecycle |
| [data-migration.md](data-migration.md) | Compatible data/schema migration and recovery |
| [test-strategy.md](test-strategy.md) | Risk-to-test and architecture-fitness mapping |
| [slo-runbook.md](slo-runbook.md) | Critical-journey objectives and operational response |
| [release-recovery.md](release-recovery.md) | Release, compatibility, rollout, and recovery gates |
| [refactor-slice.md](refactor-slice.md) | Characterized seam through cutover/deletion |

Filled, non-authoritative examples:

- [small web system profile](examples/system-profile-small-web-app.md)
- [time-bounded architecture exception](examples/architecture-exception.md)

Examples demonstrate completeness and lifecycle only. They are not recommendations, production evidence, or readiness claims for another system.
