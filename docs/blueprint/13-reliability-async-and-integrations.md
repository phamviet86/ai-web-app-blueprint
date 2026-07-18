---
guide_id: SKEL-RELIABILITY
title: Reliability, Async Work, and Integration Contracts
status: experimental
audience: human-and-ai
read_when:
  - Designing or changing external calls, retries, timeouts, idempotency, concurrency, jobs, queues, events, webhooks, or degraded behavior.
  - Deciding whether a workflow should remain synchronous or become asynchronous.
skip_when:
  - The change has no remote dependency, duplicate/concurrent execution risk, asynchronous work, or reliability behavior.
depends_on:
  - README.md
  - 04-dependency-contracts-and-sync-flows.md
owns:
  - deadlines, cancellation, and retry policy
  - idempotency and concurrency control
  - synchronous versus asynchronous selection
  - worker lifecycle, lease handoff, and partial-batch policy
  - scheduled-work overlap, misfire, and timezone semantics
  - event, outbox, inbox, ordering, and replay contracts
  - external-effect claim, finalize, and ambiguous-result policy
  - vendor and webhook reliability
  - degraded-mode behavior
---

# Reliability, async work, and integration contracts

> Core rule: distributed work may time out, arrive late, run concurrently, or execute more than once. State the delivery and consistency contract explicitly; do not imply exactly-once behavior from a successful happy path.

## Rule `SYNC-ASYNC-GATE-01`: select asynchronous work from product and failure needs

Keep work synchronous when it is bounded, fast enough for the caller, requires an immediate answer, and does not need durable retry or load smoothing.

Use asynchronous execution when one or more are true:

- duration can exceed the request/runtime deadline;
- work must survive client disconnect or process restart;
- spikes require buffering/backpressure;
- fan-out, scheduling, durable retry, or manual replay is required;
- an external dependency is too slow/unreliable for the interactive path;
- the user can act on an accepted/pending state instead of an immediate result.

Before choosing async, define acceptance semantics, user-visible state, completion/failure notification, cancellation, freshness, ordering, and operational ownership. Do not add a queue merely to hide an inefficient synchronous query or missing capacity plan.

## Rule `DEADLINE-CANCEL-01`: every remote operation has a bounded time budget

- Set an end-to-end deadline from caller/product expectations.
- Allocate smaller per-attempt timeouts to connect, read/write, and processing phases as supported.
- Leave budget for cleanup, fallback, or a bounded retry.
- Propagate cancellation/deadline through internal calls when the work is no longer useful.
- Stop or detach downstream work deliberately; do not assume client disconnect cancels it.
- Bound polls, streams, locks, leases, and long-running tasks.
- Record timeout outcomes separately from explicit rejection or business failure.

Timeout values come from observed latency, dependency limits, and user/job needs. Infinite defaults and arbitrary copied constants are not contracts.

## Rule `RETRY-BUDGET-01`: retry only transient failures and only within budget

A retry policy states:

- retryable error/status classes and non-retryable business/input/security failures;
- maximum attempts and total elapsed deadline;
- exponential or otherwise increasing delay with jitter;
- server-provided retry timing such as `Retry-After` when trustworthy;
- idempotency precondition;
- terminal outcome and operator/user feedback;
- metrics for attempts, exhaustion, latency, and downstream load.

Coordinate retries across layers. Do not let client, service, SDK, queue, and worker each multiply attempts unnoticed. Use a process/dependency retry budget where concurrent callers could create a retry storm.

Never retry permission denial, invalid input, deterministic conflict, or a non-idempotent side effect without a deduplication/compensation contract.

## Rule `IDEMPOTENCY-01`: duplicate intent produces one business effect

For retriable commands, define:

- idempotency key source and required format;
- namespace/scope, including tenant/subject and operation;
- canonical payload fingerprint;
- atomic reservation/unique constraint;
- in-progress, completed, failed, and expired behavior;
- stored response/reference returned to a duplicate;
- retention window and cleanup;
- handling of concurrent duplicates and late arrivals.

The same key with a different payload is a conflict, not a replay. A duplicate arriving while the first attempt is running must wait, return an explicit in-progress result, or use another documented behavior without executing the effect again.

Prefer natural business uniqueness when it expresses the invariant; use request idempotency when transport retries can repeat an otherwise valid command. “Check then insert” without atomic enforcement is not idempotent.

## Rule `CONCURRENCY-01`: protect the business invariant, not just the code path

For every contested mutation, name the invariant and select a mechanism:

- database unique/check/foreign-key constraint;
- conditional update or optimistic version/ETag;
- row/advisory/distributed lock with bounded ownership;
- transaction isolation with whole-transaction retry;
- single-writer/partition ownership;
- commutative operation or explicit merge policy.

Return a distinguishable conflict when another writer invalidates the caller's assumption. Re-read authorization and mutable state inside the protected operation where required.

