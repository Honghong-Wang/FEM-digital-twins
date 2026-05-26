# Research Landing Ladder

这份 ladder 把两条论文主张落成可复现实验，而不是停留在术语层面：

```text
L1: surrogate -> operator + FEM evidence
L2: static operator -> stateful path-dependent operator
```

总控入口：

```powershell
python 12_reproducibility\scripts\run_research_landing_ladder.py --preset smoke --track all --force-regenerate
```

paper-scale 入口：

```powershell
python 12_reproducibility\scripts\run_research_landing_ladder.py --preset paper --track all --force-regenerate
```

输出：

```text
10_results/reports/research_landing_ladder.json
```

## L1: Surrogate -> Operator + FEM Evidence

目标不是证明某个固定工况的代理模型有效，而是证明同一模型接口学习的是参数化 FEM-backed solution operator。

落地条件：

```text
coords / params / fields / forcing unified tensor protocol
train / test / OOD material / OOD loading splits
FEMProblemAdapter residual, boundary, and total-potential-energy callbacks
fair comparison under the same seed, split, epochs, and metrics
```

直接 runner：

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py `
  --model all `
  --epochs 50 `
  --num-seeds 5 `
  --train-samples 64 `
  --eval-samples 24 `
  --out 10_results\reports\fem2d_operator_evidence_paper.json
```

最低报告指标：

```text
relative_l2
max_absolute_error
coverage / ECE / NLL when probabilistic
fem_residual_rms / fem_residual_relative
fixed_boundary_rms / fixed_boundary_relative
energy_relative_error
OOD material and OOD loading degradation
```

验收标准：

```text
PCGNO 不是 data-only MSE 训练，而是显式接入 FEM residual / boundary / energy。
PINN / DeepONet / FNO / graph operator / PCGNO 共享同一 split 与 seed。
结果可以支持“operator + FEM evidence”，不是单案例 surrogate demo。
```

当前最重要的 L1 修复实验是 PCGNO mean-first training：

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py `
  --model pcgno `
  --pcgno-data-loss mse `
  --pcgno-hidden-dim 96 `
  --pcgno-latent-dim 16 `
  --epochs 50 `
  --num-seeds 5 `
  --out 10_results\reports\pcgno_fem_evidence_repair_mse.json
```

这个实验用于区分两类失败模式：

```text
mean operator capacity failure
probabilistic likelihood / variance calibration coupling failure
```

## L2: Static Operator -> Stateful Path-Dependent Operator

目标不是预测最后一步位移，而是学习路径依赖材料系统的内部变量推进：

```text
(coords, params, forcing_t, history_t) -> (u_{t+1}, history_{t+1})
```

落地条件：

```text
J2 plasticity FEM path snapshots
fields_sequence / forcing_sequence / material_history_sequence
sample-specific tangent stiffness and Newton residual sequence
HistoryGraphOperator recurrent update
monotonic-only training
unload-reload / cyclic / nonproportional path-OOD testing
```

直接 runner：

```powershell
python 12_reproducibility\scripts\run_j2_path_ood_comparison.py `
  --epochs 50 `
  --train-samples 32 `
  --eval-samples 12 `
  --load-steps 8 `
  --eval-load-paths monotonic,unload_reload,cyclic,nonproportional `
  --out 10_results\reports\j2_path_operator_evidence_paper.json `
  --force-regenerate
```

最低报告指标：

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

验收标准：

```text
训练路径只能是 monotonic。
OOD 测试必须覆盖 unload-reload、cyclic、nonproportional。
必须报告 history increment error，因为这比 final-state error 更能检验是否学到演化律。
```

当前最重要的 L2 修复实验是 history-increment-aware training 与 path curriculum：

```powershell
python 12_reproducibility\scripts\run_j2_path_ood_comparison.py `
  --train-load-paths monotonic `
  --history-increment-weight 0.25 `
  --eqp-increment-weight 0.10 `
  --plastic-work-increment-weight 0.10 `
  --yield-flag-weight 0.05 `
  --epochs 50 `
  --out 10_results\reports\j2_path_operator_repair_increment_loss.json
```

若 strict path-OOD 仍然退化，再运行 curriculum 上限实验：

```powershell
python 12_reproducibility\scripts\run_j2_path_ood_comparison.py `
  --train-load-paths monotonic,unload_reload `
  --history-increment-weight 0.25 `
  --eqp-increment-weight 0.10 `
  --plastic-work-increment-weight 0.10 `
  --yield-flag-weight 0.05 `
  --epochs 50 `
  --out 10_results\reports\j2_path_operator_repair_unload_curriculum.json
```

## Combined Evidence Ledger

总控 runner 会把两个阶段的命令、输出文件、研究主张和验收条件写入 ledger。先用 dry run 检查证据链：

```powershell
python 12_reproducibility\scripts\run_research_landing_ladder.py --preset paper --dry-run
```

然后执行 smoke：

```powershell
python 12_reproducibility\scripts\run_research_landing_ladder.py --preset smoke --force-regenerate
```

最后执行 paper-scale：

```powershell
python 12_reproducibility\scripts\run_research_landing_ladder.py --preset paper --force-regenerate
```
