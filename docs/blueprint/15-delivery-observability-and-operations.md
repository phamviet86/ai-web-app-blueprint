---
guide_id: SKEL-DELIVERY-OPS
title: Delivery, Observability, and Operations
status: experimental
audience: human-and-ai
read_when:
  - Designing environments, developer setup, CI trust, artifact promotion, or dependency governance.
  - Planning deployment, rollout, rollback, observability, incident response, or recovery.
skip_when:
  - The task changes no environment, artifact, release, runtime, dependency, or operational behavior.
depends_on:
  - README.md
owns:
  - environment and CI trust contracts
  - infrastructure change and drift governance
  - CI, artifact provenance, and supply-chain trust
  - first-party vulnerability response
  - release compatibility, rollout, rollback, and roll-forward
  - telemetry governance, SLO, incident command, and operational recovery coordination
---

# Delivery, observability, and operations

> A production blueprint is complete only when reviewed source becomes an identifiable, reproducible artifact that can be promoted, observed, recovered, and retired safely.

## Rule `ENV-CONTRACT-01`: environments differ by configuration, not hidden code paths

Define the purpose and isolation boundary of each environment:

| Environment | Primary purpose | Minimum boundary |
| --- | --- | --- |
| Local | Fast development and focused verification | Developer-owned data and replaceable dependencies |
| Test/CI | Deterministic automated evidence | Ephemeral or isolated resources per run/worker |
| Preview | Review one proposed artifact | Isolated namespace, sanitized data, no production authority |
| Staging | Production-like integration/release rehearsal | Controlled credentials and representative topology |
| Production | Real traffic and durable data | Least privilege, audit, monitoring, backup, recovery |

Not every repo needs preview and staging. Select only environments whose risk-reduction value exceeds their maintenance cost, then document how omitted release risks are covered.

Requirements:

- validate configuration against a typed/schema-owned contract at startup;
- distinguish secrets from safe public configuration;
- acquire secrets from an approved store and support rotation;
- record intentional environment differences; avoid `if production` business behavior;
- never copy personal or secret production data into lower environments without an approved sanitization process;
- give preview/test resources ownership, TTL, and cleanup;
- keep migrations and application versions compatible during rolling deployment.

Staging similarity is useful evidence, not proof that production will behave identically.

## Rule `INFRA-CHANGE-01`: infrastructure is reconstructable and reviewed

Keep infrastructure declarative and reproducible when the platform supports it. Review the planned change, apply with least privilege, protect state and credentials, run proportionate policy/security checks, record who changed what, detect drift, and define recovery before production use.

When a managed platform requires click-ops, preserve an equivalent configuration export or inventory, provider change/audit log, drift review, and tested rebuild runbook. Undocumented console state is not a recovery plan.

## Applying the developer onboarding contract

