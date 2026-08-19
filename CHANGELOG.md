# 更新日志

## [Unreleased]

- 统一 `hard-sample-handoff`、`dataset-version-input` 和 `deployment-feedback` 的 `created_at` 为以 `Z` 结尾的 UTC RFC3339 字符串。
- 更新契约 Schema、有效示例、Pydantic 校验、契约生成器、发布清单摘要和消费方说明；契约边界拒绝 Unix 数值时间，不保留数值兼容路径。
- 补充跨仓库时间字段说明，明确内部数据库可以使用原生时间类型，但不得将 Unix 数值时间暴露到跨仓载荷。

## [1.0.0] - 2026-08-15

- 建立 `scenara-contracts` 独立责任仓库。
- 接管 `@scenara/repository-contracts` `1.0.0` 的四项已发布跨仓库契约，保持发布摘要不变。
- 增加 Pydantic 类型、Schema/示例验证、摘要锁定、兼容性检查和确定性发布包构建。
- 建立能力词典、实体词典、开发和测试文档骨架。
