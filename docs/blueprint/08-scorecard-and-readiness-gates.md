---
guide_id: SKEL-REVIEW
title: Blueprint Scorecard, Readiness Gates, and Evidence Policy
status: experimental
audience: human-and-ai
control_catalog_version: 1.0.0
read_when:
  - Scoring a repo, reviewing architecture, deciding production readiness, or selecting proportionate verification.
skip_when:
  - A narrow task already names exact deterministic checks and changes no architecture or risk contract.
depends_on:
  - README.md
owns:
  - versioned minimum control catalog
  - reproducible ten-dimension scoring
  - readiness gates by operating mode
  - evidence ladder and completion policy
  - blueprint-package structural audit
---

# Blueprint scorecard, readiness gates, and evidence policy

> Score the named revision/deployment from current evidence. Folder names, documentation claims, a sample app, and a successful build are not production-readiness proof.

## Rule `CONTROL-CATALOG-01`: score a versioned, stable control universe

Catalog version `1.0.0` consists of the 40 IDs below and the matching machine-readable [controls/core-controls.json](controls/core-controls.json). IDs are immutable and never reused. A wording change that alters the expected outcome or historic score follows [MATURITY.md](MATURITY.md) version policy; a retired ID remains a tombstone with replacement/migration guidance.

Every assessment includes all catalog IDs exactly once. A catalog row with `baseline: true` is applicable to every web-app assessment and cannot be `N/A`. A row with `baseline: false` is conditional: it may be `N/A` only when its `critical_when` trigger is absent and an accepted system-profile decision proves that absence. The conditional IDs in catalog `1.0.0` are `CTL-SEC-AUTHZ-01`, `CTL-SEC-NEGATIVE-01`, `CTL-DATA-MIGRATION-01`, `CTL-DATA-RECOVERY-01`, `CTL-REL-ASYNC-01`, `CTL-REL-INTEGRATION-01`, `CTL-REL-RECOVERY-01`, and `CTL-GOV-REFACTOR-01`; all other core IDs are baseline. Every dimension retains at least one baseline row, so a proportionate set of valid conditional exclusions cannot erase a dimension denominator.

The accepted system profile may add stricter local controls but cannot delete or weaken the core universe. Put each selected local control in the same assessment with a distinct `CTL-*` ID, `repo_owned: true`, dimension `1..10`, `source_rule`, and verifiable `expected_outcome`; it is scored in that dimension. Do not add an inapplicable local row. Map duplicate profile/rule obligations to the canonical core ID and record their sources.

### 1. Drivers, topology, and module architecture

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-ARCH-DRIVERS-01` | System drivers, risks, and measurable quality attributes govern architecture choices. |
| `CTL-ARCH-TOPOLOGY-01` | Repository and deployment topology are explicit, and every stronger boundary has evidence. |
| `CTL-ARCH-MODULES-01` | Modules align to business capabilities and expose stable public APIs. |
| `CTL-ARCH-DEPENDENCY-01` | Dependency direction, cycles, runtime separation, and public surfaces are mechanically checked. |

### 2. Public contracts and synchronous flows

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-CONTRACT-OWNERSHIP-01` | Commands, queries, DTOs, errors, transactions, and compatibility policies have owners. |
| `CTL-CONTRACT-BOUNDARY-01` | Cross-module flows use public contracts and preserve authoritative write ownership. |
| `CTL-CONTRACT-SHAPES-01` | Transport, application, domain, and adapter shapes are translated deliberately. |
| `CTL-CONTRACT-COMPOSITION-01` | Composition roots wire concrete adapters outside business policy. |

