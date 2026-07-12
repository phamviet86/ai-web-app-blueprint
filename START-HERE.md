# Start here

This repository supports five distinct modes. Declare one before changing files.

| Mode | Choose it when | First read | Allowed primary output |
| --- | --- | --- | --- |
| `BLUEPRINT_MAINTENANCE` | Improving portable rules or governance | [`docs/blueprint/README.md`](docs/blueprint/README.md) | `docs/blueprint/**` |
| `AUTHOR_PRESET` | Creating or upgrading a reusable stack combo | [`docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md`](docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md) | `docs/presets/<preset-id>/**` |
| `APP_BOOTSTRAP` | Creating an app from a verified preset (`INSTANTIATE_PRESET` phase in the reference-app guides) | [`docs/presets/README.md`](docs/presets/README.md) | framework root files, `src/**`, and preset lock/evidence |
| `APP_DEVELOPMENT` | Changing an already-instantiated app | [`AGENTS.md`](AGENTS.md) plus the locked preset skills | paths owned by the selected task skill |
| `NEW_PATTERN` | No locked preset pattern can satisfy a required capability | [`AGENTS.md`](AGENTS.md), locked `new-pattern` skill, then the exact blueprint owner | smallest local pattern, fitness evidence, and approved catalog/ADR delta |

The preset catalog is intentionally empty today. Do not pretend a preset is verified or generate an app from a nonexistent preset. If a user needs a new combo, switch explicitly to `AUTHOR_PRESET`, finish and verify that preset, then instantiate it as a separate operation.

## Suggested prompts

Maintain the blueprint:

> Read AGENTS.md and evaluate this architecture requirement against the source-of-truth blueprint. Update only the owning rule and its required contracts/tests.

Author a preset later:

> Read AGENTS.md. In AUTHOR_PRESET mode, create an exact-version preset for my selected stack. Prove its read, write, and auth walking slices before marking any capability verified.

Instantiate an app later:

> Read AGENTS.md. Analyze my requirements, select a compatible verified preset, show fit and gaps, then instantiate it without changing the preset's architectural patterns.

Develop an existing app:

> Read AGENTS.md and the selected preset lock. Turn this requirement into a vertical task graph, select locked pattern IDs and matching preset skills, then satisfy each skill's completion and verification criteria.

## Human decisions AI must not invent

- product scope, risk acceptance, owners, and release approval;
- whether a preset fit gap is acceptable;
- destructive replacement of conflicting app files;
- promotion of a local exception into a reusable repository pattern.

All other safe, in-scope discovery and verification should proceed without turning the setup into an open-ended technology interview.
