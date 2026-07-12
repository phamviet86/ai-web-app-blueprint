---
guide_id: SKEL-TEST-FITNESS
title: Testing Strategy and Architecture Fitness
status: experimental
audience: human-and-ai
read_when:
  - Designing testability, selecting evidence for a change, or creating deterministic test data.
  - Defining automated architecture invariants, quality thresholds, or a ratchet for a legacy repo.
skip_when:
  - The task is docs-only and its structural checks are already fully routed by the review guide.
depends_on:
  - README.md
owns:
  - risk-based test portfolio
  - test lanes, flaky-test budget, and quarantine policy
  - deterministic test data and characterization-test policy
  - conditional browser/assistive-technology and generative testing
  - architecture fitness registry and ratchet
  - testing acceptance evidence
---

# Testing strategy and architecture fitness

> Test the smallest observable contract that can fail, then add broader evidence only for risks the smaller test cannot cover.

## Rule `TEST-PORTFOLIO-01`: choose tests by risk and failure mode

Do not apply one universal pyramid or require every layer for every change. Classify:

- user/business impact if wrong;
- security, privacy, money, or irreversible data risk;
- blast radius and number of consumers;
- implementation uncertainty and novelty;
- concurrency, timing, integration, or environment sensitivity;
- reversibility and rollout isolation.

Select a portfolio that proves the affected contracts:

| Test type | Best evidence for | Avoid using it as |
| --- | --- | --- |
| Domain/unit | Pure policy, calculations, state transitions, validation | Proof of persistence or wiring |
| Application/service | Use-case orchestration, permissions, transaction decisions, error mapping | A mock of every internal method |
| Repository/integration | Real query shape, constraints, transactions, serialization, migration compatibility | A substitute for domain behavior tests |
| Boundary/contract | HTTP/RPC/event/job schemas, compatibility, auth, idempotency, vendor protocol | Full end-user workflow proof |
| Component/interaction | Rendering states, accessibility semantics, input and event behavior | Server authorization or database proof |
| End-to-end | A few critical journeys and deployed-system wiring | Exhaustive field/operator combinations |
| Non-functional | Performance, load, resilience, security, accessibility, recovery | A default gate without a risk or threshold |
| Architecture fitness | Dependency direction, cycles, public surfaces, runtime isolation, budgets | Proof that product behavior is correct |

Prefer deterministic domain, application, repository, and contract evidence before browser automation. Use E2E only when crossing real boundaries is itself the risk.

## Rule `TEST-LANES-01`: feedback lanes have a purpose, budget, and trust level

Define repository-specific lanes rather than one ever-growing gate:

| Lane | Purpose | Typical evidence |
| --- | --- | --- |
| Local/pre-commit | Fast changed-scope feedback | format, static/fitness checks, focused deterministic tests |
| Pull request | Required merge confidence | impacted contract/integration tests, production build, security/supply-chain checks |
| Post-merge/nightly | Broader or slower detection | full matrix, E2E, resilience, compatibility, generative/long-running suites |
| Release/deploy | Artifact and live-path confidence | immutable-artifact checks, migration compatibility, smoke/canary and risk-routed non-functional gates |

For each lane record trigger, maximum useful duration, isolation/resources, retry policy, required versus advisory status, artifact/report retention, and failure owner. A slow test may move lanes only when the merge/release risk remains covered by cheaper evidence or an explicit gate.

Track flaky tests as a count and/or failure-rate budget. Quarantine requires a visible original failure, issue/owner, reason, bounded scope, expiry, and replacement evidence for any critical contract. Reruns may diagnose nondeterminism but must not erase the first result. Exceeding the budget blocks new unowned quarantine and triggers a reliability reduction plan; security, migration, money, tenant-isolation, and recovery gates cannot be silently waived as flaky.

## Rule `TEST-SEAM-01`: design controllable boundaries

Code that depends on time, randomness, identifiers, environment, files, network, queues, or vendor SDKs must expose a controllable boundary when deterministic behavior matters.

- Keep domain policy pure where practical.
- Pass clocks, ID generators, clients, and gateways through a stable application/infrastructure seam.
- Mock external protocols or unsafe side effects, not every internal collaborator.
- Use a real database for repository semantics that an in-memory substitute cannot reproduce.
- Assert public outputs, committed effects, and emitted contracts instead of private call order unless ordering is the behavior.

Do not distort production design solely to satisfy a mocking framework. Testability should reinforce ownership and explicit dependencies.

## Rule `TEST-DATA-01`: deterministic data has explicit ownership

Use distinct tools for distinct jobs:

- **Factory:** produces a minimal valid domain record with explicit overrides.
- **Builder:** expresses meaningful state transitions or multi-record scenarios.
- **Fixture:** stores an immutable external protocol sample, golden file, or compatibility case.
- **Seed:** creates human-usable local/demo data; it is not the normal test-data API.

Requirements:

