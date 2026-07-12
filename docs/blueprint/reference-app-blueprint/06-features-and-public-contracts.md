---
guide_id: REFAPP-FEATURES
title: Reference Features and Public Contracts
status: experimental
audience: human-and-ai
read_when:
  - Planning modules, use cases, public APIs, events, adapters, presentation, or cross-module flows.
skip_when:
  - Selecting the stack or implementing an already-approved contract.
depends_on:
  - README.md
  - ../02-module-anatomy-and-public-contracts.md
  - ../04-dependency-contracts-and-sync-flows.md
  - ../05-semantic-pattern-selection.md
owns:
  - tier-selected FulfillOps module and public-contract inventory
  - reference cross-module workflow choreography
  - feature-level showcase acceptance map
  - preset feature-layer path and inter-layer compatibility contract
---

# Reference features and public contracts

> Modules follow business ownership. Screens, database tables and provider SDKs do not define module boundaries.

The sections below are the `FULL_SHOWCASE` catalog. Implement only modules mapped by the accepted `COVERAGE-*` and omit every unselected module, event, adapter, route and table. Smaller tiers may use one module section or an equivalent custom-domain `FEATURE-*` artifact.

## Rule `REF-FEATURE-SLICE-01`: every module exposes intent, not internals

Logical module shape:

```text
modules/<module>/
├── public/          stable commands, queries, DTOs and events
├── application/     use cases, authorization orchestration and owned ports
├── domain/          only real invariants/state transitions
├── adapters/        database, vendor, event and file implementations
├── presentation/    server/browser/worker/CLI entry adapters
└── compose           module-local factory used by executable roots
```

Simple modules may omit `domain/` or combine files. Other modules import only the public surface; they never import repositories, ORM schema, provider clients or mutable entities.

## Rule `REF-FEATURE-LAYER-COMPAT-01`: a preset maps roles into one closed slice

A web preset maps the portable roles above to concrete paths. A recommended Next-style mapping is:

```text
src/features/<feature>/
├── public/              commands, queries, DTOs, result/error and event contracts
├── server/
│   ├── schema/          untrusted input/output validation and normalization
│   ├── action/          trusted context, auth gate and transport/framework mapping
│   ├── service/         use-case orchestration and transaction boundary
│   └── repository/      feature-owned query policy and persistence adapter
├── client/              query keys, remote hooks and feature UI configuration
├── views/               feature presentation composed from shared mechanics
└── optional roles       domain, policies, adapters, events and jobs when justified
```

Names may differ by preset, but [feature-plan](templates/feature-plan.md) maps every role. Do not generate empty folders: a simple feature may combine files while preserving ownership and dependency direction.

| Role | Owns | Must not own |
| --- | --- | --- |
| Action/entrypoint | Parse, trusted subject/context, call one use case, map stable result | Business transaction, ORM query or UI state |
| Service/application | Authorization orchestration, invariant/use-case flow and transaction/port coordination | Framework request/response or component behavior |
| Repository | Feature field/operator/join allowlist, mandatory access scope, ORM translation and DTO mapping | Another feature's writes or public ORM types |
| Client hook/config | Canonical request/query key, remote lifecycle, columns/fields/actions and invalidation policy | Trusted authorization or hidden database names |
| View | Compose shared surfaces with resolved feature contracts | Direct ORM/provider calls or business transaction |
| App route | Mount layout/providers and feature entrypoint | Feature policy, repository access or duplicated service logic |

Every verified preset includes at least one closed create/read/list-or-detail slice. If it claims dynamic data surfaces, the slice also proves applicable search/filter/sort/pagination; a verified calendar adds range/timezone/view behavior. If it claims edit/mutation, prove normalized input, server field error, conflict/denial, success invalidation and focus/feedback behavior.

The flow is surface/input -> feature client contract -> action/query -> service -> repository/adapter -> stable result -> feature client/view. Each handoff is versioned or mechanically typed/validated, and the preset's AI guides route changes to the role that owns the contract rather than the file nearest the symptom.

