# Preset catalog

This directory defines complete, versioned stack presets. It intentionally contains **no runnable preset yet**. A future preset is a tested reference implementation plus the agent skills and evidence needed to evolve it without losing its code patterns.

Read:

- [`PRESET-CONTRACT.md`](PRESET-CONTRACT.md) for package, manifest, compatibility, source, design, and materialization rules;
- [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md) for skill triggers, resources, verification, and evaluation;
- [`preset.schema.json`](preset.schema.json) for the machine-checkable `preset.json` shape;
- [`../blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md`](../blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md) for the author/instantiate workflow;
- [`../blueprint/reference-app-blueprint/11-preset-agent-skills-and-design-evidence.md`](../blueprint/reference-app-blueprint/11-preset-agent-skills-and-design-evidence.md) for skill and design-evidence requirements.

## Required package shape

```text
docs/presets/<preset-id>/
├── README.md
├── preset.json
├── template/
│   ├── <framework-default root files>
│   ├── public/                         # when selected by the stack
│   └── src/
│       ├── app/
│       ├── lib/
│       ├── shared/
│       └── features/
├── guides/
│   ├── <preset-id>-analyze-request/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml         # required when targets include Codex
│   ├── <preset-id>-lib/SKILL.md
│   ├── <preset-id>-shared/SKILL.md
│   ├── <preset-id>-feature/SKILL.md
│   ├── <preset-id>-app/SKILL.md
│   ├── <preset-id>-new-pattern/SKILL.md
│   ├── <preset-id>-ui/SKILL.md
│   ├── <preset-id>-audit-changes/SKILL.md  # optional, exact capability key
│   └── <preset-id>-publish/SKILL.md        # optional, exact capability key
├── patterns/
│   ├── catalog.json
│   ├── exemplars/<pattern-id>/
│   └── fixtures/<pattern-id>/{positive,negative}/
├── design/
│   ├── ui-contract.json
│   └── evidence/
└── verification/
    ├── commands.json                  # digested argv-based command lanes
    ├── sources.json
    ├── skill-evals.json
    ├── integrity.json                 # required from candidate onward
    ├── scripts/
    ├── evals/{cases,results}/
    └── evidence/
```

Each skill may add only the `references/`, `scripts/`, or `assets/` resources it actually uses. Do not add a README, changelog, installation guide, or duplicate reference text inside a skill package. A preset may add narrowly scoped skills, but it must keep the seven canonical capabilities above. `audit-changes` and `publish` are the standardized optional keys; every declared skill must have forward-evaluation coverage.

Every Codex-targeted skill also provides `agents/openai.yaml` with nonempty `interface.display_name`, `interface.short_description`, and a `default_prompt` that names `$<preset-id>-<capability>`. This metadata is a platform adapter; `SKILL.md` remains the portable trigger/workflow authority.

Framework-owned files stay in their normal locations. For Next.js with the `src` option, application code lives under `src/`; `package.json`, lockfiles, `next.config.*`, `tsconfig.json`, environment files, `public/`, and other tool-defined root paths remain at the project root. Authors must verify the topology against official documentation for the exact pinned framework version.

## Lifecycle

| Status | Meaning |
| --- | --- |
| `experimental` | Contract or evidence is incomplete |
| `candidate` | Declared flows and forward evals pass; independent use is pending |
| `verified` | Exact-version clean-room install, declared flows, dual review, freshness checks, and a distinct independent-use run pass |
| `deprecated` | Supported only for migration during a stated window |
| `retired` | Must not be selected for new apps |

Status belongs to one immutable preset version and blueprint revision. A dependency, source snapshot, skill, design contract, or verifier change makes the prior evidence stale until the affected checks run again.

## Selection and instantiation

An agent compares the requested outcome with the preset's capabilities, compatibility, hard prerequisites, and verified flows. It must not claim support from the presence of sample code alone or silently combine modules from different presets.

Instantiation materializes all declared root and `src/` entries, installs exact dependencies, maps every declared skill package through the app's `AGENTS.md`, writes `docs/governance/preset-lock.json`, verifies integrity, and executes the locked `install`, `doctor`, `test`, `check`, `build`, and `start-smoke` command lanes in clean-room verification. Local evolution remains allowed; later upgrades compare the lock, local decisions, and target preset instead of overwriting user changes.