### 3. Security, identity, and privacy

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-SEC-THREAT-01` | Material trust boundaries have a current threat and abuse model. |
| `CTL-SEC-AUTHZ-01` | Authentication, session lifecycle, and default-deny resource authorization are server enforced. |
| `CTL-SEC-LIFECYCLE-01` | Identity, session, secret, and personal-data lifecycles have owners and end states. |
| `CTL-SEC-NEGATIVE-01` | Negative tests prove horizontal, vertical, tenant, and sensitive-data denial paths. |

### 4. Data lifecycle, migration, and recovery

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-DATA-INVENTORY-01` | Authoritative and sensitive data copies have classification, ownership, retention, and deletion rules. |
| `CTL-DATA-MIGRATION-01` | Schema and data changes use compatible phases and resumable observable backfills. |
| `CTL-DATA-INTEGRITY-01` | Integrity, environment/tenant isolation, query ownership, and migration order are explicit. |
| `CTL-DATA-RECOVERY-01` | Restore drills prove declared RPO and RTO across authoritative stores. |

### 5. Reliability and external consistency

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-REL-OPERATION-01` | Remote and concurrent operations have deadlines, cancellation, retry, idempotency, and invariant protection. |
| `CTL-REL-ASYNC-01` | Durable asynchronous work has identity, state, duplicate handling, and recovery semantics. |
| `CTL-REL-INTEGRATION-01` | Vendor and webhook protocols separate authenticity, delivery state, policy, and reconciliation. |
| `CTL-REL-RECOVERY-01` | Ordering, quarantine, replay, partial failure, and degraded modes have observable recovery paths. |

### 6. Runtime, UX, accessibility, and performance

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-UX-RUNTIME-01` | Server, browser, streaming, synchronous, and asynchronous paths are selected deliberately. |
| `CTL-UX-NATIVE-01` | Native platform capability precedes wrappers and preserves semantic accessibility. |
| `CTL-UX-BUDGET-01` | Critical journeys have representative accessibility and performance budgets. |
| `CTL-UX-CAPACITY-01` | Capacity, saturation, cold start, query, bundle, and cost claims use representative evidence. |

### 7. Testing and architecture fitness

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-TEST-RISK-01` | Test types map to failure modes at the lowest sufficient evidence layer. |
| `CTL-TEST-LAYERS-01` | Domain, application, repository, contract, UI, async, migration, and nonfunctional risks have owners. |
| `CTL-TEST-DATA-01` | Test data is isolated, valid, non-sensitive, and deterministic for time, IDs, locale, and concurrency. |
| `CTL-TEST-FITNESS-01` | Architecture invariants and brownfield baselines are automated and ratcheted. |

### 8. Developer experience and delivery supply chain

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-DELIVERY-ONBOARD-01` | Clone-to-running, check, build, reset, and evidence discovery are reproducible. |
| `CTL-DELIVERY-CI-01` | CI treats untrusted contributions safely and enforces deterministic gates. |
| `CTL-DELIVERY-ARTIFACT-01` | Reviewed artifacts are immutable or reproducibly rebuilt with distinct provenance. |
| `CTL-DELIVERY-RELEASE-01` | Deploy, migration, rollout, rollback/roll-forward, and compatibility windows are rehearsable. |

