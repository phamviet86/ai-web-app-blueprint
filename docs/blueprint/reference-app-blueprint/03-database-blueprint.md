---
guide_id: REFAPP-DATA
title: Reference Relational Database Blueprint
status: experimental
audience: human-and-ai
read_when:
  - Designing the logical schema, table ownership, constraints, seed scenarios, read models, or persistence controls.
skip_when:
  - The current slice changes no stored or projected data contract.
depends_on:
  - README.md
  - ../09-query-cache-and-read-models.md
  - ../12-data-lifecycle-migrations-and-recovery.md
owns:
  - tier-selected reference logical tables and relationships
  - reference seed scenarios and persistence coverage
  - mapping from data controls to reference tables
  - preset query-policy, ORM translation, and read-shape compatibility
---

# Reference relational database blueprint

> This is a catalog of logical relational contracts. Materialize only tables and projections required by the accepted `COVERAGE-*`; `FULL_SHOWCASE` uses the complete FulfillOps catalog. The accepted stack profile chooses SQL types, ORM syntax, database enums/checks, RLS, indexes and migration commands.

## Rule `REF-DATA-OWNER-01`: every table has one write owner

Apply `DATA-INVENTORY-01`, `DEP-XMODULE-DATA-01`, and `TX-BOUNDARY-01` from the parent blueprint. Sharing one PostgreSQL database does not grant cross-module repository access.

Common conventions:

- opaque immutable IDs; UTC instants; explicit business date and timezone where relevant;
- when `CAP-TENANCY` is selected, every tenant-owned table contains `organization_id` and tenant-scoped indexes/uniqueness;
- tenant-scoped child relationships carry tenant scope so cross-tenant references cannot be created accidentally;
- money uses integer minor units plus currency, never floating point;
- contested aggregates use `version` or another declared concurrency mechanism;
- state values are bounded contracts with guarded transitions;
- immutable ledgers/history are append-only; current-state tables remain the write authority;
- archive/anonymize/retention states are deliberate, not one universal soft-delete column.

## Identity and workspace

Authentication mechanism tables—normally user, session, account and verification—are owned by the selected identity adapter. Generate and review them through the same migration history; do not duplicate credentials in application tables.

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `user_profiles` | `subject_id` PK, display name, locale, timezone, status, timestamps | Workspaces |
| `organizations` | ID, unique slug, name, status, default currency, version, timestamps | Workspaces |
| `memberships` | organization + subject PK, status, version, timestamps | Workspaces |
| `membership_roles` | organization + subject + role PK; bounded organization roles | Workspaces |
| `invitations` | organization, normalized email, requested roles, token hash, status, inviter, expiry/accept/revoke times; one active invite per tenant/email | Workspaces |
| `system_role_assignments` | subject + system role PK, grant/revoke metadata | Governance |

Identity records authenticate a subject. Membership and resource policy authorize business actions. Organization roles are `OWNER`, `ADMIN`, `SALES`, `INVENTORY`, `BILLING`, `FULFILLMENT`, `REPORTER`, and `AUDITOR`; one membership may hold several. System roles are separate and never imply organization access. The last active owner invariant is transactionally enforced.

## Customers and privacy

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `customers` | organization, external reference, name, contact fields, status, retention/anonymized state, version; unique tenant/external ref | CRM |
| `customer_addresses` | organization, customer, kind, recipient/address fields, status | CRM |
| `customer_privacy_requests` | organization, customer, request kind, verification, status, due/hold/result/completion fields | CRM |

Access/export/correction/anonymization policy must preserve required financial evidence without retaining unrelated personal data indefinitely.

## Catalog and inventory

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `products` | organization, unique SKU, name/description, default price minor/currency, status, version | Catalog |
| `stored_files` | organization, unique storage key, safe name/type/size/checksum, scan status, retention, creator | Data Exchange |
| `product_media` | organization, product, file, kind, ordering; FK-backed rather than generic polymorphic link | Catalog |
| `warehouses` | organization, unique code, name, timezone, status, version | Inventory |
| `inventory_balances` | organization + warehouse + product PK, on-hand, reserved, version; `0 <= reserved <= on_hand` | Inventory |
| `inventory_movements` | warehouse/product, type, on-hand/reserved deltas, unique source effect, actor/time; immutable | Inventory |
| `stock_reservations` | organization, order, warehouse, status, expiry, version; one full-order reservation and one warehouse per tenant/order in the reference baseline | Inventory |
| `stock_reservation_items` | reservation + product unique, positive quantity | Inventory |

Balance, movement and reservation updates share one transaction. Movement history supports reconciliation; it is not a second mutable balance.

