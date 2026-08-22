# scenara-contracts 剩余任务计划

**适用规范：** `景枢平台总体开发规范.md` 1.3.0

**当前发布：** `@scenara/repository-contracts` `1.0.1`

**当前成熟度：** `implemented`

## 已完成基线

- `model-package-admission`、`deployment-feedback`、`hard-sample-handoff`、`dataset-version-input` 四条跨仓库契约。
- Draft 2020-12 Schema、有效示例、发布索引、manifest、SHA-256 摘要和确定性 ZIP。
- RFC3339 UTC 时间、跨字段摘要一致性、Hard Sample canonical checksum 和 `--against` 兼容门禁。

## 剩余交付

| 编号 | 状态 | 任务 | 责任边界 | 验收证据 |
| --- | --- | --- | --- | --- |
| CONTRACT-P1 | implemented | 保持 v1.0.0 发布目录只读并为四仓库提供消费方回归 | Contracts | 6 项回归、manifest/checksum 和 bundle 校验 |
| CONTRACT-P2 | planned | 为新增公共 API、错误码、状态和事件建立 `contracts/api/v1/` 目录 | Contracts + 各生产方 | OpenAPI/事件目录、示例、Schema、生成包 |
| CONTRACT-P3 | planned | 发布兼容矩阵和废弃策略，禁止消费者导入源码 | Contracts + CI | `--against`、源码导入扫描、消费者兼容报告 |
| CONTRACT-P4 | planned | 依据跨仓库切流反馈发布 v1.x 兼容增量或 v2 不兼容版本 | Contracts + Core/Data/Model | 版本迁移指南、摘要锁定、回滚验证 |

已发布 `contracts/repository/v1.0.0/` 禁止原地修改；当前兼容性修订发布为 `v1.0.1`，摘要单独锁定。不兼容变更必须升主版本，兼容新增升次版本，纯文档修正确保修订版本和新摘要。

```powershell
.\.venv\Scripts\python.exe -m pytest -rA
.\.venv\Scripts\python.exe scripts\repository_contracts.py --check
.\.venv\Scripts\python.exe scripts\repository_contracts.py --check --bundle repository-contracts-1.0.1.zip
```
