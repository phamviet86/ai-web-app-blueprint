---
artifact_id: EXAMPLE-EXC-2026-0001
artifact_type: architecture-exception
schema_version: "1.0"
artifact_version: 2
title: Example resolved temporary deep import during module cutover
status: resolved
owner: example-orders-team
created_at: 2026-04-01
updated_at: 2026-04-18
scope:
  - capability:example-reporting
source_template: SKEL-TPL-ARCHITECTURE-EXCEPTION@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: 2026-04-30
---

# Example only: resolved temporary deep import

> Fictional, non-authoritative lifecycle example. Its `resolved` status grants no waiver.

## Requested deviation

- Violated rule/control ID: `DEP-XMODULE-01`
- Exact scope: reporting adapter import of `orders/internal/legacy-export-row`; one named import edge only
- Business constraint: the replacement public export DTO could not ship atomically with a scheduled report change
- Why compliant option was not initially feasible: legacy exporter and report job had different release windows
- Explicitly out of scope: writes, other reporting callers, new legacy fields, and all browser/API entrypoints

## Risk decision

| Failure/abuse outcome | Likelihood | Impact | Exposed users/data/SLO | Detection |
| --- | --- | --- | --- | --- |
| Internal row change silently corrupts report | Medium | Medium | Operations-only report; confidential order summary | Contract comparison and report checksum |

- Risk owner: example orders-team lead
- Approval authority and decision date: example architecture reviewer, 2026-04-01
- Residual risk accepted: one read-only report for at most 29 days
- Conditions revoking approval: mismatch, additional caller/import, sensitive-field exposure, or missed checkpoint

## Compensating controls and ratchet

| Control | Evidence/metric | Owner | Cadence | Failure action |
| --- | --- | --- | --- | --- |
| Import allowlist of one source/target edge | Architecture check reports exactly one baseline violation | Orders team | Every CI run | Block merge |
| Old/new row comparison | 100% equality on representative fixture and shadow sample | Reporting owner | Every release | Disable new report path |

- Baseline violation count/severity: one medium read-only deep import
- Check preventing new scope: architecture ratchet threshold `1`, exact edge allowlist
- Tracking item: fictional `TRACK-ARCH-041`
- Removal implementation owner: example reporting engineer

## Time bound and removal

- Effective from: 2026-04-01
- Expiry: 2026-04-30
- Earlier removal trigger: public export DTO available and comparison passes
- Delivery checkpoints: DTO by 2026-04-10; caller switch by 2026-04-15; deletion by 2026-04-18
- Compliant target: reporting imports `orders/public` export contract only
- Recovery limit: revert caller to the single allowlisted edge before old internal shape changes

## Verification and closure

| Review/checkpoint | Evidence | Result | Reviewer/date | Next action |
| --- | --- | --- | --- | --- |
| Public DTO contract | Fictional CI contract result at revision `example-123` | Pass | Architecture reviewer, 2026-04-15 | Switch caller |
| Ratchet after deletion | Fictional architecture result: zero forbidden edges | Pass | Orders lead, 2026-04-18 | Resolve exception |

- Resolution artifact: fictional ADR not required; implementation followed existing public-contract rule
- Deletion proof: fictional revision `example-456`, deep import absent and ratchet baseline zero
- Closed by/date: example orders-team lead, 2026-04-18
