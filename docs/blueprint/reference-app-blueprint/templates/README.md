---
guide_id: REFAPP-TEMPLATE-SCHEMA
title: Reference Application Artifact Template Mapping
status: experimental
audience: human-and-ai
read_when:
  - Instantiating any reference-application planning template.
  - Creating the contract artifact for a reusable preset.
depends_on:
  - ../../templates/README.md
  - ../README.md
owns:
  - reference artifact type and template mapping
  - schema 1.0 instantiation procedure for reference plans
  - preset-contract template mapping
---

# Reference application artifact template mapping

> Reference artifacts use the parent [artifact-instance schema `1.0`](../../templates/README.md#artifact-instance-frontmatter-schema-10). The bullet fields in each template body are a completion checklist, not an alternative metadata format.

## Template and artifact-type map

| Template ID | Version | Produces / `artifact_type` | Effective status |
| --- | --- | --- | --- |
| `REFAPP-TPL-PRESET-CONTRACT` | `1.0.0` | `preset-contract` | `accepted` |
| `REFAPP-TPL-STACK-PROFILE` | `1.0.0` | `stack-profile` | `accepted` |
| `REFAPP-TPL-CAPABILITY-COVERAGE` | `1.0.0` | `capability-coverage` | `accepted` |
| `REFAPP-TPL-DATA-MODEL` | `1.0.0` | `data-model` | `accepted` |
| `REFAPP-TPL-SHARED-PLAN` | `1.0.0` | `shared-plan` | `accepted` |
| `REFAPP-TPL-PLATFORM-PLAN` | `1.0.0` | `platform-plan` | `accepted` |
| `REFAPP-TPL-FEATURE-PLAN` | `1.0.0` | `feature-plan` | `accepted` |
| `REFAPP-TPL-ROUTE-MAP` | `1.0.0` | `route-map` | `accepted` |
| `REFAPP-TPL-REFERENCE-APP-PLAN` | `1.0.0` | `reference-app-plan` | `accepted` |

## Instantiate a template

Copy the selected template body and replace its template-definition frontmatter with:

```yaml
artifact_id: STACK-EXAMPLE-001
artifact_type: stack-profile
schema_version: "1.0"
artifact_version: 1
title: Example accepted stack
status: draft
owner: example-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:example
source_template: REFAPP-TPL-STACK-PROFILE@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-10-12
expires_at: null
```

Change the ID/type/template tuple according to the map. Keep `review_by` and `expires_at` keys even when null. Use lowercase artifact statuses. `not-required` belongs only in a plan's applicability registry with owner/rationale/revisit; it is never artifact frontmatter status.

An artifact becomes `accepted` only after its template gates pass with current decision evidence. Evidence IDs inside the body retain their separate lifecycle (`PLANNED`, `OBSERVED`, `VERIFIED`, `STALE`, `INVALID`).
