# 物理建模范围

## 基础层

- 几何描述：网格、点云、图、隐式几何或 NURBS。
- 状态变量：位移、应变、应力、温度、压力、电磁场、接触力。
- 参数变量：材料参数、载荷参数、边界参数、耦合参数。

## 多物理耦合层

候选耦合：

- magneto-mechanics
- thermo-mechanics
- fluid-structure interaction
- contact mechanics
- damage and fracture
- poromechanics

## 物理约束库

需要逐步实现以下 residual：

- PDE residual
- boundary condition residual
- initial condition residual
- interface continuity residual
- conservation residual
- energy residual
- thermodynamic admissibility residual
- contact complementarity residual

## 结构保持原则

模型设计尽量保留以下结构：

- frame invariance
- material symmetry
- energy stability
- positivity or boundedness
- conservation
- monotonicity when required
