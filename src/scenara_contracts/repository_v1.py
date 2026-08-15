from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SHA256 = r"^[0-9a-f]{64}$"
IMMUTABLE_URI = r"^.+(?:@sha256:|#sha256=)[0-9a-f]{64}$"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FeedbackKind(StrEnum):
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    WRONG_ATTRIBUTE = "wrong_attribute"
    WRONG_IDENTITY = "wrong_identity"
    OCR_CORRECTION = "ocr_correction"


class ModelReleaseStatus(StrEnum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    APPROVED = "approved"
    ACTIVE = "active"
    RETIRED = "retired"


class ModelPackageManifest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    model_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?$")
    capability: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    adapter: str = Field(min_length=2, max_length=64)
    runtime_model_id: str = Field(pattern=r"^[^/\\\s]+/[^/\\\s]+$", max_length=384)
    sha256: str = Field(pattern=SHA256)
    source_uri: str = Field(min_length=1, max_length=2048)
    license_id: str = Field(min_length=1, max_length=128)
    model_card: str = Field(min_length=1, max_length=2048)
    evaluation_evidence: tuple[str, ...] = Field(min_length=1, max_length=100)
    vram_mb: int = Field(ge=0, le=196_608)
    regression_samples: tuple[str, ...] = Field(min_length=1)
    production_ready: bool = False

    @field_validator("source_uri", "model_card")
    @classmethod
    def immutable_reference(cls, value: str) -> str:
        normalized = value.strip()
        if re.search(r"(?:@sha256:|#sha256=)[0-9a-f]{64}$", normalized) is None:
            raise ValueError("model package references must end with an immutable SHA-256 digest")
        return normalized

    @field_validator("evaluation_evidence")
    @classmethod
    def immutable_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in value)
        if len(set(normalized)) != len(normalized):
            raise ValueError("model evaluation evidence references must be unique")
        if any(
            not item or len(item) > 2048 or re.search(r"(?:@sha256:|#sha256=)[0-9a-f]{64}$", item) is None
            for item in normalized
        ):
            raise ValueError("model evaluation evidence must use immutable SHA-256 references")
        return normalized

    @model_validator(mode="after")
    def artifact_digest_matches(self) -> ModelPackageManifest:
        match = re.search(r"(?:@sha256:|#sha256=)([0-9a-f]{64})$", self.source_uri)
        if match is None or match.group(1) != self.sha256:
            raise ValueError("model artifact reference digest must match sha256")
        return self


class DatasetVersionReference(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    dataset_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?$")
    manifest_uri: str = Field(pattern=IMMUTABLE_URI, max_length=2048)
    manifest_sha256: str = Field(pattern=SHA256)
    lineage_refs: tuple[str, ...] = Field(min_length=1, max_length=100)
    authorization_id: str = Field(min_length=1, max_length=256)
    authorized_consumer_repository_ids: tuple[str, ...] = Field(min_length=1, max_length=32)
    created_at: float

    @field_validator("lineage_refs")
    @classmethod
    def immutable_lineage(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value) or any(
            len(item) > 2048 or re.fullmatch(IMMUTABLE_URI, item) is None for item in value
        ):
            raise ValueError("dataset lineage references must be unique immutable references")
        return value

    @model_validator(mode="after")
    def matching_manifest_digest(self) -> DatasetVersionReference:
        if not self.manifest_uri.endswith((f"@sha256:{self.manifest_sha256}", f"#sha256={self.manifest_sha256}")):
            raise ValueError("dataset manifest URI digest must match manifest_sha256")
        return self


class HardSampleItem(ContractModel):
    feedback_id: str
    kind: FeedbackKind
    media_ref: str
    result_ref: str
    model_id: str
    model_version: str
    pipeline_id: str
    pipeline_version: str
    correction: dict[str, Any]
    authorized_for_training: bool = True
    deidentified: bool = True


class HardSampleManifest(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    manifest_id: str
    tenant_id: str
    project_id: str
    dataset_id: str
    version: str
    label_schema: str = "scenara.feedback.correction.v1"
    split: Literal["train", "validation", "test"] = "train"
    items: tuple[HardSampleItem, ...]
    sha256: str = Field(pattern=SHA256)
    created_by: str
    created_at: float


class ModelDeploymentEvent(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    event_id: str
    tenant_id: str
    project_id: str
    model_id: str
    version: str
    capability: str
    runtime_model_id: str
    package_sha256: str = Field(pattern=SHA256)
    action: str
    from_status: ModelReleaseStatus | None
    to_status: ModelReleaseStatus
    reason: str
    operator_id: str
    audit_id: str
    created_at: float


__all__ = [
    "DatasetVersionReference",
    "FeedbackKind",
    "HardSampleItem",
    "HardSampleManifest",
    "ModelDeploymentEvent",
    "ModelPackageManifest",
    "ModelReleaseStatus",
]
