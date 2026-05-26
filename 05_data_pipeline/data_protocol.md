# 数据协议

## 数据层级

- `raw`: 原始求解器输出，不做覆盖修改。
- `processed`: 对齐、归一化、裁剪、插值后的训练数据。
- `synthetic`: 低成本 PDE 或降阶模型生成的数据。
- `metadata`: 参数范围、采样方式、求解器版本、随机种子。

## 推荐数据格式

优先使用 HDF5 或 NPZ。每个样本至少包含：

```text
sample_id
geometry
mesh_or_grid
parameters
boundary_conditions
initial_conditions
solution_fields
derived_quantities
solver_metadata
```

## 数据划分

- train: 插值参数区间。
- validation: 插值区间内但未见参数。
- test: 固定报告用测试集。
- ood: 几何、材料、载荷或边界条件分布外样本。
- inverse: 带稀疏传感观测和噪声的数据。

## 质量检查

- 物理量单位一致。
- 边界条件可追踪。
- 求解器收敛状态可追踪。
- NaN/Inf 自动检查。
- 能量、守恒量或约束残差记录。
