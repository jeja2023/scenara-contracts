# Scenara 跨仓库契约

当前已发布的契约包为 `@scenara/repository-contracts` 版本 `1.2.0`。该包为每项跨仓库载荷提供一份 Draft 2020-12 JSON Schema 及一份有效示例，并附带已计算 SHA-256 校验和的清单（manifest）。

## 契约列表

| 契约 | 生产方 | 消费方 | 传输方式 |
|---|---|---|---|
| `model-package-admission` | `scenara-model` | `scenara` | 不可变清单 |
| `deployment-feedback` | `scenara` | `scenara-model` | 事件 / 签名 Webhook |
| `hard-sample-handoff` | `scenara` | `scenara-data` | 不可变清单 |
| `dataset-version-input` | `scenara-data` | `scenara-model` | 版本化 API |
| `domain-annotation-schema` | `scenara-contracts` | `scenara-data` | 不可变清单 |

`release-index.json` 通过 SHA-256 锁定每个已发布清单。已发布目录严格不可变；不兼容变更必须发布新的主版本，向后兼容的增量变更发布新的次版本。

## 时间字段规范

`hard-sample-handoff`、`dataset-version-input` 与 `deployment-feedback` 中的 `created_at` 字段为 UTC RFC 3339 字符串。该字符串必须以 `Z` 结尾；可选的秒小数部分可包含 1 至 6 位数字。内部数据库时间戳可以使用原生日期时间类型，但跨仓库载荷必须保留 UTC 字符串形式，严禁暴露 Unix 数值时间戳。

```json
{
  "created_at": "2026-08-18T00:00:00Z"
}
```

## 生产方验证

生成并校验当前提交的契约包：

```bash
python scripts/repository_contracts.py --check
```

在发布前校验生产方文档：

```bash
python scripts/repository_contracts.py \
  --check \
  --verify-contract model-package-admission \
  --verify-document model-package.json
```

构建 CI 使用的确定性发布包（Bundle）：

```bash
python scripts/repository_contracts.py \
  --check \
  --bundle repository-contracts-1.2.0.zip
```

## 消费方兼容性

在准备后续契约发布时，需针对上一已发布目录运行候选版本兼容性检查：

```bash
python scripts/repository_contracts.py \
  --output-dir contracts/repository/v1.2.0 \
  --against contracts/repository/v1.0.1 \
  --check
```

兼容性门禁会自动解析本地 Schema 引用，并严格拒绝新增必填属性、删除已有属性、枚举或联合类型收窄、数据类型收窄、新增收紧的字符串/数值/数组限制以及关闭附加属性（`additionalProperties`）。消费方仓库亦应使用其捕获的真实载荷测试夹具针对已发布 Schema 进行验证。

`--verify-document` 会同时执行 Draft 2020-12 规范验证与规范语义校验器。语义校验会验证模型包与数据集引用的跨字段摘要一致性，并重新计算标准难例清单的校验和。
