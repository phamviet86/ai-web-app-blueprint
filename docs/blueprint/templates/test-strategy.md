---
template_id: SKEL-TPL-TEST-STRATEGY
template_version: 1.0.0
produces: test-strategy
owner_guide: ../14-testing-and-architecture-fitness.md
use_when: A module/flow has multiple material failure modes or a refactor needs characterization evidence.
---

# Test strategy: [scope]

> Instantiate with schema `1.0` from [README.md](README.md).

- Owner:
- Observable/public contracts:
- System-profile risks:
- Out of scope and rationale:

| Failure mode/invariant | Cheapest sufficient layer | Test/data/environment | Negative/concurrency cases | CI cadence/owner |
| --- | --- | --- | --- | --- |

## Determinism

- Clock/timezone/locale:
- ID/randomness:
- Database isolation/reset:
- External protocol fixtures/fakes:
- No production secrets/PII:

## Architecture fitness

| Check ID | Invariant and scope | Automated check/command | Threshold | Baseline | Ratchet/exception policy | Owner | Cadence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Completion evidence

[Focused results, remaining untested risk, and escalation trigger.]
