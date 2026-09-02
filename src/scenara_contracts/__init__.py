"""已发布的 Scenara 跨仓库契约。"""

from scenara_contracts.repository_v1 import (
    DatasetVersionReference,
    DomainAnnotationSchema,
    HardSampleManifest,
    ModelArtifactFile,
    ModelDeploymentEvent,
    ModelPackageManifest,
)

__all__ = [
    "DatasetVersionReference",
    "DomainAnnotationSchema",
    "HardSampleManifest",
    "ModelDeploymentEvent",
    "ModelArtifactFile",
    "ModelPackageManifest",
]

__version__ = "1.2.0"