## Orders

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `orders` | organization, unique order number, customer, status, currency/totals, version, creator, submit/complete times | Orders |
| `order_lines` | order, line number, product reference, SKU/name/price snapshots, positive quantity, line total; unique order/line | Orders |
| `order_addresses` | order, address kind and recipient/address snapshot | Orders |
| `order_status_history` | order, from/to status, actor/source, reason, occurred time; append-only | Orders |

Recommended lifecycle:

```text
DRAFT -> SUBMITTED -> ALLOCATING -> RESERVED
  -> PAYMENT_PENDING -> READY_TO_SHIP -> SHIPPED -> COMPLETED
                     \-> ON_HOLD
permitted active states -> CANCELLED
```

The Orders module snapshots catalog/customer facts needed for historical truth; later catalog/customer edits do not rewrite an accepted order.

## Billing and fulfillment

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `invoices` | organization, order, unique invoice number, status, totals/balance/currency, issued/due/paid times, version; one invoice per tenant/order in the reference baseline | Billing |
| `invoice_lines` | invoice, line number, description, quantity, unit/line minor amounts; unique invoice/line | Billing |
| `payment_intents` | organization, invoice, provider/ref, amount/currency, state, idempotency key, version; unique provider ref and scoped key | Billing |
| `payment_attempts` | intent, provider event, attempt kind/status/amount/safe error/time; immutable | Billing |
| `shipments` | organization, order, warehouse, status, version, timestamps; one shipment per tenant/order in the reference baseline; nullable carrier/ref/tracking only when provider capability is selected | Fulfillment |
| `shipment_items` | shipment + order line unique, positive quantity; baseline totals equal the full reserved order | Fulfillment |
| `shipment_status_history` | shipment, from/to state, source, occurred time; append-only | Fulfillment |

Each payment intent belongs to exactly one invoice; an invoice may have multiple partial-payment intents. A successful captured amount updates the intent and that invoice balance in one Billing transaction, bounded by captured and outstanding amounts. That transaction emits `PaymentCapturedV1`; it also emits `InvoicePaidV1` only when the balance reaches zero. Remote payment/carrier calls stay outside database transactions. Persist intent first, then reconcile ambiguous outcomes.

Split reservations, multiple warehouses, partial fulfillment and multiple shipments are extensions. Selecting them requires new allocation/completion invariants and removes the baseline uniqueness assumptions explicitly.

## Files, integrations and durable work

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `payment_connections` | organization, provider, encrypted-secret reference, state, config version, timestamps | Billing; secret bytes stay in secret store |
| `carrier_connections` | organization, provider, encrypted-secret reference, state, config version, timestamps | Fulfillment; conditional extension |
| `payment_webhook_receipts` | provider/event unique, organization, payload hash, authenticity/processing states, receive/process times | Billing |
| `carrier_webhook_receipts` | provider/event unique, organization, payload hash, authenticity/processing states, receive/process times | Fulfillment; conditional extension |
| `notifications` | organization, recipient, event/template version, state, read time | Notifications |
| `notification_deliveries` | notification, channel, provider ref, state, attempt, safe error, timestamps | Notifications |
| `import_jobs` | organization, kind, source file, schema version, status, checkpoint/totals, attempt/lease, creator/timestamps | Data Exchange |
| `import_rows` | job + row unique, input hash, state, error code, result reference | Data Exchange |
| `export_jobs` | organization, kind/query snapshot, state, result file, checkpoint/timestamps | Data Exchange |
| `payment_reconciliation_runs` | organization, provider, range/checkpoint, differences/repairs, state/timestamps | Billing |
| `carrier_reconciliation_runs` | organization, provider, range/checkpoint, differences/repairs, state/timestamps | Fulfillment; conditional extension |

Import jobs and notification deliveries are the application sources of truth for their workflows. Queue delivery attempts/leases remain transport state; do not add a generic `job_runs` table that competes with them. If the selected queue supplies durable inspectable dead-letter state, do not duplicate it automatically.

## Idempotency, events and audit

| Logical table | Key fields and constraints | Owner |
| --- | --- | --- |
| `idempotency_records` | scope + key PK, fingerprint, in-progress/completed/failed state, safe result/ref, expiry/timestamps | Platform persistence contract, namespace owned by command module |
| `outbox_events` | event/schema, aggregate/version, tenant, correlation/causation, payload, availability/publish/attempt/error fields | Platform messaging schema/port; fact/schema owned by producer module |
| `inbox_receipts` | consumer + event PK, tenant, state, receive/process/error fields | Platform messaging schema/port; consumer namespace owned by module |
| `security_audit_events` | tenant optional, actor/subject/action/target/outcome/reason/correlation/safe metadata/time | Governance |

