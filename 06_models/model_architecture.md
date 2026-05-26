# 模型架构设计

## 总体结构

```text
Inputs
  -> geometry encoder
  -> parameter encoder
  -> observation encoder
  -> neural operator backbone
  -> generative latent module
  -> physics projection or residual correction
  -> probabilistic field output
```

模型面向的是条件概率 solution operator，而不是固定数据集上的有限维 surrogate：

```text
(mu, g, b, y_obs) -> p_theta(u | mu, g, b, y_obs)
```

## 候选骨干

- DeepONet
- Fourier Neural Operator
- Graph Neural Operator
- Geometry-informed neural operator transformer
- Latent neural operator
- Hybrid FEM-neural operator

## 生成式模块

候选路线：

- Conditional diffusion in latent function space
- Normalizing flow over reduced field coefficients
- Transport map from reference Gaussian to solution distribution
- Variational operator model
- Score-based operator model

## 物理约束

训练目标包含：

```text
L = L_data + lambda_pde L_pde + lambda_bc L_bc
  + lambda_energy L_energy + lambda_cal L_calibration
  + lambda_inv L_inverse
```

可选约束项包括：

- PDE residual
- boundary and initial condition residual
- interface residual
- conservation residual
- energy consistency
- thermodynamic admissibility
- symmetry, invariance, or equivariance constraints
- contact or complementarity constraints

## 输出

模型不只输出均值场，而应输出：

- mean field
- sampled fields
- variance field
- credible interval
- physical residual map
- optional posterior over parameters
