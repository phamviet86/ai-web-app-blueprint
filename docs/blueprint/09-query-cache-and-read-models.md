---
guide_id: SKEL-QUERY
title: Query, Cache, and Read-Model Contracts
status: experimental
audience: human-and-ai
read_when:
  - Designing search, filters, operators, sorting, pagination, query keys, caching, projections, or read models.
skip_when:
  - The change preserves every read/query/cache contract.
depends_on:
  - README.md
  - 04-dependency-contracts-and-sync-flows.md
owns:
  - normalized query envelope and DSL
  - server-owned query policy and complexity limits
  - pagination, projection, and cache identity
  - cache failure, stampede, poisoning, and reconciliation policy
  - HTTP and CDN cache policy
  - read-model selection and freshness contracts
---

# Query, cache, and read-model contracts

> A client describes query intent. The owning application boundary decides what data and computation are allowed.

## Query channels

| Channel | Meaning | Authority |
| --- | --- | --- |
| `trustedScope` | Tenant/user/role/ownership and verified route policy | Derived server-side; never accepted as authoritative client input |
| `params` | Fixed request context such as parent ID or resource scope | Client may transmit; server revalidates and intersects with trusted scope |
| `search` | Keyword intent over approved fields | User-clearable |
| `filter` | Typed predicate tree | User-clearable and bounded |
| `sort` | Approved stable ordering | User-selectable and bounded |
| `page` | Offset/page or cursor window | User-selectable within limits |
| `view` | Date/range/map/aggregation viewport | Translated by the owning query contract |

Normalize transport-specific shapes at the callable boundary. Repositories receive a validated application query, not raw URL/form/table state.

## Rule `QUERY-BOUNDARY-01`: every flexible read is a trust boundary

Validate and authorize:

- public field/path name and projection;
- operator compatibility with field type;
- value coercion, length, enum/range membership, and null semantics;
- searchable/sortable/filterable capability;
- scope against trusted tenant/user/resource context;
- page size, total complexity, and cost-sensitive options.

Reject invalid intent explicitly. Silently dropping a denied filter can broaden results and become a data leak.

Normalization preserves meaning rather than relying on truthiness: `false`, `0`, explicit `null`, an empty value allowed by the field contract, and an omitted key remain distinguishable through transport, application DTO, translator, persistence, and response mapping. Defaults apply only at the boundary that owns them and only to the states its public contract declares absent. Test with real identifier shapes plus locale/timezone-sensitive values where they affect ordering, ranges, or cache identity.

A nontrivial flexible-read contract may implement logical pure stages for transport shape, typed values and predicate trees, field/operator/scope allowlisting, complexity/order/page enforcement, and adapter translation with minimal projection. A stack may combine these stages; no folder, class, or function count is required. The declared validation and error precedence is observable behavior: a later stage must not re-default an already normalized value, drop it by truthiness, broaden an earlier allowlist, or call an adapter after rejection. Verify both risky stages and the complete boundary, including aliases, coercion, group precedence, cumulative limits, deterministic tie-breakers, declared pagination absence/disable semantics, unknown keys, and absence of downstream I/O on invalid intent.

## Rule `QUERY-DSL-01`: controls, predicates, and groups are different concepts

UI `input/type` describes interaction. Predicate `op` describes query semantics. Logical groups compose predicates.

A normalized AST may use:

```ts
type FilterNode =
  | { kind: "predicate"; field: PublicField; op: PredicateOp; value?: unknown }
  | { kind: "group"; op: "and" | "or"; children: FilterNode[] };
```

A baseline predicate vocabulary may include equality, ordered comparison, membership, text search, and null checks. Each field allowlists a subset; not every data source must implement every operator.

Reject unknown keys/kinds, empty groups, invalid child shapes, forbidden values, prototype-polluting names, and any payload the translator cannot prove safe. Never pass a client AST directly to an ORM/search engine.

## Rule `QUERY-ALLOWLIST-01`: public query schema maps to internal data paths

Use a feature/module-owned contract equivalent to:

