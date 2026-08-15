# Scenara Contracts

`scenara-contracts` 是景枢平台能力、实体、数据结构、API、事件、错误码、状态、对象引用、版本与兼容策略的唯一事实来源。其他仓库只消费已发布版本，不得跨仓库导入本仓库源码。

- 当前契约发布：`@scenara/repository-contracts` `1.0.0`
- 当前成熟度：`implemented`（发布制品与校验已迁入；完整能力/API/事件目录仍在扩充）
- 责任团队：Scenara Platform Architecture
- 规范来源：`景枢平台总体开发规范.md` `1.2.1`

## 已发布契约

| 契约 | 生产方 | 消费方 | 传输方式 |
| --- | --- | --- | --- |
| `model-package-admission` | `scenara-model` | `scenara` | 不可变清单 |
| `deployment-feedback` | `scenara` | `scenara-model` | 事件 / 签名 Webhook |
| `hard-sample-handoff` | `scenara` | `scenara-data` | 不可变清单 |
| `dataset-version-input` | `scenara-data` | `scenara-model` | 版本化 API |

## 验证与打包

```powershell
python -m pip install -e ".[dev]"
python scripts/repository_contracts.py --check
python -m pytest
python scripts/repository_contracts.py --check --bundle repository-contracts-1.0.0.zip
```

已发布目录不可原地修改。不兼容变更必须发布新主版本；兼容新增发布次版本；纯文档修正发布修订版本。详细流程见 [开发规范](docs/DEVELOPMENT.md) 和 [契约说明](contracts/repository/README.md)。

## 已知迁移项

`1.0.0` 是已发布且摘要锁定的契约，其中部分 `created_at` 仍为 Unix 数值时间。根据总体规范，该字段将在新的主版本迁移为 UTC RFC 3339 字符串；不得修改 `1.0.0` 原文件冒充兼容变更。