Apply `DEVEX-ONBOARD-01` from [06-greenfield-bootstrap-and-portability.md](06-greenfield-bootstrap-and-portability.md#rule-devex-onboard-01-one-documented-path-from-clone-to-evidence). This guide adds environment isolation, CI trust, artifact promotion, and production operations; it does not redefine local setup commands.

## Rule `CI-TRUST-01`: CI is an untrusted execution boundary

CI must be reproducible, least-privileged, and unable to convert unreviewed input into production authority.

- Pin external workflow/actions and dependency resolution.
- Separate validation/build jobs from jobs that can access secrets or deploy.
- Give fork/preview jobs no production credentials.
- Cache only content with validated keys; never cache secrets.
- Make skipped, quarantined, or flaky tests visible and owned.
- Require declared gates through protected branch/release policy.
- Retain enough logs and reports to reproduce a failure without leaking secrets.

A typical trust pipeline is:

```text
source integrity
  -> static + architecture checks
  -> risk-routed tests
  -> production build/package
  -> dependency/license/vulnerability checks
  -> immutable artifact + provenance
  -> isolated preview/smoke
  -> authorized promotion
```

## Rule `ARTIFACT-PROMOTION-01`: prefer build once; otherwise reproduce exactly

Use [SLSA 1.2](https://slsa.dev/spec/v1.2/) as an incremental vocabulary for source/build provenance when the supply-chain risk profile warrants it; do not claim a level without verifying its required controls.

- Create the release artifact from reviewed source in CI.
- Identify it by immutable digest/version and attach build provenance.
- Generate an SBOM or equivalent dependency inventory.
- Prefer promoting the same artifact across environments. If environment-specific compilation is unavoidable, build each artifact reproducibly from the same reviewed source/lock, give it its own digest/provenance/evidence, and prevent production-only source changes.
- Inject environment configuration at deploy/runtime without mutating the artifact.
- Link artifact, source revision, migrations, config version, test evidence, and deployment record.
- Verify signature/checksum or platform-equivalent integrity before promotion.

Generated assets and database migrations are part of release compatibility even when they are not inside the runtime image/package.

## Rule `SUPPLY-CHAIN-01`: dependencies have an owned lifecycle

Define:

- approved registries/sources and lockfile policy;
- automated update cadence and review ownership;
- vulnerability severity and remediation windows;
- license and provenance policy;
- handling for abandoned, compromised, or transitive packages;
- exception owner, risk, compensating control, and expiry.

An update bot is not governance by itself. Verify compatibility, release notes, tests, and artifact provenance before promotion.

## Rule `VULN-RESPONSE-01`: first-party vulnerabilities have a response lifecycle

Publish or internally designate a vulnerability intake/disclosure channel. Define triage ownership, severity criteria, remediation/communication targets, emergency patch and release authority, risk-exception approval/expiry, affected-user or stakeholder notification policy, and root-cause prevention.

Evidence must trace a representative finding from intake through impact assessment, contained exposure, verified patch or compensating control, deployment, notification decision, and owned preventive follow-up. Dependency vulnerability handling remains under `SUPPLY-CHAIN-01`.

## Rule `RELEASE-COMPAT-01`: old and new versions must coexist deliberately

Before deployment, state compatibility for:

- database schema and backfill state;
- APIs, events, queued jobs, and cached payloads;
- background workers and scheduled tasks;
- client/server or producer/consumer version skew;
- external integration retries and webhook replay.

Prefer additive/expand-contract changes. A deploy that requires every process and consumer to switch atomically is a high-risk exception with an explicit outage and recovery plan.

## Rule `ROLLOUT-GATE-01`: progressive exposure needs measurable gates

Use a feature flag, canary, cohort, region, tenant, dark launch, or another isolation mechanism when impact or uncertainty justifies it.

Every rollout declares:

- exposure unit and ordered stages;
- owner and decision window;
- correctness, latency, error, saturation, and business guardrails;
- minimum sample/time where meaningful;
- pause, rollback, and full-release thresholds;
- kill switch and flag/config expiry;
- behavior for in-flight work and queued messages.

Flags separate deployment from release; they do not replace tests, authorization, schema compatibility, or cleanup.

## Rule `RECOVERY-DECISION-01`: choose rollback or roll-forward from state

Rollback is safe only when the previous artifact can understand current schema, data, events, jobs, and external side effects. Otherwise prefer a prepared roll-forward repair.

Before release, classify:

- artifact rollback path;
- configuration/flag disable path;
- database compatibility and irreversible writes;
- reconciliation or compensating action;
- backup restore boundary and expected data loss;
- decision owner and trigger thresholds.

A backup is not an instant rollback. Restore procedures require tested tooling, access, duration, and explicit RPO/RTO consequences.

## Rule `OBS-CORRELATION-01`: signals must explain one request or workflow

Use structured logs, metrics, and traces with a shared request/correlation/workflow identifier where boundaries permit it.

- Logs explain discrete events and decisions with severity and safe context.
- Metrics quantify rate, errors, duration, saturation, queue depth, and business guardrails.
- Traces show causal latency across services, database, queues, and vendors.
- Audit events record security- or business-sensitive actions separately from debug logs.

Propagate correlation through HTTP/RPC, jobs, events, and vendor calls. Redact secrets and sensitive data at collection; do not depend on later deletion.

## Rule `OBS-GOVERNANCE-01`: telemetry has bounded value, volume, and access

For logs, metrics, and traces define:

- an attribute allowlist and cardinality budget; never use unbounded identity/request values as metric labels;
- head/tail/error sampling policy and which critical evidence must never be sampled away;
- retention, access, deletion, and sensitive-data classification;
- expected signal volume, cost ceiling, and review owner;
- exporter outage/backpressure/drop behavior that cannot take down the business path;
- deploy, configuration, feature-flag, and migration markers used during diagnosis.

Acceptance requires measured cardinality/volume/drop/cost evidence from a representative environment, not configuration claims alone.

## Rule `SLO-OPERATIONS-01`: alerts lead to an owned action

For critical capabilities define:

- service-level indicators and objectives;
- error-budget or equivalent reliability policy;
- symptom-based alerts with severity and routing;
- dashboard links and a short diagnostic runbook;
- liveness, readiness, and dependency health semantics;
- maintenance/degradation behavior and escalation owner.

Health endpoints must be cheap, bounded, and meaningful. Liveness should not restart a healthy process because an optional dependency is slow; readiness should stop new work when required dependencies cannot serve it safely.

Operational readiness requires exercised evidence: inject or identify a known SLI result, confirm the alert reaches the intended route/on-call, execute the safe runbook or kill-switch path, record date/outcome, and assign follow-up actions. Configuration screenshots alone remain documentation-level evidence.

## Rule `INCIDENT-RECOVERY-01`: recovery is practiced evidence

Maintain incident severity, command, communication, containment, recovery, and escalation procedures. Record a timeline and follow with a blameless review that creates owned, prioritized actions.

Practice incident command, failover coordination, key rotation, dependency outage, and queue replay on a declared cadence. Data backup/restore drills and achieved RPO/RTO are owned by `RECOVERY-DRILL-01` in [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md#rule-recovery-drill-01-rehearse-recovery-in-an-isolated-environment); this guide consumes that evidence for release and incident decisions.

## Acceptance evidence

Use [templates/slo-runbook.md](templates/slo-runbook.md) and [templates/release-recovery.md](templates/release-recovery.md) for applicable critical journeys/releases.

```text
Artifact digest/source/provenance/SBOM:
CI gates and trust boundaries:
Environment/config/secrets delta:
Schema/API/event compatibility:
Rollout stages, guardrails, and owner:
Rollback/roll-forward decision and trigger:
Dashboards/alerts/runbooks/health checks:
Telemetry cardinality/sampling/retention/access/cost evidence:
Data-recovery evidence and achieved RPO/RTO from guide 12:
First-party vulnerability and infrastructure-drift status:
Residual operational risk:
```

## Stop conditions

Stop a release or redesign the path when:

- production uses an ad hoc/unreviewed rebuild, or an environment-specific build lacks reproducibility, immutable identity, and provenance;
- untrusted CI code can access production secrets or deploy authority;
- schema/data/event changes make both rollback and roll-forward undefined;
- a flag/canary has no owner, measurement, kill path, or expiry;
- logs contain secrets or cannot correlate a critical workflow;
- an alert has no actionable threshold, owner, or runbook;
- recovery targets are claimed without restore/failover evidence;
- dependency or vulnerability exceptions are unbounded;
- first-party vulnerability intake/triage/patch ownership is absent;
- production infrastructure cannot be reconstructed or its drift cannot be detected/reviewed.