```ts
const fields = {
  name: {
    type: "string",
    operators: ["eq", "contains"],
    searchable: true,
    sortable: true,
    mapTo: "internal.path",
  },
  status: {
    type: "enum",
    operators: ["eq", "in"],
    values: ["ACTIVE", "INACTIVE"],
  },
};
```

The example is a semantic contract, not a required helper. Public field names must not expose schema internals that prevent later refactor or authorization.

## Rule `QUERY-LIMITS-01`: bound syntax and execution cost

Define finite limits for:

- page/cursor window and export size;
- keyword/value/string length;
- predicate/group count, group width, and nesting depth;
- relation/path depth;
- membership-list size;
- sort fields and selected projection size;
- remote batch/fan-out/concurrency;
- exact count/aggregation options with high cost.

Syntactic limits are necessary but insufficient: use timeouts, database cost evidence, rate/abuse controls, and a separate asynchronous export/report flow for legitimately large work.

## Rule `QUERY-PAGE-01`: ordering and page semantics are one contract

| Need | Prefer |
| --- | --- |
| Small/admin list with random page access | Bounded offset/page pagination |
| Deep or continuously growing feed | Cursor/keyset pagination |
| Stable export | Snapshot/as-of contract or asynchronous job |
| Vendor API | Native vendor cursor/page semantics; do not invent global behavior from one page |

Every page contract defines deterministic tie-break ordering. Cursor payloads are opaque/signed or validated, scoped to the same query/tenant, and versionable.

Do not promise exact totals when they are prohibitively expensive; define approximate/unknown semantics explicitly.

## Rule `QUERY-PROJECTION-01`: return application DTOs, not storage rows

- Select only fields/relations needed by the public query.
- Map persistence/vendor/search shapes at the adapter boundary.
- Avoid per-row enrichment; batch/join through the owning adapter/query handler.
- Do not let presentation recompute security- or business-owned fields.
- Treat field-level authorization as part of projection, not cosmetic hiding.

## Rule `QUERY-KEY-01`: cache identity mirrors result and security identity

A cache key includes every normalized variable that changes the result:

- module/query type and version;
- trusted tenant/role/ownership scope or a safe derived partition;
- fixed params, filters, sort, page, projection, locale/timezone when relevant;
- freshness/as-of contract.

Never include credentials, raw sessions, callbacks, mutable form objects, or PII unnecessary for partitioning. Authorization changes must not reuse a broader cache entry.

Mutation invalidation/updates occur only after committed success and target affected detail/list/option/summary contracts. Broad invalidation is a deliberate fallback with measured cost, not a missing-key default.

## Rule `CACHE-FAILURE-01`: cache failure never invents authority or correctness

For every cache, declare behavior for read outage, write/invalidation outage, malformed or obsolete entries, and source-of-truth outage. A fail-open cache means a bounded fallback to the authorized source or explicitly permitted stale value; it never means skipping authorization, returning an entry from a broader scope, or accepting a cache write as the business commit.

- Prevent stampedes with request coalescing/single-flight, bounded refresh concurrency, TTL jitter, stale-while-revalidate, or a lease appropriate to the platform. Lease expiry must allow recovery from a crashed refresher.
- Apply negative caching only to safe, scoped outcomes with a short declared TTL; do not turn transient dependency or authorization failures into durable absence.
- Treat keys, tags, metadata, and serialized values as untrusted at the read boundary. Version and validate the entry shape, cap size, reject unexpected provenance/scope, and rebuild rather than deserialize or serve ambiguous data.
- Publish/update/invalidate only after committed source success. If that action can fail, record a durable repair intent or expose a measurable divergence signal.
- Reconcile sampled or enumerated source-versus-cache versions on a declared cadence, including missed invalidations, delayed events, privacy deletion, and authorization changes. The repair is idempotent, rate-bounded, observable, and owned.
- Bound retry and source fallback so a cache outage cannot become a source-of-truth or dependency overload event.

Evidence includes concurrent cold-key tests, cache/source fault injection, malformed/wrong-scope entry rejection, missed-invalidation repair, and measured fallback load. Stop if the cache is the only copy of required state, an outage widens access, or correctness depends on best-effort invalidation with no detection and repair.

