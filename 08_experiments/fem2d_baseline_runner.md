# 2D FEM Baseline Runner

## Purpose

This runner establishes the first paper-style evidence chain on a real finite-element snapshot
dataset. It uses the same split, seed, epochs, batch size, and metrics for:

- PINN
- DeepONet
- FNO
- MeshGraph operator
- Mesh-to-mesh graph operator
- PCGNO

It also supports repeated seeds and reports `mean/std` summaries.

## Dataset

The current dataset is built with a local 2D plane-stress FEM solver using CST triangular
elements:

- rectangular structured node grid
- triangular connectivity
- left edge fixed
- right edge traction
- parameters: Young's modulus, Poisson ratio, traction-x, traction-y
- fields: displacement-x, displacement-y

Generate data explicitly:

```powershell
python 12_reproducibility\scripts\generate_plane_stress_fem_dataset.py --train-samples 64 --eval-samples 24 --nx 9 --ny 7
```

Generate a geometrically perturbed triangular mesh dataset:

```powershell
python 12_reproducibility\scripts\generate_plane_stress_fem_dataset.py --mesh-kind jittered --geometry-perturbation 0.15 --train-samples 64 --eval-samples 24 --nx 9 --ny 7
```

Available geometry families:

- `structured`: tensor-product triangular mesh
- `jittered`: perturbed interior nodes and randomized cell diagonals
- `hole`: internal circular cutout on a triangular mesh
- `notch`: right-edge re-entrant notch
- `curved`: curved top boundary mapping

External mesh exports are also supported:

- Gmsh/CAD: ASCII `.msh`
- Abaqus: `.inp` with CPS3/CPE3/S3 or CPS4/CPE4/S4 style 2D elements
- FEniCS/DOLFIN: legacy `.xml`
- Inline XDMF and local `.npz`

Convert an external mesh to the local mesh NPZ format:

```powershell
python 12_reproducibility\scripts\convert_external_mesh.py path\to\mesh.inp --out 05_data_pipeline\processed\external_meshes\mesh.npz
```

Generate FEM snapshots directly from an external mesh:

```powershell
python 12_reproducibility\scripts\generate_plane_stress_fem_dataset.py --mesh-file path\to\mesh.msh --out-dir 05_data_pipeline\processed\external_mesh_demo --train-samples 64 --eval-samples 24
```

Or let the runner generate missing splits automatically.

## Fair Comparison

Run all baselines:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model all --epochs 10 --train-samples 64 --eval-samples 24 --batch-size 8 --nx 9 --ny 7
```

Run all baselines on a jittered triangular mesh:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model all --mesh-kind hole --geometry-perturbation 0.12 --epochs 10 --train-samples 64 --eval-samples 24 --batch-size 8 --nx 9 --ny 7 --force-regenerate
```

Run a mesh-to-mesh graph baseline on an imported Abaqus/Gmsh/FEniCS mesh:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model mesh2meshgno --mesh-file path\to\mesh.inp --data-dir 05_data_pipeline\processed\external_mesh_runner --epochs 50 --num-seeds 5 --force-regenerate
```

Run one model:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model pcgno --epochs 10
```

For PCGNO diagnostics, separate mean-operator fitting from probabilistic likelihood fitting:

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

`--pcgno-data-loss nll` trains the mean and variance jointly through Gaussian NLL. `--pcgno-data-loss mse` trains the mean with MSE and keeps the variance head through calibration loss, which is useful when testing whether poor FEM evidence comes from the operator backbone or from likelihood/variance coupling.

The runner reports:

- train final loss
- test relative L2 and max absolute error
- OOD material relative L2 and max absolute error
- OOD loading relative L2 and max absolute error
- PCGNO coverage and ECE
- assembled FEM residual RMS and relative residual
- fixed-boundary RMS and relative violation
- relative total-potential-energy error

## FEM Physics Callbacks

PCGNO receives assembled FEM physics terms through `FEMProblemAdapter` callbacks:

```text
residual_callback(params, fields, forcing) = K(params) u - f
boundary_callback(params, fields) = u on fixed left-edge nodes
energy_callback(params, fields, forcing) = 0.5 u^T K(params) u - f^T u
```

The residual is zeroed on constrained DOFs because those DOFs carry reaction forces. Boundary
conditions are enforced separately through the boundary callback.

