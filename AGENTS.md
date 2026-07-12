# AI operating instructions

Start every request by reading this file. Treat [`docs/blueprint`](docs/blueprint/README.md) as architecture source of truth and an instantiated preset's locked guides as the code-shape authority for that app.

## 1. Resolve operating mode

1. Inspect the user's request, whether `src/` exists, and whether `docs/governance/preset-lock.json` exists.
2. Declare exactly one primary mode:
   - `BLUEPRINT_MAINTENANCE`
   - `AUTHOR_PRESET`
   - `APP_BOOTSTRAP`
   - `APP_DEVELOPMENT`
   - `NEW_PATTERN`
3. Do not create app source in blueprint or preset-authoring mode.
4. Do not claim a preset is selected or verified without its manifest, exact version, compatibility evidence, and clean-room verification.

## 2. Route by authority

| Mode/task | Required authority | Output boundary |
| --- | --- | --- |
| Maintain source-of-truth rules | `docs/blueprint/README.md` task router | Owning blueprint guide, contracts, tests, changelog |
| Author or upgrade a preset | `docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md` and `docs/presets/PRESET-CONTRACT.md` | `docs/presets/<preset-id>/**` only |
| Instantiate an app | selected preset manifest, template, verification, and guides | framework-default root files, `src/**`, `docs/governance/**` |
| Analyze a user request | locked preset `guides/analyze-request.md` | task classification and ordered guide list |
| Add/modify library or adapter | locked preset `guides/lib.md` | preset-owned lib/data/auth/config paths |
| Add/modify shared code | locked preset `guides/shared.md` | preset-owned shared paths |
| Add/modify feature | locked preset `guides/feature.md` | preset-owned feature paths |
| Add/modify app composition | locked preset `guides/app.md` | routes, layouts, providers, and composition only |
| Introduce a new pattern | locked preset `guides/new-pattern.md`, then exact blueprint owner | smallest local pattern plus fitness evidence and guide/catalog delta |

The canonical guide filenames above are required for every preset. A preset may add narrower guides, but its request analyzer must still route to these six capabilities.

## 3. Code invariants after app bootstrap

- `app` composes routes, layouts, entrypoints, and providers; it does not absorb feature policy.
- `features` own business vocabulary, schemas, use cases/services, authorization policy, repositories, UI configuration, and public contracts.
- `lib` owns stack mechanisms and adapters, not feature field/operator/join policy.
- `shared` owns reusable mechanics and interaction contracts, not feature labels, permissions, columns, fields, or actions.
- Browser payloads never expose raw ORM column names, joins, or query objects. Feature query policy maps a validated public request to allowed repository operations and mandatory access scope.
- Identity/session adapters establish a trusted subject; feature authorization decides resource/tenant access; repositories enforce required scope.
- A surface is incomplete unless loading, empty, error, stale/success, denied, accessibility, and responsive behavior are defined where applicable.
- A change is complete only after the relevant preset guide verification passes and documentation/evidence deltas are recorded.

## 4. New-pattern escape hatch

Use `NEW_PATTERN` only after searching the locked preset and live app for a fitting pattern. Then:

1. name the missing capability and why existing patterns fail;
2. read the exact owning blueprint guide, not the whole package;
3. implement the smallest local shape and prove one closed flow;
4. add architecture/contract tests proportional to the boundary;
5. update the preset pattern catalog and relevant guide if the pattern is reusable;
6. create an ADR when a public or cross-layer contract changes;
7. keep one-off business behavior inside its feature instead of promoting it.

Stop for user direction when the change requires a new product/risk decision, destructive conflict resolution, or a materially different stack. Otherwise continue through verification.