## Workspaces

**Purpose:** tenant profile, membership, invitation and current-subject capabilities.

- Commands: create/update/suspend organization; invite/revoke/accept; add/remove organization role; change member status.
- Queries: current organizations; member list; invitation; resolved capability set.
- Events: `OrganizationCreatedV1`, `MemberInvitedV1`, `MembershipChangedV1`.
- Invariants: one membership may hold bounded organization roles; last owner cannot be removed; system role never implies organization access; expired/revoked invite cannot be accepted.
- Presentation: onboarding, organization switcher, members/invitations/settings.
- Evidence: owner/operator/viewer allow/deny matrix, stale membership, disabled organization and direct-call tests.

Auth-provider session/account mechanics remain platform-owned.

## CRM

**Purpose:** customer master data, addresses and privacy requests.

- Commands: create/update/archive/anonymize customer; manage address; open/complete privacy request.
- Queries: bounded customer list/search; detail; order-safe customer snapshot.
- Events: `CustomerCreatedV1`, `CustomerAnonymizedV1`, `PrivacyRequestCompletedV1`.
- Pattern: simple CRUD plus conditional privacy lifecycle.
- Evidence: tenant-scoped uniqueness/search, field-level access, export/anonymization and retained-financial-record behavior.

## Catalog

**Purpose:** sellable product definitions, price and media.

- Commands: create/update/archive product; attach/reorder/remove media.
- Queries: bounded catalog list; order snapshot by IDs; product detail.
- Events: `ProductChangedV1`, `ProductArchivedV1`.
- Pattern: CRUD, file integration and batch-import target.
- Evidence: SKU uniqueness, price constraints, signed upload ownership, scan/quarantine and snapshot stability.

Catalog price is current source data. Orders own the accepted price/name/SKU snapshot.

## Inventory

**Purpose:** warehouse stock authority, movements, availability and reservations.

- Commands: adjust stock; reserve/release/consume reservation; expire reservation.
- Queries: availability by bounded product/warehouse set; reservation detail; stock ledger.
- Events: `StockReservedV1`, `StockReservationRejectedV1`, `StockReleasedV1`, `StockConsumedV1`, `StockConsumptionRejectedV1`.
- Invariants: reserved never negative/exceeds on-hand; source effect applies once; concurrent reservations cannot oversell.
- Evidence: database constraints, concurrent-writer tests, duplicate event, stale version and transaction rollback.

## Orders

**Purpose:** order intent, snapshots, totals and lifecycle coordination.

- Commands: create/edit draft; submit idempotently; apply allocation/payment/shipment result; cancel under allowed state.
- Queries: detail; bounded list/search; order timeline.
- Events: `OrderSubmittedV1`, `OrderCancelledV1`, `OrderCompletedV1`.
- Invariants: positive quantities, validated totals, immutable accepted snapshots, legal state transitions and optimistic edit conflict.
- Evidence: same-key replay, changed-payload conflict, outbox atomicity and state-machine tests.

Draft creation may synchronously call CRM/Catalog public queries. It does not import their repositories.

## Billing

**Purpose:** invoice, invoice-scoped payment intent, atomic captured-balance application and provider reconciliation.

- Commands: issue invoice; create invoice-scoped payment intent; apply authenticated provider event; reverse payment; run reconciliation/repair.
- Queries: invoice/payment detail; receivables; safe provider status.
- Events: `InvoiceIssuedV1`; `PaymentCapturedV1` for each applied capture; `InvoicePaidV1` only when balance reaches zero; `PaymentFailedV1` only for a terminal intent failure, not a transient attempt.
- Ports: `PaymentGateway`, `PaymentReconciliationSource`.
- Invariants: each intent belongs to one invoice; captured amount cannot exceed intent or outstanding invoice amount; provider event applies once; only zero invoice balance emits `InvoicePaidV1`; ambiguous timeout never becomes assumed success.
- Evidence: sandbox provider, signed duplicate/out-of-order webhook, timeout/retry/reconciliation and atomic balance tests.

