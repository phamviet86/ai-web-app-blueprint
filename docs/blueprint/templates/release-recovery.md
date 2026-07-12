---
template_id: SKEL-TPL-RELEASE-RECOVERY
template_version: 1.0.0
produces: release-plan
owner_guide: ../15-delivery-observability-and-operations.md
use_when: A release changes public/data/event/runtime behavior or has material rollback limits.
---

# Release and recovery plan: [change]

> Instantiate with schema `1.0` from [README.md](README.md).

- Owner / approver / deploy window:
- Artifact identity/digest/provenance:
- Contract/schema/event compatibility window:
- Risk and affected SLOs:

## Gates

| Gate | Evidence | Owner | Go/no-go condition |
| --- | --- | --- | --- |
| CI/security/supply chain | | | |
| Infrastructure revision/plan/drift/recovery | | | |
| Migration/backfill | | | |
| Preview/staging smoke | | | |
| Telemetry/alerts/runbook | | | |
| Backup/restore or correction path | | | |

## Infrastructure evidence

- Declarative revision or managed-platform configuration export:
- Reviewed plan/policy/security result and protected-state location:
- Applied actor/change record and post-apply drift result:
- Rebuild, rollback, or roll-forward evidence:

## Rollout

- Flag/canary/cohort sequence:
- Flag owner / expiry / kill-switch path:
- Health/SLI/business comparison:
- Observation window:
- Automatic/manual abort thresholds:
- Behavior for in-flight requests and queued/background work:

## Recovery

- App rollback versus roll-forward:
- Schema/event compatibility limit:
- Partial side effects/reconciliation:
- Data restore/correction and RPO/RTO:
- Flag/transition cleanup trigger:
