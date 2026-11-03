#!/usr/bin/env python3
"""Validate the FCS unit-test specification's structural contract."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CSV = WORKSPACE_ROOT / "docs" / "fcs-unit-test-spec.csv"
DEFAULT_REQUIREMENTS = WORKSPACE_ROOT / "docs" / "drone_flight_control_system_requirements.md"
DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "assets" / "spec-schema.json"
STORY_RANGE = re.compile(r"SF-(\d{3})\s*-\s*SF-(\d{3})")
STORY_ID = re.compile(r"SF-(\d{3})")
REQUIREMENT_ID = re.compile(r"FCS-(?:F|NF|S|T)-\d{3}")


def load_rows(csv_path: Path, header: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    try:
        text = csv_path.read_text(encoding="utf-8-sig")
        rows = list(csv.DictReader(text.splitlines(), strict=True))
    except (OSError, csv.Error) as error:
        return [], [f"cannot read CSV: {error}"]

    if not rows:
        errors.append("CSV has no data records")
    if rows and list(rows[0].keys()) != header:
        errors.append("header does not match the required schema")
    elif not rows:
        first_line = text.splitlines()[0] if text.splitlines() else ""
        try:
            parsed_header = next(csv.reader([first_line], strict=True))
        except csv.Error:
            parsed_header = []
        if parsed_header != header:
            errors.append("header does not match the required schema")

    physical_lines = text.splitlines()
    if len(physical_lines) != len(rows) + 1:
        errors.append("each CSV record must occupy exactly one physical line")
    return rows, errors


def extract_stories(value: str) -> set[str]:
    expanded = set()
    for first, last in STORY_RANGE.findall(value):
        start, end = int(first), int(last)
        step = 1 if start <= end else -1
        expanded.update(f"SF-{number:03d}" for number in range(start, end + step, step))
    without_ranges = STORY_RANGE.sub("", value)
    expanded.update(f"SF-{number}" for number in STORY_ID.findall(without_ranges))
    return expanded


def validate(csv_path: Path, requirements_path: Path, schema_path: Path) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read schema: {error}"]

    rows, errors = load_rows(csv_path, schema["header"])
    if errors:
        return errors

    record_types = set(schema["record_types"])
    case_statuses = set(schema["case_statuses"])
    required_case_fields = schema["case_required_fields"]
    seen_ids: set[str] = set()
    covered_stories: set[str] = set()
    referenced_requirements: set[str] = set()
    trace_types = set(schema["trace_record_types"])

    for row_number, row in enumerate(rows, start=2):
        record_type = row["record_type"].strip()
        record_id = row["record_id"].strip()
        if record_type not in record_types:
            errors.append(f"row {row_number}: unknown record_type {record_type!r}")
        if not record_id:
            errors.append(f"row {row_number}: record_id is empty")
        elif record_id in seen_ids:
            errors.append(f"row {row_number}: duplicate record_id {record_id!r}")
        seen_ids.add(record_id)

        if record_type == "CASE":
            for field in required_case_fields:
                if not row[field].strip():
                    errors.append(f"row {row_number}: CASE field {field!r} is empty")
            status = row["status"].strip()
            if status not in case_statuses:
                errors.append(f"row {row_number}: invalid CASE status {status!r}")
            if status in {"BLOCKED", "CONDITIONAL"} and not row["blocking_decision_or_evidence"].strip():
                errors.append(f"row {row_number}: {status} CASE lacks blocking decision/evidence")

        if record_type in trace_types:
            covered_stories.update(extract_stories(row["story_ids"]))
            referenced_requirements.update(REQUIREMENT_ID.findall(row["requirement_ids"]))

    if "CONTEXT" not in {row["record_type"].strip() for row in rows}:
        errors.append("at least one CONTEXT record is required")

    story_range = schema["story_range"]
    expected_stories = {
        f"{story_range['prefix']}{number:0{story_range['digits']}d}"
        for number in range(story_range["first"], story_range["last"] + 1)
    }
    missing_stories = sorted(expected_stories - covered_stories)
    if missing_stories:
        errors.append("stories not represented by CASE/GAP/OUT_OF_SCOPE: " + ", ".join(missing_stories))

    try:
        requirements_text = requirements_path.read_text(encoding="utf-8")
    except OSError as error:
        return errors + [f"cannot read requirements: {error}"]
    known_requirements = set(REQUIREMENT_ID.findall(requirements_text))
    unknown_requirements = sorted(referenced_requirements - known_requirements)
    if unknown_requirements:
        errors.append("requirement IDs not found in SRS: " + ", ".join(unknown_requirements))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="specification CSV path")
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS, help="SRS path")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="schema JSON path")
    args = parser.parse_args()

    errors = validate(args.csv, args.requirements, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid structure and traceability: {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())