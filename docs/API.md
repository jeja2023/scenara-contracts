# API 契约说明

跨平台 HTTP API 必须在本仓库维护 OpenAPI 或等价定义，并使用 `/api/v1/`。每个写接口必须说明认证、权限 ID、幂等、错误码、超时、重试、分页和弃用策略。

当前独立仓库初搭仅接管四项跨仓库载荷契约，尚未发布完整 OpenAPI 包。新增 API 前必须先建立 `contracts/api/v<version>/` 发布目录和消费方兼容测试；在此之前不得把内部 FastAPI/Pydantic 模型视为公共契约。

`1.1.0` 新增 `domain-annotation-schema` 不可变清单，并为现有四项载荷增加可选领域元数据和多制品描述。`1.2.0` 新增 `scenara.portrait.surveillance-review.v1`，用于已授权、已脱敏的布控误报复核难例。该清单由 Contracts 发布、Data 校验和保存 Schema ID，Model 通过 Dataset Version 的 `annotation_schema_ids` 消费；各仓库不得复制后再改变同一 Schema ID 的含义。
