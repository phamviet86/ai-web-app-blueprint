---
template_id: SKEL-TPL-ARTIFACT-REGISTRY
template_version: 1.0.0
produces: artifact-registry
owner_guide: ../07-ai-operating-system-and-governance.md
use_when: Establishing the canonical inventory of governance and evidence-bearing artifacts.
---

# Artifact registry: [system/repository]

> Instantiate with schema `1.0` from [README.md](README.md). IDs survive path, title, and owner changes.

## Current and historical artifacts

| Artifact ID | Type | Version | Status | Scope | Owner | Path/evidence locator | Updated | Review/expiry | Supersedes/by | Note |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |

## Registry invariants

- One row per repo-unique `artifact_id`; never recycle IDs.
- The row matches the current artifact metadata and links to the exact revision when evidence is immutable.
- Active artifacts have an accountable owner and required review/expiry date.
- Supersession links point both directions; historical rows remain as tombstones.
- Missing files, duplicate IDs, impossible status transitions, overdue reviews, and expired active exceptions fail registry validation.
- Imported artifacts with no source template record origin and migration note.

## Registry review

| Reviewed at | Source revision | Validator result | Drift/tombstones found | Owner/action/date |
| --- | --- | --- | --- | --- |
