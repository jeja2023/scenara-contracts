from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scenara_contracts.repository_v1 import (
    DatasetVersionReference,
    HardSampleManifest,
    ModelDeploymentEvent,
    ModelPackageManifest,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "repository" / "v1.0.0"

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
    assert manifest["release_version"] == "1.0.0"
    assert {item["contract_id"] for item in manifest["contracts"]} == set(MODELS)