Physics weights can be adjusted. By default the physics terms are normalized by reference force,
field, and energy scales:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model pcgno --pde-weight 0.0001 --boundary-weight 0.01 --energy-weight 0.000001
```

Use automatic balancing when the physical terms should be balanced from the observed task losses:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model pcgno --loss-balancer uncertainty --epochs 50 --num-seeds 5
```

Available PCGNO loss balancers:

- `static`: uses the explicit `--pde-weight`, `--boundary-weight`, and `--energy-weight`.
- `uncertainty`: learns homoscedastic task uncertainty weights.
- `gradnorm`: learns task weights by balancing gradient norms.
- `softadapt`: adapts task weights from recent loss-change rates.
- `residual_adaptive`: increases physics weights when residual losses lag behind data fitting.

Physics terms can also be warmed up with a curriculum:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model pcgno --loss-balancer gradnorm --physics-curriculum cosine --physics-warmup-epochs 10 --epochs 50 --num-seeds 5
```

Disable normalization only for diagnostic comparisons:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model pcgno --no-normalize-physics
```

Run repeated seeds:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model all --num-seeds 5 --epochs 50
```

Results are written to:

```text
10_results/reports/fem2d_baseline_runner_results.json
```

Use `--out` to write a named evidence artifact:

```powershell
python 12_reproducibility\scripts\run_fem2d_baseline_runner.py --model all --epochs 50 --num-seeds 5 --out 10_results\reports\fem2d_operator_evidence_paper.json
```

The JSON contains per-seed results under `seeds` and aggregated `mean/std` values under
`summary`.

## Loss-Weight Sweep

The smoke experiments showed that adding a FEM residual term does not automatically reduce the
reported residual. The weight schedule is therefore treated as a research variable instead of a
default constant. Run a paper-scale sweep over data/PDE/boundary/energy trade-offs, automatic
balancers, curricula, grid sizes, and data sizes:

```powershell
python 12_reproducibility\scripts\run_fem2d_loss_weight_sweep.py --epochs 50 --num-seeds 5 --grid-sizes 9x7,13x9 --train-sample-counts 64,128 --balancers static,uncertainty,gradnorm,softadapt,residual_adaptive --curricula constant,linear,cosine
```

For quick triage or CI smoke tests, cap the matrix:

```powershell
python 12_reproducibility\scripts\run_fem2d_loss_weight_sweep.py --epochs 1 --num-seeds 1 --grid-sizes 5x4 --train-sample-counts 8 --balancers gradnorm,softadapt --curricula linear --max-configs 2
```

Sweep outputs are written to:

```text
10_results/reports/fem2d_loss_weight_sweep_results.json
10_results/reports/fem2d_loss_weight_sweep_results.csv
```

The ranking objective is only a triage score. Final paper tables should still report each metric
separately: relative error, FEM residual, boundary violation, energy error, coverage, calibration,
OOD degradation, and the learned effective loss weights when automatic balancing is used.

## Mesh-Resolution Transfer

A neural operator should not only work on the training mesh. Run the mesh-transfer experiment to
train on one FEM grid and evaluate on multiple finer/coarser perturbed triangular meshes. Each
evaluation grid receives its own assembled FEM residual and energy callback:

```powershell
python 12_reproducibility\scripts\run_fem2d_mesh_transfer.py --model all --mesh-kind hole --geometry-perturbation 0.12 --train-grid 9x7 --eval-grids 9x7,13x9,17x11 --epochs 50 --num-seeds 5 --loss-balancer residual_adaptive
```

For real exported meshes, align source and target mesh files with labels in `--eval-grids`:

```powershell
python 12_reproducibility\scripts\run_fem2d_mesh_transfer.py --model all --train-grid 0x0 --eval-grids 0x0,1x0 --train-mesh-file path\to\coarse.msh --eval-mesh-files path\to\coarse.msh,path\to\fine.msh --epochs 50 --num-seeds 5
```

Outputs are written to:

```text
10_results/reports/fem2d_mesh_transfer_results.json
10_results/reports/fem2d_mesh_transfer_results.csv
```

## Current Limitations

- The FEM residual callback is assembled into the PCGNO training loss, but only for the local
  plane-stress FEM solver so far.
- PCGNO uses a low-rank Gaussian latent head, not yet diffusion/flow/transport-map posterior.
- Automatic balancing currently covers uncertainty weighting, GradNorm, SoftAdapt, and
  residual-adaptive weighting; constrained/Pareto optimization remains an open ablation arm.
- The default smoke-test setting is intentionally tiny; paper results need larger meshes, more
  snapshots, repeated seeds, and longer training.
