---
template_id: SKEL-TPL-SYSTEM-PROFILE
template_version: 1.0.0
produces: system-profile
owner_guide: ../01-foundations.md
use_when: Starting a greenfield blueprint or materially changing topology/risk.
---

# System and risk profile

> Instantiate with schema `1.0` from [README.md](README.md). A filled example is available at [examples/system-profile-small-web-app.md](examples/system-profile-small-web-app.md).

## Ownership

- System/product:
- Decision owner:
- Technical owner:
- Operations/security/data owners:
- Support/incident communication owners:
- Date, approval state, and revisit trigger:

## Primary architecture profile

- Primary profile and why it dominates:
- Secondary profiles and bounded concerns:

## Critical journeys

| Journey | Users/actors | Success | Unacceptable failure | Peak/load shape |
| --- | --- | --- | --- | --- |

## Risk classification

| Dimension | Decision | Evidence/unknown owner |
| --- | --- | --- |
| Exposure | internal / partner / internet |
| Data sensitivity | public / internal / confidential / restricted |
| Tenancy | single / logical multi-tenant / isolated |
| Identity assurance | mapped IAL/AAL/FAL or equivalent; authenticator/phishing resistance/reauth/recovery requirements |
| Availability | best effort / business critical / safety critical |
| Regulation/contract | none known / named obligations |
| Scale | traffic, concurrency, dataset, growth horizon |
| Cost envelope | monthly/unit ceiling and owner |

## Data lifecycle and retention

| Data/store/cache/log/backup/vendor | Classification and tenant scope | Purpose/source of truth | Retention/deletion/legal hold | Backup/log/vendor propagation | Owner/evidence |
| --- | --- | --- | --- | --- | --- |

- Data residency and cross-border/vendor constraints:
- Erasure versus legal-hold decision authority:
- Derived/search/analytics data deletion propagation:
- Unknown classification/retention questions, owner, and resolve-by trigger:

## Service and recovery objectives

| Critical journey/capability | SLI and SLO/window | RPO | RTO | Capacity/degradation objective | Measurement/restore evidence | Owner |
| --- | --- | --- | --- | --- | --- | --- |

- SLO exclusion and error-budget decision policy:
- Backup frequency/retention/immutability and restore environment:
- Dependency objectives and behavior when they are weaker than the journey target:
- Recovery decision authority and data-correction limit:

## Support and incident model

- Support hours, timezone, holidays, and promised response:
- On-call/escalation coverage and vendor escalation:
- Incident severity owner, customer/status communication owner, and channels:
- Maintenance/change window and emergency-change authority:
- Runbook/alert/restore exercise cadence:

## Team and release capability

- Team size, relevant skills, ownership boundaries, and bus factor:
- Release cadence, change approval, and separation-of-duty constraints:
- Environment/CI/artifact-promotion capability:
- Operational capacity: self-managed versus managed services, 24x7 limits, and cost ceiling:
- Training, access, hand-off, or recovery gaps with owner and deadline:
- Capability gaps that block a topology/control or require an exception:

## Quality targets

| Quality scenario | Stimulus and source | Environment/load | Expected response and measure | Accepted trade-off | Owner | Revisit trigger |
| --- | --- | --- | --- | --- | --- | --- |

- Baseline qualities that cannot be traded away:
- Differentiating quality priorities:

## Topology

- Repository topology and rationale:
- Deployment topology and rationale:
- Data ownership boundaries:
- External dependencies/trust boundaries:
- Conditions that would trigger extraction or redesign:

## Selected controls

| Control/guide | baseline / conditional / N/A | Owner | Evidence or N/A rationale | Revisit trigger |
| --- | --- | --- | --- | --- |

## Unknowns and adoption decision

| Unknown/assumption | Decision owner | Resolve by or discovery trigger | Safe default / blocked action |
| --- | --- | --- | --- |

- Adoption stage: evaluate / profile / walking-slice / enforced / release-governed
- Accepted by/date:
- Next required artifact/gate:
- Current claim: target only / assessed result with artifact ID
