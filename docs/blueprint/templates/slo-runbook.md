---
template_id: SKEL-TPL-SLO-RUNBOOK
template_version: 1.0.0
produces: slo-runbook
owner_guide: ../15-delivery-observability-and-operations.md
use_when: A critical journey/service needs an SLO, alert, or operational response.
---

# SLO and runbook: [journey/service]

> Instantiate with schema `1.0` from [README.md](README.md).

- Service owner / on-call / escalation:
- Users and critical dependency chain:
- Review period:

## SLI/SLO

| SLI | Good/valid event definition | Source/query | Target/window | Exclusions |
| --- | --- | --- | --- | --- |

- Error-budget policy and release response:
- Capacity/saturation limit:
- RPO/RTO dependency:

## Telemetry governance

- Attribute allowlist / prohibited high-cardinality values:
- Sampling and must-retain evidence:
- Retention / access / sensitive-data policy:
- Volume, drop/backpressure, and cost budget:
- Deploy/config/flag/migration markers:

## Alerts

| Alert | User impact | Threshold/window | Owner | Dashboard/log/trace link |
| --- | --- | --- | --- | --- |

## Triage and mitigation

1. Confirm user impact and recent deploy/config/migration markers.
2. Check saturation, dependency, data, and security signals.
3. Apply safe mitigation/kill switch/rollback or roll-forward.
4. Communicate status and preserve evidence.
5. Verify recovery against SLI and reconcile partial work.

## Known failure modes

| Symptom | Likely causes | Diagnostic | Safe mitigation | Escalation |
| --- | --- | --- | --- | --- |

## Last exercised evidence

| Exercised at | SLI query/result checked | Alert route/on-call receipt | Runbook/kill-switch action | Outcome | Follow-up owner/due date |
| --- | --- | --- | --- | --- | --- |
