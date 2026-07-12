from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.validate_presets import (
    CORE_FIELDS,
    REQUIRED_SKILLS,
    PresetValidator,
    validate_presets,
)


SKILL_BODY = """---
name: {name}
description: Use when a task belongs to the {capability} capability.
---

# {capability}

## Inputs

Read the request and [preset reference](references/preset.md).

## Workflow

Follow the preset pattern catalog.

## Completion criteria

Close the requested flow.

## Verification

Run the declared verifier.

## Stop conditions

Stop when a product decision is missing.
"""


class PresetFixture:
    def __init__(self, root: Path, preset_id: str = "next-ts-example"):
        self.root = root
        self.preset = root / preset_id
        self.manifest_path = self.preset / "preset.json"
        self.preset_id = preset_id

    def write(self, relative: str, content: str = "fixture\n") -> Path:
        path = self.preset / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative: str, value) -> Path:
        return self.write(relative, json.dumps(value, indent=2) + "\n")

    @staticmethod
    def digest(path: Path) -> str:
        if path.is_file():
            return hashlib.sha256(path.read_bytes()).hexdigest()
        return PresetFixture.tree_digest(path, b"preset-skill-tree-v1")

    @staticmethod
    def tree_digest(path: Path, domain: bytes) -> str:
        digest = hashlib.sha256()
        digest.update(domain + b"\0")
        files = sorted(
            (item for item in path.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(path).as_posix().encode("utf-8"),
        )
        for child in files:
            relative = child.relative_to(path).as_posix().encode("utf-8")
            content = child.read_bytes()
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        return digest.hexdigest()

    def read_manifest(self):
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def update_manifest(self, manifest) -> None:
        self.write_json("preset.json", manifest)

    def refresh_digest(self, section: str, path: Path) -> None:
        manifest = self.read_manifest()
        if section == "patterns":
            manifest[section]["sha256"] = self.tree_digest(
                self.preset / "patterns", b"preset-pattern-tree-v1"
            )
        else:
            manifest[section]["sha256"] = self.digest(path)
        self.update_manifest(manifest)

    def build(self) -> None:
        self.write("README.md", "# Example preset\n")
        self.write("template/example.txt")

        skills = {}
        for capability in sorted(REQUIRED_SKILLS):
            name = f"{self.preset_id}-{capability}"
            skill_dir = f"guides/{name}"
            skill_path = self.write(
                f"{skill_dir}/SKILL.md",
                SKILL_BODY.format(name=name, capability=capability),
            )
            self.write(f"{skill_dir}/references/preset.md", "# Preset reference\n")
            self.write(
                f"{skill_dir}/agents/openai.yaml",
                "interface:\n"
                f"  display_name: {capability} workflow\n"
                f"  short_description: Route {capability} work through the preset\n"
                f"  default_prompt: Use ${name} to complete this preset task.\n",
            )
            skills[capability] = {
                "name": name,
                "path": skill_dir,
                "sha256": self.digest(skill_path.parent),
                "invocation": {"implicit": f"Use for {capability} tasks"},
                "targets": ["codex"],
            }

        pattern_evidence = self.write_json(
            "verification/evidence/pattern.json",
            {
                "conformance": "pass",
                "outcome": "pass",
                "observed_at": "2026-07-12T00:00:00Z",
            },
        )
        pattern_evidence_ref = {
            "path": str(pattern_evidence.relative_to(self.preset)),
            "sha256": self.digest(pattern_evidence),
        }
        exemplar = self.write("patterns/exemplars/feature-list/example.txt")
        verifier = self.write("patterns/verifiers/feature-list.py", "# verifier\n")
        positive = self.write("patterns/fixtures/feature-list/positive/example.txt")
        negative = self.write("patterns/fixtures/feature-list/negative/example.txt")
        catalog_path = self.write_json(
            "patterns/catalog.json",
            {
                "patterns": [
                    {
                        "id": "feature-list",
                        "layer": "feature",
                        "intent": "Render one feature-owned collection through shared mechanics.",
                        "applicability": {
                            "use_when": ["The feature exposes a typed list result."],
                            "avoid_when": [],
                        },
                        "public_contract": {
                            "inputs": ["list-request"],
                            "outputs": ["list-result"],
                            "states": ["loading", "empty", "error", "success"],
                        },
                        "skills": ["feature", "ui"],
                        "allowed_dependencies": ["shared"],
                        "forbidden_dependencies": ["app"],
                        "examples": [str(exemplar.relative_to(self.preset))],
                        "verifier": str(verifier.relative_to(self.preset)),
                        "fixtures": {
                            "positive": [str(positive.relative_to(self.preset))],
                            "negative": [str(negative.relative_to(self.preset))],
                        },
                        "evidence": [pattern_evidence_ref],
                    }
                ]
            },
        )
        ledger_path = self.write_json(
            "verification/sources.json",
            {
                "sources": [
                    {
                        "id": "next-docs",
                        "kind": "context7",
                        "url": "https://nextjs.org/docs",
                        "requested_ref": "16.0.0",
                        "resolved_revision": "a" * 40,
                        "retrieved_at": "2026-07-12T00:00:00Z",
                        "license": "MIT",
                        "claims": ["Framework API contract"],
                        "invalidation_triggers": ["Pinned version changes"],
                        "library_id": "/vercel/next.js",
                        "queries": ["src folder convention"],
                        "official_urls": ["https://nextjs.org/docs"],
                    },
                    {
                        "id": "ux-reference",
                        "kind": "ux-heuristic",
                        "url": "https://github.com/example/ux",
                        "requested_ref": "main",
                        "resolved_revision": "b" * 40,
                        "retrieved_at": "2026-07-12T00:00:00Z",
                        "license": "MIT",
                        "claims": ["UX heuristic input"],
                        "invalidation_triggers": ["Source revision changes"],
                        "acquisition_mode": "read-only",
                    },
                ]
            },
        )
        design_contract = self.write_json(
            "design/ui-contract.json",
            {
                "version": "1.0.0",
                "brief": {"users": ["operator"], "top_tasks": ["review records"]},
                "tokens": {
                    "primitive": {"spacing": "4px base"},
                    "semantic": {"surface": "canvas"},
                    "component_state": {"focus": "focus-ring"},
                },
                "surfaces": ["feature-list"],
                "states": [
                    "loading",
                    "empty",
                    "error",
                    "stale",
                    "denied",
                    "success",
                ],
                "responsive": {"narrow": "single-column", "wide": "data-grid"},
                "accessibility": {"target": "WCAG 2.2 AA"},
                "framework_bindings": ["next@16.0.0"],
                "source_ids": ["next-docs"],
            },
        )
        design_evidence = self.write_json(
            "design/evidence/initial.json",
            {"status": "planning-only"},
        )
        eval_evidence = self.write_json(
            "verification/evidence/forward-eval.json",
            {
                "conformance": "pass",
                "outcome": "pass",
                "observed_at": "2026-07-12T00:00:00Z",
            },
        )
        self.write_json(
            "verification/skill-evals.json",
            {
                "cases": [
                    {"id": kind, "kind": kind, "skills": skills}
                    for kind, skills in (
                        ("single-layer", ["shared", "app"]),
                        ("cross-layer", ["analyze-request", "feature"]),
                        ("new-pattern", ["new-pattern"]),
                        ("unsafe-boundary", ["lib"]),
                        ("ui-research", ["ui"]),
                    )
                ]
            },
        )

        self.update_manifest(
            {
                "schema_version": "1.0.0",
                "preset_id": self.preset_id,
                "preset_version": "0.1.0",
                "blueprint_version": "0.11.0",
                "blueprint_revision": "c" * 40,
                "status": "experimental",
                "archetype": "full-stack-web",
                "stack": [
                    {"package": "next", "version": "16.0.0", "source_id": "next-docs"}
                ],
                "capabilities": ["read-surface"],
                "verified_flows": [],
                "materialization": {"root": "template"},
                "skills": skills,
                "patterns": {
                    "catalog": "patterns/catalog.json",
                    "sha256": self.tree_digest(
                        catalog_path.parent, b"preset-pattern-tree-v1"
                    ),
                },
                "sources": {
                    "ledger": "verification/sources.json",
                    "sha256": self.digest(ledger_path),
                },
                "design": {
                    "contract": "design/ui-contract.json",
                    "sha256": self.digest(design_contract),
                    "evidence": [str(design_evidence.relative_to(self.preset))],
                },
                "verification": {"skill_evals": "verification/skill-evals.json"},
            }
        )
        evals_path = self.preset / "verification/skill-evals.json"
        evals = json.loads(evals_path.read_text(encoding="utf-8"))
        input_digests = PresetValidator(self.root).evaluation_input_locks(self.preset)
        evidence_ref = {
            "path": str(eval_evidence.relative_to(self.preset)),
            "sha256": self.digest(eval_evidence),
        }
        for case in evals["cases"]:
            case["prompt"] = f"Complete the {case['kind']} task."
            case["input_digests"] = input_digests
            case["route_trace"] = [f"skill:{case['skills'][0]}"]
            case["conformance"] = {"result": "pass", "evidence": [evidence_ref]}
            case["outcome"] = {"result": "pass", "evidence": [evidence_ref]}
        self.write_json("verification/skill-evals.json", evals)


class PresetValidatorTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> PresetFixture:
        fixture = PresetFixture(root)
        fixture.build()
        return fixture

    def test_zero_presets_is_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            findings, counts = validate_presets(Path(temporary))
        self.assertEqual(findings, [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (0, 0, 0))

    def test_schema_parses_and_matches_canonical_registry(self):
        schema_path = Path(__file__).resolve().parents[2] / "presets/preset.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), CORE_FIELDS)
        self.assertEqual(set(schema["properties"]["skills"]["required"]), REQUIRED_SKILLS)

        references = set()

        def collect(value):
            if isinstance(value, dict):
                reference = value.get("$ref")
                if isinstance(reference, str):
                    references.add(reference)
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(schema)
        definitions = set(schema.get("$defs", {}))
        unresolved = {
            reference
            for reference in references
            if reference.startswith("#/$defs/") and reference.removeprefix("#/$defs/") not in definitions
        }
        self.assertEqual(unresolved, set())

    def test_skill_tree_digest_matches_golden_vector(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "references").mkdir()
            (root / "SKILL.md").write_bytes(b"alpha\n")
            (root / "references/preset.md").write_bytes(b"beta\n")
            actual = PresetValidator.digest_path(root)
        self.assertEqual(
            actual,
            "5b234428c14db2b689aab8863aeda72923d1bd6dac65c20a2dcd7eeb3772d4c2",
        )

    def test_accepts_valid_preset(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            findings, counts = validate_presets(fixture.root)
        self.assertEqual([finding.render() for finding in findings], [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (1, 7, 1))

    def test_rejects_bad_frontmatter_and_missing_trigger(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            skill_path = fixture.preset / "guides/next-ts-example-ui/SKILL.md"
            text = skill_path.read_text(encoding="utf-8")
            text = text.replace(
                "description: Use when a task belongs to the ui capability.",
                "description: Handle UI work.\nextra: forbidden",
            )
            skill_path.write_text(text, encoding="utf-8")
            manifest = fixture.read_manifest()
            manifest["skills"]["ui"]["sha256"] = fixture.digest(skill_path.parent)
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("exactly name and description" in message for message in messages))
        self.assertTrue(any("'Use when' trigger clause" in message for message in messages))

    def test_invalid_utf8_skill_files_report_without_crashing(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            skill_dir = fixture.preset / "guides/next-ts-example-ui"
            (skill_dir / "SKILL.md").write_bytes(b"\xff\xfe")
            manifest = fixture.read_manifest()
            manifest["skills"]["ui"]["sha256"] = fixture.digest(skill_dir)
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(any("SKILL.md is not UTF-8" in finding.message for finding in findings))

    def test_invalid_utf8_codex_metadata_reports_without_crashing(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            skill_dir = fixture.preset / "guides/next-ts-example-feature"
            (skill_dir / "agents/openai.yaml").write_bytes(b"\xff\xfe")
            manifest = fixture.read_manifest()
            manifest["skills"]["feature"]["sha256"] = fixture.digest(skill_dir)
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any("agents/openai.yaml is not UTF-8" in finding.message for finding in findings)
        )

    def test_rejects_structured_frontmatter_and_noncanonical_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            skill_dir = fixture.preset / "guides/next-ts-example-ui"
            skill_path = skill_dir / "SKILL.md"
            text = skill_path.read_text(encoding="utf-8")
            text = text.replace(
                "description: Use when a task belongs to the ui capability.",
                "description: {Use when: ui}",
            )
            skill_path.write_text(text, encoding="utf-8")
            manifest = fixture.read_manifest()
            manifest["skills"]["ui"]["sha256"] = fixture.digest(skill_dir)
            manifest["skills"]["ui"]["targets"] = ["codex "]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("plain or quoted scalar strings" in message for message in messages))
        self.assertTrue(any("skill ui targets" in message for message in messages))

    def test_rejects_missing_required_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            del manifest["skills"]["ui"]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any("missing required skill capability: ui" in finding.message for finding in findings)
        )

    def test_rejects_reused_canonical_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["ui"] = dict(manifest["skills"]["feature"])
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("skill ui name must equal" in message for message in messages))
        self.assertTrue(any("duplicate skill path" in message for message in messages))

    def test_rejects_stale_skill_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["feature"]["sha256"] = "0" * 64
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(any("stale skill feature sha256" in finding.message for finding in findings))

    def test_skill_digest_covers_references(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            reference = fixture.preset / "guides/next-ts-example-feature/references/preset.md"
            reference.write_text("# Changed reference\n", encoding="utf-8")
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(any("stale skill feature sha256" in finding.message for finding in findings))

    def test_rejects_missing_pattern_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog_path = fixture.preset / "patterns/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["patterns"][0]["examples"] = ["template/missing.ts"]
            catalog["patterns"][0]["fixtures"]["negative"] = ["verification/missing.txt"]
            fixture.write_json("patterns/catalog.json", catalog)
            fixture.refresh_digest("patterns", catalog_path)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("template/missing.ts" in message for message in messages))
        self.assertTrue(any("verification/missing.txt" in message for message in messages))

    def test_rejects_incomplete_source_ledger_and_evals(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            ledger_path = fixture.preset / "verification/sources.json"
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            del ledger["sources"][0]["claims"]
            del ledger["sources"][0]["queries"]
            ledger["sources"][1]["acquisition_mode"] = "copied"
            fixture.write_json("verification/sources.json", ledger)
            fixture.refresh_digest("sources", ledger_path)
            fixture.write_json(
                "verification/skill-evals.json",
                {"cases": [{"id": "one", "kind": "single-layer", "skills": ["unknown"]}]},
            )
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("missing required field: claims" in message for message in messages))
        self.assertTrue(any("Context7 source requires queries" in message for message in messages))
        self.assertTrue(any("acquisition_mode must be read-only" in message for message in messages))
        self.assertTrue(any("references unknown skill" in message for message in messages))
        self.assertTrue(any("skill evals missing required case: ui-research" in message for message in messages))

    def test_candidate_requires_integrity_and_clean_room_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["status"] = "candidate"
            manifest["verified_flows"] = ["read-surface"]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("verification.integrity" in message for message in messages))
        self.assertTrue(any("requires nonempty clean_room_evidence" in message for message in messages))

    def test_optional_verification_fields_are_validated_when_present(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["verification"]["integrity"] = {"bad": True}
            manifest["verification"]["independent_use_evidence"] = [
                {"path": "verification/missing.json", "sha256": "0" * 64}
            ]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("verification.integrity" in message for message in messages))
        self.assertTrue(any("verification/missing.json" in message for message in messages))

    def test_verified_rejects_weak_integrity_and_plain_text_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            integrity = fixture.write_json("verification/integrity.json", {"anything": True})
            clean_room = fixture.write("verification/evidence/clean-room.txt", "passed\n")
            manifest = fixture.read_manifest()
            manifest["status"] = "verified"
            manifest["verified_flows"] = ["read-surface"]
            manifest["verification"].update(
                {
                    "integrity": {
                        "path": str(integrity.relative_to(fixture.preset)),
                        "sha256": fixture.digest(integrity),
                    },
                    "clean_room_evidence": [
                        {
                            "path": str(clean_room.relative_to(fixture.preset)),
                            "sha256": fixture.digest(clean_room),
                        }
                    ],
                }
            )
            design_evidence = fixture.preset / "design/evidence/initial.json"
            manifest["design"]["evidence"] = [
                {
                    "path": str(design_evidence.relative_to(fixture.preset)),
                    "sha256": fixture.digest(design_evidence),
                }
            ]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("integrity algorithm must be sha256" in message for message in messages))
        self.assertTrue(any("integrity files must be a nonempty list" in message for message in messages))
        self.assertTrue(any("invalid clean-room evidence JSON" in message for message in messages))

    def test_accepts_verified_preset_with_locked_pass_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            observed_at = (
                datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            validator = PresetValidator(fixture.root)
            pattern_input_locks = validator.evaluation_input_locks(fixture.preset)
            pattern_input_locks.pop("patterns", None)
            pattern_evidence = fixture.write_json(
                "verification/evidence/pattern.json",
                {
                    "conformance": "pass",
                    "outcome": "pass",
                    "qualification": "verified",
                    "claim_type": "pattern",
                    "claim_id": "feature-list",
                    "observed_at": observed_at,
                    "input_digests": pattern_input_locks,
                },
            )
            catalog_path = fixture.preset / "patterns/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["patterns"][0]["evidence"][0]["sha256"] = fixture.digest(
                pattern_evidence
            )
            fixture.write_json("patterns/catalog.json", catalog)
            fixture.refresh_digest("patterns", catalog_path)

            claim_input_locks = validator.evaluation_input_locks(fixture.preset)
            capability_evidence = fixture.write_json(
                "verification/evidence/forward-eval.json",
                {
                    "conformance": "pass",
                    "outcome": "pass",
                    "qualification": "verified",
                    "claim_type": "capability",
                    "claim_id": "read-surface",
                    "observed_at": observed_at,
                    "input_digests": claim_input_locks,
                },
            )
            flow_evidence = fixture.write_json(
                "verification/evidence/read-surface-flow.json",
                {
                    "conformance": "pass",
                    "outcome": "pass",
                    "qualification": "verified",
                    "claim_type": "flow",
                    "claim_id": "read-surface",
                    "observed_at": observed_at,
                    "input_digests": claim_input_locks,
                },
            )

            eval_path = fixture.preset / "verification/skill-evals.json"
            capability_ref = {
                "path": str(capability_evidence.relative_to(fixture.preset)),
                "sha256": fixture.digest(capability_evidence),
            }
            flow_ref = {
                "path": str(flow_evidence.relative_to(fixture.preset)),
                "sha256": fixture.digest(flow_evidence),
            }
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            eval_input_locks = PresetValidator(
                fixture.root
            ).evaluation_input_locks(fixture.preset)
            for case in evals["cases"]:
                case["input_digests"] = eval_input_locks
                for verdict in ("conformance", "outcome"):
                    evidence_path = fixture.write_json(
                        f"verification/evals/results/{case['id']}-{verdict}.json",
                        {
                            "conformance": "pass",
                            "outcome": "pass",
                            "qualification": "verified",
                            "claim_type": f"skill-eval-{verdict}",
                            "claim_id": case["id"],
                            "observed_at": observed_at,
                            "input_digests": eval_input_locks,
                        },
                    )
                    case[verdict]["evidence"] = [
                        {
                            "path": str(evidence_path.relative_to(fixture.preset)),
                            "sha256": fixture.digest(evidence_path),
                        }
                    ]
            fixture.write_json("verification/skill-evals.json", evals)

            manifest = fixture.read_manifest()
            manifest["status"] = "verified"
            manifest["capabilities"] = [
                {
                    "id": "read-surface",
                    "status": "verified",
                    "providers": ["feature-list"],
                    "consumers": ["app-route"],
                    "payloads": ["list-request", "list-result"],
                    "states": ["loading", "empty", "error", "success"],
                    "constraints": ["authorized-scope"],
                    "patterns": ["feature-list"],
                    "evidence": [capability_ref],
                }
            ]
            manifest["verified_flows"] = [
                {
                    "id": "read-surface",
                    "capability_id": "read-surface",
                    "steps": ["request", "query", "render"],
                    "evidence": [flow_ref],
                }
            ]
            manifest["upgrade_policy"] = {
                "strategy": "explicit-merge",
                "breaking_change_policy": "require-decision",
                "stale_after_days": 30,
            }
            manifest["verification"]["skill_evals"] = {
                "path": str(eval_path.relative_to(fixture.preset)),
                "sha256": fixture.digest(eval_path),
            }
            fixture.update_manifest(manifest)
            input_locks = PresetValidator(fixture.root).evidence_input_locks(
                fixture.preset
            )

            design_evidence = fixture.write_json(
                "design/evidence/initial.json",
                {
                    "result": "pass",
                    "qualification": "verified",
                    "context": "ui-review",
                    "run_id": "ui-review-run",
                    "actor": "preset-author-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "clean-fixture",
                    "observed_at": observed_at,
                    "input_digests": input_locks,
                },
            )
            clean_room = fixture.write_json(
                "verification/evidence/clean-room.json",
                {
                    "result": "pass",
                    "qualification": "verified",
                    "context": "clean-room",
                    "run_id": "clean-room-run",
                    "actor": "preset-author-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "clean-fixture",
                    "observed_at": observed_at,
                    "input_digests": input_locks,
                    "commands": [{"command": "verify", "exit_code": 0}],
                },
            )
            independent = fixture.write_json(
                "verification/evidence/independent-use.json",
                {
                    "result": "pass",
                    "qualification": "verified",
                    "context": "independent-use",
                    "run_id": "independent-use-run",
                    "independent_from_run_id": "clean-room-run",
                    "actor": "independent-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "separate-fixture",
                    "observed_at": observed_at,
                    "input_digests": input_locks,
                    "commands": [{"command": "verify-independent", "exit_code": 0}],
                },
            )
            manifest = fixture.read_manifest()
            manifest["design"]["evidence"] = [
                {
                    "path": str(design_evidence.relative_to(fixture.preset)),
                    "sha256": fixture.digest(design_evidence),
                }
            ]
            manifest["verification"]["clean_room_evidence"] = [
                {
                    "path": str(clean_room.relative_to(fixture.preset)),
                    "sha256": fixture.digest(clean_room),
                }
            ]
            manifest["verification"]["independent_use_evidence"] = [
                {
                    "path": str(independent.relative_to(fixture.preset)),
                    "sha256": fixture.digest(independent),
                }
            ]
            fixture.update_manifest(manifest)

            integrity_records = []
            for path in sorted(
                (item for item in fixture.preset.rglob("*") if item.is_file()),
                key=lambda item: item.relative_to(fixture.preset).as_posix(),
            ):
                relative = path.relative_to(fixture.preset).as_posix()
                if relative == "preset.json":
                    continue
                integrity_records.append({"path": relative, "sha256": fixture.digest(path)})
            integrity = fixture.write_json(
                "verification/integrity.json",
                {
                    "algorithm": "sha256",
                    "result": "pass",
                    "generated_at": "2026-07-12T00:00:00Z",
                    "files": integrity_records,
                },
            )
            manifest = fixture.read_manifest()
            manifest["verification"]["integrity"] = {
                "path": str(integrity.relative_to(fixture.preset)),
                "sha256": fixture.digest(integrity),
            }
            fixture.update_manifest(manifest)

            findings, counts = validate_presets(fixture.root)
            changed_manifest = fixture.read_manifest()
            changed_manifest["stack"][0]["version"] = "99.0.0"
            fixture.update_manifest(changed_manifest)
            changed_findings, _ = validate_presets(fixture.root)
        self.assertEqual([finding.render() for finding in findings], [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (1, 7, 1))
        self.assertTrue(
            any(
                "input_digests.manifest_inputs is stale or misbound"
                in finding.message
                for finding in changed_findings
            )
        )
        self.assertTrue(
            any("requested_ref must equal the exact stack version" in finding.message for finding in changed_findings)
        )
        self.assertTrue(
            any("UI framework binding is not an exact stack item" in finding.message for finding in changed_findings)
        )

    def test_rejects_schema_shape_divergence(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["archetype"] = "NOT KEBAB"
            manifest["capabilities"] = [None]
            manifest["materialization"] = {"root": 42}
            manifest["unknown_typo"] = True
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("unknown manifest field: unknown_typo" in message for message in messages))
        self.assertTrue(any("archetype must be lowercase kebab-case" in message for message in messages))
        self.assertTrue(any("must be a kebab ID or capability object" in message for message in messages))
        self.assertTrue(any("must be a path or materialization object" in message for message in messages))

    def test_malformed_nested_values_report_without_crashing(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog_path = fixture.preset / "patterns/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["patterns"][0]["allowed_dependencies"] = [{}]
            fixture.write_json("patterns/catalog.json", catalog)
            fixture.refresh_digest("patterns", catalog_path)
            manifest = fixture.read_manifest()
            manifest["skills"]["ui"]["invocation"] = [{}]
            manifest["status"] = "verified"
            manifest["materialization"] = {"root": "foo\u0000bar"}
            manifest["verification"]["clean_room_evidence"] = None
            manifest["verification"]["independent_use_evidence"] = [
                {"path": [], "sha256": "0" * 64}
            ]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("skill ui invocation" in message for message in messages))
        self.assertTrue(any("nonempty relative path" in message for message in messages))
        self.assertTrue(any("allowed_dependencies must be a string list" in message for message in messages))
        self.assertTrue(any("portable POSIX-relative path" in message for message in messages))

    def test_rejects_nonportable_and_overlapping_materialization_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            source = fixture.preset / "template/example.txt"
            common = {
                "source": "template/example.txt",
                "operation": "create",
                "conflict_policy": "fail",
                "sha256": fixture.digest(source),
            }
            manifest = fixture.read_manifest()
            manifest["materialization"] = [
                {**common, "target": "src"},
                {**common, "target": "src/app"},
                {**common, "target": "case/App"},
                {**common, "target": "case/app"},
                {**common, "target": "C:\\escape"},
                {**common, "target": "a/./b"},
                {**common, "target": "CON"},
                {**common, "target": "foo:bar"},
            ]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("overlaps another materialization target" in message for message in messages))
        self.assertGreaterEqual(sum("portable POSIX-relative path" in message for message in messages), 4)

    def test_rejects_symlinked_preset_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            catalog = base / "catalog"
            catalog.mkdir()
            outside = base / "outside"
            fixture = self.make_fixture(outside)
            (catalog / fixture.preset_id).symlink_to(fixture.preset, target_is_directory=True)
            findings, counts = validate_presets(catalog)
        self.assertEqual(counts.presets, 0)
        self.assertTrue(
            any("preset directory must not be a symbolic link" in finding.message for finding in findings)
        )

    def test_rejects_symlinked_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = self.make_fixture(root)
            external = root / "external.json"
            external.write_text(fixture.manifest_path.read_text(encoding="utf-8"), encoding="utf-8")
            fixture.manifest_path.unlink()
            fixture.manifest_path.symlink_to(external)
            findings, counts = validate_presets(root)
        self.assertEqual(counts.presets, 0)
        self.assertTrue(
            any("preset manifest must not be a symbolic link" in finding.message for finding in findings)
        )

    def test_dual_verdict_evidence_obeys_freshness_window(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["upgrade_policy"] = {
                "strategy": "explicit-merge",
                "breaking_change_policy": "require-decision",
                "stale_after_days": 1,
            }
            fixture.update_manifest(manifest)
            evidence = fixture.write_json(
                "verification/evidence/stale-dual.json",
                {
                    "conformance": "pass",
                    "outcome": "pass",
                    "qualification": "verified",
                    "claim_type": "flow",
                    "claim_id": "stale-flow",
                    "observed_at": "2000-01-01T00:00:00Z",
                    "input_digests": PresetValidator(
                        fixture.root
                    ).evaluation_input_locks(fixture.preset),
                },
            )
            validator = PresetValidator(fixture.root)
            validator.validate_dual_verdict_evidence(
                fixture.preset,
                evidence,
                "dual evidence",
                "verified",
                "flow",
                "stale-flow",
            )
        self.assertTrue(any("is stale after 1 days" in finding.message for finding in validator.findings))

    def test_rejects_missing_design_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            del manifest["design"]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("missing required manifest field: design" in message for message in messages))
        self.assertTrue(any("design must be an object" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