Avoid unprotected read-check-write flows. Locks require timeout, lease/owner semantics, crash recovery, and a consistent acquisition order. Serialization/deadlock retries restart the complete transaction with bounded attempts.

## Rule `ASYNC-STATE-01`: durable work has an explicit state machine

Use a contract equivalent to:

```text
accepted/queued -> running -> succeeded
                    |  |
                    |  -> retrying -> failed/dead-lettered
                    -> cancel-requested -> cancelled or completed
```

Record stable job identity, type/version, subject/tenant, created/started/updated/completed time, attempt, lease/worker, progress/checkpoint when meaningful, terminal result/reference, and safe error code.

Workers use leases/heartbeats or queue settlement appropriate to the runtime. Define crash recovery, stale-work reclamation, cancellation race behavior, and how callers observe status. Do not keep the only job state in process memory.

## Rule `WORKER-LIFECYCLE-01`: shutdown preserves ownership and committed progress

A worker becomes ready only after it can safely claim work. On termination or drain it must, within a deadline shorter than the platform kill window:

1. stop polling/claiming and advertise not-ready;
2. propagate cancellation to safe interruptible I/O and stop starting new batch items;
3. finish, compensate, or durably checkpoint each started effect according to its contract;
4. acknowledge/settle only work whose required effect and idempotency/inbox state are durable;
5. release or let leases expire only after durable ownership/progress is visible to the next worker.

Lease renewal has a bounded interval, expiry, owner, and fencing/attempt token so an expired worker cannot commit after handoff. Handoff transfers a durable checkpoint or causes safe replay; it never transfers only in-memory state.

For batches, define atomicity per item versus whole batch, stable item identity, partial-success response/checkpoint, retry selection, and poison-item isolation. One failed item must not silently replay already committed non-idempotent items or acknowledge unprocessed items.

Evidence sends normal termination during claim, I/O, commit, and acknowledgement, then injects abrupt death and stale-lease takeover. It proves no lost required work, bounded duplicates, fenced late commits, correct partial-batch retry, and shutdown within the platform budget.

## Rule `SCHEDULED-WORK-01`: every schedule defines occurrence semantics

For cron or timer work, record:

- canonical timezone and calendar; if business-local time is required, define daylight-saving skipped/duplicated-time behavior;
- occurrence identity and idempotency scope, including behavior after retries, manual runs, and schedule edits;
- overlap policy: forbid/skip, serialize, replace, or allow bounded parallel runs;
- misfire policy after downtime: skip, run once, or bounded catch-up with a maximum age/count/rate;
- singleton ownership where required, using a lease plus fencing rather than process memory;
- start/deadline limits, cancellation, backpressure, observability, pause/resume, and operator-trigger authorization.

Test clock skew/boundaries, duplicate triggers, overlap, downtime recovery, DST when applicable, and a runner dying while holding ownership. Stop if scheduler delivery is treated as exactly once, a singleton has no fencing, or catch-up can create unbounded load or stale business effects.

## Rule `EVENT-ENVELOPE-01`: events are versioned, traceable facts

An event envelope should provide, as applicable:

```text
eventId, eventType, schemaVersion, occurredAt,
producer, subject/aggregate, tenant/partition,
correlationId, causationId, trace context, payload
```

- Event ID is globally unique enough for deduplication.
- Event type and schema version have compatibility rules.
- Ordering key matches the business aggregate only when ordering is required.
- Tenant/security context is trusted producer metadata, not consumer authorization proof.
- Payload is minimal, contains no secrets, and follows data classification/retention rules.
- Events describe completed facts; commands/requests use a distinct contract.

Consumers tolerate additive evolution and reject or quarantine incompatible events explicitly. Do not silently reinterpret an old event when business meaning changes.

## Rule `OUTBOX-INBOX-01`: bridge atomic boundaries explicitly

When one transaction must change local state and publish an event, write business state plus an outbox record atomically. A separate publisher delivers the outbox with retries and marks progress safely.

Consumers use an inbox/deduplication record or an equivalent atomic business constraint so repeated delivery does not repeat the effect.

Assume at-least-once delivery unless the complete platform contract proves something stronger. Even broker-side deduplication does not remove the need for idempotent consumers.

When a database write and vendor side effect cannot be atomic, use an explicit state machine plus one or more of:

- idempotent vendor request;
- durable intent before the call;
- reconciliation from the authoritative source;
- compensating action;
- operator-visible unresolved state.

Do not hold a database transaction open across remote network I/O merely to simulate atomicity.

## Rule `EXTERNAL-EFFECT-01`: claim, perform, and finalize external effects explicitly

When several workers or retries can issue the same non-transactional external mutation:

1. atomically claim eligible intent in a short local transaction, recording stable intent identity, attempt/fencing token, owner/lease, and prior terminal state;
2. commit the claim before external I/O, then call the dependency with a bounded deadline and provider idempotency key when supported;
3. classify the result as confirmed success, confirmed rejection, or ambiguous because the effect may have committed;
4. finalize in another short transaction only if the claim/fencing token is still current;
5. reconcile ambiguous or stale claims through an authoritative status/read path, webhook/event, bounded expiry policy, or operator-visible workflow.

