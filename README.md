# AI Web App Blueprint

A public, cloneable blueprint for building web applications with AI agents without letting generated code drift away from the repository's architecture.

This repository deliberately separates three concerns:

- [`docs/blueprint`](docs/blueprint/README.md) is the stack-neutral source of truth.
- [`docs/presets`](docs/presets/README.md) is the catalog and contract for complete, versioned stack presets.
- `src/` is application code and does **not** exist until a preset is selected and instantiated.

No runnable preset is included yet. The current repository is the governed foundation from which presets will be authored and verified.

## Use the repository

```bash
git clone https://github.com/phamviet86/ai-web-app-blueprint.git
cd ai-web-app-blueprint
```

Then give an AI agent a product request and ask it to start at [`AGENTS.md`](AGENTS.md). The agent must first determine whether it is maintaining the blueprint, authoring a preset, instantiating a preset, or changing an existing app.

## Repository shape

```text
.
├── AGENTS.md                 # AI task router
├── START-HERE.md             # Human and AI adoption entrypoint
├── docs/
│   ├── blueprint/            # Architecture source of truth
│   ├── presets/              # Preset catalog, contracts, and future preset packages
│   └── governance/           # App-local lock/evidence location after instantiation
└── src/                      # Absent until an app is instantiated
```

For a Next.js preset, application code may live under `src/`, for example `src/app`, `src/lib`, `src/shared`, and `src/features`. Files that Next.js normally keeps at the project root remain there: package and lock files, framework/TypeScript/lint configuration, environment files, `public/`, and other tool-owned root paths. A preset describes both root files and `src/`; it does not force every project file into `src/`.

## Main workflows

1. **Maintain the blueprint** — improve portable architecture rules in `docs/blueprint`.
2. **Author a preset** — create one complete exact-version implementation under `docs/presets/<preset-id>` and verify its inter-layer walking slices.
3. **Instantiate an app** — select a compatible preset, materialize its root and `src/` files, record the selected revision, then route all code changes through that preset's guides.
4. **Extend an app** — let the user describe the outcome; the AI request router selects the relevant lib/shared/feature/app guide. A genuinely new pattern returns to the exact blueprint owner before it changes repository conventions.

Start with [`START-HERE.md`](START-HERE.md). Preset authors should read the [`preset contract`](docs/presets/PRESET-CONTRACT.md) and the blueprint's [`preset authoring and instantiation guide`](docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md).

## Documentation quality checks

```bash
PYTHONPATH=docs/blueprint python3 -m unittest discover -s docs/blueprint/scripts -p 'test_*.py'
python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .
python3 docs/blueprint/scripts/score_readiness.py docs/blueprint/reference-app-blueprint/examples/basic-web-artifacts/readiness.json --json --expect not-ready
```

Passing these checks proves structural documentation conformance, not that an app or preset is production-ready. See [`docs/blueprint/MATURITY.md`](docs/blueprint/MATURITY.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
