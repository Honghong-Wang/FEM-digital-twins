# Verification and Validation Plan

## Verification

验证实现是否正确：

- 单元测试核心算子。
- 数据加载和归一化可逆。
- residual 计算与解析解或数值基准一致。
- 训练配置可复现。
- 固定随机种子下结果稳定。

## Validation

验证模型是否解决真实力学问题：

- 与高保真 FEM/IGA/MPM/SPH 基准对比。
- 与传统 ROM 和神经算子基线对比。
- 在插值和 OOD 条件下分别报告。
- 在稀疏观测和噪声条件下验证。

## UQ 校准

必须报告：

- prediction interval coverage probability
- expected calibration error
- negative log likelihood
- CRPS if applicable
- reliability diagram

## 物理可信性

必须报告：

- PDE residual map
- BC residual
- interface residual
- conservation or energy error
- invalid samples ratio
