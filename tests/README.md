# Tests

测试分三层：

- `unit`: 核心函数、指标、数据 schema 和 residual 计算。
- `integration`: 数据加载、模型 forward、loss 组合和训练 step。
- `regression`: 固定小数据集上的指标回归，防止论文结果漂移。
