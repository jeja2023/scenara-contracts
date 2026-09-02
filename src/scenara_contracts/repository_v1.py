from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SHA256 = r"^[0-9a-f]{64}$"
IMMUTABLE_URI = r"^.+(?:@sha256:|#sha256=)[0-9a-f]{64}$"
RFC3339_UTC = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _validate_utc_rfc3339(value: str) -> str:
    normalized = value.strip()
    if re.fullmatch(RFC3339_UTC, normalized) is None:
        raise ValueError("时间必须是 UTC RFC 3339 字符串，并以 Z 结尾")
    try:
        parsed = datetime.fromisoformat(normalized[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("时间不是有效的 UTC RFC 3339 值") from exc
    if parsed.tzinfo is None:
        raise ValueError("时间必须包含 UTC 时区")
    return normalized


class FeedbackKind(StrEnum):
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    WRONG_ATTRIBUTE = "wrong_attribute"
    WRONG_IDENTITY = "wrong_identity"
    OCR_CORRECTION = "ocr_correction"
    ACTION_CORRECTION = "action_correction"
    TEMPORAL_CORRECTION = "temporal_correction"
    STYLE_CORRECTION = "style_correction"
    CHARACTER_CORRECTION = "character_correction"
    ACCESSORY_CORRECTION = "accessory_correction"


class ModelReleaseStatus(StrEnum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    APPROVED = "approved"
    ACTIVE = "active"
    RETIRED = "retired"


class ModelArtifactFile(ContractModel):
    path: str = Field(pattern=r"^[^/\\\s][^\\]*$", max_length=512)
    sha256: str = Field(pattern=SHA256)
    size_bytes: int = Field(ge=0)
    media_type: str = Field(min_length=1, max_length=128)

    @field_validator("path")
    @classmethod
    def portable_relative_path(cls, value: str) -> str:
        if "\\" in value:
            raise ValueError("模型制品文件路径必须使用正斜杠")
        path = PurePosixPath(value)
        if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError("模型制品文件路径必须位于包内")
        return path.as_posix()


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
    domain: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{1,63}$")
    artifact_format: Literal["onnx", "paddle", "pytorch", "bundle"] = "onnx"
    artifact_files: tuple[ModelArtifactFile, ...] = Field(default_factory=tuple, max_length=1000)
    input_schema: str | None = Field(default=None, pattern=IMMUTABLE_URI, max_length=2048)
    output_schema: str | None = Field(default=None, pattern=IMMUTABLE_URI, max_length=2048)

    @field_validator("source_uri", "model_card")
    @classmethod
    def immutable_reference(cls, value: str) -> str:
        normalized = value.strip()
        if re.search(r"(?:@sha256:|#sha256=)[0-9a-f]{64}$", normalized) is None:
            raise ValueError("模型包引用必须以不可变的 SHA-256 摘要结尾")
        return normalized

    @field_validator("evaluation_evidence")
    @classmethod
    def immutable_evidence(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in value)
        if len(set(normalized)) != len(normalized):
            raise ValueError("模型评估证据引用必须唯一")
        if any(
            not item or len(item) > 2048 or re.search(r"(?:@sha256:|#sha256=)[0-9a-f]{64}$", item) is None
            for item in normalized
        ):
            raise ValueError("模型评估证据必须使用不可变的 SHA-256 引用")
        return normalized

    @model_validator(mode="after")
    def artifact_digest_matches(self) -> ModelPackageManifest:
        match = re.search(r"(?:@sha256:|#sha256=)([0-9a-f]{64})$", self.source_uri)
        if match is None or match.group(1) != self.sha256:
            raise ValueError("模型制品引用摘要必须与 sha256 匹配")
        paths = [item.path for item in self.artifact_files]
        if len(paths) != len(set(paths)):
            raise ValueError("模型制品文件路径必须唯一")
        if self.artifact_format == "bundle" and not self.artifact_files:
            raise ValueError("bundle 格式模型包必须枚举 artifact_files")
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
    created_at: str = Field(pattern=RFC3339_UTC)
    domain: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{1,63}$")
    annotation_schema_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=100)

    @field_validator("created_at")
    @classmethod
    def utc_created_at(cls, value: str) -> str:
        return _validate_utc_rfc3339(value)

    @field_validator("lineage_refs")
    @classmethod
    def immutable_lineage(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value) or any(
            len(item) > 2048 or re.fullmatch(IMMUTABLE_URI, item) is None for item in value
        ):
            raise ValueError("数据集血缘引用必须为唯一的不可变引用")
        return value

    @model_validator(mode="after")
    def matching_manifest_digest(self) -> DatasetVersionReference:
        if not self.manifest_uri.endswith((f"@sha256:{self.manifest_sha256}", f"#sha256={self.manifest_sha256}")):
            raise ValueError("数据集清单 URI 摘要必须与 manifest_sha256 匹配")
        if len(self.annotation_schema_ids) != len(set(self.annotation_schema_ids)):
            raise ValueError("标注模式标识符必须唯一")
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
    domain: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{1,63}$")
    annotation_schema_id: str | None = Field(default=None, min_length=1, max_length=256)


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
    created_at: str = Field(pattern=RFC3339_UTC)

    @field_validator("created_at")
    @classmethod
    def utc_created_at(cls, value: str) -> str:
        return _validate_utc_rfc3339(value)


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
    created_at: str = Field(pattern=RFC3339_UTC)
    domain: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_.-]{1,63}$")

    @field_validator("created_at")
    @classmethod
    def utc_created_at(cls, value: str) -> str:
        return _validate_utc_rfc3339(value)


class DomainAnnotationSchema(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    schema_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,255}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?$")
    domain: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,63}$")
    task_type: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    supported_media_kinds: tuple[Literal["image", "video", "document", "stream"], ...] = Field(min_length=1)
    payload_schema: dict[str, Any]
    quality_rules: tuple[str, ...] = Field(default_factory=tuple, max_length=100)

    @model_validator(mode="after")
    def validate_definition(self) -> DomainAnnotationSchema:
        if len(self.supported_media_kinds) != len(set(self.supported_media_kinds)):
            raise ValueError("支持的媒体类型必须唯一")
        if len(self.quality_rules) != len(set(self.quality_rules)):
            raise ValueError("质量规则必须唯一")
        if self.payload_schema.get("type") != "object":
            raise ValueError("标注载荷模式根节点必须为对象")
        return self


__all__ = [
    "DatasetVersionReference",
    "DomainAnnotationSchema",
    "FeedbackKind",
    "HardSampleItem",
    "HardSampleManifest",
    "ModelDeploymentEvent",
    "ModelArtifactFile",
    "ModelPackageManifest",
    "ModelReleaseStatus",
]
