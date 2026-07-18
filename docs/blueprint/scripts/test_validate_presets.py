from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.validate_presets import (
    AUDIT_NEGATIVE_EVAL_KINDS,
    BASELINE_COMMAND_LANES,
    CORE_FIELDS,
    PUBLISH_NEGATIVE_EVAL_KINDS,
    REQUIRED_SKILLS,
    PresetValidator,
    validate_presets as validate_presets_at,
)


TEST_NOW = datetime(2026, 7, 18, 0, 0, 0, tzinfo=timezone.utc)


def validate_presets(root: Path):
    return validate_presets_at(root, now=TEST_NOW)


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

    def write_skill(self, capability: str) -> dict[str, object]:
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
        return {
            "name": name,
            "path": skill_dir,
            "sha256": self.digest(skill_path.parent),
            "invocation": {"implicit": f"Use for {capability} tasks"},
            "targets": ["codex"],
        }

    def eval_case(
        self,
        case_id: str,
        kind: str,
        skills: list[str],
        *,
        conformance: str = "PASS",
        outcome: str = "PASS",
        adversarial: bool | None = None,
        prompt: str | None = None,
    ) -> dict[str, object]:
        manifest = self.read_manifest()
        qualification = str(manifest["status"])
        input_digests = PresetValidator(self.root).evaluation_input_locks(self.preset)
        case: dict[str, object] = {
            "id": case_id,
            "kind": kind,
            "skills": skills,
            "prompt": prompt or f"Complete the {kind} task.",
            "input_digests": input_digests,
            "route_trace": [f"skill:{skills[0]}"],
        }
        if adversarial is None:
            adversarial = kind in (
                AUDIT_NEGATIVE_EVAL_KINDS | PUBLISH_NEGATIVE_EVAL_KINDS
            )
        if adversarial:
            adversarial_path = self.write_json(
                f"verification/evals/fixtures/{case_id}.json",
                {
                    "scenario": kind,
                    "hazard": "Exercise the declared negative boundary.",
                },
            )
            case.update(
                {
                    "adversarial_input": {
                        "path": str(adversarial_path.relative_to(self.preset)),
                        "sha256": self.digest(adversarial_path),
                    },
                    "expected_disposition": "BLOCKED",
                    "expected_failure_code": kind,
                }
            )
        case_input_sha256 = PresetValidator.evaluation_case_digest(case)
        verdicts: dict[str, dict[str, object]] = {}
        for axis, result in (("conformance", conformance), ("outcome", outcome)):
            observed_adversarial = (
                {
                    "observed_disposition": case["expected_disposition"],
                    "observed_failure_code": case["expected_failure_code"],
                }
                if adversarial
                else {}
            )
            evidence_path = self.write_json(
                f"verification/evals/results/{case_id}-{axis}.json",
                {
                    "result": result,
                    "qualification": qualification,
                    "claim_type": f"skill-eval-{axis}",
                    "claim_id": case_id,
                    "case_input_sha256": case_input_sha256,
                    **observed_adversarial,
                    "observed_at": "2026-07-12T00:00:00Z",
                    "input_digests": input_digests,
                },
            )
            verdicts[axis] = {
                "result": result,
                "evidence": [
                    {
                        "path": str(evidence_path.relative_to(self.preset)),
                        "sha256": self.digest(evidence_path),
                    }
                ],
            }
        return {**case, **verdicts}

    def refresh_eval_cases(self, cases: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            self.eval_case(
                str(case["id"]),
                str(case["kind"]),
                list(case["skills"]),
                conformance=str(
                    case.get("conformance", {}).get("result", "PASS")
                    if isinstance(case.get("conformance"), dict)
                    else "PASS"
                ),
                outcome=str(
                    case.get("outcome", {}).get("result", "PASS")
                    if isinstance(case.get("outcome"), dict)
                    else "PASS"
                ),
            )
            for case in cases
        ]

    def pattern_execution(self, observed_at: str) -> dict[str, object]:
        catalog = json.loads(
            (self.preset / "patterns/catalog.json").read_text(encoding="utf-8")
        )
        pattern = catalog["patterns"][0]
        verifier = str(pattern["verifier"])

        def fixtures(polarity: str, observed: str) -> list[dict[str, object]]:
            records: list[dict[str, object]] = []
            for path in pattern["fixtures"][polarity]:
                record: dict[str, object] = {
                    "path": path,
                    "sha256": self.digest(self.preset / path),
                    "observed": observed,
                }
                if polarity == "negative":
                    record["observed_failure"] = pattern["fixtures"][
                        "expected_failures"
                    ][path]
                records.append(record)
            return records

        return {
            "run_id": "pattern-verifier-run",
            "actor": "preset-author-agent",
            "toolchain": "fixture-toolchain",
            "environment": "clean-fixture",
            "observed_at": observed_at,
            "pattern_contract_sha256": PresetValidator.pattern_contract_digest(
                pattern
            ),
            "verifier": {
                "path": verifier,
                "sha256": self.digest(self.preset / verifier),
                "argv": list(pattern["verifier_argv"]),
                "exit_code": 0,
            },
            "fixtures": {
                "positive": fixtures("positive", "accept"),
                "negative": fixtures("negative", "reject"),
            },
        }

    def build(self) -> None:
        self.write("README.md", "# Example preset\n")
        self.write("template/example.txt")

        skills = {}
        for capability in sorted(REQUIRED_SKILLS):
            skills[capability] = self.write_skill(capability)

        pattern_evidence = self.write_json(
            "verification/evidence/pattern.json",
            {
                "conformance": "PASS",
                "outcome": "PASS",
                "observed_at": "2026-07-12T00:00:00Z",
            },
        )
        pattern_evidence_ref = {
            "path": str(pattern_evidence.relative_to(self.preset)),
            "sha256": self.digest(pattern_evidence),
        }
        exemplar = self.write("patterns/exemplars/feature-list/example.txt")
        verifier = self.write(
            "patterns/verifiers/feature-list.py",
            "print('fixture verifier executed')\n",
        )
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
                        "primary_owner": "feature",
                        "support_skills": ["ui"],
                        "allowed_dependencies": ["shared"],
                        "forbidden_dependencies": ["app"],
                        "examples": [str(exemplar.relative_to(self.preset))],
                        "verifier": str(verifier.relative_to(self.preset)),
                        "verifier_argv": [
                            "python3",
                            str(verifier.relative_to(self.preset)),
                        ],
                        "fixtures": {
                            "positive": [str(positive.relative_to(self.preset))],
                            "negative": [str(negative.relative_to(self.preset))],
                            "expected_failures": {
                                str(negative.relative_to(self.preset)): {
                                    "code": "forbidden-dependency",
                                    "reason": "Rejects the fixture's forbidden dependency.",
                                }
                            },
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
        command_lanes = {
            lane: {
                "argv": ["fixture-tool", lane],
                **({"timeout_seconds": 30} if lane == "start-smoke" else {}),
            }
            for lane in sorted(BASELINE_COMMAND_LANES)
        }
        commands_path = self.write_json(
            "verification/commands.json",
            {
                "$schema": "../../../blueprint/schemas/verification-command-registry.schema.json",
                "schema_version": "1.0.0",
                "lanes": command_lanes,
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
                "schema_version": "1.1.0",
                "preset_id": self.preset_id,
                "preset_version": "0.1.0",
                "blueprint_version": "0.12.0",
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
                "verification": {
                    "commands": {
                        "path": str(commands_path.relative_to(self.preset)),
                        "sha256": self.digest(commands_path),
                    },
                    "skill_evals": "verification/skill-evals.json",
                },
            }
        )
        evals_path = self.preset / "verification/skill-evals.json"
        evals = json.loads(evals_path.read_text(encoding="utf-8"))
        evals["cases"] = self.refresh_eval_cases(evals["cases"])
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
        self.assertTrue(
            {"audit-changes", "publish"}
            <= set(schema["properties"]["skills"]["properties"])
        )
        self.assertEqual(
            schema["properties"]["skills"]["propertyNames"]["$ref"],
            "#/$defs/kebabId",
        )
        self.assertEqual(
            schema["properties"]["skills"]["additionalProperties"]["$ref"],
            "#/$defs/skill",
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.1.0")
        self.assertIn("commands", schema["properties"]["verification"]["required"])

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

        command_schema_path = (
            Path(__file__).resolve().parents[1]
            / "schemas/verification-command-registry.schema.json"
        )
        command_schema = json.loads(command_schema_path.read_text(encoding="utf-8"))
        self.assertEqual(
            set(command_schema["properties"]["lanes"]["required"]),
            BASELINE_COMMAND_LANES,
        )
        self.assertEqual(
            set(
                command_schema["properties"]["lanes"]["propertyNames"]["allOf"][1][
                    "not"
                ]["enum"]
            ),
            {"publish", "release", "deploy"},
        )
        start_smoke = command_schema["properties"]["lanes"]["properties"][
            "start-smoke"
        ]
        self.assertTrue(
            any(
                clause.get("required") == ["timeout_seconds"]
                for clause in start_smoke["allOf"]
            )
        )

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

    def test_case_and_pattern_contract_digests_match_golden_vectors(self):
        case = {
            "id": "one",
            "kind": "single-layer",
            "skills": ["feature"],
            "prompt": "Café",
            "route_trace": ["skill:feature"],
            "input_digests": {"skill:feature": "a" * 64},
        }
        pattern = {
            "id": "example",
            "layer": "feature",
            "primary_owner": "feature",
            "support_skills": ["ui"],
            "intent": "Café",
            "applicability": {"use_when": ["x"], "avoid_when": []},
            "public_contract": {
                "inputs": ["in"],
                "outputs": ["out"],
                "states": ["success"],
            },
            "allowed_dependencies": ["shared"],
            "forbidden_dependencies": ["app"],
            "examples": ["patterns/exemplars/example.txt"],
            "verifier": "patterns/verifiers/example.py",
            "verifier_argv": ["python3", "patterns/verifiers/example.py"],
            "fixtures": {
                "positive": ["positive.json"],
                "negative": ["negative.json"],
                "expected_failures": {
                    "negative.json": {
                        "code": "bad-input",
                        "reason": "Bad input.",
                    }
                },
            },
            "evidence": [{"path": "ignored.json", "sha256": "0" * 64}],
        }
        self.assertEqual(
            PresetValidator.evaluation_case_digest(case),
            "9c7532af0e70b0eab8bf81eb796a4227938b899960dc10813c728de856b65f57",
        )
        self.assertEqual(
            PresetValidator.pattern_contract_digest(pattern),
            "387c056a87e3a70de60093804c5d81b41084c9867fb969ec6aaf8f839df6efb7",
        )

    def test_accepts_valid_preset(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            findings, counts = validate_presets(fixture.root)
        self.assertEqual([finding.render() for finding in findings], [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (1, 7, 1))

    def test_accepts_standard_optional_skills_with_bound_negative_evals(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            for capability in ("audit-changes", "publish"):
                manifest["skills"][capability] = fixture.write_skill(capability)
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"].extend(
                {"id": kind, "kind": kind, "skills": [capability]}
                for capability, kinds in (
                    (
                        "audit-changes",
                        ("audit-immutable-range", "audit-checkpoint"),
                    ),
                    (
                        "publish",
                        (
                            "publish-topology",
                            "publish-conflict",
                            "publish-final-revision",
                        ),
                    ),
                )
                for kind in kinds
            )
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            fixture.write_json("verification/skill-evals.json", evals)
            findings, counts = validate_presets(fixture.root)
        self.assertEqual([finding.render() for finding in findings], [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (1, 9, 1))

    def test_accepts_nonstandard_narrow_skill_with_forward_eval(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["data-export"] = fixture.write_skill("data-export")
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"].append(
                {
                    "id": "data-export",
                    "kind": "data-export",
                    "skills": ["data-export"],
                }
            )
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            fixture.write_json("verification/skill-evals.json", evals)
            findings, counts = validate_presets(fixture.root)
        self.assertEqual([finding.render() for finding in findings], [])
        self.assertEqual((counts.presets, counts.skills, counts.patterns), (1, 8, 1))

    def test_optional_negative_eval_kind_must_reference_its_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            for capability in ("audit-changes", "publish"):
                manifest["skills"][capability] = fixture.write_skill(capability)
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"].append(
                {
                    "id": "optional-happy-paths",
                    "kind": "optional-happy-paths",
                    "skills": ["audit-changes", "publish"],
                }
            )
            for kind in (
                "audit-immutable-range",
                "audit-checkpoint",
                "publish-topology",
                "publish-conflict",
                "publish-final-revision",
            ):
                evals["cases"].append(
                    {"id": kind, "kind": kind, "skills": ["feature"]}
                )
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(
            any(
                "required audit-changes negative case audit-checkpoint must reference skill"
                in message
                for message in messages
            )
        )
        self.assertTrue(
            any(
                "required publish negative case publish-topology must reference skill"
                in message
                for message in messages
            )
        )

    def test_every_declared_optional_skill_requires_forward_eval(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["audit-changes"] = fixture.write_skill(
                "audit-changes"
            )
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "skill evals do not forward-test declared skill: audit-changes"
                in finding.message
                for finding in findings
            )
        )

    def test_experimental_optional_stub_does_not_satisfy_negative_coverage(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["audit-changes"] = fixture.write_skill(
                "audit-changes"
            )
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            evals["cases"].append(
                fixture.eval_case(
                    "audit-checkpoint", "audit-checkpoint", ["audit-changes"]
                )
            )
            evals["cases"].append(
                {
                    "id": "audit-immutable-range",
                    "kind": "audit-immutable-range",
                    "skills": ["audit-changes"],
                }
            )
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(
            any("missing required forward-eval field: prompt" in message for message in messages)
        )
        self.assertTrue(
            any(
                "missing required audit-changes negative case: audit-immutable-range"
                in message
                for message in messages
            )
        )

    def test_optional_negative_kind_with_happy_path_input_does_not_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["audit-changes"] = fixture.write_skill(
                "audit-changes"
            )
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            evals["cases"].extend(
                [
                    fixture.eval_case(
                        "audit-immutable-range",
                        "audit-immutable-range",
                        ["audit-changes"],
                    ),
                    fixture.eval_case(
                        "audit-checkpoint",
                        "audit-checkpoint",
                        ["audit-changes"],
                        adversarial=False,
                        prompt="Advance an already valid checkpoint.",
                    ),
                ]
            )
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("adversarial_input must include" in message for message in messages))
        self.assertTrue(
            any(
                "missing required audit-changes negative case: audit-checkpoint"
                in message
                for message in messages
            )
        )

    def test_optional_negative_evidence_must_match_expected_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["audit-changes"] = fixture.write_skill(
                "audit-changes"
            )
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"].extend(
                {"id": kind, "kind": kind, "skills": ["audit-changes"]}
                for kind in sorted(AUDIT_NEGATIVE_EVAL_KINDS)
            )
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            checkpoint = next(
                case for case in evals["cases"] if case["id"] == "audit-checkpoint"
            )
            evidence_ref = checkpoint["conformance"]["evidence"][0]
            evidence_path = fixture.preset / evidence_ref["path"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["observed_failure_code"] = "happy-path"
            fixture.write_json(evidence_ref["path"], evidence)
            evidence_ref["sha256"] = fixture.digest(evidence_path)
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(
            any(
                "observed_failure_code must equal audit-checkpoint" in message
                for message in messages
            )
        )
        self.assertTrue(
            any(
                "missing required audit-changes negative case: audit-checkpoint"
                in message
                for message in messages
            )
        )

    def test_experimental_not_executed_case_does_not_satisfy_coverage(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["skills"]["audit-changes"] = fixture.write_skill(
                "audit-changes"
            )
            fixture.update_manifest(manifest)
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"] = fixture.refresh_eval_cases(evals["cases"])
            evals["cases"].extend(
                [
                    fixture.eval_case(
                        "audit-checkpoint", "audit-checkpoint", ["audit-changes"]
                    ),
                    fixture.eval_case(
                        "audit-immutable-range",
                        "audit-immutable-range",
                        ["audit-changes"],
                        conformance="NOT_EXECUTED",
                    ),
                ]
            )
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "missing required audit-changes negative case: audit-immutable-range"
                in finding.message
                for finding in findings
            )
        )

    def test_rejects_noncanonical_verdict_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            eval_path = fixture.preset / "verification/skill-evals.json"
            evals = json.loads(eval_path.read_text(encoding="utf-8"))
            evals["cases"][0]["conformance"]["result"] = "pass"
            fixture.write_json("verification/skill-evals.json", evals)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "conformance.result must be one of" in finding.message
                for finding in findings
            )
        )

    def test_eval_evidence_rejects_prompt_or_route_trace_mutation(self):
        for field, value in (
            ("prompt", "A changed task prompt."),
            ("route_trace", ["skill:feature", "skill:app"]),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                eval_path = fixture.preset / "verification/skill-evals.json"
                evals = json.loads(eval_path.read_text(encoding="utf-8"))
                evals["cases"][0][field] = value
                fixture.write_json("verification/skill-evals.json", evals)
                findings, _ = validate_presets(fixture.root)
            self.assertTrue(
                any(
                    "case_input_sha256 is stale or misbound" in finding.message
                    for finding in findings
                )
            )

    def test_rejects_incomplete_or_shell_string_command_registry(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            command_path = fixture.preset / "verification/commands.json"
            commands = json.loads(command_path.read_text(encoding="utf-8"))
            del commands["lanes"]["doctor"]
            commands["lanes"]["check"]["argv"] = "fixture-tool check"
            fixture.write_json("verification/commands.json", commands)
            manifest = fixture.read_manifest()
            manifest["verification"]["commands"]["sha256"] = fixture.digest(command_path)
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(any("missing required lane: doctor" in message for message in messages))
        self.assertTrue(any("lanes.check.argv" in message for message in messages))

    def test_command_registry_digest_binds_manifest_reference(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            command_path = fixture.preset / "verification/commands.json"
            commands = json.loads(command_path.read_text(encoding="utf-8"))
            commands["lanes"]["build"]["argv"].append("--changed")
            fixture.write_json("verification/commands.json", commands)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "stale verification.commands.sha256" in finding.message
                for finding in findings
            )
        )

    def test_start_smoke_registry_requires_positive_timeout(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            command_path = fixture.preset / "verification/commands.json"
            commands = json.loads(command_path.read_text(encoding="utf-8"))
            del commands["lanes"]["start-smoke"]["timeout_seconds"]
            fixture.write_json("verification/commands.json", commands)
            manifest = fixture.read_manifest()
            manifest["verification"]["commands"]["sha256"] = fixture.digest(command_path)
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "lanes.start-smoke.timeout_seconds is required for start-smoke"
                in finding.message
                for finding in findings
            )
        )

    def test_command_registry_cwd_must_be_an_existing_directory(self):
        scenarios = (
            ("missing-dir", "does not exist"),
            ("template/example.txt", "must reference a directory"),
        )
        for cwd, expected in scenarios:
            with self.subTest(cwd=cwd), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                command_path = fixture.preset / "verification/commands.json"
                commands = json.loads(command_path.read_text(encoding="utf-8"))
                commands["lanes"]["check"]["cwd"] = cwd
                fixture.write_json("verification/commands.json", commands)
                manifest = fixture.read_manifest()
                manifest["verification"]["commands"]["sha256"] = fixture.digest(
                    command_path
                )
                fixture.update_manifest(manifest)
                findings, _ = validate_presets(fixture.root)
            self.assertTrue(
                any(
                    f"lanes.check.cwd {expected}" in finding.message
                    for finding in findings
                )
            )

    def test_command_registry_rejects_external_mutation_lane_keys(self):
        for lane in ("publish", "release", "deploy"):
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                command_path = fixture.preset / "verification/commands.json"
                commands = json.loads(command_path.read_text(encoding="utf-8"))
                commands["lanes"][lane] = {"argv": ["fixture-tool", lane]}
                fixture.write_json("verification/commands.json", commands)
                manifest = fixture.read_manifest()
                manifest["verification"]["commands"]["sha256"] = fixture.digest(
                    command_path
                )
                fixture.update_manifest(manifest)
                findings, _ = validate_presets(fixture.root)
            self.assertTrue(
                any(
                    f"command lane {lane} is externally mutating and forbidden"
                    in finding.message
                    for finding in findings
                )
            )

    def test_start_smoke_evidence_requires_readiness_and_termination(self):
        scenarios = (
            ("missing", {}),
            (
                "false",
                {"readiness_observed": False, "termination_observed": False},
            ),
        )
        for scenario, observations in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                validator = PresetValidator(fixture.root)
                manifest = fixture.read_manifest()
                command_registry = validator.validate_command_registry(
                    fixture.preset,
                    fixture.manifest_path,
                    manifest["verification"]["commands"],
                )
                evidence = fixture.write_json(
                    "verification/evidence/start-smoke-binding.json",
                    {
                        "result": "pass",
                        "qualification": "experimental",
                        "context": "clean-room",
                        "run_id": "start-smoke-binding",
                        "actor": "fixture-agent",
                        "toolchain": "fixture-toolchain",
                        "environment": "clean-fixture",
                        "observed_at": "2026-07-12T00:00:00Z",
                        "input_digests": validator.evidence_input_locks(
                            fixture.preset
                        ),
                        "commands": [
                            {
                                "lane": "start-smoke",
                                "argv": ["fixture-tool", "start-smoke"],
                                "exit_code": 0,
                                **observations,
                            }
                        ],
                    },
                )
                validator.validate_pass_evidence(
                    fixture.preset,
                    evidence,
                    "clean-room evidence",
                    status="experimental",
                    required_context="clean-room",
                    require_commands=True,
                    command_registry=command_registry,
                )
                messages = [finding.message for finding in validator.findings]
                self.assertTrue(
                    any("readiness_observed must equal true" in message for message in messages)
                )
                self.assertTrue(
                    any("termination_observed must equal true" in message for message in messages)
                )

    def test_clean_room_evidence_must_cover_optional_command_lanes(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            command_path = fixture.preset / "verification/commands.json"
            commands = json.loads(command_path.read_text(encoding="utf-8"))
            commands["lanes"]["auth-smoke"] = {
                "argv": ["fixture-tool", "auth-smoke"]
            }
            fixture.write_json("verification/commands.json", commands)
            manifest = fixture.read_manifest()
            manifest["status"] = "candidate"
            manifest["upgrade_policy"] = {
                "strategy": "explicit-merge",
                "breaking_change_policy": "require-decision",
                "stale_after_days": 30,
            }
            manifest["verification"]["commands"]["sha256"] = fixture.digest(
                command_path
            )
            fixture.update_manifest(manifest)
            input_locks = PresetValidator(fixture.root).evidence_input_locks(
                fixture.preset
            )
            clean_room = fixture.write_json(
                "verification/evidence/optional-command-clean-room.json",
                {
                    "result": "pass",
                    "qualification": "candidate",
                    "context": "clean-room",
                    "run_id": "optional-command-clean-room",
                    "actor": "fixture-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "clean-fixture",
                    "observed_at": "2026-07-12T00:00:00Z",
                    "input_digests": input_locks,
                    "commands": [
                        {
                            "lane": lane,
                            "argv": ["fixture-tool", lane],
                            "exit_code": 0,
                            **(
                                {
                                    "readiness_observed": True,
                                    "termination_observed": True,
                                }
                                if lane == "start-smoke"
                                else {}
                            ),
                        }
                        for lane in sorted(BASELINE_COMMAND_LANES)
                    ],
                },
            )
            manifest = fixture.read_manifest()
            manifest["verification"]["clean_room_evidence"] = [
                {
                    "path": str(clean_room.relative_to(fixture.preset)),
                    "sha256": fixture.digest(clean_room),
                }
            ]
            fixture.update_manifest(manifest)
            findings, _ = validate_presets(fixture.root)
        self.assertTrue(
            any(
                "clean-room evidence did not execute declared command lane: auth-smoke"
                in finding.message
                for finding in findings
            )
        )

    def test_clean_room_command_evidence_must_match_declared_argv(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            validator = PresetValidator(fixture.root)
            manifest = fixture.read_manifest()
            command_registry = validator.validate_command_registry(
                fixture.preset,
                fixture.manifest_path,
                manifest["verification"]["commands"],
            )
            evidence = fixture.write_json(
                "verification/evidence/command-binding.json",
                {
                    "result": "pass",
                    "qualification": "experimental",
                    "context": "clean-room",
                    "run_id": "command-binding",
                    "actor": "fixture-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "clean-fixture",
                    "observed_at": "2026-07-12T00:00:00Z",
                    "input_digests": validator.evidence_input_locks(fixture.preset),
                    "commands": [
                        {
                            "lane": "check",
                            "argv": ["different-tool", "check"],
                            "exit_code": 0,
                        }
                    ],
                },
            )
            validator.validate_pass_evidence(
                fixture.preset,
                evidence,
                "clean-room evidence",
                status="experimental",
                required_context="clean-room",
                require_commands=True,
                command_registry=command_registry,
            )
        self.assertTrue(
            any("argv does not match the declared lane" in finding.message for finding in validator.findings)
        )

    def test_verdict_evidence_rejects_cross_axis_and_misbound_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            validator = PresetValidator(fixture.root)
            case = {
                "id": "single-layer",
                "kind": "single-layer",
                "skills": ["shared", "app"],
                "prompt": "Complete the single-layer task.",
                "route_trace": ["skill:shared"],
                "input_digests": validator.evaluation_input_locks(fixture.preset),
            }
            evidence = fixture.write_json(
                "verification/evidence/misbound-verdict.json",
                {
                    "result": "PASS",
                    "conformance": "PASS",
                    "outcome": "FAIL",
                    "qualification": "verified",
                    "claim_type": "skill-eval-outcome",
                    "claim_id": "wrong-case",
                    "case_input_sha256": validator.evaluation_case_digest(case),
                    "observed_at": "2026-07-12T00:00:00Z",
                    "input_digests": validator.evaluation_input_locks(fixture.preset),
                },
            )
            validator.validate_verdict_evidence(
                fixture.preset,
                evidence,
                "skill-eval evidence",
                "verified",
                "skill-eval-conformance",
                "single-layer",
                "PASS",
                validator.evaluation_case_digest(case),
                None,
                None,
            )
        messages = [finding.message for finding in validator.findings]
        self.assertTrue(any("must record one result axis" in message for message in messages))
        self.assertTrue(any("claim_type must equal skill-eval-conformance" in message for message in messages))
        self.assertTrue(any("claim_id must equal single-layer" in message for message in messages))

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

    def test_pattern_owner_roles_must_resolve_without_overlap(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog_path = fixture.preset / "patterns/catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            pattern = catalog["patterns"][0]
            pattern["support_skills"] = [pattern["primary_owner"], "unknown-skill"]
            fixture.write_json("patterns/catalog.json", catalog)
            fixture.refresh_digest("patterns", catalog_path)
            findings, _ = validate_presets(fixture.root)
        messages = [finding.message for finding in findings]
        self.assertTrue(
            any("primary_owner must not also appear" in message for message in messages)
        )
        self.assertTrue(
            any("support_skills references unknown skill" in message for message in messages)
        )

    def test_candidate_pattern_rejects_empty_comment_only_or_gitkeep_exemplar(self):
        for scenario in ("empty-file", "comment-only", "gitkeep-only"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                catalog_path = fixture.preset / "patterns/catalog.json"
                catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
                if scenario == "empty-file":
                    exemplar = fixture.preset / catalog["patterns"][0]["examples"][0]
                    exemplar.write_text("", encoding="utf-8")
                elif scenario == "comment-only":
                    exemplar = fixture.write(
                        "patterns/exemplars/feature-list/comment-only.py",
                        "# no implementation\n",
                    )
                    catalog["patterns"][0]["examples"] = [
                        str(exemplar.relative_to(fixture.preset))
                    ]
                else:
                    exemplar = fixture.preset / "patterns/exemplars/feature-list/empty"
                    exemplar.mkdir()
                    (exemplar / ".gitkeep").write_text("keep\n", encoding="utf-8")
                    catalog["patterns"][0]["examples"] = [
                        str(exemplar.relative_to(fixture.preset))
                    ]
                fixture.write_json("patterns/catalog.json", catalog)
                fixture.refresh_digest("patterns", catalog_path)
                manifest = fixture.read_manifest()
                validator = PresetValidator(fixture.root, now=TEST_NOW)
                validator.validate_patterns(
                    fixture.preset,
                    fixture.manifest_path,
                    manifest["patterns"],
                    set(manifest["skills"]),
                    "candidate",
                )
            self.assertTrue(
                any(
                    "examples must contain substantive regular content"
                    in finding.message
                    for finding in validator.findings
                )
            )

    def test_pattern_exemplar_tree_accepts_substantive_regular_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            exemplar = Path(temporary) / "example"
            exemplar.mkdir()
            (exemplar / ".gitkeep").write_text("keep\n", encoding="utf-8")
            (exemplar / "implementation.py").write_text(
                "print('substantive')\n", encoding="utf-8"
            )
            self.assertTrue(
                PresetValidator.has_substantive_pattern_resource(exemplar)
            )

    def test_pattern_evidence_requires_execution_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            evidence_path = fixture.write_json(
                "verification/evidence/missing-pattern-execution.json",
                {"observed_at": "2026-07-12T00:00:00Z"},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": "2026-07-12T00:00:00Z"},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertTrue(
            any(
                "pattern evidence.execution must be an object" in finding.message
                for finding in validator.findings
            )
        )

    def test_pattern_execution_rejects_verifier_digest_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            execution["verifier"]["sha256"] = "0" * 64
            evidence_path = fixture.write_json(
                "verification/evidence/drifted-pattern-execution.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertTrue(
            any(
                "stale pattern execution.verifier.sha256" in finding.message
                for finding in validator.findings
            )
        )

    def test_pattern_execution_rejects_pattern_contract_mutation(self):
        mutations = (
            ("applicability", lambda pattern: pattern["applicability"]["use_when"].append("Changed use.")),
            ("public-contract", lambda pattern: pattern["public_contract"]["states"].append("changed")),
            ("ownership", lambda pattern: pattern.update({"primary_owner": "app"})),
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                catalog = json.loads(
                    (fixture.preset / "patterns/catalog.json").read_text(
                        encoding="utf-8"
                    )
                )
                observed_at = "2026-07-12T00:00:00Z"
                execution = fixture.pattern_execution(observed_at)
                pattern = catalog["patterns"][0]
                mutate(pattern)
                evidence_path = fixture.write_json(
                    "verification/evidence/stale-pattern-contract.json",
                    {"observed_at": observed_at, "execution": execution},
                )
                validator = PresetValidator(fixture.root)
                validator.validate_pattern_execution_evidence(
                    fixture.preset,
                    evidence_path,
                    {"observed_at": observed_at, "execution": execution},
                    pattern,
                    "pattern[0]",
                )
            self.assertTrue(
                any(
                    "pattern_contract_sha256 is stale or misbound"
                    in finding.message
                    for finding in validator.findings
                )
            )

    def test_pattern_execution_rejects_noop_or_wrong_interpreter_argv(self):
        for argv in (
            ["true", "patterns/verifiers/feature-list.py"],
            ["ruby", "patterns/verifiers/feature-list.py"],
        ):
            with self.subTest(argv=argv), tempfile.TemporaryDirectory() as temporary:
                fixture = self.make_fixture(Path(temporary))
                catalog = json.loads(
                    (fixture.preset / "patterns/catalog.json").read_text(
                        encoding="utf-8"
                    )
                )
                observed_at = "2026-07-12T00:00:00Z"
                execution = fixture.pattern_execution(observed_at)
                execution["verifier"]["argv"] = argv
                evidence_path = fixture.write_json(
                    "verification/evidence/wrong-verifier-argv.json",
                    {"observed_at": observed_at, "execution": execution},
                )
                validator = PresetValidator(fixture.root)
                validator.validate_pattern_execution_evidence(
                    fixture.preset,
                    evidence_path,
                    {"observed_at": observed_at, "execution": execution},
                    catalog["patterns"][0],
                    "pattern[0]",
                )
            self.assertTrue(
                any(
                    "verifier.argv must equal catalog verifier_argv"
                    in finding.message
                    for finding in validator.findings
                )
            )

    def test_pattern_execution_rejects_omitted_negative_fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            execution["fixtures"]["negative"] = []
            evidence_path = fixture.write_json(
                "verification/evidence/omitted-negative-execution.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertTrue(
            any(
                "pattern execution omitted negative fixture" in finding.message
                for finding in validator.findings
            )
        )

    def test_pattern_execution_rejects_negative_accept_and_nonzero_verifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            execution["verifier"]["exit_code"] = 1
            execution["fixtures"]["negative"][0]["observed"] = "accept"
            evidence_path = fixture.write_json(
                "verification/evidence/false-green-negative-execution.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        messages = [finding.message for finding in validator.findings]
        self.assertTrue(any("verifier.exit_code must equal 0" in message for message in messages))
        self.assertTrue(any("observed must equal reject" in message for message in messages))

    def test_pattern_execution_rejects_negative_failure_for_wrong_reason(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            execution["fixtures"]["negative"][0]["observed_failure"] = {
                "code": "parser-crash",
                "reason": "The fixture failed before the intended rule ran.",
            }
            evidence_path = fixture.write_json(
                "verification/evidence/wrong-negative-reason.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertTrue(
            any(
                "observed_failure must equal the catalog expected failure"
                in finding.message
                for finding in validator.findings
            )
        )

    def test_pattern_execution_rejects_comment_only_verifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            verifier_path = fixture.preset / "patterns/verifiers/feature-list.py"
            verifier_path.write_text("# comment only\n", encoding="utf-8")
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            evidence_path = fixture.write_json(
                "verification/evidence/comment-only-verifier.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertTrue(
            any(
                "verifier must contain substantive content" in finding.message
                for finding in validator.findings
            )
        )

    def test_pattern_execution_accepts_full_bound_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            catalog = json.loads(
                (fixture.preset / "patterns/catalog.json").read_text(encoding="utf-8")
            )
            observed_at = "2026-07-12T00:00:00Z"
            execution = fixture.pattern_execution(observed_at)
            evidence_path = fixture.write_json(
                "verification/evidence/full-pattern-execution.json",
                {"observed_at": observed_at, "execution": execution},
            )
            validator = PresetValidator(fixture.root)
            validator.validate_pattern_execution_evidence(
                fixture.preset,
                evidence_path,
                {"observed_at": observed_at, "execution": execution},
                catalog["patterns"][0],
                "pattern[0]",
            )
        self.assertEqual(validator.findings, [])

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
            observed_at = TEST_NOW.isoformat().replace("+00:00", "Z")
            validator = PresetValidator(fixture.root, now=TEST_NOW)
            pattern_input_locks = validator.evaluation_input_locks(fixture.preset)
            pattern_input_locks.pop("patterns", None)
            pattern_evidence = fixture.write_json(
                "verification/evidence/pattern.json",
                {
                    "conformance": "PASS",
                    "outcome": "PASS",
                    "qualification": "verified",
                    "claim_type": "pattern",
                    "claim_id": "feature-list",
                    "observed_at": observed_at,
                    "input_digests": pattern_input_locks,
                    "execution": fixture.pattern_execution(observed_at),
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
                    "conformance": "PASS",
                    "outcome": "PASS",
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
                    "conformance": "PASS",
                    "outcome": "PASS",
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
                case_input_sha256 = PresetValidator.evaluation_case_digest(case)
                for verdict in ("conformance", "outcome"):
                    evidence_path = fixture.write_json(
                        f"verification/evals/results/{case['id']}-{verdict}.json",
                        {
                            "result": "PASS",
                            "qualification": "verified",
                            "claim_type": f"skill-eval-{verdict}",
                            "claim_id": case["id"],
                            "case_input_sha256": case_input_sha256,
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
                    "commands": [
                        {
                            "lane": lane,
                            "argv": ["fixture-tool", lane],
                            "exit_code": 0,
                            **(
                                {
                                    "readiness_observed": True,
                                    "termination_observed": True,
                                }
                                if lane == "start-smoke"
                                else {}
                            ),
                        }
                        for lane in sorted(BASELINE_COMMAND_LANES)
                    ],
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
                    "commands": [
                        {
                            "lane": "check",
                            "argv": ["fixture-tool", "check"],
                            "exit_code": 0,
                        }
                    ],
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
                    "conformance": "PASS",
                    "outcome": "PASS",
                    "qualification": "verified",
                    "claim_type": "flow",
                    "claim_id": "stale-flow",
                    "observed_at": "2000-01-01T00:00:00Z",
                    "input_digests": PresetValidator(
                        fixture.root
                    ).evaluation_input_locks(fixture.preset),
                },
            )
            validator = PresetValidator(fixture.root, now=TEST_NOW)
            validator.validate_dual_verdict_evidence(
                fixture.preset,
                evidence,
                "dual evidence",
                "verified",
                "flow",
                "stale-flow",
            )
        self.assertTrue(any("is stale after 1 days" in finding.message for finding in validator.findings))

    def test_dual_verdict_evidence_future_check_uses_injected_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            manifest = fixture.read_manifest()
            manifest["upgrade_policy"] = {
                "strategy": "explicit-merge",
                "breaking_change_policy": "require-decision",
                "stale_after_days": 30,
            }
            fixture.update_manifest(manifest)
            evidence = fixture.write_json(
                "verification/evidence/future-dual.json",
                {
                    "conformance": "PASS",
                    "outcome": "PASS",
                    "qualification": "verified",
                    "claim_type": "flow",
                    "claim_id": "future-flow",
                    "observed_at": "2026-07-18T00:06:00Z",
                    "input_digests": PresetValidator(
                        fixture.root, now=TEST_NOW
                    ).evaluation_input_locks(fixture.preset),
                },
            )
            validator = PresetValidator(fixture.root, now=TEST_NOW)
            validator.validate_dual_verdict_evidence(
                fixture.preset,
                evidence,
                "dual evidence",
                "verified",
                "flow",
                "future-flow",
            )
        self.assertTrue(
            any("must not be in the future" in finding.message for finding in validator.findings)
        )

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
