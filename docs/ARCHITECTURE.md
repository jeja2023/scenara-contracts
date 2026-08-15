# 架构说明

本仓库只拥有公共语言和机器可读契约，不实现 Data、Model 或 Core 业务逻辑。发布内容由版本化 Schema、有效/无效示例、语言类型、摘要清单和兼容报告构成。

依赖方向固定为 `scenara`、`scenara-data`、`scenara-model` 消费已发布 `scenara-contracts`。消费方不得依赖未发布分支或源码路径。其他仓库中的契约副本必须记录版本和摘要，并由 CI 验证零漂移。

当前 `contracts/repository/v1.0.0/` 是不可变发布目录，`release-index.json` 锁定 Manifest SHA-256。新版本先生成候选目录，再针对上一发布运行兼容性检查。
