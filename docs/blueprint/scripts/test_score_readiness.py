from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.score_readiness import (
    build_skeleton,
    resolve_evidence_manifest,
    score_assessment as _score_assessment,
)


def score_assessment(catalog_value, assessment_value):
    references = set()
    for row in assessment_value.get("controls", []):
        references.update(row.get("evidence", []))
        references.update(row.get("applicability_evidence", []))
    for row in assessment_value.get("gates", []):
        references.update(row.get("evidence", []))
    return _score_assessment(
        catalog_value,
        assessment_value,
        verified_evidence=references,
    )


def catalog():
    controls = []
    for dimension in range(1, 11):
        controls.append(
            {
                "id": f"CTL-TEST-{dimension:02d}-01",
                "dimension": dimension,
                "baseline": True,
                "critical_when": "The test says so",
            }
        )
    return {
        "catalog_version": "test",
        "controls": controls,
        "gates": [{"id": "GATE-TEST-01"}],
    }


def assessment(score=1.0):
    controls = []
    for dimension in range(1, 11):
        controls.append(
            {
                "id": f"CTL-TEST-{dimension:02d}-01",
                "applicable": True,
                "critical": True,
                "critical_rationale": "Test control is critical",
                "score": score,
                "owner": "test-owner",
                "evidence": ["command:test"],
                "observed_at": "2026-01-01",
                "invalidation_trigger": "source changes",
            }
        )
    return {
        "assessment_id": "TEST-ASSESSMENT-001",
        "scorer_version": "1.0.0",
        "catalog_version": "test",
        "system_profile": "SYS-TEST-001",
        "operating_mode": "AUDIT",
        "source_revision": "test-revision",
        "target": "artifact:test",
        "environment": "test",
        "observed_at": "2026-01-01",
        "timezone": "UTC",
        "freshness_policy": "Refresh whenever the test catalog changes",
        "controls": controls,
        "gates": [
            {
                "id": "GATE-TEST-01",
                "applicable": True,
                "passed": True,
                "owner": "test-owner",
                "evidence": ["command:test"],
                "observed_at": "2026-01-01",
                "invalidation_trigger": "gate contract changes",
            }
        ],
    }


