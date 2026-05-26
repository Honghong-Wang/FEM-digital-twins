# FEM Snapshot Protocol

真实 FEM / IGA / MPM / FSI 求解器的数据接入不应改变模型接口。外部求解器只需导出统一张量协议：

```text
coords:  [n_samples, n_nodes, spatial_dim] or [n_nodes, spatial_dim]
params:  [n_samples, n_parameters]
fields:  [n_samples, n_nodes, n_fields]
forcing: [n_samples, n_nodes, n_fields]
```

可选数组：

```text
residual:        [n_samples, n_nodes, n_fields]
connectivity:    mesh connectivity
mass:            assembled mass matrix or lumped mass
stiffness:       assembled stiffness/tangent data
fixed_dofs:      constrained global dof indices
fixed_nodes:     constrained node indices, expanded to all field components
sample_id:       persistent sample identifiers for shuffled/stateful callbacks
tangent_stiffness: per-sample nonlinear tangent stiffness
newton_residual: residual at the exported reference state
reference_fields: reference state for Newton-linearized residuals
reference_energy: total potential at the reference state
material_history: internal variables, e.g. plastic strain, damage, phase state
parameter_names: [n_parameters]
field_names:     [n_fields]
```

路径依赖问题还可以导出完整加载路径：

```text
fields_sequence:              [n_samples, n_steps, n_nodes, n_fields]
forcing_sequence:             [n_samples, n_steps, n_nodes, n_fields]
tangent_stiffness_sequence:   [n_samples, n_steps, n_dofs, n_dofs]
newton_residual_sequence:     [n_samples, n_steps, n_nodes, n_fields]
reference_energy_sequence:    [n_samples, n_steps]
material_history_sequence:    [n_samples, n_steps, n_elements, n_history]
plastic_strain_sequence:      [n_samples, n_steps, n_elements, 6]
stress_sequence:              [n_samples, n_steps, n_elements, 3]
strain_sequence:              [n_samples, n_steps, n_elements, 3]
load_factors:                 [n_steps]
```

## 文件格式

当前支持：

- `.npz`
- `.h5`
- `.hdf5`

本地加载入口：

```python
from pcgno_dt.data.fem import load_fem_snapshots, make_fem_problem_adapter

loaded = load_fem_snapshots("fem_snapshots.npz")
tensors = loaded["tensors"]
problem = make_fem_problem_adapter(tensors, loaded["metadata"])
```

`tensors` 可以直接进入：

- `OperatorTensorDataset`
- `PhysicsConstrainedGenerativeNeuralOperator`
- `physics_constrained_loss`
- `evaluate_prediction`

路径数据加载入口：

```python
from pcgno_dt.data.fem import load_fem_path_snapshots
from pcgno_dt.data.datasets import PathOperatorTensorDataset

loaded = load_fem_path_snapshots("j2_path_snapshots.npz")
dataset = PathOperatorTensorDataset(loaded["tensors"])
```

## 外部装配 FEM residual / energy

如果外部求解器能导出共享线性刚度矩阵，runner 会自动接入物理残差：

```text
stiffness:  [n_dofs, n_dofs] or [1, n_dofs, n_dofs]
fixed_dofs: [n_fixed_dofs]
```

其中自由度按 node-major 顺序展平：

```text
dof = n_fields * node_id + field_id
```

自动 callback 计算：

```text
residual = K u - f, with constrained dofs masked out
boundary = u on fixed dofs
energy = 0.5 u^T K u - f^T u
```

本地入口：

```python
from pcgno_dt.data.fem import (
    has_assembled_linear_fem_data,
    make_assembled_linear_fem_callbacks,
    make_fem_problem_adapter,
)

loaded = load_fem_snapshots("external_solver_snapshots.npz")
if has_assembled_linear_fem_data(loaded["extra"]):
    callbacks = make_assembled_linear_fem_callbacks(loaded["tensors"], loaded["extra"])
    problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
    )
```

`run_fem2d_baseline_runner.py` 和 `run_fem2d_mesh_transfer.py` 会先检查 stateful nonlinear FEM 数据；如果没有样本相关切线刚度，再使用这类共享线性装配物理项；再否则回退到本地 `connectivity/grid_shape` plane-stress callback；三者都没有时才进入 data-only FEM adapter。

