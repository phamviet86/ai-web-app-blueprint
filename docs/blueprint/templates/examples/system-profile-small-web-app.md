---
artifact_id: EXAMPLE-SYS-PROFILE-PORTAL
artifact_type: system-profile
schema_version: "1.0"
artifact_version: 1
title: Example profile for a small customer-support portal
status: draft
owner: example-product-owner
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:example-support-portal
source_template: SKEL-TPL-SYSTEM-PROFILE@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: small customer-support portal

> Fictional, non-authoritative completion example. It has no implementation evidence and status `draft`; it does not establish readiness or recommend these targets for another system.

## Ownership

- System/product: customer-support portal
- Decision owner: example product owner
- Technical owner: example web team lead
- Operations/security/data owners: web team lead / security reviewer / product owner
- Date and revisit trigger: 2026-07-12; revisit before pilot traffic or when restricted data is proposed

## Primary architecture profile

- Primary profile and why it dominates: interactive web application; request/response journeys and one relational source of truth dominate
- Secondary profiles and bounded concerns: scheduled email notification worker; no user-facing correctness depends on immediate delivery

## Critical journeys

| Journey | Users/actors | Success | Unacceptable failure | Peak/load shape |
| --- | --- | --- | --- | --- |
| Submit support request | Authenticated customer | Request receives stable ID and is visible immediately | Cross-customer disclosure or acknowledged request loss | 20 requests/minute, burst 60 |
| Review/update assigned request | Support agent | Authorized state change and audit entry commit together | Unauthorized update or silent overwrite | 30 concurrent agents |

## Risk classification

| Dimension | Decision | Evidence/unknown owner |
| --- | --- | --- |
| Exposure | internet | Product brief; product owner |
| Data sensitivity | confidential; contact details and support text, no payment/health data allowed | Proposed field inventory; data owner must verify before pilot |
| Tenancy | logical multi-tenant by customer account | Product brief; technical owner |
| Identity assurance | managed login, phishing-resistant admin MFA, reauth for role changes; recovery handled by identity provider | Security review pending; security owner |
| Availability | business critical during weekday support hours | Support policy draft; product owner |
| Regulation/contract | privacy and customer deletion obligations; jurisdiction review pending | Legal question owned by product owner before pilot |
| Scale | 5k accounts, 100k requests after 12 months, 60 write requests/minute peak | Forecast; product owner |
| Cost envelope | USD 500/month pilot ceiling; product owner approves increase | Finance assumption |

## Data lifecycle and retention

| Data/store | Class/tenant scope | Purpose | Retention/deletion | Backup/log/vendor propagation | Owner |
| --- | --- | --- | --- | --- | --- |
| Account/contact | confidential/account | Identity and response | Active account + 30 days; deletion request within 30 days unless hold | Backup expiry within 35 days; redact logs; identity provider deletion verified | Data owner |
| Support request | confidential/account | Resolve support issue | 365 days after closure, then delete or documented hold | Backup expiry within 35 days; email contains link, not body | Product owner |
| Audit event | internal/account | Privileged change investigation | 400 days, access restricted | Separate retention check; no free-text request body | Security owner |

- Legal hold/erasure conflict: product owner records named authority and scoped hold; non-held derived/search data still deletes
- Data residency/vendor constraints: pilot region and email processor contract remain unknown; product owner resolves before pilot

## Service, recovery, and support objectives

| Journey/capability | SLI/SLO and window | RPO | RTO | Measurement/restore evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Submit/review requests | 99.5% successful non-user-error requests over 28 days; p95 under 800 ms at forecast load | 15 minutes | 2 hours in support window | Synthetic journey plus server metric; restore rehearsal required before pilot | Technical owner |
| Notification worker | 99% delivered or quarantined within 15 minutes over 28 days | 15 minutes | 4 hours | Queue age/DLQ metric and replay exercise | Technical owner |

- Support hours/timezone: Monday-Friday 08:00-18:00 Asia/Ho_Chi_Minh, excluding published holidays
- On-call/escalation: technical owner during support hours; product owner communicates customer impact; managed vendors use contracted escalation
- Incident ownership/communication: technical owner declares severity and mitigation; product owner owns status updates
- Maintenance/change window: Tuesday 20:00-22:00 local; emergency security fixes require product-owner notification

## Team and release capability

- Team/skills: three product engineers; no dedicated SRE; security review available before pilot and quarterly
- Delivery ownership/bus factor: technical owner plus one backup can release and recover; restore currently owner-only and is a pilot blocker
- Release cadence/change approval: weekly small releases; technical owner approves low-risk, product/security owner approves declared risk changes
- Environment/CI capability: isolated development/test/staging planned; protected production; deterministic CI and immutable artifact promotion required
- Operational capacity: support-hours response only; no 24x7 promise; managed database/backups preferred
- Training/hand-off gaps: second engineer must pass restore/recovery exercise before pilot

## Quality targets

| Quality scenario | Stimulus and source | Environment/load | Expected response and measure | Accepted trade-off | Owner | Revisit trigger |
| --- | --- | --- | --- | --- | --- | --- |
| Tenant isolation | Customer requests another account's ID | Production-shaped integration environment | Default deny, no metadata leakage, negative test passes | None | Security owner | Any auth/query change |
| Submit latency | Forecast peak burst | Staging with representative dataset | p95 under 800 ms and no acknowledged loss | Notification may lag 15 minutes | Technical owner | 2x traffic/data forecast |
| Restore | Primary datastore unavailable | Isolated recovery environment | Verified RPO 15m/RTO 2h | Read-only status page during restore | Technical owner | Storage/topology change |

- Baseline qualities that cannot be traded away: tenant isolation, no acknowledged request loss, secret/PII redaction, recoverability
- Differentiating quality priorities: simple support-hours operations and low pilot cost over global availability

## Topology

- Repository topology and rationale: one repository to match one small team and atomic contract changes
- Deployment topology and rationale: one modular web deployable plus bounded notification worker; managed relational database
- Data ownership boundaries: support capability owns requests; identity adapter maps external subject to internal account
- External dependencies/trust boundaries: identity provider, email provider, managed database, browser clients
- Conditions triggering redesign: independent scaling/ownership need, worker harms request SLO, regional contract, or measured resource isolation failure

## Selected controls

| Control/guide | baseline / conditional / N/A | Owner | Evidence or N/A rationale | Revisit trigger |
| --- | --- | --- | --- | --- |
| `CTL-SEC-AUTHZ-01` | baseline | Security owner | Negative tenant/role tests required; missing in draft | Any identity/query change |
| `CTL-DATA-RECOVERY-01` | baseline | Technical owner | Restore drill required; missing in draft | Storage/topology change |
| `CTL-REL-ASYNC-01` | conditional | Technical owner | Notification delivery/replay contract required | Worker/vendor change |
| `CTL-OPS-SLO-01` | baseline | Technical owner | SLI query and alert route required | SLO/journey change |

## Unknowns and adoption decision

| Unknown | Owner | Resolve by/trigger | Effect if unresolved |
| --- | --- | --- | --- |
| Jurisdiction/vendor residency | Product owner | Before pilot data | Pilot blocked |
| Identity assurance mapping | Security owner | Before auth implementation acceptance | Privileged flows blocked |
| Restore bus factor | Technical owner | Before production gate | Production gate fails |

- Adoption stage: profile-only evaluation
- Next artifact: threat model and access matrix after unknowns resolve
- Current readiness claim: none; this is a draft example without implementation evidence
