# 数值基线计划

## 必须基线

1. High-fidelity solver: FEM、IGA、MPM、SPH 或已有专业求解器。
2. ROM baseline: POD、reduced basis、hyper-reduction 或 latent ROM。
3. PINN baseline: 单工况或小参数空间。
4. DeepONet baseline: branch-trunk operator learning。
5. FNO baseline: 网格数据上的算子学习。
6. GNN baseline: mesh/graph-based operator or surrogate。

## 对比定位

本项目不是证明某个 AI 模型比求解器快，而是证明一个概率式 solution-operator 框架在精度、可信性、泛化、反演和不确定性传播上形成综合优势。

## 公平对比原则

- 使用相同训练/验证/测试划分。
- 记录训练数据量、训练时间、推理时间和参数量。
- 统一误差指标和物理违背指标。
- 对 OOD 条件单独报告。
- 对不确定性任务报告校准指标，而不仅是均值误差。

## Benchmark ladder

| Level | 问题 | 作用 |
|---|---|---|
| L0 | 1D/2D 参数 PDE | 调试模型与 loss |
| L1 | 非线性弹性结构 | 验证 mechanics consistency |
| L2 | 多物理耦合结构 | 验证 operator generalization |
| L3 | 稀疏观测反问题 | 验证 digital twin 能力 |
| L4 | 跨 benchmark family 泛化 | 支撑 CMAME 论文主实验 |

## OOD 与不确定性对比

所有主要基线尽量在以下任务上比较：

- interpolation forward prediction
- OOD material prediction
- OOD boundary prediction
- OOD loading prediction
- sparse-observation inverse identification
- material/boundary/load uncertainty propagation
- predictive calibration and coverage