Platform is the only repository/schema owner for the three generic technical tables; modules use transaction-scoped, namespace-enforcing ports and cannot query another namespace. Atomic claim, business effect and completion share a transaction. Do not store secrets, raw payment credentials, unnecessary webhook payloads or unbounded telemetry in these tables.

## Read models

| Projection | Grain and purpose | Freshness contract |
| --- | --- | --- |
| `order_operations_projection` | `CAP-READMODEL`: one order with customer, stock, payment and shipment states | Event/source-version checkpoint; rebuildable |
| `inventory_availability_projection` | Conditional: add only when the authoritative bounded availability query is insufficient | Transactional or declared event lag |
| `receivables_aging_projection` | Extension: add for a real finance-report requirement | Scheduled/checkpointed, reports `as_of` |
| `daily_operations_projection` | Extension: add for a real aggregate dashboard requirement | Scheduled/event projection with refreshed time |

The stack profile may implement these as queries, views, materialized views or projection tables. They remain read-only derived representations with explicit source authority.

## Rule `REF-DATA-QUERY-CONTRACT-01`: dynamic query intent is public, bounded, and translated

Every preset that provides remote data surfaces defines one canonical request family:

| Request part | Purpose | Required guard |
| --- | --- | --- |
| `params` | Stable route/resource context | Trusted schema and ownership/access checks |
| `search` | Keyword over approved public aliases | Length, normalization and approved fields |
| `filters` | Typed predicates | Field/operator/value allowlist and bounded depth/count |
| `sort` | One or more approved order terms | Stable tie-breaker and bounded term count |
| `pagination` | Page/offset or cursor intent | Maximum size and deterministic ordering |
| `range` / `view` | Calendar/time-window or another selected viewport | Bounded dates, timezone and feature-owned semantics |

Table/list/masonry normally emit search, filters, sort and pagination. Calendar normally emits search, filters, range, timezone and view mode. Options/pickers use a bounded subset. Changing search/filter/range resets incompatible pagination, and canonicalized intent forms the query/cache identity together with access scope and fixed params.

Generic `lib/database` code may provide validated primitives and ORM-specific translator helpers. The owning feature must map each public alias to its type, allowed operators, column/relation expression, mandatory subject/tenant predicate, projection/join, stable order and query budget. Unknown or forbidden intent is rejected; it is never dropped in a way that broadens results. Client payloads never contain raw ORM `where`, SQL, internal column names or arbitrary relation paths.

The feature repository returns stable application DTOs plus page/cursor or range metadata, optional total policy and material freshness (`as_of`) when relevant. ORM-generated row types, provider errors and query-builder objects do not cross its public contract.

## Join, view, and calculated-read policy for presets

- Prefer explicit bounded joins/projections for ordinary relational reads.
- Use a database view when a stable reusable calculated read shape benefits from database semantics.
- Use a materialized view/projection only with measured need, freshness/rebuild ownership and comparison evidence.
- Prove filters, sort, pagination and totals at the layer where calculation occurs; never page base rows and then filter/sort a derived value in memory.
- Test invalid aliases/operators, mandatory access scope, stable page boundaries, representative joins/cardinality and view/projection freshness.

Record this mapping and evidence in [data-model](templates/data-model.md) and the feature plan. A generic dynamic-query helper never grants a feature access to another module's tables.

## Rule `REF-DATA-SEED-01`: deterministic seed data proves boundary cases

Seed or fixture generation must cover the accepted tier without inventing unselected modules:

- `BASIC_WEB`: valid/invalid/empty/paged records for the selected CRUD/query journey;
- `MULTI_TENANT_SAAS`: two organizations, allowed/denied roles, stale membership and cross-tenant IDs;
- `ASYNC_INTEGRATION`: pending/succeeded/failed work, duplicate delivery and ambiguous provider outcome;
- `REGULATED`: classified/synthetic records, retention/privacy states, privileged/denied actors and audit evidence;
- `FULL_SHOWCASE`: the union above plus order, stock, payment, shipment, import, notification and projection boundary states.

Seeds are deterministic, re-runnable in isolated environments and contain no production personal data. Public demo reset policy belongs to guide `09`.

## Migration and recovery

The implementation must use versioned reviewed migrations and the parent data-migration template. Production or public-demo environments never use reset/push shortcuts. Backup/restore, RPO/RTO and expand-contract evolution remain owned by parent guide `12`.

## Stop conditions

Stop when a table has multiple write owners, tenant scope depends only on application filters, client query intent names raw ORM/SQL fields, denied query terms broaden results, calculated values are filtered after pagination, cross-tenant FK relationships are possible, money uses floating point, current state and immutable evidence compete as authorities, provider payloads become domain records, or a projection can mutate business truth.