## Fulfillment

**Purpose:** shipment/package/tracking lifecycle and optional carrier reconciliation.

- Commands: create shipment; add items; request dispatch; apply stock-consumed/rejected result; mark dispatched/delivered/failed; optionally apply/reconcile carrier event.
- Queries: shipment detail/list; ready-to-ship orders; tracking view.
- Events: `ShipmentDispatchRequestedV1`, `ShipmentDispatchedV1`, `ShipmentDeliveredV1`, `ShipmentExceptionV1`.
- Port: add `CarrierGateway` only when `CAP-CARRIER-PROVIDER` is selected; the baseline uses deterministic internal/manual dispatch without a provider protocol.
- Invariants: shipment quantity is positive and covers the reserved order in the one-shipment reference baseline; dispatch remains pending until Inventory confirms `StockConsumedV1`; only eligible orders dispatch; transitions are guarded. A partial/multi-shipment extension must replace the completion rule explicitly.
- Evidence: stock-consumption rejection, duplicate transition and local simulator; add carrier duplicate/out-of-order/outage/reconciliation only when `CAP-CARRIER-PROVIDER` is selected.

## Notifications

**Purpose:** in-app notification and external delivery intent/state.

- Commands: create delivery intent from business event; mark read; retry/cancel authorized delivery.
- Queries: current-subject notifications; delivery status for operators.
- Port: `NotificationSender` implemented by email or another selected channel.
- Events: `NotificationDeliveryFailedV1`, `NotificationDeliveredV1` when other policy needs them.
- Evidence: inbox dedupe, bounded retry, dead-letter inspection, safe template data and sandbox recipient policy.

## Files and Data Exchange

**Purpose:** stored-file metadata plus durable import/export workflows.

- Commands: create/finalize/quarantine/delete stored-file metadata; upload/validate/preview/start/pause/resume/cancel catalog or inventory import; request order export.
- Queries: job progress, row errors, preview and result download authorization.
- Public target calls: Catalog/Inventory commands in controlled batches; no raw table writes.
- Invariants: stable checkpoint/order, deterministic row hash, idempotent retry and bounded partial-result semantics.
- Evidence: poison row, crash/restart, cancellation, duplicate row and reconciliation.

## Insights

**Purpose:** read-only operational projections.

- `CAP-READMODEL` query: order-operations projection. Inventory availability remains an authoritative Inventory query; aging/daily projections are extensions selected by real reporting needs.
- Contract: bounded filters/page/order, `as_of`/freshness metadata and tenant-scoped cache identity.
- Presentation: dashboard cards, charts, report table and safe export link.
- Evidence: source/projection comparison, rebuild, stale indicator, representative query plan/cardinality.

Insights never becomes a write authority.

## Governance

**Purpose:** system-role authority, searchable security audit, operational evidence and privileged inspection.

- Queries: audit search/detail, failed-work references and deployment/config markers.
- Commands: grant/revoke system role with reauthentication and audit; otherwise only narrowly authorized operational actions delegated to the owning module, such as preview/replay request. Governance records but does not own business repair.
- Invariants: system role never implies organization access; grant/revoke is explicit, bounded and independently audited.
- Evidence: access-controlled append-only audit, correlation, redaction and privileged-action reauthentication.

## `FULL_SHOWCASE` order-to-fulfillment event registry

