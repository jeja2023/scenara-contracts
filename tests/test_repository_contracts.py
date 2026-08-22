from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from scenara_contracts.repository_v1 import (
    DatasetVersionReference,
    HardSampleManifest,
    ModelDeploymentEvent,
    ModelPackageManifest,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "repository" / "v1.0.1"

MODELS = {
    "dataset-version-input": DatasetVersionReference,
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
    assert manifest["release_version"] == "1.0.1"
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
