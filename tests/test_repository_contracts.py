from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from scripts.domain_annotation_schemas import definitions

from scenara_contracts.repository_v1 import (
    DatasetVersionReference,
    DomainAnnotationSchema,
    HardSampleManifest,
    ModelDeploymentEvent,
    ModelPackageManifest,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "repository" / "v1.2.0"

MODELS = {
    "dataset-version-input": DatasetVersionReference,
    "domain-annotation-schema": DomainAnnotationSchema,
    "deployment-feedback": ModelDeploymentEvent,
    "hard-sample-handoff": HardSampleManifest,
    "model-package-admission": ModelPackageManifest,
}


def test_published_examples_match_schema_and_python_types() -> None:
    for contract_id, model in MODELS.items():
        schema = json.loads((CONTRACT_ROOT / f"{contract_id}.schema.json").read_text(encoding="utf-8"))
        example = json.loads((CONTRACT_ROOT / f"{contract_id}.example.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(example)
        model.model_validate(example)


def test_release_catalog_names_all_published_contracts() -> None:
    manifest = json.loads((CONTRACT_ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["package_name"] == "@scenara/repository-contracts"
    assert manifest["release_version"] == "1.2.0"
    assert {item["contract_id"] for item in manifest["contracts"]} == set(MODELS)


@pytest.mark.parametrize(
    ("model", "field"),
    (
        (DatasetVersionReference, "created_at"),
        (HardSampleManifest, "created_at"),
        (ModelDeploymentEvent, "created_at"),
    ),
)
def test_cross_repository_times_reject_unix_numbers(model: type[object], field: str) -> None:
    contract_id = {
        DatasetVersionReference: "dataset-version-input",
        HardSampleManifest: "hard-sample-handoff",
        ModelDeploymentEvent: "deployment-feedback",
    }[model]
    example = json.loads((CONTRACT_ROOT / f"{contract_id}.example.json").read_text(encoding="utf-8"))
    example[field] = 1.0

    with pytest.raises(ValidationError):
        model.model_validate(example)


def test_cross_repository_examples_use_utc_rfc3339() -> None:
    for contract_id in ("dataset-version-input", "hard-sample-handoff", "deployment-feedback"):
        example = json.loads((CONTRACT_ROOT / f"{contract_id}.example.json").read_text(encoding="utf-8"))
        assert isinstance(example["created_at"], str)
        assert example["created_at"].endswith("Z")


def test_previous_release_examples_remain_valid_in_minor_release() -> None:
    previous_root = ROOT / "contracts" / "repository" / "v1.0.1"
    for contract_id, model in MODELS.items():
        previous_example = previous_root / f"{contract_id}.example.json"
        if previous_example.exists():
            model.model_validate_json(previous_example.read_bytes())


def test_multidomain_contract_fields_are_published() -> None:
    hard_sample_schema = json.loads((CONTRACT_ROOT / "hard-sample-handoff.schema.json").read_text(encoding="utf-8"))
    feedback_values = set(hard_sample_schema["$defs"]["FeedbackKind"]["enum"])
    assert {
        "action_correction",
        "temporal_correction",
        "style_correction",
        "character_correction",
        "accessory_correction",
    } <= feedback_values

    package = json.loads((CONTRACT_ROOT / "model-package-admission.example.json").read_text(encoding="utf-8"))
    assert package["domain"] == "behavior"
    assert package["artifact_format"] == "bundle"
    assert package["artifact_files"][0]["path"].endswith(".pdparams")

    annotation = json.loads((CONTRACT_ROOT / "domain-annotation-schema.example.json").read_text(encoding="utf-8"))
    assert annotation["schema_id"] == "scenara.portrait.surveillance-review.v1"
    assert annotation["payload_schema"]["type"] == "object"


def test_all_domain_annotation_instances_are_published_and_valid() -> None:
    published_root = ROOT / "contracts" / "domain-annotations" / "v1.1.0"
    manifest = json.loads((published_root / "manifest.json").read_text(encoding="utf-8"))
    assert {item.schema_id for item in definitions()} == {item["schema_id"] for item in manifest["schemas"]}
    for definition in definitions():
        document = json.loads((published_root / f"{definition.schema_id}.json").read_text(encoding="utf-8"))
        DomainAnnotationSchema.model_validate(document)
        Draft202012Validator.check_schema(document["payload_schema"])