- control clock, timezone, locale, randomness, and generated identifiers;
- isolate tests by transaction, schema, database, tenant, or unique namespace;
- make parallel execution safe and cleanup idempotent;
- encode valid defaults centrally without hiding scenario-critical values;
- keep secrets, personal data, and unsanitized production snapshots out of tests;
- version protocol fixtures when external schemas change;
- make large datasets intentional and generated from a declared cardinality profile.

A test must not depend on run order, an existing developer database, or ambient machine state.

## Rule `TEST-MATRIX-GENERATIVE-01`: expensive matrices and generative tests are risk-selected

For browser UI, derive a small supported matrix from product support policy and representative usage: rendering engine/browser, viewport/input mode, operating-system differences that affect behavior, and assistive technology for critical accessible journeys. Test the highest-risk workflow on every supported class; use pairwise/targeted coverage for the rest. Record versions, cadence, owner, and evidence; a single headless browser plus an automated accessibility scan is not cross-browser or assistive-technology proof.

Add property-based tests or fuzzing when the input space or invariant makes examples insufficient—for parsers/decoders, query DSLs, validators, serializers, state machines, numerical rules, or security-sensitive bounded input. Declare generators/corpus, invariant/oracle, resource limits, deterministic seed/replay, shrink/minimization, and retention of regressions. Run unsafe fuzz targets only in isolated environments. Do not require generative tests for simple mappings with a finite example table, and do not accept “no crash” when semantic correctness is the risk.

## Rule `TEST-CHARACTERIZATION-01`: characterize before risky replacement

A characterization test records observable legacy behavior at a stable seam before internals change. Use it when behavior is under-documented, coupled, or unsafe to infer.

Capture only behavior consumers can observe:

- public response/status/error semantics;
- persisted state and transactional effects;
- emitted event/job/vendor contract;
- permission and ownership outcomes;
- relevant ordering, rounding, time, or concurrency behavior.

Record known nondeterminism and normalize only irrelevant values. A characterization test may preserve an undesirable behavior temporarily, but the target decision must classify it as **preserve**, **fix deliberately**, or **retire**. Replace temporary characterizations with target contract tests after migration; do not fossilize accidental internals.

## Rule `FITNESS-REGISTRY-01`: invariants must be executable where feasible

Maintain a small architecture fitness registry. Each entry declares:

```text
id | invariant | scope | automated check | threshold | owner | cadence | exception policy
```

Useful fitness functions include:

- forbidden imports and dependency cycles;
- feature/public-surface leakage;
- server-only code or secrets entering client artifacts;
- unguarded callable boundaries;
- query complexity and page-size limits;
- schema/API/event compatibility;
- bundle, latency, error-rate, or query-count budgets;
- critical contract suites and migration checks;
- broken guide links, duplicate rule ownership, and stale generated artifacts.

Automate mechanical invariants in lint, tests, build analysis, schema comparison, or repository scripts. A prose rule without an enforceable check must name the manual evidence and review owner.

## Rule `FITNESS-RATCHET-01`: improve without blocking all progress

For a brownfield baseline:

1. measure existing violations without silently waiving them;
2. prevent new violations in changed scope;
3. set a finite reduction target for the current slice;
4. record any exception with owner, reason, scope, and expiry;
5. tighten the threshold only after the new baseline is reproducible.

Do not use a global coverage percentage as the sole quality target. Prefer contract coverage, mutation/state-transition cases, risk paths, and non-regression of architecture violations.

## AI execution procedure

Use [templates/test-strategy.md](templates/test-strategy.md) when the scope has several material failure modes; do not require it for a trivial change.

1. State the changed observable contract and risk class.
2. Map each material failure mode to the cheapest sufficient test type.
3. Identify required seams and deterministic data before implementation.
4. Add characterization evidence first when current behavior is uncertain.
5. Run focused tests after a coherent batch; escalate to integration, E2E, or non-functional evidence only when required.
6. Run applicable architecture fitness functions and compare with the recorded baseline.
7. Report untested risks explicitly; never translate “build passed” into “behavior verified.”

## Acceptance evidence

Record:

```text
Risk and observable contracts:
Selected test portfolio and why:
Deterministic data/isolation:
Characterization baseline, if any:
Fitness functions and before/after counts:
Lane budgets, flaky count/rate, quarantines and expiry:
Supported browser/AT matrix and conditional generative evidence:
Commands/environment/results:
Unverified behavior and residual risk:
```

Acceptance requires passing evidence for every material failure mode, no unexplained fitness regression, and reproducible commands/data.

## Stop conditions

Stop and redesign the evidence plan when:

- tests assert mostly private implementation details;
- a repository test uses a substitute that cannot reproduce required database behavior;
- test data depends on production records, secrets, order, or ambient state;
- a risky replacement starts without an observable baseline;
- E2E/browser loops are compensating for missing deterministic lower-level tests;
- a required lane has no duration/trust owner, reruns hide its original failure, or flaky quarantine has no expiry/replacement evidence;
- browser/AT support is claimed outside the tested matrix, or fuzz/property results cannot replay from a retained seed/case;
- a fitness threshold is weakened or an exception is made without owner and expiry;
- a quality claim has no command, dataset/environment, threshold, or result.
