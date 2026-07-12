# Preset catalog

This directory will contain complete, versioned stack presets. It currently contains **no runnable preset**; the files here define how future presets must be authored, verified, selected, instantiated, and evolved.

Read:

- [`PRESET-CONTRACT.md`](PRESET-CONTRACT.md) for package shape, manifest, capability, compatibility, and materialization rules;
- [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md) for the required request router and code-change guides;
- [`../blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md`](../blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md) for the source-of-truth author/instantiate workflow.

## Planned directory shape

```text
docs/presets/<preset-id>/
├── README.md
├── preset.yaml
├── template/
│   ├── <framework-default root files>
│   ├── public/                 # when selected by the stack
│   └── src/
│       ├── app/
│       ├── lib/
│       ├── shared/
│       └── features/
├── guides/
│   ├── analyze-request.md
│   ├── lib.md
│   ├── shared.md
│   ├── feature.md
│   ├── app.md
│   └── new-pattern.md
└── verification/
    ├── README.md
    └── <tests, fixtures, and evidence descriptors>
```

Framework-owned root files stay at their normal root locations. For Next.js with the `src` option, `src/app` and application modules live under `src/`, while `package.json`, lockfiles, `next.config.*`, `tsconfig.json`, environment files, `public/`, and other tool-defined root paths remain outside it.

Preset authors must re-check this topology against the pinned framework version. The current rule matches the official [Next.js `src` folder convention](https://nextjs.org/docs/app/api-reference/file-conventions/src-folder): application code may move under `src`, while `public` and project configuration remain at the project root.

## Lifecycle

| Status | Meaning |
| --- | --- |
| `experimental` | Contract may change; evidence is incomplete |
| `candidate` | Package shape and declared walking slices pass, awaiting independent use |
| `verified` | Exact-version clean-room install and every declared verified flow pass |
| `deprecated` | Supported only for migration during a stated window |
| `retired` | Must not be selected for new apps |

Status applies to a specific preset version and blueprint revision. It never transfers automatically to another framework/library version.

## Selection and instantiation

An AI agent must compare user requirements with the preset's provided/verified/conditional/unsupported matrix before selection. Instantiation materializes the preset's complete root and `src/` contract, installs its exact dependencies, writes `docs/governance/preset-lock.json`, and runs the preset verification commands. It must not silently combine arbitrary modules from different presets.

After instantiation, users may modify both the app and their local blueprint/preset copy. Divergence is explicit: upgrades compare the lock, local decisions, and target preset; they never overwrite local work merely because the upstream preset changed.