## Rule `HTTP-CACHE-01`: browsers and CDNs cache only an explicit representation contract

For each cacheable route or asset, define whether it is public, private to one user/tenant, or non-cacheable; the cache tier; freshness and revalidation; and purge/version behavior.

- Use `no-store` for responses whose sensitivity or side effects make reuse unsafe. Use private caching only when the user agent and authenticated representation contract justify it.
- A shared cache key includes every response-changing dimension. Set `Vary` only for bounded headers; prefer normalized path/key design over unbounded cookies or request headers.
- Never let `Authorization`, cookies, tenant headers, locale, content negotiation, or feature/cohort state leak one representation into another. A shared response carrying `Set-Cookie` is non-cacheable unless the platform contract proves safe handling.
- Give immutable fingerprinted assets long freshness; give mutable HTML/API responses bounded freshness plus validators or an owned purge. Define behavior when purge fails.
- Cache redirects, errors, absence, and personalized fragments only with an explicit status-specific TTL and security review. Do not let attacker-controlled host/path/query/header input poison canonical URLs, keys, or cached metadata.

Acceptance evidence inspects real response headers and CDN key configuration, proves cross-user/tenant isolation, exercises revalidation and failed purge, and verifies privacy deletion reaches every applicable tier.

## Read-model decision

| Need | Preferred shape |
| --- | --- |
| Normal relations and bounded filters | Base model/repository query with explicit projection |
| Runtime field, one row per entity | Calculated entity projection or database view when measured |
| Stable derived value needing index/constraint | Stored/generated/trigger-maintained field with ownership tests |
| Aggregate/report grain | Dedicated read model/query repository |
| Full-text/faceted/geospatial workload | Specialized index/search adapter with source-of-truth and sync contract |
| Expensive read with accepted staleness | Cache/materialized projection with refresh/invalidation contract |

Do not add a view/index merely to flatten an ordinary relation or hide an unowned query.

## Rule `READMODEL-ENTITY-01`: calculated entity projections preserve identity

Use when one read row maps to one base aggregate/entity:

- stable base identity and authorization scope remain intact;
- writes target the source-of-truth model;
- calculated filter/sort/page semantics are proven, not merged incorrectly after paging;
- large ID prefilters and mixed base/calculated predicates have bounded query plans;
- read projection failures do not create a second write authority.

## Rule `READMODEL-AGGREGATE-01`: report grain has its own contract

Define:

- row/grain identity and source-of-truth datasets;
- supported filters/sort/page/count;
- freshness, lag, refresh/invalidation, and failure semantics;
- source mutations/events that update it;
- reconciliation/backfill path;
- authorization/tenant partitioning.

A report projection is not generic entity CRUD and does not inherit entity mutation APIs.

## Rule `READMODEL-FRESHNESS-01`: every duplicate representation names consistency

For cache, materialized view, search index, warehouse, or vendor mirror, record:

```text
source of truth
update mechanism
expected/max lag
read behavior when stale/unavailable
rebuild/reconciliation owner
deletion/privacy propagation
```

“Eventually consistent” without a bounded expectation and repair mechanism is incomplete.

## Verification

- allowed and denied fields/operators/projections/scopes;
- coercion, enum/null/range semantics and malformed ASTs;
- `false`, `0`, explicit `null`, empty, and omitted-value round trips, including declared defaults and real identifier/timezone cases;
- depth/width/value/page/export limits and timeout behavior;
- stable ordering, cursor tampering, empty/duplicate/deleted rows;
- cache separation by every result/security dimension and success-only invalidation;
- cache stampede/failure/poisoning behavior, fallback load, and invalidation reconciliation;
- browser/CDN headers, key dimensions, revalidation/purge, and cross-scope isolation;
- query count/timing/plan at representative cardinality;
- read-model freshness, rebuild, reconciliation, authorization, and deletion propagation.

## Stop conditions

Stop when the client can name internal fields/operators, invalid intent broadens results, cache identity omits security scope, cache/CDN failure can widen access or overload the source, invalidation has no repair path, pagination lacks stable order, calculated filters page incorrectly, or a duplicate read representation has no freshness/repair contract.