| Event | Producer | Required consumers/purpose |
| --- | --- | --- |
| `OrderSubmittedV1` | Orders | Inventory reserves; Notifications/Insights may project |
| `OrderCancelledV1` | Orders | Inventory releases; Billing closes open intents; Fulfillment cancels only an un-dispatched shipment |
| `StockReservedV1` | Inventory | Orders enters payment pending; Billing issues invoice |
| `StockReservationRejectedV1` | Inventory | Orders enters on hold; Notifications informs operator |
| `StockReleasedV1` | Inventory | Orders enters on hold unless already terminal/cancelled; Billing closes open intents and reconciles any late capture |
| `InvoiceIssuedV1` | Billing | Orders records invoice availability; Notifications may inform the customer/operator |
| `PaymentCapturedV1` | Billing | Billing records the partial/full capture; Notifications/Insights may project without advancing shipment eligibility |
| `InvoicePaidV1` | Billing | Full invoice balance reached zero; Orders enters ready-to-ship and Fulfillment may create shipment |
| `PaymentFailedV1` | Billing | Orders records payment failure/hold; Notifications informs operator |
| `ShipmentDispatchRequestedV1` | Fulfillment | Inventory consumes the named reservation |
| `StockConsumedV1` | Inventory | Fulfillment may perform carrier dispatch |
| `StockConsumptionRejectedV1` | Inventory | Fulfillment stays exception/pending; Orders does not advance |
| `ShipmentDispatchedV1` | Fulfillment | Orders enters shipped; Notifications/Insights project |
| `ShipmentExceptionV1` | Fulfillment | Orders records shipment exception without false completion; Notifications informs operator |
| `ShipmentDeliveredV1` | Fulfillment | The baseline full shipment was delivered; Orders enters completed and emits `OrderCompletedV1` |
| `OrderCompletedV1` | Orders | Notifications/Insights project final completion |

Schemas include stable event ID, version, tenant, aggregate/version, correlation/causation, occurred time and classified payload. Additive compatibility and consumer ownership are explicit.

## `FULL_SHOWCASE` cross-module order-to-fulfillment flow

```text
Orders submit transaction
  -> order + OrderSubmittedV1 outbox
  -> Inventory inbox reserves atomically
  -> StockReservedV1 or StockReservationRejectedV1
  -> Orders consumes allocation result and owns order-state transition
  -> Billing consumes StockReservedV1, issues invoice and records payment intent
  -> authenticated capture -> PaymentCapturedV1
  -> invoice balance reaches zero -> InvoicePaidV1
  -> Orders enters READY_TO_SHIP; Fulfillment creates DISPATCH_PENDING shipment
  -> ShipmentDispatchRequestedV1
  -> Inventory atomically consumes reservation -> StockConsumedV1/rejected
  -> Fulfillment dispatches only after StockConsumedV1 -> ShipmentDispatchedV1
  -> Orders enters SHIPPED
  -> ShipmentDeliveredV1 -> Orders enters COMPLETED and emits OrderCompletedV1

Notifications consumes selected facts independently.
Insights projects facts with declared freshness.
```

Every consumer assumes at-least-once delivery. Ordering is scoped by aggregate/partition key; failures remain inspectable and replayable.

Cancellation/expiry is a closed alternate flow: `OrderCancelledV1` makes Inventory release the still-active reservation, Billing close pending intents and Fulfillment cancel only pre-dispatch work. Inventory emits `StockReleasedV1` for explicit release or expiry; Orders moves to `ON_HOLD` unless it is already cancelled/terminal. A late provider capture remains a Billing reconciliation/refund case and never reopens shipment eligibility implicitly.

## Feature-plan requirements

For each selected module fill one [templates/feature-plan.md](templates/feature-plan.md) `FEATURE-*` artifact with:

- module/data owner and archetype;
- public commands/queries/DTOs/events/errors;
- authorization/resource/tenant policy;
- transaction, idempotency and concurrency boundary;
- application-owned ports and concrete adapters;
- route/worker/CLI entrypoints;
- cache/freshness and failure/degraded behavior;
- test/evidence ownership;
- dependencies allowed through public contracts only.

Every feature artifact links the selected `CAP-*`, owner `MOD-*`, data/platform artifact IDs, entry `ROUTE-*`/job, `JRN-*`, and planned/result `EVID-*`. Unselected modules do not receive empty feature plans.

## Stop conditions

Stop when a preset guide routes feature policy into `app`, `shared` or generic `lib`, a module owns only a screen, an action owns a transaction/query, an event consumer writes another module's tables, order snapshots follow mutable catalog data, provider payloads escape adapters, Notifications decides business eligibility, Insights mutates authority, or “shared service” becomes a route around module contracts.
