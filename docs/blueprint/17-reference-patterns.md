---
guide_id: SKEL-REFERENCES
title: Illustrative Logical Implementation Patterns
status: experimental
audience: human-and-ai
read_when:
  - Generating a module, command/query, port/adapter, entrypoint, composition root, or idempotent event consumer.
skip_when:
  - Reviewing architecture or changing a concrete stack API without generating these contracts.
depends_on:
  - 02-module-anatomy-and-public-contracts.md
  - 04-dependency-contracts-and-sync-flows.md
  - 13-reliability-async-and-integrations.md
owns:
  - illustrative logical code shapes implementing core rules
  - anti-pattern contrasts for generated slices
---

# Illustrative logical implementation patterns

> These are intentionally incomplete TypeScript-shaped pseudocode, not compile-ready source. Adapt the smallest applicable shape through the selected stack profile, supply missing types/imports/platform behavior, and verify it; do not create every layer for simple CRUD.

## Minimal module tree

```text
modules/orders/
├── public/
│   ├── contracts.ts       stable commands, queries, DTOs, published events
│   └── index.ts           only cross-module import surface
├── application/
│   ├── place-order.ts     use case and owned ports
│   └── get-order.ts
├── domain/                add only when invariants/state deserve a model
│   └── order.ts
├── adapters/
│   ├── order-repository.ts
│   └── payment-gateway.ts
├── presentation/
│   └── order-entrypoint.ts
└── compose.ts             module-local wiring called by app composition root
```

For a thin record module, `domain/` may be pure validation/policy functions or absent. Preserve the application/public/adapter boundary rather than adding empty folders.

## Stable result and error contract

