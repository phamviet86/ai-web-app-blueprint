---
guide_id: SKEL-SHARED-LIB
title: Shared Kernel, Shared UI, and Platform Boundaries
status: experimental
audience: human-and-ai
read_when:
  - Promoting code outside a business module.
  - Adding shared UI, configuration, runtime infrastructure, or dependency wiring.
skip_when:
  - The change stays inside one module and introduces no reusable or platform contract.
depends_on:
  - README.md
  - 01-foundations.md
  - 02-module-anatomy-and-public-contracts.md
owns:
  - shared-kernel and shared-UI boundaries
  - promotion rules
  - platform ownership
  - composition-root ownership
  - runtime initialization and import/build isolation
  - configuration and secret boundary
---

# Shared kernel, shared UI, and platform boundaries

> Loading rule: code leaves a business module only when its new owner and stability contract are clearer than its original owner.

## Logical map

```text
shared/
├── kernel/        small pure cross-module concepts
└── ui/            reusable presentation primitives when the system has a UI

platform/
├── config/
├── auth/
├── database/
├── messaging/
├── telemetry/
└── runtime-adapters/

app/ or entrypoints/
└── composition/   web, worker, CLI, test wiring
```

Names are replaceable. The ownership differences are not.

## Rule `SHARED-KERNEL-01`: keep the shared kernel small and pure

The shared kernel contains stable concepts that genuinely mean the same thing across modules, such as a common identifier representation or a carefully agreed cross-domain value type.

It must not contain:

- one module's business vocabulary or permissions;
- database, framework, transport, or vendor types;
- mutable global state;
- generic repositories, service locators, or catch-all utilities;
- behavior promoted only because two files look similar.

Every kernel addition increases coupling between modules. Prefer duplication of a small unstable concept over premature shared ownership.

## Rule `SHARED-UI-01`: shared UI renders resolved contracts

When the product has a user interface, shared UI may own accessible, themeable, reusable presentation and interaction primitives.

Shared UI accepts resolved values, generic configuration, state, and callbacks. It must not:

- import a business module;
- fetch module data or select application commands;
- interpret business statuses, permissions, or messages;
- own module query keys or transport payloads;
- weaken native accessibility to simplify its API.

Promote the reusable shell; keep business labels, fields, policies, and actions in the owning module.

## Rule `SHARED-PROMOTION-01`: promote semantic stability, not repetition

Promotion requires all of:

1. one clear owner and purpose after promotion;
2. consumers share the same semantics, not merely similar syntax;
3. the contract is less volatile than module-specific policy;
4. the dependency direction remains acyclic;
5. the contract can be verified independently;
6. an existing platform, language, or library primitive does not already solve it.

Multiple consumers are useful evidence, not an automatic rule. App-wide concerns may begin shared; two consumers with different meanings should remain separate.