## 非线性 / stateful FEM callback

非线性多物理场数据应导出 persistent `sample_id` 和每个样本对应的 Newton 状态：

```text
sample_id:          [n_samples]
tangent_stiffness:  [n_samples, n_dofs, n_dofs]
reference_fields:   [n_samples, n_nodes, n_fields], optional, defaults to fields
newton_residual:    [n_samples, n_nodes, n_fields] or [n_samples, n_dofs], optional
reference_energy:   [n_samples], optional
material_history:   [n_samples, ...], optional
fixed_dofs:         [n_fixed_dofs] or [n_samples, n_fixed_dofs]
```

自动 stateful callback 使用 `sample_id` 在 shuffled batch 中取回正确的 `K_i`、参考状态和历史变量：

```text
R_i(u) ~= R_i(u_ref) + K_tangent_i (u - u_ref_i)
Pi_i(u) ~= Pi_i(u_ref) + R_i(u_ref)^T (u - u_ref_i)
          + 0.5 (u - u_ref_i)^T K_tangent_i (u - u_ref_i)
```

本地入口：

```python
from pcgno_dt.data.fem import (
    has_stateful_nonlinear_fem_data,
    make_stateful_nonlinear_fem_callbacks,
    make_fem_problem_adapter,
)

loaded = load_fem_snapshots("nonlinear_solver_snapshots.npz")
if has_stateful_nonlinear_fem_data(loaded["tensors"], loaded["extra"]):
    callbacks = make_stateful_nonlinear_fem_callbacks(loaded["tensors"], loaded["extra"])
    problem = make_fem_problem_adapter(
        loaded["tensors"],
        loaded["metadata"],
        residual_callback=callbacks[0],
        boundary_callback=callbacks[1],
        energy_callback=callbacks[2],
        thermodynamic_callback=callbacks[3],
    )
```

`physics_constrained_loss` 和 `evaluate_physics_consistency` 会自动把 batch 中的 `sample_id` 注入 `FEMProblemAdapter`。如果 partial/shuffled batch 没有 `sample_id`，stateful callback 会显式报错，而不是错误地按 batch 顺序索引。

当前 `material_history` 的默认热力学诊断是对负历史变量加惩罚，适合 plastic strain、damage、phase fraction 等非负内部变量的 smoke check。真正的材料模型可以继续替换为 solver-side thermodynamic callback。

## Built-in Neo-Hookean Exporter

仓库内置了一个小型真实非线性材料导出器：

```text
src/pcgno_dt/numerics/hyperelastic2d.py
```

它使用 total-Lagrangian CST 三角单元、compressible Neo-Hookean 能量和 Newton 求解，导出：

```text
coords / params / fields / forcing / sample_id
tangent_stiffness / newton_residual / reference_energy / material_history / fixed_dofs
```

命令行生成入口：

```bash
python 12_reproducibility/scripts/generate_neo_hookean_fem_dataset.py \
  --out-dir 05_data_pipeline/processed/neo_hookean_fem2d \
  --train-samples 32 \
  --eval-samples 12 \
  --nx 4 \
  --ny 3
```

之后可以直接复用 baseline runner：

```bash
python 12_reproducibility/scripts/run_fem2d_baseline_runner.py \
  --data-dir 05_data_pipeline/processed/neo_hookean_fem2d \
  --model pcgno \
  --epochs 10
```

runner 会自动识别 `tangent_stiffness`，并使用 stateful nonlinear FEM callback。

## Built-in J2 Plasticity Exporter

仓库还内置了一个路径依赖小应变 J2 plasticity 导出器：

```text
src/pcgno_dt/numerics/j2plasticity2d.py
```

它使用 plane-strain CST 三角单元、von Mises J2 屈服、线性各向同性硬化、分步加载和 return mapping。每个载荷步中 Newton 迭代使用上一收敛步的内部变量，收敛后才 commit history，因此导出的 history 是真正路径依赖的材料状态，而不是后处理诊断量。

导出字段：

