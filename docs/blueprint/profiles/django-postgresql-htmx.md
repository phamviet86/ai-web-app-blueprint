---
guide_id: SKEL-PROFILE-DJANGO-HTMX
title: Django, PostgreSQL, and HTMX Reference Profile
status: experimental
audience: human-and-ai
verified_on: 2026-07-12
builder_profile_id: BUILDER-DJANGO-POSTGRESQL-HTMX
evidence_sources:
  - /websites/djangoproject_en_6_0
  - /bigskysoftware/htmx/v2.0.4
read_when:
  - Mapping the core blueprint to a Django server-rendered web application enhanced with HTMX.
skip_when:
  - The selected stack differs materially or only core architecture is being decided.
depends_on:
  - ../README.md
  - ../02-module-anatomy-and-public-contracts.md
  - ../10-runtime-accessibility-and-performance.md
owns:
  - concrete Django module, view, template, and composition mapping
  - WSGI/ASGI and sync/async selection boundaries
  - PostgreSQL ORM, transaction, migration, and deployment mapping
  - HTMX partial/full response, history, security, focus, and fallback mapping
---

# Django, PostgreSQL, and HTMX reference profile

> This is a maintained implementation mapping, not an accepted project stack. Resolve Python, PostgreSQL, driver, server, and package versions together and record them in the project-local `STACK-*` artifact.

## Reference-app builder fit

Use this profile through the [reference-app builder](../reference-app-blueprint/README.md) when Python, server-rendered HTML and progressive enhancement fit the product/team. It is especially economical for `BASIC_WEB` and `MULTI_TENANT_SAAS`; it also supports other tiers when their worker, provider and assurance mechanisms are selected deliberately.

| Tier/need | Mapping posture |
| --- | --- |
| `BASIC_WEB` | One synchronous Django web root, PostgreSQL, full-page views plus HTMX fragments, native forms and no broker/cache by default |
| `MULTI_TENANT_SAAS` | Add application-owned membership/resource policy and tenant-scoped queries/constraints; Django auth remains identity mechanism |
| `ASYNC_INTEGRATION` | Add a durable worker/queue or database-backed job mechanism selected by deployment risk; do not mistake an async view for durable work |
| `REGULATED` | Strengthen identity assurance, audit, privacy, retention, migration and recovery evidence; framework defaults do not prove compliance |
| `FULL_SHOWCASE` | Map all selected modules/ports while keeping carrier/email/cache/advanced identity conditional |

Record `Source mapping: ../profiles/django-postgresql-htmx.md` and deviations in the generated `STACK-*` artifact.

## Verified source basis

This mapping was checked against Django `6.0` documentation and HTMX `2.0.4` documentation on `2026-07-12`. Re-verify before implementation when either version changes.

