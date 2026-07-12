#!/usr/bin/env python3
"""Validate and score a control-level readiness assessment JSON file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


ALLOWED_SCORES = {0.0, 0.25, 0.5, 0.75, 1.0}
SCORER_VERSION = "1.0.0"
ASSESSMENT_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}$")
LOCAL_CONTROL_ID = re.compile(r"^CTL-[A-Z0-9]+(?:-[A-Z0-9]+){2,}$")
OPERATING_MODES = {"GREENFIELD", "EVOLUTION", "REFACTOR", "RELEASE", "AUDIT"}
MODE_GATE = {
    "GREENFIELD": "GATE-GREENFIELD-01",
    "EVOLUTION": "GATE-EVOLUTION-01",
    "REFACTOR": "GATE-REFACTOR-01",
    "RELEASE": "GATE-RELEASE-01",
}
EVIDENCE_REFERENCE = re.compile(
    r"^(?P<kind>command|test|artifact|measurement|drill|runtime|review|planning):\S.+$"
)
STRONG_EVIDENCE_KINDS = {"command", "test", "measurement", "drill", "runtime"}
EVIDENCE_MANIFEST_VERSION = "1.0.0"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve_evidence_manifest(
    assessment_path: Path,
    assessment: dict[str, Any],
    *,
    allowed_root: Path | None = None,
) -> tuple[set[str], list[str], dict[str, Any] | None]:
    """Resolve evidence references to immutable local artifacts.

    This proves locator integrity, not that a producer identity is trustworthy. A
    repository's release policy still decides which CI/runtime/reviewer producers
    are accepted.
    """

    locator = assessment.get("evidence_manifest")
    declared_digest = assessment.get("evidence_manifest_sha256")
    if locator in (None, "") and declared_digest in (None, ""):
        return set(), [], None

    errors: list[str] = []
    if not isinstance(locator, str) or not locator.strip():
        return set(), ["evidence_manifest must be a non-empty relative path"], None
    if Path(locator).is_absolute():
        return set(), ["evidence_manifest must be relative to the assessment file"], None
    if not isinstance(declared_digest, str) or not SHA256.fullmatch(declared_digest):
        errors.append("evidence_manifest_sha256 must be a lowercase SHA-256 digest")

    manifest_path = (assessment_path.parent / locator).resolve()
    evidence_root = (allowed_root or assessment_path.parent).resolve()
    try:
        manifest_path.relative_to(evidence_root)
    except ValueError:
        return set(), ["evidence_manifest resolves outside the allowed repository root"], None
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"cannot read evidence manifest {locator}: {error}")
        return set(), errors, None
    if not isinstance(manifest, dict):
        errors.append("evidence manifest root must be an object")
        return set(), errors, None

    actual_digest = hashlib.sha256(manifest_bytes).hexdigest()
    if declared_digest != actual_digest:
        errors.append(
            f"evidence manifest digest mismatch: declared={declared_digest!r} actual={actual_digest!r}"
        )
    if manifest.get("manifest_version") != EVIDENCE_MANIFEST_VERSION:
        errors.append(
            f"evidence manifest version must be {EVIDENCE_MANIFEST_VERSION}"
        )
    manifest_id = manifest.get("manifest_id")
    if not isinstance(manifest_id, str) or not ASSESSMENT_ID.fullmatch(manifest_id):
        errors.append("evidence manifest requires a stable uppercase manifest_id")
    for field in ("assessment_id", "source_revision", "target", "environment"):
        if manifest.get(field) != assessment.get(field):
            errors.append(f"evidence manifest {field} must match the assessment")
    trusted_producers = assessment.get("trusted_evidence_producers")
    if not isinstance(trusted_producers, list) or not trusted_producers or not all(
        isinstance(producer, str) and producer.strip() for producer in trusted_producers
    ):
        errors.append("manifest-backed assessment requires trusted_evidence_producers")
        trusted_producers = []
    if not isinstance(assessment.get("evidence_acceptor"), str) or not assessment[
        "evidence_acceptor"
    ].strip():
        errors.append("manifest-backed assessment requires evidence_acceptor")

    assessment_date_value = assessment.get("observed_at")
    try:
        assessment_date = date.fromisoformat(assessment_date_value)
    except (TypeError, ValueError):
        assessment_date = None

    records = manifest.get("records")
    if not isinstance(records, list):
        errors.append("evidence manifest records must be an array")
        return set(), errors, {
            "path": locator,
            "sha256": actual_digest,
            "manifest_id": manifest_id,
        }

    verified: set[str] = set()
    seen: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"evidence manifest records[{index}]"
        record_valid = True
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        reference = record.get("reference")
        if not isinstance(reference, str) or not EVIDENCE_REFERENCE.fullmatch(reference):
            errors.append(f"{prefix} requires a valid evidence reference")
            record_valid = False
        elif reference in seen:
            errors.append(f"duplicate evidence manifest reference: {reference}")
            record_valid = False
        else:
            seen.add(reference)
        if record.get("result") != "pass":
            errors.append(f"{prefix} result must be pass")
            record_valid = False
        if not isinstance(record.get("producer"), str) or not record["producer"].strip():
            errors.append(f"{prefix} requires producer")
            record_valid = False
        elif record["producer"] not in trusted_producers:
            errors.append(f"{prefix} producer is not accepted by trusted_evidence_producers")
            record_valid = False
        observed_value = record.get("observed_at")
        try:
            observed = date.fromisoformat(observed_value)
        except (TypeError, ValueError):
            errors.append(f"{prefix} observed_at must use YYYY-MM-DD")
            observed = None
            record_valid = False
        if observed and (observed > date.today() or (assessment_date and observed > assessment_date)):
            errors.append(f"{prefix} observed_at cannot follow the assessment/current date")
            record_valid = False

        artifact_locator = record.get("artifact")
        artifact_digest = record.get("sha256")
        if not isinstance(artifact_locator, str) or not artifact_locator.strip() or Path(artifact_locator).is_absolute():
            errors.append(f"{prefix} artifact must be a non-empty relative path")
            record_valid = False
        if not isinstance(artifact_digest, str) or not SHA256.fullmatch(artifact_digest):
            errors.append(f"{prefix} sha256 must be a lowercase SHA-256 digest")
            record_valid = False
        if isinstance(artifact_locator, str) and artifact_locator.strip() and not Path(artifact_locator).is_absolute():
            artifact_path = (manifest_path.parent / artifact_locator).resolve()
            try:
                artifact_path.relative_to(evidence_root)
            except ValueError:
                errors.append(f"{prefix} artifact resolves outside the allowed repository root")
                record_valid = False
                continue
            try:
                actual_artifact_digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            except OSError as error:
                errors.append(f"{prefix} cannot read artifact {artifact_locator}: {error}")
                record_valid = False
            else:
                if artifact_digest != actual_artifact_digest:
                    errors.append(f"{prefix} artifact digest mismatch for {artifact_locator}")
                    record_valid = False
        if record_valid and isinstance(reference, str):
            verified.add(reference)

    if errors:
        verified = set()
    return verified, errors, {
        "path": locator,
        "sha256": actual_digest,
        "manifest_id": manifest_id,
    }


def unique_by_id(rows: Any, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        errors.append(f"{label} must be an array")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append(f"{label}[{index}] must be an object with string id")
            continue
        identifier = row["id"]
        if identifier in result:
            errors.append(f"duplicate {label} id: {identifier}")
        result[identifier] = row
    return result


def parse_date(value: Any, field: str, identifier: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{identifier}: {field} must use YYYY-MM-DD")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{identifier}: {field} must use YYYY-MM-DD")
        return None


def score_assessment(
    catalog: dict[str, Any],
    assessment: dict[str, Any],
    *,
    verified_evidence: set[str] | None = None,
    evidence_resolution_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = list(evidence_resolution_errors or [])
    resolved_references = verified_evidence or set()
    assessment_id = assessment.get("assessment_id")
    if not isinstance(assessment_id, str) or not ASSESSMENT_ID.fullmatch(assessment_id):
        errors.append("assessment_id must be a stable uppercase ID with at least three segments")
    operating_mode = assessment.get("operating_mode")
    if operating_mode not in OPERATING_MODES:
        errors.append(f"operating_mode must be one of {sorted(OPERATING_MODES)}")
    for field in (
        "system_profile",
        "source_revision",
        "target",
        "environment",
        "timezone",
        "freshness_policy",
    ):
        if not isinstance(assessment.get(field), str) or not assessment[field].strip():
            errors.append(f"assessment metadata requires non-empty {field}")
    if assessment.get("scorer_version") != SCORER_VERSION:
        errors.append(
            f"scorer_version mismatch: assessment={assessment.get('scorer_version')!r} scorer={SCORER_VERSION!r}"
        )
    assessment_date = parse_date(
        assessment.get("observed_at"), "observed_at", str(assessment_id or "assessment"), errors
    )
    if assessment_date and assessment_date > date.today():
        errors.append("assessment observed_at cannot be in the future")
    if assessment.get("catalog_version") != catalog.get("catalog_version"):
        errors.append(
            "catalog_version mismatch: "
            f"assessment={assessment.get('catalog_version')!r} catalog={catalog.get('catalog_version')!r}"
        )

    catalog_controls = unique_by_id(catalog.get("controls"), "catalog.controls", errors)
    catalog_gates = unique_by_id(catalog.get("gates"), "catalog.gates", errors)
    assessed_controls = unique_by_id(assessment.get("controls"), "assessment.controls", errors)
    assessed_gates = unique_by_id(assessment.get("gates"), "assessment.gates", errors)

    missing_controls = sorted(set(catalog_controls) - set(assessed_controls))
    unknown_controls = sorted(set(assessed_controls) - set(catalog_controls))
    if missing_controls:
        errors.append("missing controls: " + ", ".join(missing_controls))
    local_controls: dict[str, dict[str, Any]] = {}
    for identifier in unknown_controls:
        row = assessed_controls[identifier]
        if not LOCAL_CONTROL_ID.fullmatch(identifier) or row.get("repo_owned") is not True:
            errors.append(
                f"unknown control {identifier}: repo-owned extensions require a CTL-* ID and repo_owned=true"
            )
            continue
        if not isinstance(row.get("source_rule"), str) or not row["source_rule"].strip():
            errors.append(f"{identifier}: repo-owned control requires source_rule")
        if not isinstance(row.get("expected_outcome"), str) or not row["expected_outcome"].strip():
            errors.append(f"{identifier}: repo-owned control requires expected_outcome")
        local_controls[identifier] = row

    missing_gates = sorted(set(catalog_gates) - set(assessed_gates))
    unknown_gates = sorted(set(assessed_gates) - set(catalog_gates))
    if missing_gates:
        errors.append("missing gates: " + ", ".join(missing_gates))
    if unknown_gates:
        errors.append("unknown gates: " + ", ".join(unknown_gates))

    scores: dict[int, list[Decimal]] = defaultdict(list)
    critical_below_threshold: list[str] = []
    stale_evidence: list[str] = []
    today = date.today()

    control_definitions = {**catalog_controls, **local_controls}
    for identifier, catalog_control in control_definitions.items():
        row = assessed_controls.get(identifier)
        dimension = catalog_control.get("dimension")
        if not isinstance(dimension, int) or dimension not in range(1, 11):
            errors.append(f"catalog control {identifier}: invalid dimension")
            continue
        if not row:
            scores[dimension].append(Decimal("0"))
            continue
        applicable = row.get("applicable")
        if not isinstance(applicable, bool):
            errors.append(f"{identifier}: applicable must be boolean")
            scores[dimension].append(Decimal("0"))
            continue
        if not applicable:
            if identifier in local_controls:
                errors.append(f"{identifier}: omit an inapplicable repo-owned extension instead of marking it N/A")
            if catalog_control.get("baseline") is True:
                errors.append(f"{identifier}: baseline control cannot be marked N/A")
                scores[dimension].append(Decimal("0"))
            for field in ("n_a_rationale", "owner", "revisit_trigger"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    errors.append(f"{identifier}: N/A control requires {field}")
            applicability_evidence = row.get("applicability_evidence")
            if not isinstance(applicability_evidence, list) or not applicability_evidence:
                errors.append(f"{identifier}: N/A control requires applicability_evidence")
            else:
                for reference in applicability_evidence:
                    match = EVIDENCE_REFERENCE.fullmatch(reference) if isinstance(reference, str) else None
                    if not match or match.group("kind") not in {"artifact", "review"}:
                        errors.append(
                            f"{identifier}: N/A applicability_evidence must use artifact: or review: references"
                        )
                    elif reference not in resolved_references:
                        errors.append(
                            f"{identifier}: N/A applicability_evidence is not resolved by the evidence manifest: {reference}"
                        )
            parse_date(row.get("decision_observed_at"), "decision_observed_at", identifier, errors)
            continue

        owner = row.get("owner")
        evidence = row.get("evidence")
        critical = row.get("critical")
        critical_rationale = row.get("critical_rationale")
        declared_score = row.get("score")
        if not isinstance(owner, str) or not owner.strip():
            errors.append(f"{identifier}: applicable control requires owner")
        if not isinstance(critical, bool):
            errors.append(f"{identifier}: applicable control requires boolean critical")
            critical = False
        if not isinstance(critical_rationale, str) or not critical_rationale.strip():
            errors.append(f"{identifier}: applicable control requires critical_rationale")
        if isinstance(declared_score, bool) or not isinstance(declared_score, (int, float)) or float(declared_score) not in ALLOWED_SCORES:
            errors.append(f"{identifier}: score must be one of {sorted(ALLOWED_SCORES)}")
            continue
        if not isinstance(evidence, list) or not all(isinstance(item, str) and item.strip() for item in evidence):
            errors.append(f"{identifier}: evidence must be an array of non-empty references")
            evidence = []
        evidence_kinds: set[str] = set()
        strong_references: set[str] = set()
        for reference in evidence:
            match = EVIDENCE_REFERENCE.fullmatch(reference)
            if not match:
                errors.append(f"{identifier}: invalid evidence reference '{reference}'")
            else:
                evidence_kinds.add(match.group("kind"))
                if match.group("kind") in STRONG_EVIDENCE_KINDS:
                    strong_references.add(reference)

        observed = parse_date(row.get("observed_at"), "observed_at", identifier, errors)
        valid_until = None
        if row.get("valid_until") is not None:
            valid_until = parse_date(row.get("valid_until"), "valid_until", identifier, errors)
        invalidation_trigger = row.get("invalidation_trigger")
        if valid_until is None and (
            not isinstance(invalidation_trigger, str) or not invalidation_trigger.strip()
        ):
            errors.append(f"{identifier}: requires valid_until or invalidation_trigger")
        if observed and assessment_date and observed > assessment_date:
            errors.append(f"{identifier}: observed_at cannot follow the assessment observed_at")
        if observed and valid_until and valid_until < observed:
            errors.append(f"{identifier}: valid_until cannot precede observed_at")

        effective = Decimal(str(declared_score))
        if effective >= Decimal("0.75") and not (evidence_kinds & STRONG_EVIDENCE_KINDS):
            errors.append(f"{identifier}: score >= 0.75 requires command/test/measurement/drill/runtime evidence")
            effective = Decimal("0")
        if effective >= Decimal("0.75"):
            unresolved = sorted(strong_references - resolved_references)
            if unresolved:
                errors.append(
                    f"{identifier}: strong evidence is not resolved by the evidence manifest: "
                    + ", ".join(unresolved)
                )
                effective = Decimal("0")
        if not evidence:
            effective = Decimal("0")
        if valid_until and valid_until < today:
            stale_evidence.append(identifier)
            effective = min(effective, Decimal("0.5"))
        if observed and observed > today:
            errors.append(f"{identifier}: observed_at cannot be in the future")

        scores[dimension].append(effective)
        if critical and effective < Decimal("0.75"):
            critical_below_threshold.append(identifier)

    dimension_scores: dict[str, Decimal] = {}
    for dimension in range(1, 11):
        values = scores.get(dimension, [])
        if not values:
            errors.append(f"dimension {dimension} has zero applicable controls")
        dimension_scores[str(dimension)] = sum(values, Decimal("0")) / len(values) if values else Decimal("0")
    total = sum(dimension_scores.values(), Decimal("0"))

    failed_gates: list[str] = []
    stale_gates: list[str] = []
    applicable_gates: set[str] = set()
    for identifier, _catalog_gate in catalog_gates.items():
        row = assessed_gates.get(identifier)
        if not row:
            continue
        applicable = row.get("applicable")
        if not isinstance(applicable, bool):
            errors.append(f"{identifier}: applicable must be boolean")
            continue
        if not applicable:
            for field in ("n_a_rationale", "owner", "revisit_trigger"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    errors.append(f"{identifier}: N/A gate requires {field}")
            continue
        applicable_gates.add(identifier)
        if not isinstance(row.get("owner"), str) or not row["owner"].strip():
            errors.append(f"{identifier}: applicable gate requires owner")
        if not isinstance(row.get("passed"), bool):
            errors.append(f"{identifier}: passed must be boolean")
        if row.get("passed") is not True:
            failed_gates.append(identifier)
        evidence = row.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(item, str) and item.strip() for item in evidence
        ):
            errors.append(f"{identifier}: applicable gate requires evidence")
            evidence = []
        gate_kinds: set[str] = set()
        gate_strong_references: set[str] = set()
        for reference in evidence:
            match = EVIDENCE_REFERENCE.fullmatch(reference)
            if not match:
                errors.append(f"{identifier}: invalid evidence reference '{reference}'")
            else:
                gate_kinds.add(match.group("kind"))
                if match.group("kind") in STRONG_EVIDENCE_KINDS:
                    gate_strong_references.add(reference)
        if row.get("passed") is True and not (gate_kinds & STRONG_EVIDENCE_KINDS):
            errors.append(f"{identifier}: passed gate requires strong observed evidence")
        if row.get("passed") is True:
            unresolved = sorted(gate_strong_references - resolved_references)
            if unresolved:
                errors.append(
                    f"{identifier}: strong evidence is not resolved by the evidence manifest: "
                    + ", ".join(unresolved)
                )
                if identifier not in failed_gates:
                    failed_gates.append(identifier)
        gate_observed = parse_date(row.get("observed_at"), "observed_at", identifier, errors)
        gate_valid_until = None
        if row.get("valid_until") is not None:
            gate_valid_until = parse_date(row.get("valid_until"), "valid_until", identifier, errors)
        gate_invalidation_trigger = row.get("invalidation_trigger")
        if gate_valid_until is None and (
            not isinstance(gate_invalidation_trigger, str) or not gate_invalidation_trigger.strip()
        ):
            errors.append(f"{identifier}: requires valid_until or invalidation_trigger")
        if gate_observed and assessment_date and gate_observed > assessment_date:
            errors.append(f"{identifier}: observed_at cannot follow the assessment observed_at")
        if gate_observed and gate_valid_until and gate_valid_until < gate_observed:
            errors.append(f"{identifier}: valid_until cannot precede observed_at")
        if gate_valid_until and gate_valid_until < today:
            stale_gates.append(identifier)
            if identifier not in failed_gates:
                failed_gates.append(identifier)

    if not applicable_gates:
        errors.append("at least one readiness gate must be applicable")
    required_gate = MODE_GATE.get(str(operating_mode))
    if required_gate and required_gate not in applicable_gates:
        errors.append(f"operating_mode {operating_mode} requires applicable gate {required_gate}")

    all_dimensions_ready = all(score >= Decimal("0.75") for score in dimension_scores.values())
    ready = not errors and not critical_below_threshold and not failed_gates and all_dimensions_ready
    nine_five_ready = ready and total >= Decimal("9.5") and not stale_evidence and not stale_gates
    result = "9.5-ready" if nine_five_ready else "ready" if ready else "not-ready"
    dimension_display = {
        key: str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        for key, value in dimension_scores.items()
    }
    total_display = str(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    return {
        "assessment_id": assessment_id,
        "scorer_version": SCORER_VERSION,
        "catalog_version": catalog.get("catalog_version"),
        "system_profile": assessment.get("system_profile"),
        "source_revision": assessment.get("source_revision"),
        "target": assessment.get("target"),
        "environment": assessment.get("environment"),
        "observed_at": assessment.get("observed_at"),
        "timezone": assessment.get("timezone"),
        "operating_mode": operating_mode,
        "dimension_scores": {
            key: float(value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
            for key, value in dimension_scores.items()
        },
        "dimension_display": dimension_display,
        "total": float(total.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)),
        "total_display": total_display,
        "critical_below_0_75": sorted(critical_below_threshold),
        "failed_gates": sorted(failed_gates),
        "stale_evidence": sorted(stale_evidence),
        "stale_gates": sorted(stale_gates),
        "resolved_evidence_count": len(resolved_references),
        "errors": errors,
        "result": result,
    }


def build_skeleton(catalog: dict[str, Any]) -> dict[str, Any]:
    today = date.today().isoformat()
    controls = []
    for row in catalog.get("controls", []):
        controls.append(
            {
                "id": row["id"],
                "applicable": None,
                "critical": None,
                "critical_rationale": "",
                "score": 0.0,
                "owner": "",
                "evidence": [],
                "observed_at": today,
                "valid_until": None,
                "invalidation_trigger": "",
                "n_a_rationale": "",
                "revisit_trigger": "",
                "applicability_evidence": [],
                "decision_observed_at": today,
            }
        )
    gates = []
    for row in catalog.get("gates", []):
        gates.append(
            {
                "id": row["id"],
                "applicable": None,
                "passed": None,
                "owner": "",
                "evidence": [],
                "observed_at": today,
                "valid_until": None,
                "invalidation_trigger": "",
                "n_a_rationale": "",
                "revisit_trigger": "",
            }
        )
    return {
        "assessment_id": "ASSESSMENT-REPLACE-001",
        "scorer_version": SCORER_VERSION,
        "catalog_version": catalog.get("catalog_version"),
        "system_profile": "SYS-REPLACE-001",
        "operating_mode": None,
        "source_revision": "",
        "target": "",
        "environment": "",
        "observed_at": today,
        "timezone": "",
        "freshness_policy": "",
        "evidence_manifest": None,
        "evidence_manifest_sha256": None,
        "trusted_evidence_producers": [],
        "evidence_acceptor": None,
        "controls": controls,
        "gates": gates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assessment", nargs="?", type=Path)
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "controls" / "core-controls.json",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--require", choices=("ready", "9.5-ready"))
    parser.add_argument("--expect", choices=("not-ready", "ready", "9.5-ready"))
    parser.add_argument("--init", metavar="PATH", type=Path, help="Write a complete assessment skeleton")
    args = parser.parse_args(argv)

    try:
        catalog = load_json(args.catalog)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    if args.init:
        if args.assessment:
            parser.error("assessment and --init cannot be used together")
        if args.init.exists():
            print(f"refusing to overwrite existing file: {args.init}", file=sys.stderr)
            return 2
        args.init.parent.mkdir(parents=True, exist_ok=True)
        args.init.write_text(json.dumps(build_skeleton(catalog), indent=2) + "\n", encoding="utf-8")
        print(f"created assessment skeleton: {args.init}")
        return 0
    if not args.assessment:
        parser.error("assessment is required unless --init is used")
    if args.require and args.expect:
        parser.error("--require and --expect cannot be used together")

    try:
        assessment = load_json(args.assessment)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    verified_evidence, resolution_errors, manifest_info = resolve_evidence_manifest(
        args.assessment,
        assessment,
        allowed_root=args.catalog.resolve().parent.parent,
    )
    result = score_assessment(
        catalog,
        assessment,
        verified_evidence=verified_evidence,
        evidence_resolution_errors=resolution_errors,
    )
    result["assessment_sha256"] = hashlib.sha256(args.assessment.read_bytes()).hexdigest()
    result["catalog_sha256"] = hashlib.sha256(args.catalog.read_bytes()).hexdigest()
    result["evidence_manifest"] = manifest_info
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"assessment={result['assessment_id']!r} result={result['result']} total={result['total']:.4f}/10")
        for dimension, value in result["dimension_scores"].items():
            print(f"dimension {dimension}: {value:.4f}")
        for error in result["errors"]:
            print(f"error: {error}")
        if result["critical_below_0_75"]:
            print("critical below 0.75: " + ", ".join(result["critical_below_0_75"]))
        if result["failed_gates"]:
            print("failed gates: " + ", ".join(result["failed_gates"]))
        if result["stale_evidence"]:
            print("stale evidence: " + ", ".join(result["stale_evidence"]))
        if result["stale_gates"]:
            print("stale gates: " + ", ".join(result["stale_gates"]))

    if result["errors"]:
        return 2
    if args.require == "ready" and result["result"] == "not-ready":
        return 1
    if args.require == "9.5-ready" and result["result"] != "9.5-ready":
        return 1
    if args.expect and result["result"] != args.expect:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