class ReadinessScorerTests(unittest.TestCase):
    def test_skeleton_contains_complete_catalog(self):
        value = build_skeleton(catalog())
        self.assertEqual(len(value["controls"]), 10)
        self.assertEqual(len(value["gates"]), 1)
        self.assertTrue(all(row["applicable"] is None for row in value["controls"]))

    def test_reports_nine_five_ready(self):
        result = score_assessment(catalog(), assessment())
        self.assertEqual(result["result"], "9.5-ready")
        self.assertEqual(result["total"], 10.0)

    def test_critical_gap_caps_readiness(self):
        value = assessment()
        value["controls"][0]["score"] = 0.5
        result = score_assessment(catalog(), value)
        self.assertEqual(result["result"], "not-ready")
        self.assertEqual(result["critical_below_0_75"], ["CTL-TEST-01-01"])

    def test_requires_complete_control_universe(self):
        value = assessment()
        value["controls"].pop()
        result = score_assessment(catalog(), value)
        self.assertTrue(any("missing controls" in error for error in result["errors"]))

    def test_requires_nonempty_freshness_trigger(self):
        value = assessment()
        value["controls"][0]["invalidation_trigger"] = ""
        result = score_assessment(catalog(), value)
        self.assertTrue(any("requires valid_until or invalidation_trigger" in error for error in result["errors"]))

    def test_na_requires_owner_rationale_and_revisit(self):
        value = assessment()
        value["controls"][0] = {
            "id": "CTL-TEST-01-01",
            "applicable": False,
        }
        result = score_assessment(catalog(), value)
        self.assertTrue(any("N/A control requires" in error for error in result["errors"]))

    def test_baseline_and_gate_na_cannot_manufacture_nine_five(self):
        value = assessment()
        value["controls"] = [
            {
                "id": f"CTL-TEST-{dimension:02d}-01",
                "applicable": False,
                "owner": "test-owner",
                "n_a_rationale": "Generic exclusion",
                "revisit_trigger": "Never",
            }
            for dimension in range(1, 11)
        ]
        value["gates"] = [
            {
                "id": "GATE-TEST-01",
                "applicable": False,
                "owner": "test-owner",
                "n_a_rationale": "Generic exclusion",
                "revisit_trigger": "Never",
            }
        ]
        result = score_assessment(catalog(), value)
        self.assertEqual(result["result"], "not-ready")
        self.assertTrue(any("baseline control cannot be marked N/A" in error for error in result["errors"]))
        self.assertIn("at least one readiness gate must be applicable", result["errors"])

    def test_rejects_dimension_with_zero_applicable_controls(self):
        value = assessment()
        catalog_value = catalog()
        catalog_value["controls"][0]["baseline"] = False
        value["controls"][0] = {
            "id": "CTL-TEST-01-01",
            "applicable": False,
            "n_a_rationale": "Not in this system",
            "owner": "test-owner",
            "revisit_trigger": "Topology changes",
        }
        result = score_assessment(catalog_value, value)
        self.assertTrue(any("dimension 1 has zero applicable" in error for error in result["errors"]))

    def test_conditional_na_requires_profile_evidence(self):
        value = assessment()
        catalog_value = catalog()
        catalog_value["controls"][0]["baseline"] = False
        value["controls"][0] = {
            "id": "CTL-TEST-01-01",
            "applicable": False,
            "n_a_rationale": "The accepted profile has no identity boundary",
            "owner": "test-owner",
            "revisit_trigger": "Identity or private routes are introduced",
            "applicability_evidence": ["artifact:SYS-TEST-001@1.0.0#identity"],
            "decision_observed_at": "2026-01-01",
        }
        result = score_assessment(catalog_value, value)
        self.assertFalse(any("CTL-TEST-01-01:" in error for error in result["errors"]))

    def test_repo_owned_control_is_validated_and_scored(self):
        value = assessment()
        value["controls"].append(
            {
                "id": "CTL-REPO-PRIVACY-01",
                "repo_owned": True,
                "source_rule": "REPO-PRIVACY-01",
                "expected_outcome": "The local privacy export contract is enforced",
                "dimension": 3,
                "applicable": True,
                "critical": True,
                "critical_rationale": "A failure discloses personal data",
                "score": 0.75,
                "owner": "test-owner",
                "evidence": ["test:privacy-export-negative-case"],
                "observed_at": "2026-01-01",
                "invalidation_trigger": "privacy export changes",
            }
        )
        result = score_assessment(catalog(), value)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["dimension_scores"]["3"], 0.875)

    def test_unknown_control_without_repo_contract_is_rejected(self):
        value = assessment()
        value["controls"].append({"id": "CTL-UNKNOWN-LOCAL-01", "applicable": True})
        result = score_assessment(catalog(), value)
        self.assertTrue(any("unknown control CTL-UNKNOWN-LOCAL-01" in error for error in result["errors"]))

    def test_rejects_boolean_score(self):
        value = assessment()
        value["controls"][0]["score"] = True
        result = score_assessment(catalog(), value)
        self.assertTrue(any("score must be one of" in error for error in result["errors"]))

    def test_rejects_evidence_observed_after_assessment(self):
        value = assessment()
        value["controls"][0]["observed_at"] = "2026-01-02"
        result = score_assessment(catalog(), value)
        self.assertTrue(any("observed_at cannot follow" in error for error in result["errors"]))

    def test_stale_passed_gate_fails_readiness(self):
        value = assessment()
        value["gates"][0]["observed_at"] = "2019-12-31"
        value["gates"][0]["valid_until"] = "2020-01-01"
        value["gates"][0].pop("invalidation_trigger")
        result = score_assessment(catalog(), value)
        self.assertEqual(result["result"], "not-ready")
        self.assertEqual(result["stale_gates"], ["GATE-TEST-01"])

    def test_unresolved_command_strings_cannot_claim_readiness(self):
        result = _score_assessment(catalog(), assessment())
        self.assertEqual(result["result"], "not-ready")
        self.assertEqual(result["total"], 0.0)
        self.assertTrue(any("not resolved by the evidence manifest" in error for error in result["errors"]))

    def test_hashed_evidence_manifest_resolves_and_detects_tampering(self):
        value = assessment()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "command-result.txt"
            evidence.write_text("exit=0\n", encoding="utf-8")
            manifest = {
                "manifest_id": "EVIDENCE-MANIFEST-001",
                "manifest_version": "1.0.0",
                "assessment_id": value["assessment_id"],
                "source_revision": value["source_revision"],
                "target": value["target"],
                "environment": value["environment"],
                "records": [
                    {
                        "reference": "command:test",
                        "artifact": evidence.name,
                        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                        "result": "pass",
                        "producer": "ci:test-job",
                        "observed_at": "2026-01-01",
                    }
                ],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            value["evidence_manifest"] = manifest_path.name
            value["evidence_manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()
            value["trusted_evidence_producers"] = ["ci:test-job"]
            value["evidence_acceptor"] = "test-release-owner"

            verified, errors, _info = resolve_evidence_manifest(
                root / "assessment.json", value, allowed_root=root
            )
            self.assertEqual(errors, [])
            result = _score_assessment(
                catalog(), value, verified_evidence=verified, evidence_resolution_errors=errors
            )
            self.assertEqual(result["result"], "9.5-ready")

            evidence.write_text("exit=1\n", encoding="utf-8")
            verified, errors, _info = resolve_evidence_manifest(
                root / "assessment.json", value, allowed_root=root
            )
            self.assertEqual(verified, set())
            self.assertTrue(any("artifact digest mismatch" in error for error in errors))

    def test_golden_assessment_is_pinned_fail_closed(self):
        root = Path(__file__).resolve().parent.parent
        assessment_path = (
            root
            / "reference-app-blueprint"
            / "examples"
            / "basic-web-artifacts"
            / "readiness.json"
        )
        catalog_path = root / "controls" / "core-controls.json"
        assessment_value = json.loads(assessment_path.read_text(encoding="utf-8"))
        catalog_value = json.loads(catalog_path.read_text(encoding="utf-8"))
        result = _score_assessment(catalog_value, assessment_value)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["result"], "not-ready")
        self.assertEqual(result["total"], 0.0)
        self.assertEqual(result["failed_gates"], ["GATE-GREENFIELD-01"])

        record = assessment_path.with_name("readiness-assessment.md").read_text(encoding="utf-8")
        assessment_digest = hashlib.sha256(assessment_path.read_bytes()).hexdigest()
        catalog_digest = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
        self.assertIn(f"assessment input SHA-256: {assessment_digest}", record)
        self.assertIn(f"catalog SHA-256: {catalog_digest}", record)


if __name__ == "__main__":
    unittest.main()