```text
coords / params / fields / forcing / sample_id
tangent_stiffness / newton_residual / reference_energy / material_history
plastic_strain / fixed_dofs
```

其中：

```text
material_history[..., 0] = equivalent plastic strain
material_history[..., 1] = accumulated plastic work
material_history[..., 2] = last plastic multiplier increment
material_history[..., 3] = yielded flag
material_history[..., 4] = von Mises stress
plastic_strain[..., :]   = [ep_xx, ep_yy, ep_zz, ep_xy, ep_yz, ep_xz]
```

命令行生成入口：

```bash
python 12_reproducibility/scripts/generate_j2_plasticity_fem_dataset.py \
  --out-dir 05_data_pipeline/processed/j2_plasticity_fem2d \
  --train-samples 24 \
  --eval-samples 8 \
  --nx 3 \
  --ny 3 \
  --load-steps 6
```

J2 数据集同样可直接进入 baseline runner；runner 会自动走 stateful nonlinear FEM callback。

J2 exporter 同时保存 final-state 和 path-state。`fields/forcing/tangent_stiffness/newton_residual/material_history` 对应最后一个载荷步；`*_sequence` 对应完整路径。路径一致性诊断入口：

```python
from pcgno_dt.evaluation.path_history import evaluate_j2_path_history_consistency

metrics = evaluate_j2_path_history_consistency(loaded["tensors"])
```

当前检查：

```text
eq_plastic_strain monotonicity
plastic_work monotonicity
non-negative plastic multiplier increment
yield flag bounds
path Newton residual RMS
```

J2 exporter 支持四类加载路径，用于检验 recurrent operator 是否真正学习塑性记忆：

```text
monotonic:        proportional monotonic ramp
unload_reload:    load to yield, unload, then reload
cyclic:           forward, reverse, reload, final unload
nonproportional:  x/y traction components follow different paths
```

生成示例：

```bash
python 12_reproducibility/scripts/generate_j2_plasticity_fem_dataset.py \
  --out-dir 05_data_pipeline/processed/j2_cyclic_fem2d \
  --load-path cyclic \
  --load-steps 8
```

训练/评估示例：

```bash
python 12_reproducibility/scripts/run_j2_history_operator.py \
  --data-dir 05_data_pipeline/processed/j2_cyclic_fem2d \
  --load-path cyclic \
  --epochs 20
```

## HistoryGraphOperator / Recurrent Neural Operator

路径依赖 J2 数据可以直接训练 mesh-aware recurrent operator：

```text
src/pcgno_dt/models/history_gno.py
```

模型递推：

```text
(coords, graph, params, forcing_t, u_{t-1}, history_{t-1})
    -> u_t, history_t, logvar_t
```

其中节点图消息传递负责位移场，单元级 recurrent state 负责内部变量演化。对 J2 的前 5 个 history channel 使用热力学投影：

```text
eq_plastic_strain_t >= eq_plastic_strain_{t-1}
plastic_work_t >= plastic_work_{t-1}
Delta_gamma_t >= 0
yield_flag_t in [0, 1]
von_mises_t >= 0
```

训练入口：

```bash
python 12_reproducibility/scripts/run_j2_history_operator.py \
  --data-dir 05_data_pipeline/processed/j2_plasticity_fem2d \
  --epochs 20 \
  --batch-size 4
```

训练 loss：

```text
displacement path error
history path error
predictive variance calibration
eqp/plastic work monotonicity
plastic multiplier non-negativity
yield flag bounds
```

## Path-OOD Comparison Runner

正式的路径泛化实验入口：

```text
12_reproducibility/scripts/run_j2_path_ood_comparison.py
```

这个 runner 固定训练分布为 `monotonic/train.npz`，再在同一材料/载荷参数测试分布下评估：

```text
monotonic/test.npz
unload_reload/test.npz
cyclic/test.npz
nonproportional/test.npz
```

因此它隔离检验的是 load-path OOD，而不是把材料 OOD、载荷幅值 OOD 和路径 OOD 混在一起。默认报告会写出：

```text
10_results/reports/j2_path_ood_comparison.json
10_results/reports/j2_path_ood_comparison.csv
```