Promotion evidence compares complete lifecycle semantics, including success, failure and thrown-error handling; meaningful `false`, `null`, zero, empty and omitted values; callback/effect ordering; and reset/close timing when observable. Similar syntax with different authorization, labels, fields, messages, actions, or lifecycle policy remains module-owned. Candidate classification and closure follow [`REFACTOR-CANDIDATE-01`](16-refactor-and-evolution.md#rule-refactor-candidate-01-metrics-nominate-candidates-not-solutions) during brownfield work.

## Rule `PLATFORM-BOUNDARY-01`: platform owns mechanisms, not product policy

Platform code initializes and operates technical capabilities shared by entrypoints or adapters:

- validated configuration and secrets;
- authentication/session mechanisms;
- database, cache, queue, and object-storage clients;
- logging, metrics, tracing, and health primitives;
- process lifecycle, scheduling, and runtime integration.

Platform code may depend on external libraries. It does not own business authorization, state transitions, domain retry rules, product messages, or module data orchestration.

Modules reach platform mechanisms through owned ports when isolation or deterministic testing matters. A platform client must not become an unrestricted global service locator.

## Rule `COMPOSITION-ROOT-01`: wire concrete dependencies at entrypoints

The composition root is the only place that knows both abstract ports and selected concrete adapters.

Create one root per executable boundary when lifecycles differ:

```text
web root       -> HTTP/UI presentation + application modules + adapters
worker root    -> event/job handlers + application modules + adapters
CLI root       -> command presentation + application modules + adapters
test root      -> application modules + controlled adapters
```

The root owns construction order, dependency lifetimes, startup validation, and graceful shutdown. It contains no business workflow.

Prefer explicit factories/constructor parameters. A dependency-injection container is optional; hidden runtime lookup from arbitrary modules is not.

## Rule `RUNTIME-INITIALIZATION-01`: importing code does not start the runtime

Import, static analysis, and test discovery of reusable modules must not open data/network connections, schedule work, mutate external state, construct effectful clients or clients requiring runtime secrets/I/O, or demand runtime-only secrets. Inert factories and configuration values are allowed. Initialize runtime mechanisms at the owning operation or executable composition root, where startup validation, dependency lifetime, and shutdown are explicit.

Declare an artifact-build dependency separately from a runtime-only dependency. A claim that `check` or `build` is independent of an external service is proven with runtime-only secrets absent and relevant endpoints unreachable, while also verifying that no connection attempt occurred. A successful build while live services are reachable proves no such independence. A legitimate build-time dependency names its owner, purpose, isolated source, secret boundary, failure behavior, and reproducible evidence. Apply the execution-based negative proof in [`TEST-SEAM-01`](14-testing-and-architecture-fitness.md#rule-test-seam-01-design-controllable-boundaries); apply [`FITNESS-CHECK-PROOF-01`](14-testing-and-architecture-fitness.md#rule-fitness-check-proof-01-architecture-checkers-prove-that-they-can-fail) when a static checker enforces this invariant.

## Rule `CONFIG-BOUNDARY-01`: configuration has one validated boundary

Only the configuration/platform boundary reads raw environment, secret providers, process arguments, or deployment metadata directly.

Classify values before implementation:

| Kind | Examples | Policy |
| --- | --- | --- |
| Build-time | Compile target, optional static asset settings | Immutable after build; never hold secrets exposed to clients |
| Runtime environment | Host, timeouts, connection endpoints | Validate at startup; explicit environment precedence |
| Secret | Credentials, signing keys | Server/process only; redact from logs and diagnostics |
| Feature flag | Controlled rollout or kill switch | Named owner, default, expiry/review date, removal plan |
| Product/tenant setting | Business-configurable behavior | Store behind an application-owned contract, not arbitrary environment variables |

Configuration rules:

- parse into a typed/validated immutable object;
- fail fast for missing or invalid required values;
- make defaults explicit and safe;
- expose only the smallest approved public subset;
- provide a sanitized template listing names, purpose, and example shape;
- do not log secrets, raw connection strings, personal data, or full configuration dumps;
- inject configuration into adapters instead of importing environment access throughout the repo.

Test and local overrides use the same schema. Silent production fallbacks are forbidden when they could weaken security or data integrity.

## Ownership decision

| Signal | Owner |
| --- | --- |
| Knows one business capability, invariant, or message | Business module |
| Pure concept deliberately shared across domains | `shared/kernel` |
| Generic resolved presentation/interaction primitive | `shared/ui` |
| Initializes technical runtime mechanism | `platform` |
| Implements one module's external-I/O port | That module's `adapters` |
| Selects concrete adapter and lifetime for an executable | Composition root |
| Maps transport/UI protocol | Presentation adapter |

Database and vendor implementations are not automatically global platform code. Put shared connection/client mechanics in platform; keep module-specific queries and protocol translation in module adapters.

## Stop conditions

Stop and re-evaluate when:

- shared code imports a business module;
- a kernel API contains source-module vocabulary;
- a platform helper decides business policy;
- modules pull concrete dependencies from a global container;
- arbitrary files read environment variables;
- a feature flag has no owner or removal condition;
- promotion is justified only by line-count reduction;
- a wrapper hides required native capability without adding stable semantics.

Use [04-dependency-contracts-and-sync-flows.md](04-dependency-contracts-and-sync-flows.md) for dependency direction and runtime flow through the composition root.
