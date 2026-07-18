from __future__ import annotations

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.validate_app_profile import (
    BASELINE_COMMAND_LANES,
    NEGATIVE_EVAL_KINDS,
    REQUIRED_SKILLS,
    AppProfileValidator,
    main,
    validate_app_profile,
)


REVISION = "a" * 64
BLUEPRINT_REVISION = "b" * 64
OBSERVED_AT = (
    datetime.now(timezone.utc)
    .replace(microsecond=0)
    .isoformat()
    .replace("+00:00", "Z")
)


class AppProfileFixture:
    def __init__(self, root: Path):
        self.root = root
        self.profile_path = root / "docs/governance/app-profile.json"

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative: str, value) -> Path:
        return self.write(relative, json.dumps(value, indent=2) + "\n")

    @staticmethod
    def digest(path: Path) -> str:
        return AppProfileValidator.digest_path(path)

    def read_profile(self):
        return json.loads(self.profile_path.read_text(encoding="utf-8"))

    def update_profile(self, profile) -> None:
        self.write_json("docs/governance/app-profile.json", profile)

    def refresh_reference(self, field: str) -> None:
        profile = self.read_profile()
        target = self.root / profile[field]["path"]
        profile[field]["sha256"] = self.digest(target)
        self.update_profile(profile)

    def refresh_skill(self, capability: str) -> None:
        profile = self.read_profile()
        target = self.root / profile["skills"][capability]["path"]
        profile["skills"][capability]["sha256"] = self.digest(target)
        self.update_profile(profile)

    def refresh_skill_evals(self) -> None:
        profile = self.read_profile()
        reference = profile["guidance_evidence"]["skill_evals"]
        reference["sha256"] = self.digest(self.root / reference["path"])
        self.update_profile(profile)

    def authority_input_digests(self):
        return AppProfileValidator.profile_input_digests(self.read_profile())

    def write_skill_eval_case(
        self,
        case_id: str,
        kind: str,
        skills: list[str],
        input_digests,
    ):
        case = {
            "id": case_id,
            "kind": kind,
            "skills": skills,
            "prompt": f"Complete the {kind} evaluation.",
            "route_trace": [f"skill:{skills[0]}"],
            "input_digests": input_digests,
        }
        if kind in NEGATIVE_EVAL_KINDS:
            expected_failure = f"{kind}-guard"
            expected_disposition = "REFUSED"
            adversarial = self.write_json(
                f"docs/governance/evidence/evals/fixtures/{case_id}.json",
                {
                    "schema_version": "1.0.0",
                    "adversarial": True,
                    "scenario": f"Exercise the forbidden {kind} condition.",
                    "expected_disposition": expected_disposition,
                    "expected_failure": expected_failure,
                },
            )
            case.update(
                {
                    "prompt": f"Exercise the adversarial {kind} condition.",
                    "adversarial_fixture": {
                        "path": adversarial.relative_to(self.root).as_posix(),
                        "sha256": self.digest(adversarial),
                    },
                    "expected_disposition": expected_disposition,
                    "expected_failure": expected_failure,
                }
            )
        case_input_sha256 = AppProfileValidator.skill_eval_case_input_digest(case)
        verdicts = {}
        for axis in ("conformance", "outcome"):
            evidence = self.write_json(
                f"docs/governance/evidence/evals/{case_id}-{axis}.json",
                {
                    "schema_version": "1.0.0",
                    "source_revision": REVISION,
                    "case_id": case_id,
                    "axis": axis,
                    "result": "PASS",
                    "input_digests": input_digests,
                    "case_input_sha256": case_input_sha256,
                    "run_id": f"{case_id}-{axis}-01",
                    "actor": "fixture-agent",
                    "toolchain": "fixture-toolchain",
                    "environment": "isolated-fixture",
                    "observed_at": OBSERVED_AT,
                    **(
                        {
                            "observed_disposition": case["expected_disposition"],
                            "observed_failure": case["expected_failure"],
                        }
                        if kind in NEGATIVE_EVAL_KINDS
                        else {}
                    ),
                },
            )
            verdicts[axis] = {
                "result": "PASS",
                "evidence": [
                    {
                        "path": evidence.relative_to(self.root).as_posix(),
                        "sha256": self.digest(evidence),
                    }
                ],
            }
        return {**case, **verdicts}

    def replace_skill_eval_cases(self, specs) -> None:
        profile = self.read_profile()
        input_digests = self.authority_input_digests()
        cases = [
            self.write_skill_eval_case(case_id, kind, skills, input_digests)
            for case_id, kind, skills in specs
        ]
        reference = profile["guidance_evidence"]["skill_evals"]
        path = self.write_json(
            reference["path"],
            {
                "schema_version": "1.0.0",
                "source_revision": profile["source_revision"],
                "cases": cases,
            },
        )
        reference["sha256"] = self.digest(path)
        self.update_profile(profile)

    def current_skill_eval_specs(self):
        profile = self.read_profile()
        reference = profile["guidance_evidence"]["skill_evals"]
        data = json.loads((self.root / reference["path"]).read_text(encoding="utf-8"))
        return [
            (case["id"], case["kind"], list(case["skills"]))
            for case in data["cases"]
        ]

    def read_pattern_catalog(self):
        profile = self.read_profile()
        path = self.root / profile["pattern_catalog"]["path"]
        return json.loads(path.read_text(encoding="utf-8"))

    def update_pattern_catalog(self, catalog) -> None:
        profile = self.read_profile()
        reference = profile["pattern_catalog"]
        path = self.write_json(reference["path"], catalog)
        reference["sha256"] = self.digest(path)
        self.update_profile(profile)

    def read_pattern_evidence(self):
        catalog = self.read_pattern_catalog()
        reference = catalog["patterns"][0]["verification_evidence"]
        path = self.root / reference["path"]
        return json.loads(path.read_text(encoding="utf-8"))

    def update_pattern_evidence(self, evidence) -> None:
        profile = self.read_profile()
        catalog_reference = profile["pattern_catalog"]
        catalog_path = self.root / catalog_reference["path"]
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        reference = catalog["patterns"][0]["verification_evidence"]
        evidence_path = self.write_json(reference["path"], evidence)
        reference["sha256"] = self.digest(evidence_path)
        self.write_json(catalog_reference["path"], catalog)
        catalog_reference["sha256"] = self.digest(catalog_path)
        self.update_profile(profile)

    def read_skill_evals(self):
        profile = self.read_profile()
        path = self.root / profile["guidance_evidence"]["skill_evals"]["path"]
        return json.loads(path.read_text(encoding="utf-8"))

    def update_skill_evals(self, data) -> None:
        profile = self.read_profile()
        reference = profile["guidance_evidence"]["skill_evals"]
        path = self.write_json(reference["path"], data)
        reference["sha256"] = self.digest(path)
        self.update_profile(profile)

    def update_axis_evidence(self, case_index: int, axis: str, evidence) -> None:
        data = self.read_skill_evals()
        reference = data["cases"][case_index][axis]["evidence"][0]
        path = self.write_json(reference["path"], evidence)
        reference["sha256"] = self.digest(path)
        self.update_skill_evals(data)

    def read_clean_room_evidence(self):
        profile = self.read_profile()
        path = self.root / profile["clean_room_evidence"]["path"]
        return json.loads(path.read_text(encoding="utf-8"))

    def update_clean_room_evidence(self, evidence) -> None:
        profile = self.read_profile()
        reference = profile["clean_room_evidence"]
        path = self.write_json(reference["path"], evidence)
        reference["sha256"] = self.digest(path)
        self.update_profile(profile)

    def rebind_clean_room_evidence(self) -> None:
        profile = self.read_profile()
        command_reference = profile["verification_commands"]
        commands = json.loads(
            (self.root / command_reference["path"]).read_text(encoding="utf-8")
        )
        evidence = self.read_clean_room_evidence()
        evidence["source_revision"] = profile["source_revision"]
        evidence["verification_commands_sha256"] = command_reference["sha256"]
        evidence["input_digests"] = AppProfileValidator.evidence_authority_inputs(
            self.authority_input_digests()
        )
        evidence["commands"] = [
            {
                "lane": lane,
                "argv": command["argv"],
                "cwd": command.get("cwd", "."),
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
            for lane, command in sorted(commands["lanes"].items())
        ]
        self.update_clean_room_evidence(evidence)

    def rebind_pattern_evidence(self) -> None:
        profile = self.read_profile()
        catalog_reference = profile["pattern_catalog"]
        catalog_path = self.root / catalog_reference["path"]
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        authority_inputs = self.authority_input_digests()
        for pattern in catalog["patterns"]:
            evidence_reference = pattern["verification_evidence"]
            evidence_path = self.root / evidence_reference["path"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["source_revision"] = profile["source_revision"]
            evidence["input_digests"] = AppProfileValidator.pattern_input_digests(
                pattern,
                authority_inputs,
            )
            self.write_json(evidence_reference["path"], evidence)
            evidence_reference["sha256"] = self.digest(evidence_path)
        self.write_json(catalog_reference["path"], catalog)
        catalog_reference["sha256"] = self.digest(catalog_path)
        self.update_profile(profile)

    def rebind_guidance_evidence(self) -> None:
        profile = self.read_profile()
        reference = profile["guidance_evidence"]
        path = self.root / reference["path"]
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["source_revision"] = profile["source_revision"]
        evidence["input_digests"] = AppProfileValidator.evidence_authority_inputs(
            self.authority_input_digests()
        )
        self.write_json(reference["path"], evidence)
        reference["sha256"] = self.digest(path)
        self.update_profile(profile)

    def rebind_all_evidence(self, specs=None) -> None:
        if specs is None:
            specs = self.current_skill_eval_specs()
        self.rebind_pattern_evidence()
        self.rebind_clean_room_evidence()
        self.rebind_guidance_evidence()
        self.replace_skill_eval_cases(specs)

    def build(self) -> None:
        system = self.write(
            "docs/governance/profiles/system-profile.md",
            "---\n"
            "artifact_id: SYS-EXAMPLE-01\n"
            "artifact_type: system-profile\n"
            "status: active\n"
            "---\n\n"
            "# System profile\n",
        )
        stack = self.write(
            "docs/governance/profiles/stack-profile.md",
            "---\n"
            "artifact_id: STK-EXAMPLE-01\n"
            "artifact_type: stack-profile\n"
            "status: accepted\n"
            "---\n\n"
            "# Stack profile\n",
        )
        registry = self.write(
            "docs/governance/artifact-registry.md",
            "---\n"
            "artifact_id: REG-EXAMPLE-01\n"
            "artifact_type: artifact-registry\n"
            "status: active\n"
            "---\n\n"
            "# Artifact registry\n\n"
            "| Artifact ID | Type | Status | Path/evidence locator |\n"
            "| --- | --- | --- | --- |\n"
            "| REG-EXAMPLE-01 | artifact-registry | active | `docs/governance/artifact-registry.md` |\n"
            "| SYS-EXAMPLE-01 | system-profile | active | `profiles/system-profile.md` |\n"
            "| STK-EXAMPLE-01 | stack-profile | accepted | `profiles/stack-profile.md` |\n",
        )

        skills = {}
        for capability in sorted(REQUIRED_SKILLS):
            name = f"example-{capability}"
            directory = self.root / ".agents/skills" / name
            skill = self.write(
                f".agents/skills/{name}/SKILL.md",
                "---\n"
                f"name: {name}\n"
                f"description: Route {capability} work.\n"
                "---\n\n"
                f"# {capability}\n",
            )
            self.write(
                f".agents/skills/{name}/references/contract.md",
                f"# {capability} contract\n",
            )
            skills[capability] = {
                "name": name,
                "path": directory.relative_to(self.root).as_posix(),
                "sha256": self.digest(skill.parent),
            }

        exemplar = self.write(
            "docs/governance/patterns/exemplars/feature-workflow.md",
            "# Feature workflow exemplar\n",
        )
        verifier = self.write(
            "docs/governance/patterns/verifiers/feature-workflow.py",
            "import sys\n\nsys.exit(0)\n",
        )
        positive = self.write_json(
            "docs/governance/patterns/fixtures/feature-workflow/positive.json",
            {"case": "accepted"},
        )
        negative = self.write_json(
            "docs/governance/patterns/fixtures/feature-workflow/negative.json",
            {"case": "rejected"},
        )
        pattern_record = {
            "id": "feature-workflow",
            "intent": "Close one feature-owned vertical outcome.",
            "primary_owner": "feature",
            "support_skills": ["lib", "ui"],
            "applicability": {
                "use_when": ["The outcome crosses feature and adapter seams."],
                "avoid_when": ["The request changes no observable outcome."],
            },
            "public_contract": {
                "inputs": ["validated feature intent"],
                "outputs": ["typed feature outcome"],
                "states": ["success", "denied", "error"],
            },
            "allowed_dependencies": ["feature public contracts"],
            "forbidden_dependencies": ["raw persistence payloads"],
            "exemplar": {
                "path": exemplar.relative_to(self.root).as_posix(),
                "sha256": self.digest(exemplar),
            },
            "verifier": {
                "path": verifier.relative_to(self.root).as_posix(),
                "sha256": self.digest(verifier),
            },
            "verifier_argv": [
                "python3",
                verifier.relative_to(self.root).as_posix(),
            ],
            "fixtures": {
                "positive": [
                    {
                        "path": positive.relative_to(self.root).as_posix(),
                        "sha256": self.digest(positive),
                    }
                ],
                "negative": [
                    {
                        "path": negative.relative_to(self.root).as_posix(),
                        "sha256": self.digest(negative),
                    }
                ],
                "expected_failures": {
                    negative.relative_to(self.root).as_posix(): {
                        "code": "feature-policy-rejected",
                        "reason": "The negative fixture must be rejected by feature policy.",
                    }
                },
            },
        }
        pattern_inputs = {
            "exemplar": pattern_record["exemplar"]["sha256"],
            "verifier": pattern_record["verifier"]["sha256"],
            "fixture:positive:0": pattern_record["fixtures"]["positive"][0]["sha256"],
            "fixture:negative:0": pattern_record["fixtures"]["negative"][0]["sha256"],
        }
        pattern_evidence = self.write_json(
            "docs/governance/evidence/pattern-feature-workflow.json",
            {
                "schema_version": "1.0.0",
                "source_revision": REVISION,
                "pattern_id": "feature-workflow",
                "input_digests": pattern_inputs,
                "run_id": "pattern-feature-workflow-01",
                "actor": "fixture-agent",
                "toolchain": "fixture-toolchain",
                "environment": "isolated-fixture",
                "observed_at": OBSERVED_AT,
                "result": "PASS",
                "positive_result": "PASS",
                "negative_result": "PASS",
                "verifier_argv": pattern_record["verifier_argv"],
                "verifier_exit_code": 0,
                "fixture_results": [
                    {
                        "polarity": "positive",
                        "path": pattern_record["fixtures"]["positive"][0]["path"],
                        "sha256": pattern_record["fixtures"]["positive"][0]["sha256"],
                        "observed": "accept",
                        "exit_code": 0,
                    },
                    {
                        "polarity": "negative",
                        "path": pattern_record["fixtures"]["negative"][0]["path"],
                        "sha256": pattern_record["fixtures"]["negative"][0]["sha256"],
                        "observed": "reject",
                        "observed_failure": pattern_record["fixtures"]["expected_failures"][
                            pattern_record["fixtures"]["negative"][0]["path"]
                        ],
                        "exit_code": 0,
                    },
                ],
            },
        )
        pattern_record["verification_evidence"] = {
            "path": pattern_evidence.relative_to(self.root).as_posix(),
            "sha256": self.digest(pattern_evidence),
        }
        patterns = self.write_json(
            "docs/governance/patterns/catalog.json",
            {
                "schema_version": "1.0.0",
                "patterns": [pattern_record],
            },
        )
        commands = self.write_json(
            "docs/governance/verification/commands.json",
            {
                "schema_version": "1.0.0",
                "lanes": {
                    lane: {
                        "argv": ["project-tool", lane],
                        "cwd": ".",
                        **({"timeout_seconds": 30} if lane == "start-smoke" else {}),
                    }
                    for lane in sorted(BASELINE_COMMAND_LANES)
                },
            },
        )
        clean_room = self.write_json(
            "docs/governance/evidence/clean-room.json",
            {
                "schema_version": "1.0.0",
                "source_revision": REVISION,
                "verification_commands_sha256": self.digest(commands),
                "run_id": "clean-room-example-01",
                "actor": "fixture-agent",
                "toolchain": "fixture-toolchain",
                "environment": "isolated-fixture",
                "observed_at": OBSERVED_AT,
                "input_digests": {},
                "status": "current",
                "result": "PASS",
                "commands": [
                    {
                        "lane": lane,
                        "argv": ["project-tool", lane],
                        "cwd": ".",
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
        evidence = self.write_json(
            "docs/governance/evidence/current-guidance.json",
            {
                "schema_version": "1.0.0",
                "evidence_id": "EVD-EXAMPLE-01",
                "source_revision": REVISION,
                "input_digests": {},
                "run_id": "guidance-example-01",
                "actor": "fixture-agent",
                "toolchain": "fixture-toolchain",
                "environment": "isolated-fixture",
                "observed_at": OBSERVED_AT,
                "result": "PASS",
                "checks": ["repository-local"],
            },
        )
        input_digests = {
            "artifact_registry": self.digest(registry),
            "system_profile": self.digest(system),
            "stack_profile": self.digest(stack),
            "pattern_catalog": self.digest(patterns),
            "verification_commands": self.digest(commands),
            **{
                f"skill:{capability}": record["sha256"]
                for capability, record in sorted(skills.items())
            },
        }
        skill_evals = self.write_json(
            "docs/governance/evidence/skill-evals.json",
            {
                "schema_version": "1.0.0",
                "source_revision": REVISION,
                "cases": [
                    self.write_skill_eval_case(
                        f"{capability}-forward",
                        "forward",
                        [capability],
                        input_digests,
                    )
                    for capability in sorted(REQUIRED_SKILLS)
                ],
            },
        )
        self.update_profile(
            {
                "$schema": "../../blueprint/schemas/app-profile.schema.json",
                "schema_version": "1.0.0",
                "profile_id": "example-app",
                "blueprint_version": "0.12.0",
                "blueprint_revision": BLUEPRINT_REVISION,
                "source_revision": REVISION,
                "freshness_policy": {"stale_after_days": 30},
                "artifact_registry": {
                    "id": "REG-EXAMPLE-01",
                    "status": "active",
                    "path": registry.relative_to(self.root).as_posix(),
                    "sha256": self.digest(registry),
                },
                "artifact_closure": [
                    {
                        "id": "SYS-EXAMPLE-01",
                        "status": "active",
                        "path": system.relative_to(self.root).as_posix(),
                        "sha256": self.digest(system),
                    },
                    {
                        "id": "STK-EXAMPLE-01",
                        "status": "accepted",
                        "path": stack.relative_to(self.root).as_posix(),
                        "sha256": self.digest(stack),
                    },
                ],
                "system_profile": {
                    "id": "SYS-EXAMPLE-01",
                    "status": "active",
                    "path": system.relative_to(self.root).as_posix(),
                    "sha256": self.digest(system),
                },
                "stack_profile": {
                    "id": "STK-EXAMPLE-01",
                    "status": "accepted",
                    "path": stack.relative_to(self.root).as_posix(),
                    "sha256": self.digest(stack),
                },
                "skills": skills,
                "pattern_catalog": {
                    "path": patterns.relative_to(self.root).as_posix(),
                    "sha256": self.digest(patterns),
                },
                "verification_commands": {
                    "path": commands.relative_to(self.root).as_posix(),
                    "sha256": self.digest(commands),
                },
                "clean_room_evidence": {
                    "path": clean_room.relative_to(self.root).as_posix(),
                    "sha256": self.digest(clean_room),
                },
                "guidance_evidence": {
                    "id": "EVD-EXAMPLE-01",
                    "current_revision": REVISION,
                    "path": evidence.relative_to(self.root).as_posix(),
                    "sha256": self.digest(evidence),
                    "skill_evals": {
                        "path": skill_evals.relative_to(self.root).as_posix(),
                        "sha256": self.digest(skill_evals),
                    },
                },
            }
        )
        self.rebind_all_evidence()


class AppProfileValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture = AppProfileFixture(self.root)
        self.fixture.build()

    def messages(
        self,
        *,
        expected_revision: str | None = REVISION,
        expected_blueprint_revision: str | None = BLUEPRINT_REVISION,
    ) -> list[str]:
        return [
            finding.message
            for finding in validate_app_profile(
                self.fixture.profile_path,
                self.root,
                expected_revision=expected_revision,
                expected_blueprint_revision=expected_blueprint_revision,
            )
        ]

    def test_valid_profile_accepts_content_revision(self) -> None:
        self.assertEqual(self.messages(expected_revision=REVISION), [])

    def test_schema_is_parseable_and_requires_the_machine_contract(self) -> None:
        schema_path = (
            Path(__file__).parents[1] / "schemas/app-profile.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.0.0")
        self.assertTrue(
            {
                "artifact_registry",
                "artifact_closure",
                "system_profile",
                "stack_profile",
                "skills",
                "pattern_catalog",
                "verification_commands",
                "clean_room_evidence",
                "guidance_evidence",
                "freshness_policy",
            }.issubset(schema["required"])
        )
        self.assertEqual(
            schema["properties"]["pattern_catalog"]["x-referenced-document-schema"],
            "#/$defs/patternCatalogDocument",
        )
        skill_eval_schema = schema["$defs"]["guidanceReference"]["properties"][
            "skill_evals"
        ]
        self.assertEqual(
            skill_eval_schema["x-referenced-document-schema"],
            "#/$defs/skillEvaluationDocument",
        )
        self.assertIn("app-profile-skill-eval-case-v1", skill_eval_schema["description"])

    def test_cli_requires_explicit_repo_root_and_reports_success(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(
                [
                    str(self.fixture.profile_path),
                    "--repo-root",
                    str(self.root),
                    "--expected-revision",
                    REVISION,
                    "--expected-blueprint-revision",
                    BLUEPRINT_REVISION,
                ]
            )
        self.assertEqual(result, 0)
        self.assertIn("app-profile-quality: findings=0", output.getvalue())

    def test_missing_canonical_skill_fails_but_extra_skill_is_allowed(self) -> None:
        profile = self.fixture.read_profile()
        del profile["skills"]["ui"]
        extra_name = "example-release-notes"
        extra_dir = self.root / ".agents/skills" / extra_name
        self.fixture.write(
            f".agents/skills/{extra_name}/SKILL.md",
            "---\nname: example-release-notes\n---\n\n# Release notes\n",
        )
        profile["skills"]["release-notes"] = {
            "name": extra_name,
            "path": extra_dir.relative_to(self.root).as_posix(),
            "sha256": self.fixture.digest(extra_dir),
        }
        self.fixture.update_profile(profile)
        specs = [
            spec
            for spec in self.fixture.current_skill_eval_specs()
            if spec[2] != ["ui"]
        ]
        specs.append(
            ("release-notes-forward", "forward", ["release-notes"])
        )
        self.fixture.replace_skill_eval_cases(specs)
        messages = self.messages()
        self.assertIn("skills is missing required capability: ui", messages)
        self.assertFalse(any("release-notes" in message for message in messages))

    def test_duplicate_skill_name_and_path_fail(self) -> None:
        profile = self.fixture.read_profile()
        profile["skills"]["shared"] = dict(profile["skills"]["lib"])
        self.fixture.update_profile(profile)
        messages = self.messages()
        self.assertTrue(any("duplicate skill name" in message for message in messages))
        self.assertTrue(any("duplicate skill path" in message for message in messages))

    def test_canonical_preset_lock_cannot_coexist_with_app_profile(self) -> None:
        self.fixture.write_json(
            "docs/governance/preset-lock.json",
            {"preset_id": "conflicting-preset"},
        )
        self.assertIn(
            "app-profile and canonical preset-lock authorities cannot coexist",
            self.messages(),
        )

    def test_absolute_and_escaping_reference_paths_fail(self) -> None:
        for raw in ("/tmp/catalog.json", "../catalog.json", "docs/../catalog.json"):
            with self.subTest(raw=raw):
                profile = self.fixture.read_profile()
                profile["pattern_catalog"]["path"] = raw
                self.fixture.update_profile(profile)
                self.assertTrue(
                    any(
                        "pattern_catalog.path must be a portable repository-relative path"
                        in message
                        for message in self.messages()
                    )
                )
                self.fixture.build()

    def test_missing_file_fails(self) -> None:
        profile = self.fixture.read_profile()
        profile["pattern_catalog"]["path"] = "docs/governance/patterns/missing.json"
        self.fixture.update_profile(profile)
        self.assertTrue(any("does not exist" in message for message in self.messages()))

    def test_symlinked_reference_fails(self) -> None:
        target = self.root / "docs/governance/patterns/catalog.json"
        link = self.root / "docs/governance/patterns/catalog-link.json"
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        profile = self.fixture.read_profile()
        profile["pattern_catalog"]["path"] = link.relative_to(self.root).as_posix()
        self.fixture.update_profile(profile)
        self.assertTrue(
            any("must not traverse a symbolic link" in message for message in self.messages())
        )

    def test_digest_mismatch_fails(self) -> None:
        profile = self.fixture.read_profile()
        profile["pattern_catalog"]["sha256"] = "0" * 64
        self.fixture.update_profile(profile)
        self.assertTrue(
            any("stale pattern_catalog.sha256" in message for message in self.messages())
        )

    def test_skill_tree_digest_rejects_nested_symlink(self) -> None:
        skill_dir = self.root / ".agents/skills/example-app"
        target = self.root / "outside.txt"
        target.write_text("outside\n", encoding="utf-8")
        try:
            (skill_dir / "linked.txt").symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        self.assertTrue(
            any(
                "directory digest does not permit symbolic links" in message
                for message in self.messages()
            )
        )

    def test_artifact_frontmatter_id_and_status_must_match(self) -> None:
        path = self.root / "docs/governance/profiles/system-profile.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            .replace("SYS-EXAMPLE-01", "SYS-WRONG-01")
            .replace("status: active", "status: draft"),
            encoding="utf-8",
        )
        self.fixture.refresh_reference("system_profile")
        messages = self.messages()
        self.assertIn("artifact_id does not match system_profile.id", messages)
        self.assertIn("status does not match system_profile.status", messages)

    def test_registry_missing_current_artifact_row_fails(self) -> None:
        registry = self.root / "docs/governance/artifact-registry.md"
        registry.write_text(
            "\n".join(
                line
                for line in registry.read_text(encoding="utf-8").splitlines()
                if "STK-EXAMPLE-01" not in line
            )
            + "\n",
            encoding="utf-8",
        )
        self.fixture.refresh_reference("artifact_registry")
        self.assertIn(
            "artifact registry is missing row for STK-EXAMPLE-01",
            self.messages(),
        )

    def test_registry_contradictory_status_and_path_fail(self) -> None:
        registry = self.root / "docs/governance/artifact-registry.md"
        registry.write_text(
            registry.read_text(encoding="utf-8").replace(
                "| SYS-EXAMPLE-01 | system-profile | active | `profiles/system-profile.md` |",
                "| SYS-EXAMPLE-01 | system-profile | draft | `profiles/other.md` |",
            ),
            encoding="utf-8",
        )
        self.fixture.refresh_reference("artifact_registry")
        messages = self.messages()
        self.assertIn(
            "artifact registry status contradicts system_profile: SYS-EXAMPLE-01",
            messages,
        )
        self.assertIn(
            "artifact registry path contradicts system_profile: SYS-EXAMPLE-01",
            messages,
        )

    def test_duplicate_registry_row_fails(self) -> None:
        registry = self.root / "docs/governance/artifact-registry.md"
        registry.write_text(
            registry.read_text(encoding="utf-8")
            + "| SYS-EXAMPLE-01 | system-profile | active | `profiles/system-profile.md` |\n",
            encoding="utf-8",
        )
        self.fixture.refresh_reference("artifact_registry")
        self.assertIn(
            "artifact registry has duplicate rows for SYS-EXAMPLE-01",
            self.messages(),
        )

    def test_artifact_closure_rejects_missing_extra_and_stale_entries(self) -> None:
        profile = self.fixture.read_profile()
        profile["artifact_closure"] = [
            item
            for item in profile["artifact_closure"]
            if item["id"] != "SYS-EXAMPLE-01"
        ]
        self.fixture.update_profile(profile)
        self.assertIn(
            "artifact_closure is missing effective registry artifact: SYS-EXAMPLE-01",
            self.messages(),
        )

        self.fixture.build()
        extra = self.fixture.write(
            "docs/governance/profiles/extra.md",
            "---\nartifact_id: EXTRA-EXAMPLE-01\nartifact_type: design-contract\nstatus: active\n---\n\n# Extra\n",
        )
        profile = self.fixture.read_profile()
        profile["artifact_closure"].append(
            {
                "id": "EXTRA-EXAMPLE-01",
                "status": "active",
                "path": extra.relative_to(self.root).as_posix(),
                "sha256": self.fixture.digest(extra),
            }
        )
        self.fixture.update_profile(profile)
        self.assertIn(
            "artifact_closure contains extra or ineffective artifact: EXTRA-EXAMPLE-01",
            self.messages(),
        )

        self.fixture.build()
        profile = self.fixture.read_profile()
        profile["artifact_closure"][0]["sha256"] = "0" * 64
        self.fixture.update_profile(profile)
        self.assertTrue(
            any("stale artifact_closure[0].sha256" in message for message in self.messages())
        )

    def test_artifact_closure_accepts_all_effective_statuses(self) -> None:
        for status, token in (
            ("final", "FINAL"),
            ("approved", "APPROVED"),
            ("in-progress", "INPROGRESS"),
        ):
            with self.subTest(status=status):
                artifact_id = f"DSG-{token}-01"
                filename = f"design-{status}.md"
                design = self.fixture.write(
                    f"docs/governance/profiles/{filename}",
                    "---\n"
                    f"artifact_id: {artifact_id}\n"
                    "artifact_type: design-contract\n"
                    f"status: {status}\n"
                    "---\n\n"
                    "# Design contract\n",
                )
                registry = self.root / "docs/governance/artifact-registry.md"
                registry.write_text(
                    registry.read_text(encoding="utf-8")
                    + f"| {artifact_id} | design-contract | {status} | `profiles/{filename}` |\n",
                    encoding="utf-8",
                )
                self.fixture.refresh_reference("artifact_registry")
                profile = self.fixture.read_profile()
                profile["artifact_closure"].append(
                    {
                        "id": artifact_id,
                        "status": status,
                        "path": design.relative_to(self.root).as_posix(),
                        "sha256": self.fixture.digest(design),
                    }
                )
                self.fixture.update_profile(profile)
                self.fixture.rebind_all_evidence()
                self.assertEqual(self.messages(), [])
                self.fixture.build()

    def test_skill_name_path_and_frontmatter_mismatches_fail(self) -> None:
        profile = self.fixture.read_profile()
        record = profile["skills"]["app"]
        original = self.root / record["path"]
        renamed = original.parent / "wrong-path"
        original.rename(renamed)
        record["path"] = renamed.relative_to(self.root).as_posix()
        record["name"] = "declared-app"
        record["sha256"] = self.fixture.digest(renamed)
        self.fixture.update_profile(profile)
        messages = self.messages()
        self.assertIn("skills.app.path basename must match its skill name", messages)
        self.assertIn("frontmatter name does not match skills.app.name", messages)

    def test_malformed_pattern_catalog_fails(self) -> None:
        path = self.root / "docs/governance/patterns/catalog.json"
        self.fixture.write_json(
            "docs/governance/patterns/catalog.json",
            {
                "schema_version": "1.0.0",
                "patterns": [{"id": "duplicate"}, {"id": "duplicate"}],
            },
        )
        self.fixture.refresh_reference("pattern_catalog")
        self.assertIn("duplicate pattern id: duplicate", self.messages())
        self.assertTrue(path.is_file())

    def test_pattern_catalog_rejects_id_only_record(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"] = [{"id": "id-only"}]
        self.fixture.update_pattern_catalog(catalog)
        messages = self.messages()
        self.assertIn("patterns[0].intent must be nonempty", messages)
        self.assertIn(
            "patterns[0].primary_owner must reference exactly one declared skill",
            messages,
        )
        self.assertIn("patterns[0].exemplar must be a JSON object", messages)
        self.assertIn("patterns[0].verifier must be a JSON object", messages)
        self.assertIn("patterns[0].fixtures must be a JSON object", messages)

    def test_pattern_catalog_rejects_unknown_duplicate_and_primary_support(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        pattern = catalog["patterns"][0]
        pattern["primary_owner"] = "feature"
        pattern["support_skills"] = [
            "lib",
            "example-lib",
            "unknown-skill",
            "feature",
        ]
        self.fixture.update_pattern_catalog(catalog)
        messages = self.messages()
        self.assertIn("patterns[0] has duplicate support skill: example-lib", messages)
        self.assertIn(
            "patterns[0] references unknown support skill: unknown-skill",
            messages,
        )
        self.assertIn(
            "patterns[0].support_skills must exclude primary_owner",
            messages,
        )

    def test_pattern_catalog_rejects_unknown_or_multiple_primary_owner(self) -> None:
        for owner in ("unknown-skill", ["feature", "ui"]):
            with self.subTest(owner=owner):
                catalog = self.fixture.read_pattern_catalog()
                catalog["patterns"][0]["primary_owner"] = owner
                self.fixture.update_pattern_catalog(catalog)
                self.assertIn(
                    "patterns[0].primary_owner must reference exactly one declared skill",
                    self.messages(),
                )
                self.fixture.build()

    def test_pattern_catalog_allows_empty_dependency_lists(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"][0]["allowed_dependencies"] = []
        catalog["patterns"][0]["forbidden_dependencies"] = []
        self.fixture.update_pattern_catalog(catalog)
        self.fixture.rebind_all_evidence()
        self.assertEqual(self.messages(), [])

    def test_pattern_catalog_requires_nonempty_negative_fixtures(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"][0]["fixtures"]["negative"] = []
        self.fixture.update_pattern_catalog(catalog)
        self.assertIn(
            "patterns[0].fixtures.negative must be a nonempty reference list",
            self.messages(),
        )

    def test_pattern_catalog_rejects_task_time_evidence_tier(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"][0]["evidence_tier"] = "PATTERN_EXTENSION"
        self.fixture.update_pattern_catalog(catalog)
        self.assertIn(
            "patterns[0].evidence_tier is task-time state and must not appear in the established catalog",
            self.messages(),
        )

    def test_pattern_catalog_rejects_unsafe_resource_path(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"][0]["exemplar"]["path"] = "../exemplar.md"
        self.fixture.update_pattern_catalog(catalog)
        self.assertTrue(
            any(
                "patterns[0].exemplar.path must be a portable repository-relative path"
                in message
                for message in self.messages()
            )
        )

    def test_pattern_catalog_rejects_symlinked_verifier(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        verifier = catalog["patterns"][0]["verifier"]
        target = self.root / verifier["path"]
        link = target.with_name("linked-verifier.py")
        try:
            link.symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        verifier["path"] = link.relative_to(self.root).as_posix()
        self.fixture.update_pattern_catalog(catalog)
        self.assertTrue(
            any(
                "patterns[0].verifier.path must not traverse a symbolic link" in message
                for message in self.messages()
            )
        )

    def test_pattern_catalog_rejects_fixture_digest_mismatch(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        catalog["patterns"][0]["fixtures"]["positive"][0]["sha256"] = "0" * 64
        self.fixture.update_pattern_catalog(catalog)
        self.assertTrue(
            any(
                "stale patterns[0].fixtures.positive[0].sha256" in message
                for message in self.messages()
            )
        )

    def test_pattern_resources_must_be_substantive(self) -> None:
        mutations = (
            ("exemplar", "<!-- placeholder only -->\n"),
            ("verifier", "# placeholder only\n"),
            ("positive", "{}\n"),
            ("negative", "// placeholder only\n"),
        )
        for resource, content in mutations:
            with self.subTest(resource=resource):
                catalog = self.fixture.read_pattern_catalog()
                pattern = catalog["patterns"][0]
                reference = (
                    pattern[resource]
                    if resource in {"exemplar", "verifier"}
                    else pattern["fixtures"][resource][0]
                )
                target = self.root / reference["path"]
                target.write_text(content, encoding="utf-8")
                reference["sha256"] = self.fixture.digest(target)
                self.fixture.update_pattern_catalog(catalog)
                messages = self.messages()
                self.assertTrue(
                    any(
                        f"patterns[0].{resource}" in message
                        or f"fixtures.{resource}[0]" in message
                        for message in messages
                    )
                )
                self.assertTrue(
                    any(
                        "substantive content" in message
                        or "comment-only" in message
                        or "empty JSON placeholder" in message
                        for message in messages
                    )
                )
                self.fixture.build()

    def test_pattern_catalog_requires_execution_evidence(self) -> None:
        catalog = self.fixture.read_pattern_catalog()
        del catalog["patterns"][0]["verification_evidence"]
        self.fixture.update_pattern_catalog(catalog)
        self.assertIn(
            "patterns[0] missing required field: verification_evidence",
            self.messages(),
        )

    def test_pattern_evidence_binds_verifier_argv_and_exit(self) -> None:
        evidence = self.fixture.read_pattern_evidence()
        evidence["verifier_argv"] = ["other-tool", "verify"]
        evidence["verifier_exit_code"] = 2
        self.fixture.update_pattern_evidence(evidence)
        messages = self.messages()
        self.assertIn("pattern verification evidence verifier_argv is misbound", messages)
        self.assertIn(
            "pattern verification evidence verifier_exit_code must be 0",
            messages,
        )

    def test_pattern_evidence_binds_source_inputs_and_reference_digest(self) -> None:
        evidence = self.fixture.read_pattern_evidence()
        evidence["source_revision"] = "c" * 64
        evidence["input_digests"]["verifier"] = "0" * 64
        self.fixture.update_pattern_evidence(evidence)
        messages = self.messages()
        self.assertIn("pattern verification evidence source_revision is stale", messages)
        self.assertIn(
            "pattern verification evidence input_digests.verifier is stale or misbound",
            messages,
        )

        profile = self.fixture.read_profile()
        catalog_path = self.root / profile["pattern_catalog"]["path"]
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        evidence_path = self.root / catalog["patterns"][0]["verification_evidence"]["path"]
        evidence_path.write_text(evidence_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "stale patterns[0].verification_evidence.sha256" in message
                for message in self.messages()
            )
        )

    def test_pattern_evidence_requires_exact_fixture_result_coverage(self) -> None:
        evidence = self.fixture.read_pattern_evidence()
        negative = evidence["fixture_results"].pop()
        evidence["fixture_results"].append(
            {
                **negative,
                "path": "docs/governance/patterns/fixtures/undeclared.json",
            }
        )
        self.fixture.update_pattern_evidence(evidence)
        messages = self.messages()
        self.assertTrue(any("does not match a declared fixture" in message for message in messages))
        self.assertTrue(
            any(
                "pattern verification evidence missing fixture result: negative:" in message
                for message in messages
            )
        )

    def test_pattern_negative_must_fail_for_declared_reason(self) -> None:
        evidence = self.fixture.read_pattern_evidence()
        negative = next(
            item for item in evidence["fixture_results"] if item["polarity"] == "negative"
        )
        negative["observed"] = "accept"
        negative["observed_failure"] = {
            "code": "parser-crashed",
            "reason": "An unrelated parser crash occurred.",
        }
        self.fixture.update_pattern_evidence(evidence)
        messages = self.messages()
        self.assertTrue(any(".observed must equal reject" in message for message in messages))
        self.assertTrue(
            any(
                ".observed_failure must match declared expected_failures entry" in message
                for message in messages
            )
        )

    def test_pattern_evidence_binds_semantic_contract(self) -> None:
        mutations = (
            ("owner", lambda pattern: pattern.update(primary_owner="app")),
            (
                "applicability",
                lambda pattern: pattern["applicability"]["use_when"].append(
                    "A new semantic condition applies."
                ),
            ),
            (
                "public-contract",
                lambda pattern: pattern["public_contract"]["outputs"].append(
                    "a changed wire outcome"
                ),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                catalog = self.fixture.read_pattern_catalog()
                mutate(catalog["patterns"][0])
                self.fixture.update_pattern_catalog(catalog)
                self.assertIn(
                    "pattern verification evidence input_digests.pattern_contract is stale or misbound",
                    self.messages(),
                )
                self.fixture.build()

    def test_command_registry_requires_object_lanes(self) -> None:
        self.fixture.write_json(
            "docs/governance/verification/commands.json",
            {"schema_version": "1.0.0", "lanes": []},
        )
        self.fixture.refresh_reference("verification_commands")
        self.assertIn("command registry lanes must be a JSON object", self.messages())

    def test_command_registry_requires_every_baseline_lane(self) -> None:
        commands = self.root / "docs/governance/verification/commands.json"
        data = json.loads(commands.read_text(encoding="utf-8"))
        del data["lanes"]["doctor"]
        self.fixture.write_json("docs/governance/verification/commands.json", data)
        self.fixture.refresh_reference("verification_commands")
        self.assertIn("missing baseline command lane: doctor", self.messages())

    def test_command_registry_accepts_shared_optional_command_fields(self) -> None:
        commands = self.root / "docs/governance/verification/commands.json"
        data = json.loads(commands.read_text(encoding="utf-8"))
        data["$schema"] = (
            "../../../blueprint/schemas/verification-command-registry.schema.json"
        )
        data["lanes"]["doctor"] = {
            "argv": ["project-tool", "doctor"],
            "required_environment": ["APP_ENV"],
            "timeout_seconds": 30,
        }
        self.fixture.write_json("docs/governance/verification/commands.json", data)
        self.fixture.refresh_reference("verification_commands")
        self.fixture.rebind_all_evidence()
        self.assertEqual(self.messages(), [])

    def test_command_lane_requires_argv_array_and_safe_cwd(self) -> None:
        commands = self.root / "docs/governance/verification/commands.json"
        data = json.loads(commands.read_text(encoding="utf-8"))
        data["lanes"]["check"] = {"argv": "project-tool check", "cwd": "../outside"}
        self.fixture.write_json("docs/governance/verification/commands.json", data)
        self.fixture.refresh_reference("verification_commands")
        messages = self.messages()
        self.assertIn(
            "lanes.check.argv must be a nonempty array of nonempty arguments",
            messages,
        )
        self.assertIn(
            "lanes.check.cwd must be a portable repository-relative path",
            messages,
        )

    def test_command_lane_rejects_invalid_environment_timeout_and_unknown_field(self) -> None:
        commands = self.root / "docs/governance/verification/commands.json"
        data = json.loads(commands.read_text(encoding="utf-8"))
        data["lanes"]["build"] = {
            "argv": ["project-tool", "build"],
            "required_environment": ["APP-ENV"],
            "timeout_seconds": True,
            "shell": True,
        }
        data["lanes"]["test"]["required_environment"] = ["APP_ENV", "APP_ENV"]
        self.fixture.write_json("docs/governance/verification/commands.json", data)
        self.fixture.refresh_reference("verification_commands")
        messages = self.messages()
        self.assertIn("lanes.build has unknown field: shell", messages)
        self.assertIn(
            "lanes.build.required_environment contains an invalid name",
            messages,
        )
        self.assertIn(
            "lanes.test.required_environment must be a unique string list",
            messages,
        )
        self.assertIn(
            "lanes.build.timeout_seconds must be a positive integer",
            messages,
        )

    def test_start_smoke_requires_positive_timeout(self) -> None:
        commands_path = self.root / "docs/governance/verification/commands.json"
        for timeout in (None, 0, -1):
            with self.subTest(timeout=timeout):
                data = json.loads(commands_path.read_text(encoding="utf-8"))
                if timeout is None:
                    data["lanes"]["start-smoke"].pop("timeout_seconds", None)
                else:
                    data["lanes"]["start-smoke"]["timeout_seconds"] = timeout
                self.fixture.write_json("docs/governance/verification/commands.json", data)
                self.fixture.refresh_reference("verification_commands")
                messages = self.messages()
                if timeout is None:
                    self.assertIn("lanes.start-smoke.timeout_seconds is required", messages)
                else:
                    self.assertIn(
                        "lanes.start-smoke.timeout_seconds must be a positive integer",
                        messages,
                    )
                self.fixture.build()

    def test_clean_room_start_smoke_requires_readiness_and_termination(self) -> None:
        for field, value in (
            ("readiness_observed", None),
            ("readiness_observed", False),
            ("termination_observed", None),
            ("termination_observed", False),
        ):
            with self.subTest(field=field, value=value):
                evidence = self.fixture.read_clean_room_evidence()
                start = next(
                    item for item in evidence["commands"] if item["lane"] == "start-smoke"
                )
                if value is None:
                    del start[field]
                else:
                    start[field] = value
                self.fixture.update_clean_room_evidence(evidence)
                messages = self.messages()
                if value is None:
                    self.assertTrue(
                        any(
                            f"missing required field: {field}" in message
                            for message in messages
                        )
                    )
                self.assertTrue(
                    any(f".{field} must equal true" in message for message in messages)
                )
                self.fixture.build()

    def test_clean_room_requires_every_declared_optional_lane(self) -> None:
        commands_path = self.root / "docs/governance/verification/commands.json"
        commands = json.loads(commands_path.read_text(encoding="utf-8"))
        commands["lanes"]["browser-smoke"] = {
            "argv": ["project-tool", "browser-smoke"],
            "cwd": ".",
            "timeout_seconds": 30,
        }
        self.fixture.write_json("docs/governance/verification/commands.json", commands)
        self.fixture.refresh_reference("verification_commands")
        profile = self.fixture.read_profile()
        evidence = self.fixture.read_clean_room_evidence()
        evidence["verification_commands_sha256"] = profile["verification_commands"]["sha256"]
        evidence["input_digests"] = AppProfileValidator.evidence_authority_inputs(
            self.fixture.authority_input_digests()
        )
        self.fixture.update_clean_room_evidence(evidence)
        self.assertIn(
            "clean-room evidence missing declared lane: browser-smoke",
            self.messages(),
        )

    def test_command_registry_rejects_external_effect_lane_names(self) -> None:
        commands_path = self.root / "docs/governance/verification/commands.json"
        for lane in ("publish", "release", "deploy"):
            with self.subTest(lane=lane):
                commands = json.loads(commands_path.read_text(encoding="utf-8"))
                commands["lanes"][lane] = {
                    "argv": ["project-tool", lane],
                    "cwd": ".",
                    "timeout_seconds": 30,
                }
                self.fixture.write_json("docs/governance/verification/commands.json", commands)
                self.fixture.refresh_reference("verification_commands")
                self.assertTrue(
                    any(f"command lane {lane} is forbidden" in message for message in self.messages())
                )
                self.fixture.build()

        commands = json.loads(commands_path.read_text(encoding="utf-8"))
        commands["lanes"]["publish-simulate"] = {
            "argv": ["project-tool", "publish-simulate"],
            "cwd": ".",
            "timeout_seconds": 30,
        }
        self.fixture.write_json("docs/governance/verification/commands.json", commands)
        self.fixture.refresh_reference("verification_commands")
        self.fixture.rebind_all_evidence()
        self.assertEqual(self.messages(), [])

    def test_clean_room_evidence_is_required(self) -> None:
        profile = self.fixture.read_profile()
        del profile["clean_room_evidence"]
        self.fixture.update_profile(profile)
        self.assertIn(
            "app profile is missing required field: clean_room_evidence",
            self.messages(),
        )

    def test_clean_room_evidence_requires_every_baseline_lane(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        evidence["commands"] = [
            command for command in evidence["commands"] if command["lane"] != "doctor"
        ]
        self.fixture.update_clean_room_evidence(evidence)
        self.assertIn(
            "clean-room evidence missing baseline lane: doctor",
            self.messages(),
        )

    def test_clean_room_evidence_rejects_duplicate_lane(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        duplicate = dict(evidence["commands"][0])
        evidence["commands"].append(duplicate)
        self.fixture.update_clean_room_evidence(evidence)
        self.assertIn(
            f"duplicate clean-room command lane: {duplicate['lane']}",
            self.messages(),
        )

    def test_clean_room_evidence_rejects_undeclared_lane(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        evidence["commands"].append(
            {
                "lane": "unknown-smoke",
                "argv": ["project-tool", "unknown-smoke"],
                "cwd": ".",
                "exit_code": 0,
            }
        )
        self.fixture.update_clean_room_evidence(evidence)
        self.assertIn(
            "clean-room evidence references undeclared lane: unknown-smoke",
            self.messages(),
        )

    def test_clean_room_evidence_binds_exact_argv_and_defaulted_cwd(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        record = next(
            command for command in evidence["commands"] if command["lane"] == "doctor"
        )
        record["argv"] = ["different-tool", "doctor"]
        record["cwd"] = "docs"
        self.fixture.update_clean_room_evidence(evidence)
        messages = self.messages()
        self.assertTrue(
            any(".argv does not match declared lane: doctor" in message for message in messages)
        )
        self.assertTrue(
            any(".cwd does not match declared lane: doctor" in message for message in messages)
        )

    def test_clean_room_evidence_requires_current_overall_and_zero_exit(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        evidence["status"] = "stale"
        evidence["result"] = "FAIL"
        evidence["commands"][0]["exit_code"] = 1
        self.fixture.update_clean_room_evidence(evidence)
        messages = self.messages()
        self.assertIn("clean-room evidence status must be current", messages)
        self.assertIn("clean-room evidence result must be PASS", messages)
        self.assertIn("commands[0].exit_code must be 0", messages)

    def test_clean_room_evidence_binds_source_and_command_registry_digest(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        evidence["source_revision"] = "older-release"
        evidence["verification_commands_sha256"] = "0" * 64
        self.fixture.update_clean_room_evidence(evidence)
        messages = self.messages()
        self.assertIn("clean-room evidence source_revision is stale", messages)
        self.assertIn(
            "clean-room evidence verification_commands_sha256 does not match app profile",
            messages,
        )

    def test_clean_room_evidence_requires_execution_provenance(self) -> None:
        evidence = self.fixture.read_clean_room_evidence()
        del evidence["actor"]
        evidence["run_id"] = ""
        evidence["environment"] = "bad\nenvironment"
        evidence["observed_at"] = "2026-99-99T10:00:00"
        self.fixture.update_clean_room_evidence(evidence)
        messages = self.messages()
        self.assertTrue(any("missing required field: actor" in message for message in messages))
        self.assertIn(
            "clean-room evidence actor must be a nonempty control-free string",
            messages,
        )
        self.assertIn(
            "clean-room evidence run_id must be a nonempty control-free string",
            messages,
        )
        self.assertIn(
            "clean-room evidence environment must be a nonempty control-free string",
            messages,
        )
        self.assertIn(
            "clean-room evidence observed_at must be timezone-aware RFC 3339",
            messages,
        )

    def test_clean_room_evidence_rejects_unsafe_and_missing_paths(self) -> None:
        for raw, expected in (
            ("../clean-room.json", "must be a portable repository-relative path"),
            (
                "docs/governance/evidence/missing-clean-room.json",
                "does not exist",
            ),
        ):
            with self.subTest(raw=raw):
                profile = self.fixture.read_profile()
                profile["clean_room_evidence"]["path"] = raw
                self.fixture.update_profile(profile)
                self.assertTrue(
                    any(
                        "clean_room_evidence.path" in message and expected in message
                        for message in self.messages()
                    )
                )
                self.fixture.build()

    def test_clean_room_evidence_rejects_stale_evidence_digest(self) -> None:
        profile = self.fixture.read_profile()
        path = self.root / profile["clean_room_evidence"]["path"]
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "stale clean_room_evidence.sha256" in message
                for message in self.messages()
            )
        )

    def test_freshness_policy_is_required_and_binds_evidence(self) -> None:
        profile = self.fixture.read_profile()
        del profile["freshness_policy"]
        self.fixture.update_profile(profile)
        self.assertIn(
            "app profile is missing required field: freshness_policy",
            self.messages(),
        )

        self.fixture.build()
        profile = self.fixture.read_profile()
        profile["freshness_policy"]["stale_after_days"] = 31
        self.fixture.update_profile(profile)
        messages = self.messages()
        self.assertIn(
            "clean-room evidence input_digests.freshness_policy is stale or misbound",
            messages,
        )
        self.assertIn(
            "pattern verification evidence input_digests.profile_inputs is stale or misbound",
            messages,
        )

    def test_all_execution_evidence_rejects_future_and_expired_timestamps(self) -> None:
        now = datetime.now(timezone.utc)
        timestamps = {
            "future": (now + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
            "expired": (now - timedelta(days=31)).isoformat().replace("+00:00", "Z"),
        }
        for status, observed_at in timestamps.items():
            for evidence_kind in ("clean-room", "pattern", "guidance", "skill-axis"):
                with self.subTest(status=status, evidence=evidence_kind):
                    if evidence_kind == "clean-room":
                        evidence = self.fixture.read_clean_room_evidence()
                        evidence["observed_at"] = observed_at
                        self.fixture.update_clean_room_evidence(evidence)
                    elif evidence_kind == "pattern":
                        evidence = self.fixture.read_pattern_evidence()
                        evidence["observed_at"] = observed_at
                        self.fixture.update_pattern_evidence(evidence)
                    elif evidence_kind == "guidance":
                        profile = self.fixture.read_profile()
                        reference = profile["guidance_evidence"]
                        path = self.root / reference["path"]
                        evidence = json.loads(path.read_text(encoding="utf-8"))
                        evidence["observed_at"] = observed_at
                        self.fixture.write_json(reference["path"], evidence)
                        reference["sha256"] = self.fixture.digest(path)
                        self.fixture.update_profile(profile)
                    else:
                        evals = self.fixture.read_skill_evals()
                        reference = evals["cases"][0]["conformance"]["evidence"][0]
                        path = self.root / reference["path"]
                        evidence = json.loads(path.read_text(encoding="utf-8"))
                        evidence["observed_at"] = observed_at
                        self.fixture.update_axis_evidence(0, "conformance", evidence)
                    messages = self.messages()
                    label = {
                        "clean-room": "clean-room evidence",
                        "pattern": "pattern verification evidence",
                        "guidance": "guidance evidence",
                        "skill-axis": "skill evaluation axis evidence",
                    }[evidence_kind]
                    expected = (
                        f"{label} observed_at must not be in the future"
                        if status == "future"
                        else f"{label} evidence is expired by freshness_policy"
                    )
                    self.assertIn(expected, messages)
                    self.fixture.build()

    def test_revision_mismatch_and_unsafe_revision_fail(self) -> None:
        self.assertIn(
            f"source_revision does not match expected revision {'c' * 64}",
            self.messages(expected_revision="c" * 64),
        )
        profile = self.fixture.read_profile()
        profile["source_revision"] = "unsafe revision"
        self.fixture.update_profile(profile)
        self.assertIn(
            "source_revision must be an immutable source revision, not a movable selector",
            self.messages(),
        )

    def test_symbolic_branch_tag_and_release_revisions_never_qualify(self) -> None:
        for revision in ("main", "latest", "HEAD", "release-2026.07+build.3"):
            with self.subTest(revision=revision):
                profile = self.fixture.read_profile()
                profile["source_revision"] = revision
                profile["guidance_evidence"]["current_revision"] = revision
                self.fixture.update_profile(profile)
                messages = self.messages(expected_revision=revision)
                self.assertIn(
                    "source_revision must be an immutable source revision, not a movable selector",
                    messages,
                )
                self.assertIn(
                    "expected revision must be an immutable source revision, not a movable selector",
                    messages,
                )
                self.fixture.build()

    def test_validation_requires_external_expected_revision(self) -> None:
        self.assertIn(
            "expected revision is required to qualify an effective app profile",
            self.messages(expected_revision=None),
        )
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(
                [
                    str(self.fixture.profile_path),
                    "--repo-root",
                    str(self.root),
                    "--expected-blueprint-revision",
                    BLUEPRINT_REVISION,
                ]
            )

    def test_validation_requires_and_matches_expected_blueprint_revision(self) -> None:
        self.assertIn(
            "expected blueprint revision is required to qualify an effective app profile",
            self.messages(expected_blueprint_revision=None),
        )
        self.assertIn(
            f"blueprint_revision does not match expected blueprint revision {'c' * 64}",
            self.messages(expected_blueprint_revision="c" * 64),
        )
        self.assertIn(
            "expected blueprint revision must be a full immutable content revision",
            self.messages(expected_blueprint_revision="main"),
        )
        profile = self.fixture.read_profile()
        profile["blueprint_revision"] = "release-0.12.0"
        self.fixture.update_profile(profile)
        self.assertIn(
            "blueprint_revision must be a full immutable content revision",
            self.messages(),
        )
        self.fixture.build()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(
                [
                    str(self.fixture.profile_path),
                    "--repo-root",
                    str(self.root),
                    "--expected-revision",
                    REVISION,
                ]
            )

    def test_profile_identity_and_blueprint_metadata_invalidate_evidence(self) -> None:
        mutations = (
            ("profile-id", lambda profile: profile.update(profile_id="changed-app")),
            (
                "blueprint-revision",
                lambda profile: profile.update(blueprint_revision="c" * 64),
            ),
            (
                "blueprint-version",
                lambda profile: profile.update(blueprint_version="0.11.0"),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                profile = self.fixture.read_profile()
                mutate(profile)
                self.fixture.update_profile(profile)
                messages = self.messages()
                self.assertIn(
                    "clean-room evidence input_digests.profile_inputs is stale or misbound",
                    messages,
                )
                self.assertTrue(
                    any(
                        ".input_digests.profile_inputs is stale or misbound" in message
                        and message.startswith("cases[")
                        for message in messages
                    )
                )
                self.fixture.build()

    def test_schema_manual_validator_parity_for_profile_id_max_length(self) -> None:
        profile = self.fixture.read_profile()
        profile["profile_id"] = "a" * 97
        self.fixture.update_profile(profile)
        self.assertIn(
            "profile_id must be a kebab-case identifier",
            self.messages(),
        )

    def test_guidance_revision_and_evidence_identity_must_match(self) -> None:
        profile = self.fixture.read_profile()
        profile["guidance_evidence"]["current_revision"] = "c" * 64
        self.fixture.update_profile(profile)
        messages = self.messages()
        self.assertIn(
            "guidance_evidence.current_revision must equal source_revision",
            messages,
        )
        self.assertIn(
            "guidance source_revision does not match current_revision",
            messages,
        )

    def test_skill_evaluation_must_cover_every_declared_skill(self) -> None:
        path = self.root / "docs/governance/evidence/skill-evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["cases"] = [
            case for case in data["cases"] if case["skills"] != ["ui"]
        ]
        self.fixture.write_json("docs/governance/evidence/skill-evals.json", data)
        self.fixture.refresh_skill_evals()
        self.assertIn(
            "skill evaluations do not cover declared skill: ui",
            self.messages(),
        )

    def test_skill_evaluation_requires_two_pass_axes_with_distinct_evidence(self) -> None:
        path = self.root / "docs/governance/evidence/skill-evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        case = data["cases"][0]
        case["conformance"]["result"] = "pass"
        case["outcome"]["result"] = "FAIL"
        case["outcome"]["evidence"] = case["conformance"]["evidence"]
        self.fixture.write_json("docs/governance/evidence/skill-evals.json", data)
        self.fixture.refresh_skill_evals()
        messages = self.messages()
        self.assertTrue(
            any(".conformance.result must use PASS, FAIL, BLOCKED or NOT_EXECUTED" in message for message in messages)
        )
        self.assertTrue(
            any(".outcome.result must be PASS for an effective app profile" in message for message in messages)
        )
        self.assertTrue(
            any("conformance and outcome evidence files must be distinct" in message for message in messages)
        )

    def test_skill_evaluation_cases_require_prompt_route_and_authority_inputs(self) -> None:
        data = self.fixture.read_skill_evals()
        case = data["cases"][0]
        del case["prompt"]
        del case["route_trace"]
        del case["input_digests"]
        self.fixture.update_skill_evals(data)
        messages = self.messages()
        self.assertTrue(any("missing required field: prompt" in message for message in messages))
        self.assertTrue(any(".route_trace must be a nonempty string list" in message for message in messages))
        self.assertTrue(any(".input_digests must be a JSON object" in message for message in messages))

    def test_skill_axis_evidence_binds_case_prompt_and_route_trace(self) -> None:
        data = self.fixture.read_skill_evals()
        data["cases"][0]["prompt"] = "A materially different request."
        data["cases"][0]["route_trace"].append("TASK_REROUTED:analyze-request")
        self.fixture.update_skill_evals(data)
        self.assertIn(
            "skill evaluation axis evidence case_input_sha256 is stale or misbound",
            self.messages(),
        )

    def test_skill_axis_reference_digest_is_enforced(self) -> None:
        data = self.fixture.read_skill_evals()
        reference = data["cases"][0]["conformance"]["evidence"][0]
        path = self.root / reference["path"]
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "stale cases[0].conformance.evidence[0].sha256" in message
                for message in self.messages()
            )
        )

    def test_skill_axis_evidence_rejects_misbound_envelope(self) -> None:
        data = self.fixture.read_skill_evals()
        reference = data["cases"][0]["conformance"]["evidence"][0]
        path = self.root / reference["path"]
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["source_revision"] = "c" * 64
        evidence["case_id"] = "different-case"
        evidence["axis"] = "outcome"
        evidence["result"] = "FAIL"
        evidence["input_digests"]["profile_inputs"] = "0" * 64
        evidence["case_input_sha256"] = "0" * 64
        self.fixture.update_axis_evidence(0, "conformance", evidence)
        messages = self.messages()
        for expected in (
            "skill evaluation axis evidence source_revision is stale",
            "skill evaluation axis evidence case_id is misbound",
            "skill evaluation axis evidence axis is misbound",
            "skill evaluation axis evidence result must equal PASS case verdict",
            "skill evaluation axis evidence case_input_sha256 is stale or misbound",
            "skill evaluation axis evidence input_digests.profile_inputs is stale or misbound",
        ):
            self.assertIn(expected, messages)

    def test_optional_negative_kind_requires_adversarial_fixture_not_happy_prompt(self) -> None:
        profile = self.fixture.read_profile()
        for capability in ("audit-changes", "publish"):
            name = f"example-{capability}"
            directory = self.root / ".agents/skills" / name
            self.fixture.write(
                f".agents/skills/{name}/SKILL.md",
                f"---\nname: {name}\n---\n\n# {capability}\n",
            )
            profile["skills"][capability] = {
                "name": name,
                "path": directory.relative_to(self.root).as_posix(),
                "sha256": self.fixture.digest(directory),
            }
        self.fixture.update_profile(profile)
        specs = self.fixture.current_skill_eval_specs()
        specs.extend(
            (kind, kind, [capability])
            for capability, kinds in (
                ("audit-changes", ("audit-immutable-range", "audit-checkpoint")),
                (
                    "publish",
                    ("publish-topology", "publish-conflict", "publish-final-revision"),
                ),
            )
            for kind in kinds
        )
        self.fixture.rebind_all_evidence(specs)
        data = self.fixture.read_skill_evals()
        case = next(item for item in data["cases"] if item["kind"] == "publish-topology")
        case["prompt"] = "Publish a normal happy-path change."
        del case["adversarial_fixture"]
        del case["expected_disposition"]
        del case["expected_failure"]
        self.fixture.update_skill_evals(data)
        messages = self.messages()
        for field in ("adversarial_fixture", "expected_disposition", "expected_failure"):
            self.assertTrue(any(f"missing required field: {field}" in message for message in messages))

    def test_optional_negative_adversarial_fixture_digest_is_enforced(self) -> None:
        profile = self.fixture.read_profile()
        capability = "audit-changes"
        name = f"example-{capability}"
        directory = self.root / ".agents/skills" / name
        self.fixture.write(
            f".agents/skills/{name}/SKILL.md",
            f"---\nname: {name}\n---\n\n# {capability}\n",
        )
        profile["skills"][capability] = {
            "name": name,
            "path": directory.relative_to(self.root).as_posix(),
            "sha256": self.fixture.digest(directory),
        }
        self.fixture.update_profile(profile)
        specs = self.fixture.current_skill_eval_specs() + [
            ("audit-immutable-range", "audit-immutable-range", [capability]),
            ("audit-checkpoint", "audit-checkpoint", [capability]),
        ]
        self.fixture.rebind_all_evidence(specs)
        data = self.fixture.read_skill_evals()
        case = next(item for item in data["cases"] if item["kind"] == "audit-checkpoint")
        reference = case["adversarial_fixture"]
        path = self.root / reference["path"]
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "stale cases[" in message and ".adversarial_fixture.sha256" in message
                for message in self.messages()
            )
        )

    def test_optional_negative_axis_binds_observed_disposition_and_failure(self) -> None:
        profile = self.fixture.read_profile()
        capability = "audit-changes"
        name = f"example-{capability}"
        directory = self.root / ".agents/skills" / name
        self.fixture.write(
            f".agents/skills/{name}/SKILL.md",
            f"---\nname: {name}\n---\n\n# {capability}\n",
        )
        profile["skills"][capability] = {
            "name": name,
            "path": directory.relative_to(self.root).as_posix(),
            "sha256": self.fixture.digest(directory),
        }
        self.fixture.update_profile(profile)
        specs = self.fixture.current_skill_eval_specs() + [
            ("audit-immutable-range", "audit-immutable-range", [capability]),
            ("audit-checkpoint", "audit-checkpoint", [capability]),
        ]
        self.fixture.rebind_all_evidence(specs)
        data = self.fixture.read_skill_evals()
        case_index = next(
            index
            for index, case in enumerate(data["cases"])
            if case["kind"] == "audit-checkpoint"
        )
        reference = data["cases"][case_index]["conformance"]["evidence"][0]
        path = self.root / reference["path"]
        evidence = json.loads(path.read_text(encoding="utf-8"))
        del evidence["observed_disposition"]
        evidence["observed_failure"] = "unrelated-failure"
        self.fixture.update_axis_evidence(case_index, "conformance", evidence)
        messages = self.messages()
        self.assertTrue(
            any("missing required field: observed_disposition" in message for message in messages)
        )
        self.assertIn(
            "skill evaluation axis evidence observed_disposition is misbound",
            messages,
        )
        self.assertIn(
            "skill evaluation axis evidence observed_failure is misbound",
            messages,
        )

        self.fixture.build()
        data = self.fixture.read_skill_evals()
        reference = data["cases"][0]["conformance"]["evidence"][0]
        path = self.root / reference["path"]
        evidence = json.loads(path.read_text(encoding="utf-8"))
        evidence["observed_disposition"] = "REFUSED"
        evidence["observed_failure"] = "not-applicable"
        self.fixture.update_axis_evidence(0, "conformance", evidence)
        messages = self.messages()
        self.assertIn(
            "skill evaluation axis evidence has unknown field: observed_disposition",
            messages,
        )
        self.assertIn(
            "skill evaluation axis evidence has unknown field: observed_failure",
            messages,
        )

    def test_optional_audit_and_publish_require_bound_negative_evaluations(self) -> None:
        profile = self.fixture.read_profile()
        for capability in ("audit-changes", "publish"):
            name = f"example-{capability}"
            directory = self.root / ".agents/skills" / name
            self.fixture.write(
                f".agents/skills/{name}/SKILL.md",
                f"---\nname: {name}\n---\n\n# {capability}\n",
            )
            profile["skills"][capability] = {
                "name": name,
                "path": directory.relative_to(self.root).as_posix(),
                "sha256": self.fixture.digest(directory),
            }
        self.fixture.update_profile(profile)

        specs = self.fixture.current_skill_eval_specs()
        specs.extend(
            [
                ("optional-forward", "optional-forward", ["audit-changes", "publish"]),
                ("audit-immutable-range", "audit-immutable-range", ["audit-changes"]),
                ("audit-checkpoint", "audit-checkpoint", ["feature"]),
                ("publish-topology", "publish-topology", ["feature"]),
            ]
        )
        self.fixture.replace_skill_eval_cases(specs)
        messages = self.messages()
        self.assertIn(
            "required audit-changes negative case audit-checkpoint must reference skill: audit-changes",
            messages,
        )
        self.assertIn(
            "required publish negative case publish-topology must reference skill: publish",
            messages,
        )
        self.assertIn(
            "skill evaluations missing required publish negative case: publish-conflict",
            messages,
        )
        self.assertIn(
            "skill evaluations missing required publish negative case: publish-final-revision",
            messages,
        )

    def test_optional_audit_and_publish_accept_complete_negative_evaluations(self) -> None:
        profile = self.fixture.read_profile()
        for capability in ("audit-changes", "publish"):
            name = f"example-{capability}"
            directory = self.root / ".agents/skills" / name
            self.fixture.write(
                f".agents/skills/{name}/SKILL.md",
                f"---\nname: {name}\n---\n\n# {capability}\n",
            )
            profile["skills"][capability] = {
                "name": name,
                "path": directory.relative_to(self.root).as_posix(),
                "sha256": self.fixture.digest(directory),
            }
        self.fixture.update_profile(profile)
        specs = self.fixture.current_skill_eval_specs()
        specs.extend(
            (kind, kind, [capability])
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
        self.fixture.rebind_all_evidence(specs)
        self.assertEqual(self.messages(), [])

    def test_profile_outside_repo_root_fails(self) -> None:
        other = Path(self.temporary.name).parent / "outside-app-profile.json"
        other.write_text("{}\n", encoding="utf-8")
        self.addCleanup(lambda: other.unlink(missing_ok=True))
        findings = validate_app_profile(other, self.root)
        self.assertTrue(
            any("must be inside the explicit repo root" in item.message for item in findings)
        )

    def test_findings_are_deterministic_and_sorted(self) -> None:
        profile = self.fixture.read_profile()
        del profile["skills"]["ui"]
        profile["pattern_catalog"]["sha256"] = hashlib.sha256(b"wrong").hexdigest()
        self.fixture.update_profile(profile)
        first = validate_app_profile(self.fixture.profile_path, self.root)
        second = validate_app_profile(self.fixture.profile_path, self.root)
        self.assertEqual(first, second)
        self.assertEqual(first, sorted(first))


if __name__ == "__main__":
    unittest.main()
