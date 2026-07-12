---
template_id: SKEL-TPL-EXCEPTION-LEDGER
template_version: 1.0.0
produces: exception-ledger
owner_guide: ../07-ai-operating-system-and-governance.md
use_when: Tracking active, expired, resolved, rejected, and superseded architecture/control exceptions.
---

# Exception ledger: [system/repository]

> Instantiate with schema `1.0` from [README.md](README.md). The ledger indexes decisions; each row links to a complete exception artifact.

## Ledger

| Exception ID | Rule/control | Exact scope | Risk owner | Approved by/date | Effective/expiry | Removal trigger/tracking | Compensating evidence | Status | Artifact link | Last/next check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Ledger invariants

- Only a linked `active` exception whose `expires_at` is in the future grants a waiver.
- `proposed`, `expired`, `resolved`, `rejected`, and `superseded` rows do not suppress a gate or ratchet.
- Every active row names exact scope, violated stable ID, risk owner, compensating evidence, expiry, and removal trigger.
- A scope increase requires a newly approved artifact version or replacement; never widen a ledger row silently.
- Expired items fail the governed check until remediated or replaced through fresh approval.
- Historical rows remain as tombstones; link moves update the registry without changing the exception ID.

## Review record

| Reviewed at | Reviewer | Active count | Expired count | Missing/stale evidence | Actions/owners/dates |
| --- | --- | ---: | ---: | --- | --- |
