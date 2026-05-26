from __future__ import annotations

from collections.abc import Mapping

import torch
from torch.utils.data import Dataset


class OperatorTensorDataset(Dataset[dict[str, torch.Tensor]]):
    """Torch dataset for operator-learning tensors."""

    def __init__(self, tensors: Mapping[str, torch.Tensor]) -> None:
        required = {"coords", "params", "fields", "forcing"}
        missing = required.difference(tensors)
        if missing:
            raise KeyError(f"missing required tensors: {sorted(missing)}")
        n_samples = tensors["params"].shape[0]
        for key in required:
            if tensors[key].shape[0] != n_samples:
                raise ValueError(f"{key} has inconsistent batch dimension")
        self.tensors = {
            key: value
            for key, value in tensors.items()
            if isinstance(value, torch.Tensor) and value.ndim > 0 and value.shape[0] == n_samples
        }

    def __len__(self) -> int:
        return self.tensors["params"].shape[0]

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        return {key: value[index] for key, value in self.tensors.items()}


class PathOperatorTensorDataset(Dataset[dict[str, torch.Tensor]]):
    """Torch dataset for path-dependent operator-learning tensors."""

    def __init__(self, tensors: Mapping[str, torch.Tensor]) -> None:
        required = {"coords", "params", "fields_sequence", "forcing_sequence"}
        missing = required.difference(tensors)
        if missing:
            raise KeyError(f"missing required path tensors: {sorted(missing)}")
        n_samples = tensors["params"].shape[0]
        for key, value in tensors.items():
            if not isinstance(value, torch.Tensor):
                continue
            if value.ndim > 0 and value.shape[0] == n_samples:
                continue
            if key in required or key in {"sample_id", "fields", "forcing"}:
                raise ValueError(f"{key} has inconsistent batch dimension")
        fields_sequence = tensors["fields_sequence"]
        forcing_sequence = tensors["forcing_sequence"]
        if fields_sequence.shape != forcing_sequence.shape:
            raise ValueError("fields_sequence and forcing_sequence must share shape")
        if tensors["coords"].shape[1] != fields_sequence.shape[2]:
            raise ValueError("coords and fields_sequence must share node count")
        self.tensors = {key: value for key, value in tensors.items() if isinstance(value, torch.Tensor)}

    def __len__(self) -> int:
        return self.tensors["params"].shape[0]

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        return {key: value[index] for key, value in self.tensors.items()}