- Django: [async support](https://docs.djangoproject.com/en/6.0/topics/async/), [ASGI deployment](https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/), [deployment checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/), [transactions](https://docs.djangoproject.com/en/6.0/topics/db/transactions/), [migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/), [writing migrations](https://docs.djangoproject.com/en/6.0/howto/writing-migrations/), and [static deployment](https://docs.djangoproject.com/en/6.0/howto/static-files/deployment/).
- HTMX: versioned [core documentation](https://github.com/bigskysoftware/htmx/blob/v2.0.4/www/content/docs.md), [`hx-boost`](https://github.com/bigskysoftware/htmx/blob/v2.0.4/www/content/attributes/hx-boost.md), and [security guidance](https://github.com/bigskysoftware/htmx/blob/v2.0.4/www/content/essays/web-security-basics-with-htmx.md).

## Recommended logical mapping

```text
project/
├── config/
│   ├── settings/                 base + environment settings boundary
│   ├── urls.py                   thin protocol/route composition
│   ├── asgi.py                   selected only for an ASGI deployment
│   └── wsgi.py                   selected synchronous deployment root
├── modules/<module>/
│   ├── public/                   commands, queries, DTOs/errors/events
│   ├── application/              use cases, authz and owned ports
│   ├── domain/                   optional pure policy/state transitions
│   ├── adapters/                 Django ORM/vendor/job implementations
│   ├── presentation/
│   │   ├── views.py              full/partial protocol adaptation
│   │   ├── forms.py              boundary parsing/presentation validation
│   │   ├── urls.py
│   │   └── templates/<module>/   pages + named fragments
│   └── apps.py                   framework registration, not business wiring
├── platform/                     config/auth/db/http/storage/jobs/telemetry mechanics
├── shared/                       small kernel and resolved template/UI primitives
├── templates/                    app shell only; module templates stay with owners
└── manage.py                     CLI entry adapter
```

Django app labels may align with business modules, but `models.py` does not define a module boundary. Other modules use intentional public application contracts, not foreign model managers or internal views.

## Rule `PROFILE-DJANGO-RUNTIME-01`: choose WSGI/ASGI and sync/async deliberately

- Use a conventional synchronous WSGI or ASGI deployment for ordinary request/response work; choose ASGI when the accepted profile includes a real async stack need such as slow streaming or long-lived connections.
- An async view under WSGI runs in a one-off event loop and does not provide the benefits of a full async stack. Mixing sync and async middleware/views adds context switches, so verify the complete middleware chain.
- Do not call blocking sync code from async views. Wrap required sync Django work with `sync_to_async(..., thread_sensitive=True)` and audit third-party libraries because Django cannot protect every blocking call.
- Async request handling is not a durable queue. Work that must survive request/process failure uses a selected job/worker contract with idempotency, retry and recovery.
- Keep web, worker, migration and management-command roots explicit. Graceful startup/shutdown and telemetry follow the actual server/worker runtime.

## Rule `PROFILE-DJANGO-HTMX-01`: one URL contract serves full and partial HTML

- A normal request returns the complete accessible page. When `HX-Request` is present, the same application query/command may return a named fragment; both paths share authorization, validation and business behavior.
- Keep stable URLs, native anchors and forms. `hx-boost` enhances eligible navigation/submission while the original `href`, `action` and method remain a functional progressive fallback.
- When responses vary by `HX-Request`, include that distinction in cache identity and response variation policy. Never let a shared cache serve a fragment as a full document.
- Use `hx-push-url` only when the resulting URL can render a full page directly. Handle `HX-History-Restore-Request`/history misses safely and prefer a full refresh when a partial restoration would be ambiguous.
- Every swapped target has a stable element contract. Loading, validation, denied, empty, stale and unexpected states remain valid HTML, not client-only policy.
- Preserve keyboard focus deliberately: give replaceable controls stable IDs, verify focus after swaps, and use `focus-scroll` only when intentional; HTMX's default focus scrolling is off.
- Keep native form submission and full-page navigation tests alongside HTMX interaction tests. A failed JavaScript load must not make core read/write journeys impossible unless the product explicitly accepted that constraint.

## HTMX and Django security boundary

- Django template auto-escaping remains on. Render untrusted content as text; never interpolate it into `hx-*`, script or executable attribute contexts.
- Put `hx-disable` on an untrusted-content container to prevent injected descendants from activating HTMX attributes; it complements, not replaces, output encoding and sanitization.
- Same-origin state-changing requests carry Django CSRF proof through the rendered form token or an approved `X-CSRFToken` header sourced from the CSRF cookie/token contract. Test a missing/invalid token and do not disable CSRF middleware for HTMX routes.
- Production session and CSRF cookies use HTTPS-appropriate `Secure`, `HttpOnly` where applicable, and deliberate `SameSite` policy. Application authorization still checks subject + action + resource + optional tenant.
- Keep HTMX requests same-origin by default; review any external target as an integration/trust boundary. Consider disabling script/eval features when the CSP and interaction model permit it.
- `HX-Request` is a presentation hint, never authentication, authorization or proof of origin.

## Rule `PROFILE-DJANGO-DATA-01`: ORM and transactions stay inside adapters

- Application-owned repository/query ports expose domain/application DTOs. Django model/queryset types remain inside adapters and presentation-specific read mapping.
- Use narrow `values`/projections, `select_related`/`prefetch_related` only from measured query shapes, bounded pagination and database indexes verified against representative cardinality.
- One application use case owns `transaction.atomic()` and the contested invariant. Avoid blanket `ATOMIC_REQUESTS` without measuring transaction overhead and lock duration; remote provider calls stay outside database transactions.
- Use constraints, uniqueness, row locks or optimistic versions according to the race. Catch/translate database exceptions at the adapter/application boundary.
- Versioned reviewed migrations are the production path. Release applies pending migrations once, separately from request startup, with application/schema compatibility.
- Large data work may use a non-atomic migration with resumable batches, each bounded by `transaction.atomic()`. Use historical models through the migration app registry and declare cross-app migration dependencies explicitly.
- Follow expand -> backfill -> compare -> switch -> contract; never use destructive reset or development-only schema shortcuts in public/production environments.

## Deployment, security, and static-files gate

Before `STACK-*` acceptance or release:

1. run `django-admin check --deploy --settings=<production-settings>` and own every warning/exception;
2. use a production WSGI/ASGI server, not `runserver` or `runserver --insecure`;
3. keep `DEBUG` off, secrets outside source, `ALLOWED_HOSTS`/trusted origins explicit, HTTPS termination understood, and secure session/CSRF settings verified;
4. run `collectstatic` into the selected immutable/static asset path and let the web server/CDN/object store serve it; do not make Django development serving the production design;
5. run migrations as a reviewed release job, then smoke full-page and HTMX paths against the promoted artifact;
6. record database connection/pool limits, health/readiness, telemetry flushing, rollback/roll-forward and backup/restore boundaries.

## Verification routing

| Contract | Minimum useful evidence |
| --- | --- |
| Domain/application rule | Fast Django/Python unit or application test with fixed clock/IDs |
| ORM constraint/query/transaction | Real isolated PostgreSQL integration and race/rollback case |
| Full/partial response | Django client test for normal and `HX-Request`, including cache variation |
| Progressive fallback | Browser or HTTP journey with HTMX disabled plus enhanced interaction test |
| CSRF/authz/tenant | Missing/invalid token and direct-call horizontal/vertical deny tests |
| History/focus/accessibility | Browser back/forward/history miss, swap focus, keyboard and semantic checks |
| Migration/release | Fresh install, upgrade from supported revision, `check --deploy`, `collectstatic`, release smoke and recovery proof |
| Async/worker | Selected ASGI middleware spike or durable worker duplicate/crash/replay evidence |

## Profile stop conditions

Stop when an HTMX fragment has no full-page URL/fallback, `HX-Request` becomes an authorization signal, CSRF is disabled for convenience, untrusted HTML can activate `hx-*`, async Django code calls blocking libraries, async views substitute for durable jobs, models/querysets escape as public module contracts, `ATOMIC_REQUESTS` is assumed safe without measurement, migrations run on every request instance startup, or production static files use the development server.
