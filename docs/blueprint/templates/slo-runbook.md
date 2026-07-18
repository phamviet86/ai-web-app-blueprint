---
template_id: SKEL-TPL-SLO-RUNBOOK
template_version: 1.1.0
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

## Diagnostic and action authority

| Step | Data mode: `NONE` / `LIVE_READ` / `TEST_MUTATION` / `PRODUCTION_HANDOFF` | Allowed interface / target | External side effect: none / isolated simulation / operator action | Guard / approval | Success observation / postcheck / recovery / owner |
| --- | --- | --- | --- | --- | --- |

- No-fallback rule for live diagnostics:
- Operator boundary for production data change and for real publish/release/deploy (tracked separately):

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

| Exercised at | SLI/dashboard result checked | Alert route/on-call receipt | Runbook action + authority/stop path | Outcome/postcheck | Follow-up owner/due date |
| --- | --- | --- | --- | --- | --- |
