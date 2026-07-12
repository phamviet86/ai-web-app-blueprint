---
guide_id: REFAPP-OPERATIONS
title: Showcase Operations, Verification, and Extension
status: experimental
audience: human-and-ai
read_when:
  - Preparing a local/public showcase, completion audit, operational labs, deployment, or fork-to-product handoff.
skip_when:
  - Designing an unimplemented module with no demo or release decision.
depends_on:
  - README.md
  - ../08-scorecard-and-readiness-gates.md
  - ../14-testing-and-architecture-fitness.md
  - ../15-delivery-observability-and-operations.md
owns:
  - safe showcase mode and reset contract
  - showcase completion evidence and operational labs
  - reference-app fork-to-product handoff
  - preset demo-removal, promotion, deprecation, and upgrade policy
---

# Showcase operations, verification, and extension

> A public showcase is an operated environment, not a production-readiness certificate. It must be safe, resettable, observable and honest about simulated capabilities.

## Rule `REF-DEMO-SAFETY-01`: demo mode cannot create uncontrolled real effects

For a public showcase:

- require authentication for mutations and privileged routes;
- use synthetic data and clearly identified demo organizations/personas;
- isolate database, cache, storage, queue, email and provider namespaces;
- use a payment simulator, deterministic internal shipment dispatch, and email/storage local or sandbox adapters; add a carrier simulator only when the carrier capability is selected;
- cap users, uploads, rows, payloads, jobs, exports, retries and expensive queries;
- rate-limit public/auth edges without using limits as authorization;
- schedule deterministic reset or per-tenant TTL/cleanup with visible policy;
- prevent demo credentials/secrets from granting production authority;
- disable or explicitly label unsupported recovery/security features;
- retain enough safe audit/telemetry for investigation.

Local demo may use local adapters. Production starter mode replaces them through declared ports and re-runs compatibility/readiness gates.

## Deterministic personas and scenarios

Provide only personas needed by the selected tier. A `BASIC_WEB` app may need one operator and one denied/anonymous case; tenancy/full tiers add documented synthetic accounts for:

- organization owner;
- sales/catalog operator;
- inventory/fulfillment operator;
- billing operator;
- reporter/auditor or read-only member;
- disabled or stale member for deny evidence;
- system operator only in isolated/admin testing.

Organization personas receive one or more roles through the membership-role relation; the system operator uses a separate system-role assignment and has no implicit organization access.

Seed two organizations only when `CAP-TENANCY` is selected. Add low-stock conflict, duplicate submit, payment ambiguity, shipment exception, partial import, failed notification or stale projection only when the corresponding `CAP-*` is selected.

Never publish reusable privileged passwords without reset/rotation and environment guards.

## Operational labs

Demonstrate selected non-UI controls through reproducible labs rather than extra screens:

| Lab | Required proof |
| --- | --- |
| Duplicate and crash | Idempotent submit; worker crash around outbox/inbox; one business effect |
| Provider outage | Deadline/retry budget, safe degradation, ambiguous result and reconciliation |
| Import resume | Poison row, checkpoint, cancel/restart and deterministic row results |
| Tenant escape | Horizontal/vertical/stale-role direct-call denial and audit |
| Restore | Restore isolated backup/seed and verify order/stock/payment invariants plus achieved time/point |
| Evolution | Expand/backfill/compare/switch/contract a sample schema and remove transition residue |
| Refactor | Characterize one seam, switch implementation, prove no consumer, decommission old path |

`BASIC_WEB` requires only the labs implied by its access, migration and recovery risks. Async/provider/import/tenant labs become required only when their capability is selected. Labs keep evidence and final clean state; they do not leave intentional dual-write or legacy debt in the runtime.

## Verification portfolio

- domain/application tests for selected states, permissions, failures and ports;
- PostgreSQL integration tests for constraints, transactions, concurrency, migrations and projections;
- event/job/webhook/provider contract and duplicate/crash/replay tests when selected;
- shared component accessibility/interaction tests;
- selected critical browser journeys from the `COVERAGE-*` artifact, using browser coverage only where observable wiring needs it;
- architecture import/cycle/server-browser and public-surface fitness checks;
- representative query/load/bundle/web-vitals evidence;
- CI build, dependency/license/vulnerability and artifact/provenance checks;
- deployment, migration, alert/runbook and restore lab evidence.

Quarantined/flaky/skipped evidence is visible and owned; it cannot silently satisfy coverage.