This mirrors the logical contract owned by `ERROR-TAXONOMY-01` in [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md#rule-error-taxonomy-01-expected-failures-have-typed-semantics).

```ts
type AppErrorCategory =
  | "validation"
  | "unauthenticated"
  | "forbidden"
  | "not_found"
  | "conflict"
  | "domain"
  | "rate_limited"
  | "dependency_unavailable";

type AppError = {
  code: string;
  category: AppErrorCategory;
  safeDetails?: Record<string, string | number | boolean>;
  retryable?: boolean;
};

type Result<T> =
  | { ok: true; value: T; meta?: Record<string, unknown> }
  | { ok: false; error: AppError };
```

Expected failures use the typed result. Unexpected programming/infrastructure failures retain their cause, are correlated/logged at the boundary, and are not disguised as `ok: false` without policy.

## Public module contracts

```ts
export type PlaceOrderCommand = {
  customerId: string;
  lines: Array<{ productId: string; quantity: number }>;
  idempotencyKey: string;
};
export type OrderDto = {
  id: string;
  status: "PENDING" | "CONFIRMED";
  totalMinor: number;
  version: number;
};

export type OperationContext = { trusted: TrustedContext; deadlineAt: Date; signal: AbortSignal };
export interface OrdersApi {
  place(command: PlaceOrderCommand, operation: OperationContext): Promise<Result<OrderDto>>;
  get(query: GetOrderQuery, operation: OperationContext): Promise<Result<OrderDto>>;
}
```

Public DTOs expose application meaning, not ORM rows, framework request objects, localized UI messages, or vendor payloads.

## Application command with owned ports

```ts
type IdempotencyRecord<T> =
  | { state: "in_progress"; fingerprint: string }
  | { state: "completed"; fingerprint: string; value: T };

type IdempotencyClaim<T> =
  | { state: "acquired" }
  | IdempotencyRecord<T>;

type PlaceOrderDeps = {
  orders: {
    insert(order: OrderRecord, tx: Transaction, operation: OperationContext): Promise<void>;
  };
  productCatalog: {
    loadForOrder(ids: string[], operation: OperationContext): Promise<ProductSnapshot[]>;
  };
  idempotency: {
    find(scope: string, key: string, operation: OperationContext): Promise<IdempotencyRecord<OrderDto> | null>;
    claim(scope: string, key: string, fingerprint: string, tx: Transaction, operation: OperationContext): Promise<IdempotencyClaim<OrderDto>>;
    complete(scope: string, key: string, value: OrderDto, tx: Transaction, operation: OperationContext): Promise<void>;
  };
  unitOfWork: UnitOfWork;
  ids: { next(): string };
  clock: { now(): Date };
};

type GetOrderDeps = {
  orderQueries: { get(query: AuthorizedGetOrderQuery, operation: OperationContext): Promise<OrderDto | null> };
};

export const makePlaceOrder = (deps: PlaceOrderDeps) =>
  async (command: PlaceOrderCommand, operation: OperationContext): Promise<Result<OrderDto>> => {
    const access = authorizePlaceOrder(operation.trusted, command.customerId);
    if (!access.ok) return access;

    const scope = idempotencyScope(operation.trusted, "orders.place");
    const fingerprint = canonicalFingerprint(command);
    const prior = await deps.idempotency.find(scope, command.idempotencyKey, operation);
    if (prior) return resolveIdempotency(prior, fingerprint);

    const products = await deps.productCatalog.loadForOrder(uniqueProductIds(command), operation);
    const created = Order.create(command, products, deps.ids.next(), deps.clock.now());
    if (!created.ok) return created;

    return deps.unitOfWork.run(operation, async (tx) => {
      const claim = await deps.idempotency.claim(scope, command.idempotencyKey, fingerprint, tx, operation);
      if (claim.state !== "acquired") return resolveIdempotency(claim, fingerprint);

      const value = toOrderDto(created.value.record);
      await deps.orders.insert(created.value.record, tx, operation);
      await tx.outbox.add(created.value.events.map(toIntegrationEvent), operation);
      await deps.idempotency.complete(scope, command.idempotencyKey, value, tx, operation);
      return { ok: true, value };
    });
  };
```

`claim` uses an atomic unique reservation for `(scope, key)` inside the same transaction as the business write, stored result, and outbox. `resolveIdempotency` rejects a changed fingerprint, returns the stored completed value, or returns an explicit retryable in-progress conflict. The second claim closes the race after the optional fast lookup. Retention, expiry, failed-attempt, and stale in-progress recovery remain required choices under `IDEMPOTENCY-01`; this focused snippet shows only the success/concurrent-replay path.

The application owns ports because it owns the need. Adapters implement them; no DI container is required.

## Pure domain model only when valuable

```ts
class Order {
  private constructor(private state: OrderState) {}

  static create(command: PlaceOrderCommand, products: ProductSnapshot[], id: string, now: Date) {
    const lines = priceAndValidate(command.lines, products);
    if (!lines.ok) return lines;

    const state = { id, status: "PENDING", lines: lines.value, version: 0, createdAt: now };
    return success({
      record: state,
      events: [{ type: "OrderPlaced", orderId: id, totalMinor: total(lines.value) }],
    });
  }
}
```

Domain code imports no framework, database, environment, telemetry SDK, or vendor client. Simple validation should remain simple functions rather than an anemic class hierarchy.

## Adapter and mapper

```ts
export const makeOrderRepository = (db: Database): PlaceOrderDeps["orders"] => ({
  async insert(record, tx, operation) {
    await tx.orders.insert(toRow(record), { signal: operation.signal, deadlineAt: operation.deadlineAt });
  },
});

export const makeIdempotencyRepository = (db: Database): PlaceOrderDeps["idempotency"] =>
  createAtomicIdempotencyStore(db, { uniqueBy: ["scope", "key"] });
```

The idempotency adapter implements atomic claim-or-read and stores fingerprint/result in the transaction supplied by the use case. Business decisions remain in application/domain code.

## Entrypoint/presenter

```ts
export const makePlaceOrderEntrypoint = (orders: OrdersApi) => async (request: Request) => {
  const parsed = parsePlaceOrderTransport(request);
  if (!parsed.ok) return presentError(parsed.error);

  try {
    const operation = await trustedOperationContext(request, { maxDurationMs: 5_000 });
    const result = await orders.place(parsed.value, operation);
    return result.ok ? presentOrder(result.value) : presentError(result.error);
  } catch (cause) {
    const incidentId = recordUnexpected(cause, request);
    return presentUnexpected(incidentId);
  }
};
```

Transport parsing and HTTP/RPC/UI/localization mapping stay at the presentation boundary. `trustedOperationContext` derives trusted request context plus a bounded deadline/cancellation signal; ports honor it where safe, stop starting work after expiry, and do not mistake a disconnect for rollback of a committed effect. Durable work that must outlive the request uses the async contracts in guide `13`. The use case does not return an HTTP response.

## Composition root

```ts
type OrdersCompositionDeps = {
  platform: Platform;
  productCatalog: PlaceOrderDeps["productCatalog"];
};

export const composeOrders = ({ platform, productCatalog }: OrdersCompositionDeps): OrdersApi => {
  const orders = makeOrderRepository(platform.database);
  const orderQueries = makeOrderQueryRepository(platform.database);
  const idempotency = makeIdempotencyRepository(platform.database);
  const unitOfWork = makeUnitOfWork(platform.database);

  return {
    place: makePlaceOrder({ orders, productCatalog, idempotency, unitOfWork, ids: platform.ids, clock: platform.clock }),
    get: makeGetOrder({ orderQueries }),
  };
};

export const composeApp = (platform: Platform) => {
  const products = composeProducts(platform);
  const orders = composeOrders({ platform, productCatalog: products.publicCatalog });
  return { orders, products: products.api };
};
```

The app composition root creates platform clients, composes modules, and injects one module's public contract into another module's owned port. `orderQueries` implements the application-owned GetOrder query port; the write repository is not reused as an accidental read facade. `Platform` contains mechanisms such as database, clock, IDs, and telemetry—not a Products business API. A module-local compose function is a private subordinate factory; callers import only the returned public API.

## Query handler

```ts
export const makeListOrders = ({ readRepository }: QueryDeps) =>
  async (raw: unknown, operation: OperationContext): Promise<Result<OrderPageDto>> => {
    const query = normalizeAndAuthorizeOrderQuery(raw, operation.trusted);
    if (!query.ok) return query;
    return success(await readRepository.list(query.value, operation));
  };
```

The normalizer applies [09-query-cache-and-read-models.md](09-query-cache-and-read-models.md); the read adapter receives no untrusted field/operator or tenant scope.

## At-least-once event consumer

```ts
export const makeOrderPlacedConsumer = (deps: ConsumerDeps) => async (event: IntegrationEvent, operation: OperationContext) => {
  validateEventEnvelope(event);

  await deps.unitOfWork.run(operation, async (tx) => {
    const claim = await tx.inbox.claimUnique(event.eventId, "reserve-stock", operation);
    if (!claim.acquired) return;
    await reserveStock(event.payload, tx, operation);
    await tx.inbox.markCompleted(event.eventId, "reserve-stock", operation);
  });
};
```

`claimUnique`, the business effect, and inbox completion use one transaction with a unique `(eventId, consumer)` constraint; rollback releases the claim/effect together. Retries, DLQ/quarantine, replay authorization, and ordering key are owned by [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md).

## Focused test ownership

```text
domain test          invariants/state transitions with fixed clock/IDs
application test     authorization, use-case branches, port interactions
adapter integration  real schema/query/mapping/transaction behavior
contract test        public DTO/error/event compatibility
entrypoint test      transport/auth/error mapping
E2E                  only critical journey wiring and observable behavior
```

## Anti-patterns

- Module A imports Module B's repository/schema instead of public API.
- Application service imports ORM/SDK and returns framework responses.
- Domain object reads environment/time/UUID directly.
- Public DTO re-exports a database or vendor type.
- Entry point contains transaction/business policy.
- Event consumer assumes exactly-once delivery.
- Shared utility contains branches for module names/statuses.
- Composition happens implicitly through mutable globals.

## Stop conditions

Do not adapt these shapes when a smaller pure function suffices, when the selected stack has a safer equivalent, when the operation lacks a bounded deadline/cancellation contract, or when a pattern would create unused layers. Preserve the rule intent, not the syntax.
