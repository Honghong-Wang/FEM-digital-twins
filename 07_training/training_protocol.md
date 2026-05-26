# 训练协议

## 训练阶段

1. Data-only deterministic pretraining。
2. Physics residual fine-tuning。
3. Generative/UQ module training。
4. Inverse module training or posterior inference。
5. Digital-twin online update testing。

## 损失项记录

每次实验必须记录：

- data loss
- PDE residual loss
- boundary residual loss
- energy or conservation residual
- calibration loss
- inverse identification loss
- total loss

## 必须保存的实验元数据

- git commit or archive tag
- config file
- random seed
- dataset version
- model version
- training time
- hardware
- final metrics

## 消融实验

- without physics constraints
- without generative module
- without UQ calibration
- without sparse observation encoder
- deterministic operator only
- different geometry encoders