## Rule `REF-SHOWCASE-READY-01`: declare showcase-ready from traceable evidence

Fill the completion section of [templates/reference-app-plan.md](templates/reference-app-plan.md). `showcase-ready` requires:

- all tier-required and additive `CAP-*` rows implemented and linked to current `VERIFIED` `EVID-*` results;
- every selected critical `JRN-*` passes at its required layers;
- deterministic seed/reset and public-demo safety controls execute;
- stack compatibility/build/migration/runtime spikes pass;
- access and isolation appropriate to the selected tier pass, including tenant denial only when selected;
- async/integration failure and recovery labs pass when selected;
- accessibility, performance and operational budgets have representative evidence;
- deploy identity, telemetry, owner and rollback/roll-forward path are recorded;
- no blocking TODO, unbounded exception or unknown critical control remains.

Showcase readiness does not imply the parent `/10` maturity score or production readiness. Run the parent [readiness assessment](../templates/readiness-assessment.md) against the actual deployment for that claim.

## Deployment handoff

Record:

- source revision, lockfile, artifact identity/provenance and configuration version;
- web/worker/migration/cron topology, regions and service ownership;
- secret classes, rotation and sandbox/production separation;
- database migration order, compatibility and backup/restore evidence;
- queue/storage/email/provider quotas and degraded behavior;
- SLI/SLO, dashboards, alerts, on-call/escalation and runbooks;
- demo reset/TTL and cleanup owner;
- residual risks and next review trigger.

## Rule `REF-PRESET-EVOLVE-01`: a preset demo proves contracts and remains removable

An `AUTHOR_PRESET` walking slice exists to prove the exact stack and inter-layer contracts. Keep its domain small, deterministic and isolated; mark sample routes, data, identities and providers; document how an instantiated app replaces or removes them without deleting shared/platform contracts still in use.

Promote a preset maturity level only when its current exact version passes the clean-room gates in guide `08`. Record:

- manifest, template, guide and evidence revision/digests;
- supported, conditional and unsupported capabilities;
- breaking/compatible changes and application upgrade steps;
- dependency/security support window and next review trigger;
- deprecation/removal path for preset code, migrations, secrets and demo artifacts.

`INSTANTIATE_PRESET` creates a user-owned application variant. App-local changes do not mutate the upstream preset automatically. To adopt a newer preset, compare the installed preset lock with the target version, create bounded upgrade slices, preserve app decisions, migrate data/config compatibly and rerun every affected flow.

Preset verification and a safe showcase do not establish application production readiness. Production claims require the instantiated app's own deployment, operations, recovery and parent scorecard evidence.

## Rule `REF-EXTEND-01`: fork by preserving contracts, not sample vocabulary

When turning the reference app into a product:

1. write the real system/risk profile and capability map;
2. keep, rename, replace or remove FulfillOps modules by explicit ownership mapping;
3. remove demo users, reset endpoints, simulators, sample flags/content and sandbox credentials;
4. replace selected providers behind existing ports and re-run contract/failure tests;
5. migrate seed-only data/schema through reviewed additive migrations;
6. re-evaluate privacy, assurance, tenancy, retention, SLO, capacity and recovery for real users;
7. update routes/copy/design without moving business policy into presentation;
8. decommission unused sample modules, tables, jobs, events, secrets, telemetry and docs completely;
9. run the parent readiness scorecard with real operational evidence.

Do not keep a sample capability merely because it demonstrates the blueprint. A smaller real product with explicit N/A decisions is better than unused production code.

## Acceptance report

```text
Environment and source/artifact identity:
Selected tier/capability and journey coverage:
Seed/reset/demo-safety evidence:
Architecture/test/build/migration evidence:
Failure/replay/reconciliation labs:
Accessibility/performance evidence:
Telemetry/SLO/alert/runbook evidence:
Restore/release/recovery evidence:
Showcase-ready decision:
Production-readiness assessment link or explicit not-assessed:
Fork-to-product removals/replacements:
Residual risk, owner and next trigger:
```

## Stop conditions

Stop publication when preset sample code has no removal path, upgrade steps would overwrite local application decisions, demo data/credentials can affect production, reset is destructive outside an isolated namespace, simulated providers are presented as real, critical journeys lack evidence, failures cannot be inspected/recovered, telemetry exposes sensitive data, or “production-ready” is inferred from screenshots, build success or showcase coverage.
