---
template_id: SKEL-TPL-ARCHITECTURE-EXCEPTION
template_version: 1.0.0
produces: architecture-exception
owner_guide: ../07-ai-operating-system-and-governance.md
use_when: A scoped architecture, security, data, reliability, or quality rule cannot currently be met.
---

# Architecture exception: [bounded deviation]

> Instantiate with schema `1.0` from [README.md](README.md). Only status `active` before `expires_at` grants a waiver.

## Requested deviation

- Violated rule/control ID:
- Exact component/path/runtime/data scope:
- Business constraint and evidence:
- Why a compliant option is not currently feasible:
- Explicitly out of scope:

## Risk decision

| Failure/abuse outcome | Likelihood | Impact | Exposed users/data/SLO | Detection |
| --- | --- | --- | --- | --- |

- Risk owner:
- Approval authority and decision date:
- Residual risk accepted:
- Conditions that immediately revoke approval:

## Compensating controls and ratchet

| Control | Evidence/metric | Owner | Cadence | Failure action |
| --- | --- | --- | --- | --- |

- Baseline violation count/severity:
- Check preventing new scope or severity:
- Tracking item:
- Removal implementation owner:

## Time bound and removal

- Effective from:
- Expiry (`expires_at`):
- Earlier measurable removal trigger:
- Delivery checkpoints:
- Compliant target state and migration/cutover path:
- Rollback/recovery limit:

## Verification and closure

| Review/checkpoint | Evidence | Result | Reviewer/date | Next action |
| --- | --- | --- | --- | --- |

- Resolution/supersession artifact:
- Deletion/remediation proof:
- Closed by/date:

On expiry, mark `expired`; do not extend by editing the old date. Approve a new artifact version or replacement after a fresh risk review, and keep the original as a ledger tombstone.