核心指标：

```text
displacement_relative_l2
history_relative_l2
history_increment_relative_l2
eq_plastic_strain_relative_l2 / increment_relative_l2
plastic_work_relative_l2 / increment_relative_l2
plastic_multiplier_increment_relative_l2
yield_flag_mae
von_mises_relative_l2
path_ood_degradation_vs_monotonic
```

命令行示例：

```bash
python 12_reproducibility/scripts/run_j2_path_ood_comparison.py \
  --data-root 05_data_pipeline/processed/j2_path_ood_comparison \
  --epochs 50 \
  --train-samples 32 \
  --eval-samples 12 \
  --load-steps 8 \
  --eval-load-paths monotonic,unload_reload,cyclic,nonproportional \
  --force-regenerate
```

这个实验直接回答：recurrent operator 在只看过单调加载时，是否能把 `history_t -> history_{t+1}` 推进规律迁移到卸载-再加载、循环加载和非比例加载路径。

为诊断 cyclic degradation，runner 还支持 history-increment-aware training：

```bash
python 12_reproducibility/scripts/run_j2_path_ood_comparison.py \
  --train-load-paths monotonic \
  --history-increment-weight 0.25 \
  --eqp-increment-weight 0.10 \
  --plastic-work-increment-weight 0.10 \
  --yield-flag-weight 0.05 \
  --epochs 50
```

以及 path curriculum / upper-bound 诊断：

```bash
python 12_reproducibility/scripts/run_j2_path_ood_comparison.py \
  --train-load-paths monotonic,unload_reload \
  --eval-load-paths monotonic,unload_reload,cyclic,nonproportional \
  --history-increment-weight 0.25 \
  --eqp-increment-weight 0.10 \
  --plastic-work-increment-weight 0.10 \
  --yield-flag-weight 0.05
```

当 `train-load-paths` 不是单独 `monotonic` 时，报告中的 `strict_path_ood=false`，这些结果用于定位失败模式，而不是替代严格 path-OOD 主表。

## FEM residual 接入

如果有 FEM 装配器，可以向 `make_fem_problem_adapter` 传入 callback：

```python
problem = make_fem_problem_adapter(
    tensors,
    metadata,
    residual_callback=assembled_residual,
    boundary_callback=boundary_residual,
    energy_callback=total_potential_energy,
)
```

callback 约定：

```python
residual_callback(params, fields, forcing) -> residual
boundary_callback(params, fields) -> boundary_residual
energy_callback(params, fields, forcing) -> energy
```

stateful callback 也可以接收最后一个 `batch_context` 参数：

```python
residual_callback(params, fields, forcing, batch_context) -> residual
boundary_callback(params, fields, batch_context) -> boundary_residual
energy_callback(params, fields, forcing, batch_context) -> energy
thermodynamic_callback(params, batch_context) -> scalar_penalty
```

这样真实 FEM 数据和 manufactured benchmark 使用同一套：

```text
coords / params / fields / forcing / residual
```

## Local 2D Plane-Stress Callback

The local 2D FEM solver provides ready-to-use callbacks:

```python
from pcgno_dt.numerics.fem2d import make_plane_stress_fem_callbacks

callbacks = make_plane_stress_fem_callbacks(
    coords=tensors["coords"],
    connectivity=extra["connectivity"],
    grid_shape=extra["grid_shape"],
)

problem = make_fem_problem_adapter(
    tensors,
    metadata,
    residual_callback=callbacks[0],
    boundary_callback=callbacks[1],
    energy_callback=callbacks[2],
)
```

For the plane-stress solver:

```text
residual = K(E, nu) u - f
boundary = u on fixed left-edge nodes
energy = 0.5 u^T K(E, nu) u - f^T u
```

## 设计原则

- FEM 是高保真数据源和物理残差评估器，不改变 operator-learning 协议。
- benchmark family 与真实 FEM 数据共享相同评估指标和 baseline registry。
- 没有 residual callback 时，FEM adapter 可用于 data-only training 和 baseline comparison。
- 有 residual callback 时，FEM adapter 可用于 physics-constrained training。
