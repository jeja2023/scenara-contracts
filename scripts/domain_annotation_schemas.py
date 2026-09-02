from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from scenara_contracts.repository_v1 import DomainAnnotationSchema  # noqa: E402

RELEASE_VERSION = "1.1.0"
OUTPUT_DIR = ROOT / "contracts" / "domain-annotations" / f"v{RELEASE_VERSION}"


def _object_array(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "array",
        "items": {
            "type": "object",
            "required": required,
            "properties": properties,
            "additionalProperties": True,
        },
    }


def definitions() -> tuple[DomainAnnotationSchema, ...]:
    non_negative_integer = {"type": "integer", "minimum": 0}
    confidence = {"type": "number", "minimum": 0, "maximum": 1}
    nullable_string = {"type": ["string", "null"]}
    return (
        DomainAnnotationSchema(
            schema_id="scenara.feedback.correction.v1",
            version="1.0.0",
            domain="feedback",
            task_type="generic_correction",
            supported_media_kinds=("image", "video", "document", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "minProperties": 1,
                "additionalProperties": True,
            },
            quality_rules=("non_empty_correction",),
        ),
        DomainAnnotationSchema(
            schema_id="scenara.portrait.detection.v1",
            version="1.0.0",
            domain="portrait",
            task_type="person_detection",
            supported_media_kinds=("image", "video", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["persons"],
                "properties": {
                    "persons": _object_array(
                        {
                            "label": {"type": "string", "minLength": 1},
                            "bbox": {
                                "type": "array",
                                "prefixItems": [
                                    {"type": "number", "minimum": 0},
                                    {"type": "number", "minimum": 0},
                                    {"type": "number", "exclusiveMinimum": 0},
                                    {"type": "number", "exclusiveMinimum": 0},
                                ],
                                "minItems": 4,
                                "maxItems": 4,
                            },
                            "confidence": confidence,
                        },
                        ["label", "bbox"],
                    )
                },
                "additionalProperties": False,
            },
            quality_rules=("valid_bbox", "non_empty_persons"),
        ),
        DomainAnnotationSchema(
            schema_id="scenara.portrait.surveillance-review.v1",
            version="1.0.0",
            domain="portrait",
            task_type="surveillance_match_review",
            supported_media_kinds=("image", "video", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["alert_id", "triage_reason", "review_outcome"],
                "properties": {
                    "alert_id": {"type": "string", "pattern": "^alt_[A-Za-z0-9]+$"},
                    "triage_reason": {"type": "string", "minLength": 1, "maxLength": 256},
                    "review_outcome": {"const": "false_positive"},
                    "notes": {"type": "string", "maxLength": 2000},
                },
                "additionalProperties": True,
            },
            quality_rules=("false_positive_review", "non_empty_triage_reason"),
        ),
        DomainAnnotationSchema(
            schema_id="scenara.ocr.document.v1",
            version="1.0.0",
            domain="ocr",
            task_type="document_recognition",
            supported_media_kinds=("image", "document", "video", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["blocks"],
                "properties": {
                    "text": {"type": "string"},
                    "language": nullable_string,
                    "blocks": _object_array(
                        {
                            "text": {"type": "string"},
                            "block_type": {
                                "enum": ["text", "title", "paragraph", "image", "table"]
                            },
                            "reading_order": non_negative_integer,
                            "score": confidence,
                            "polygon": {
                                "type": "array",
                                "minItems": 3,
                                "items": {
                                    "type": "array",
                                    "prefixItems": [{"type": "number"}, {"type": "number"}],
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                            },
                        },
                        ["text", "block_type", "polygon"],
                    ),
                },
                "additionalProperties": False,
            },
            quality_rules=("valid_polygon", "reading_order_unique", "non_empty_text_or_region"),
        ),
        DomainAnnotationSchema(
            schema_id="scenara.behavior.action.v1",
            version="1.0.0",
            domain="behavior",
            task_type="action_recognition",
            supported_media_kinds=("video", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["actions"],
                "properties": {
                    "actions": _object_array(
                        {
                            "action_type": {"type": "string", "minLength": 1},
                            "start_ms": non_negative_integer,
                            "end_ms": non_negative_integer,
                            "track_id": nullable_string,
                            "confidence": confidence,
                        },
                        ["action_type", "start_ms", "end_ms"],
                    ),
                    "segments": _object_array(
                        {
                            "segment_type": {"type": "string", "minLength": 1},
                            "start_ms": non_negative_integer,
                            "end_ms": non_negative_integer,
                            "confidence": confidence,
                        },
                        ["segment_type", "start_ms", "end_ms"],
                    ),
                },
                "additionalProperties": False,
            },
            quality_rules=("non_empty_actions", "valid_temporal_range", "non_overlapping_duplicate_labels"),
        ),
        DomainAnnotationSchema(
            schema_id="scenara.fashion.style.v1",
            version="1.0.0",
            domain="fashion",
            task_type="fashion_recognition",
            supported_media_kinds=("image", "video", "stream"),
            payload_schema={
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["cosplay", "clothing_styles", "accessories"],
                "properties": {
                    "cosplay": _object_array(
                        {
                            "character_name": {"type": "string", "minLength": 1},
                            "series_name": {"type": "string", "minLength": 1},
                            "confidence": confidence,
                        },
                        ["character_name", "series_name"],
                    ),
                    "clothing_styles": _object_array(
                        {
                            "style_type": {"type": "string", "minLength": 1},
                            "style_label": {"type": "string", "minLength": 1},
                            "confidence": confidence,
                        },
                        ["style_type", "style_label"],
                    ),
                    "accessories": _object_array(
                        {
                            "accessory_type": {"type": "string", "minLength": 1},
                            "accessory_label": {"type": "string", "minLength": 1},
                            "confidence": confidence,
                        },
                        ["accessory_type", "accessory_label"],
                    ),
                },
                "additionalProperties": False,
            },
            quality_rules=("known_label_set", "confidence_in_range", "at_least_one_fashion_label"),
        ),
    )


def _document(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def rendered_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    entries: list[dict[str, str]] = []
    for definition in definitions():
        document = definition.model_dump(mode="json")
        Draft202012Validator.check_schema(document["payload_schema"])
        filename = f"{definition.schema_id}.json"
        content = _document(document)
        files[filename] = content
        entries.append(
            {
                "schema_id": definition.schema_id,
                "version": definition.version,
                "path": f"contracts/domain-annotations/v{RELEASE_VERSION}/{filename}",
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    files["manifest.json"] = _document(
        {"schema_version": "1.0", "release_version": RELEASE_VERSION, "schemas": entries}
    )
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="生成不可变领域标注模式实例")
    parser.add_argument("--check", action="store_true", help="校验模式文件是否发生漂移")
    args = parser.parse_args()
    files = rendered_files()
    if args.check:
        drifted = [
            name
            for name, content in files.items()
            if not (OUTPUT_DIR / name).is_file() or (OUTPUT_DIR / name).read_bytes() != content
        ]
        if drifted:
            raise SystemExit("领域标注模式发生漂移：" + ", ".join(drifted))
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (OUTPUT_DIR / name).write_bytes(content)


if __name__ == "__main__":
    main()