### 9. Observability and operations

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-OPS-TELEMETRY-01` | Logs, metrics, and traces correlate critical request and workflow paths safely. |
| `CTL-OPS-SLO-01` | Critical capabilities have owned SLIs, SLOs, alerts, health semantics, and runbooks. |
| `CTL-OPS-INCIDENT-01` | Incident detection, communication, mitigation, recovery, and follow-up are exercised. |
| `CTL-OPS-GOVERNANCE-01` | Telemetry cardinality, sampling, retention, access, privacy, drop behavior, and cost are governed. |

### 10. Evolution, governance, and human/AI usability

| Control ID | Minimum verifiable outcome |
| --- | --- |
| `CTL-GOV-DECISION-01` | Costly decisions and bounded exceptions have owners, evidence, expiry, and revisit triggers. |
| `CTL-GOV-CONTRACT-01` | Public contracts have compatibility, deprecation, consumer migration, and decommission paths. |
| `CTL-GOV-REFACTOR-01` | Refactors characterize behavior and migrate through an explicit measurable seam. |
| `CTL-GOV-GUIDANCE-01` | Repo guidance routes humans and agents to minimal current owners and verified evidence. |

## Rule `SCORE-EVIDENCE-01`: maturity is enforceability plus reproducible proof

Freeze assessment metadata before scoring using the machine fields `assessment_id`, `scorer_version`, `catalog_version`, `system_profile`, `operating_mode`, `source_revision`, `target`, `environment`, `observed_at`, `timezone`, and `freshness_policy`. `operating_mode` is `GREENFIELD`, `EVOLUTION`, `REFACTOR`, `RELEASE`, or `AUDIT`; the first four require the matching gate below, while `AUDIT` requires at least one explicitly selected gate.

| Score | Evidence meaning |
| --- | --- |
| `0.00` | Missing, contradictory, unknown applicability, or required control omitted |
| `0.25` | Ad hoc behavior known by individuals; not reliably repeatable |
| `0.50` | Documented/implemented and repeatable, but current proof or enforcement is incomplete |
| `0.75` | Implemented with current positive/negative evidence, partial automation, named operational owner |
| `1.00` | Enforced/measured continuously or at declared cadence; relevant failure/recovery paths are proven |

For every control record applicability (`yes`, `no`, `unknown`), criticality and rationale, expected outcome, exact evidence locator/result, observation/validity, owner, score, and `N/A` rationale/revisit. `unknown` is applicable and scores `0.00`. A conditional `no` also requires `decision_observed_at` and `applicability_evidence` using an `artifact:` or `review:` locator to the accepted profile decision. Missing/contradictory evidence is `0.00`; stale/invalidated evidence cannot exceed `0.50` until refreshed.

Machine evidence references use `kind:locator`. Allowed kinds are `command`, `test`, `artifact`, `measurement`, `drill`, `runtime`, `review`, and `planning`. `artifact`, `review`, and `planning` may support early scores, but `0.75` or `1.00` requires observed `command`, `test`, `measurement`, `drill`, or `runtime` references. Those strong references, passed-gate references, and conditional-N/A applicability references must resolve through a versioned evidence manifest whose digest is pinned by the assessment; [controls/README.md](controls/README.md#resolve-evidence-integrity-before-readiness) owns the record format. The resolver checks assessment identity, file/manifest hashes, dates, result, exact trusted-producer membership, and a named evidence acceptor. That proves integrity, not identity authentication: repo policy must protect the assessment and trusted CI/runtime/reviewer producers, and human release/risk acceptance remains mandatory.

Classify criticality before seeing the score. A control is critical when failure can violate a system-profile baseline, trust boundary, data integrity/recovery, money/entitlement, irreversible side effect, safety/contract obligation, or critical-journey SLO. Do not change criticality to improve an average.

For dimension `d`, with applicable core and selected repo-owned scores `s`:

```text
D[d] = sum(s[d,i]) / count(applicable[d])
TOTAL = D[1] + D[2] + ... + D[10]
```

Use unrounded decimal values for all comparisons. Display with decimal `ROUND_HALF_UP` to two places. No catalog control has hidden weight. A dimension with no applicable control is an error and scores `0.00`.

Canonical scorer:

```text
python3 docs/blueprint/scripts/score_readiness.py --init path/to/assessment.json
python3 docs/blueprint/scripts/score_readiness.py <assessment.json>
python3 docs/blueprint/scripts/score_readiness.py <assessment.json> --json
python3 docs/blueprint/scripts/score_readiness.py <assessment.json> --require ready
python3 docs/blueprint/scripts/score_readiness.py <assessment.json> --require 9.5-ready
python3 docs/blueprint/scripts/score_readiness.py <assessment.json> --expect not-ready
```

Run `--init` first: it creates, without overwriting, an input containing all 40 controls and four gates with unresolved applicability. Resolve every row before scoring; unresolved/null applicability deliberately fails. Use the artifact's stable ID as `assessment_id`. The generated N/A fields are not permission to exclude a baseline row.

The catalog defaults to `controls/core-controls.json`. Machine output includes assessment/scorer/catalog/profile/source/target/environment/time identity, assessment/catalog/evidence-manifest SHA-256 identity, resolved-evidence count, four-decimal dimension/total values, half-up display values, critical failures, failed gates, stale control/gate evidence, errors, and result. Store the output digest with [templates/readiness-assessment.md](templates/readiness-assessment.md). `--expect` pins a fixture's exact result; `--require` enforces a release threshold.

Result contract:

- `target`: profile/design intent only; no implementation score claim;
- `estimated`: incomplete, stale, or non-reproducible assessment; never release authority;
- `not-ready`: any validation error/applicable gate failure exists, any critical control is below `0.75`, or any dimension is below `0.75`;
- `ready`: no validation error, required evidence is manifest-resolved, applicable gates and critical minima pass, every dimension is at least `0.75`, and no high-risk unknown is hidden;
- `9.5-ready`: `ready` conditions pass, total `>= 9.50`, and no evidence row is stale.

## Versioned readiness gates

### Greenfield walking-skeleton gate

Gate ID: `GATE-GREENFIELD-01`.

- accepted system profile/topology and artifact registry exist;
- one real vertical slice crosses intended boundaries;
- import/config/error/test contracts are enforced;
- no speculative platform has replaced the slice.

### Feature/evolution gate

Gate ID: `GATE-EVOLUTION-01`.

- public/observable contract delta and affected callers are explicit;
- security/data/reliability/operations impacts are assessed;
- dependency delta is allowed or has active bounded exception;
- focused deterministic evidence covers changed failure modes.

### Refactor/cutover gate

Gate ID: `GATE-REFACTOR-01`.

- characterization baseline, seam, owner, metric, expiry, abort limit, and recovery exist;
- shadow/dual paths compare the same contract when used;
- callers/data migrate through monitored checkpoints;
- legacy paths, flags, adapters, and exceptions have deletion proof.

### Production release gate

Gate ID: `GATE-RELEASE-01`.

- compatible application/schema/event order and promoted artifact identity are proven;
- CI/security/test/build gates passed for that artifact;
- telemetry, SLO/alerts, owner, runbook, and deploy marker are ready;
- rollback/roll-forward, partial-side-effect correction, RPO/RTO, and residual-risk acceptance are explicit.

Each applicable gate is `pass` or `fail`, never averaged. Record exact evidence, owner, `observed_at`, and either `valid_until` or `invalidation_trigger`; a passed gate requires observed `command`, `test`, `measurement`, `drill`, or `runtime` evidence. A failed, missing, or stale gate caps the result at `not-ready`. Evidence cannot postdate the assessment, and validity cannot precede observation. A non-selected gate records `owner`, `n_a_rationale`, and `revisit_trigger`; at least one gate must remain applicable, and the named operating mode selects its required gate.

## Evidence ladder

Use the lowest layer that can falsify the changed contract; escalate for risks it cannot observe:

```text
static/schema -> unit/property -> application/repository integration
-> boundary/event/vendor contract -> component/accessibility interaction
-> critical-journey runtime -> representative performance/security
-> deploy/restore/failover/incident drill -> production SLI observation
```

Browser tests do not prove authorization, transaction, migration, or event determinism. Lint/build do not prove UI, runtime, security, performance, or recovery.

## Docs-only package verification

Run `python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .` and `PYTHONPATH=docs/blueprint python3 -m unittest discover -s docs/blueprint/scripts -p 'test_*.py'`. This proves the structural contract in rule `DOCS-VALIDATION-01`; it cannot prove semantic coverage or implementation readiness. Review package maturity/graduation separately with [MATURITY.md](MATURITY.md). No browser run is required for docs-only restructuring.

## Review report

```text
Mode/scope + profile/catalog/schema/source/deployment identity:
Evidence policy and exact evidence inspected:
Control rows, N/A/critical rationale, calculations, scorer input/output:
Applicable gate IDs and pass/fail evidence:
Risk-ordered findings and decisions/fixes:
Exceptions/transitions/residual risk and human acceptors:
Result, invalidation trigger, owners, next review:
```

## Stop conditions

Do not declare readiness from docs/sample code alone, average away a critical failure, hide an unknown as `N/A`, round before comparison, infer runtime controls from build success, or let an expired exception suppress a gate.