Do not keep the claim transaction open across the network call. Do not automatically retry an ambiguous mutation unless an end-to-end idempotency contract proves the repeated request cannot duplicate the effect; a correlation ID alone is not that proof. Preserve ambiguous state instead of converting it to success, failure, or eligibility for ordinary retry.

## Rule `ORDER-DLQ-REPLAY-01`: ordering and replay are scoped operational contracts

- Require ordering only per business key/partition that needs it; global ordering is exceptional.
- Consumers handle duplicates and define late/out-of-order behavior.
- Bound attempts and move permanent/poison failures to a dead-letter or failed-work store with reason and context.
- Alert on age, backlog, retry exhaustion, and dead-letter growth.
- Define retention and ownership for queued/failed work.
- Provide an access-controlled replay tool/runbook with preview, filter, rate limit, audit, and idempotency protection.
- Preserve the original event and distinguish replay attempt metadata.

Replaying unvalidated historical payloads into current code is a migration and security decision, not a generic retry.

## Rule `DEGRADE-01`: dependency failure has a safe product mode

For every critical dependency, decide:

- fail closed, fail fast, serve stale data, disable a capability, queue intent, or use a proven fallback;
- maximum accepted staleness or pending duration;
- circuit-breaker/bulkhead/concurrency and resource limits when applicable;
- user/operator feedback and recovery trigger;
- reconciliation after the dependency returns;
- security and financial actions that must never use an unsafe fallback.

Keep a dependency failure matrix. A fallback that returns plausible but incorrect business data is worse than an explicit partial outage.

## Rule `VENDOR-WEBHOOK-01`: integrations separate protocol, policy, and delivery state

Outbound vendor calls require:

- documented capability/version and normalized application contract;
- deadline, retry, rate/quota, idempotency, and credential policy;
- handling for ambiguous timeout where the vendor may have committed;
- durable sync status/reconciliation when local correctness depends on remote state;
- safe capture of diagnostic metadata without raw secrets/sensitive payloads.

Inbound webhooks require:

- provider-supported authenticity and integrity: prefer raw-request signature verification with timestamp/replay and key rotation; when unavailable, combine the strongest supported controls such as mTLS, scoped tokens, network restrictions, strict validation, and reconciliation, then record the residual-risk exception;
- bounded parsing before expensive work;
- durable acceptance before acknowledging when processing must survive failure;
- event/provider ID deduplication;
- version handling and duplicate/out-of-order behavior;
- fast acknowledgement plus asynchronous processing when provider deadlines require it;
- reconciliation for missed or irrecoverable events.

An HTTP success acknowledges the documented acceptance stage; it must not claim completed business processing unless that work really finished.

## Acceptance evidence

- [ ] Each remote dependency has deadline, timeout, retryable errors, attempt/budget, quota, and degraded-mode policy.
- [ ] Retriable mutations pass same-key replay, conflicting-payload, concurrent-duplicate, and expired-key tests.
- [ ] Contested invariants have concurrent-writer tests proving the selected constraint/lock/version behavior.
- [ ] Sync versus async choice records product state, cancellation, notification, ownership, and failure semantics.
- [ ] Event envelope/schema compatibility and tenant/data classification rules are tested.
- [ ] Outbox/inbox or equivalent failure-injection tests cover crash before/after publish and duplicate delivery.
- [ ] External mutations prove atomic claim/fenced finalize, short transactions, crash recovery, and no automatic retry of ambiguous results.
- [ ] Workers recover stale leases/checkpoints and expose bounded backlog/retry/dead-letter evidence.
- [ ] Worker drain/death tests prove graceful shutdown, fenced handoff, durable acknowledgement, and correct partial-batch retry.
- [ ] Scheduled work has tested timezone, occurrence identity, overlap, misfire/catch-up, and singleton ownership semantics where applicable.
- [ ] Replay has preview, authorization, rate limit, audit, and idempotency evidence.
- [ ] Webhook tests cover failed authenticity/integrity checks, replay where the protocol supports it, duplicate, late/out-of-order event, provider retry, and processing failure.
- [ ] A dependency-failure test proves safe degraded behavior and eventual reconciliation.

## Stop conditions

Stop and redesign when a remote call has no deadline, retries are infinite/multiplied or include permanent failures, a non-idempotent or ambiguous external mutation is automatically retried without end-to-end deduplication, an invariant relies on read-check-write, async work has no durable identity/state/owner, worker shutdown can lose acknowledged work, lease handoff allows a stale commit, schedule overlap/misfire is undefined, exactly-once is claimed without end-to-end proof, DB state and external side effects have no claim/finalize or reconciliation path, ordered delivery is assumed globally, failed work cannot be inspected/replayed safely, webhook acknowledgement can lose required work, or fallback behavior widens access or corrupts financial/security state.
