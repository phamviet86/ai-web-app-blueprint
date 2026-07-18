---
template_id: SKEL-TPL-TEST-STRATEGY
template_version: 1.1.0
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

## Public contract evidence

| Boundary/consumer | Callable signature and serialized wire shape | `false` / `null` / `0` / empty / omitted/default cases | Compatibility/error/authorization cases | `EVID-*` / result |
| --- | --- | --- | --- | --- |

## Determinism

- Clock/timezone/locale:
- ID/randomness:
- Real identifier shapes and omitted/default semantics:
- Import/startup discovery without runtime-only secrets or eager data/network connections:
- Database isolation/reset:
- Data-access mode and in-process mutation guard, if applicable:
- External protocol fixtures/fakes:
- No production secrets/PII:

## Architecture fitness

| Check ID | Invariant and scope | Automated check/command | Positive/negative fixtures and excluded/parser cases | Threshold/baseline | Ratchet/exception | Owner/cadence |
| --- | --- | --- | --- | --- | --- | --- |

- Required command lanes / clean-room environment:
- Passed / failed / skipped / unparsed / `NOT_EXECUTED` accounting:

## Completion evidence

[Focused results, independent requested-outcome and pattern-conformance verdicts, remaining untested risk, and escalation trigger.]
