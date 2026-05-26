# 实验矩阵

## 主实验

| ID | 实验 | 目的 |
|---|---|---|
| E1 | Operator forward prediction | 验证参数化 PDE / 多物理 solution operator 的全场预测精度 |
| E2 | Cross-benchmark transfer | 验证同一计算策略跨 benchmark family 的适用性 |
| E3 | Parameter inversion | 验证材料/载荷/边界反演 |
| E4 | Uncertainty propagation | 验证响应分布预测 |
| E5 | OOD generalization | 验证材料、边界、载荷分布外稳健性 |
| E6 | Physics consistency | 验证物理约束效果 |
| E7 | Systematic baseline comparison | 验证相比 FEM、ROM、PINN、DeepONet/FNO 的综合优势 |
| E8 | Ablation study | 验证每个模块的必要性 |
| E9 | Sparse observation update | 验证数字孪生状态更新 |

## 两层落地证据链

| Level | 主张 | 证据入口 | 验收核心 |
|---|---|---|---|
| L1 | 从 surrogate 到 operator + FEM evidence | `run_fem2d_baseline_runner.py` / `run_research_landing_ladder.py --track operator_fem` | 同一 FEM tensor protocol、同一 split/seed/epochs、FEM residual/boundary/energy 指标、系统 baseline |
| L2 | 从静态 operator 到 stateful path-dependent operator | `run_j2_path_ood_comparison.py` / `run_research_landing_ladder.py --track stateful_path` | monotonic-only training、unload-reload/cyclic/nonproportional path-OOD、history increment error |

总控说明见 `08_experiments/research_landing_ladder.md`。

## Benchmark families

实验设计至少包含两个 benchmark families，避免论文被理解为单一工程案例：

- nonlinear solid/structural mechanics
- coupled thermo-/electro-/magneto-mechanics
- fluid-structure or fluid-thermal-structure interaction
- heterogeneous material full-field response
- stochastic PDE / reliability-oriented mechanics

## 结果表最低要求

- relative L2 error
- max pointwise error
- residual norm
- boundary violation
- energy violation
- NLL
- coverage probability
- calibration error
- inference latency
- speedup factor

## 必须报告的泛化切片

- in-distribution interpolation
- OOD material parameters
- OOD boundary conditions
- OOD loading patterns
- sparse observations with noise
- posterior multi-modality when inverse solutions are non-unique
