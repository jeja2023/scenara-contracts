# 测试说明

最低门禁包括 Ruff、Pytest、Draft 2020-12 Schema 验证、Pydantic 类型验证、发布摘要锁定、确定性 ZIP 构建和上一版本兼容检查。

```powershell
python -m ruff check src scripts tests
python -m pytest
python scripts/repository_contracts.py --check
python scripts/repository_contracts.py --check --against contracts/repository/v1.0.1
python scripts/domain_annotation_schemas.py --check
python scripts/repository_contracts.py --check --bundle repository-contracts-1.2.0.zip
```

消费仓库还必须使用捕获的真实载荷夹具验证其锁定版本。跳过测试不计为通过。
