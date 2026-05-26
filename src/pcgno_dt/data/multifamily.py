from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True)
class MultiFamilySpec:
    """Common padded shape for multi-family operator learning."""

    max_parameters: int
    max_fields: int
    num_points: int
    spatial_dim: int
    family_names: tuple[str, ...]


def infer_multifamily_spec(datasets: Sequence[Mapping[str, Any]]) -> MultiFamilySpec:
    if not datasets:
        raise ValueError("at least one dataset is required")
    num_points = _as_tensor(datasets[0]["coords"]).shape[1]
    spatial_dim = _as_tensor(datasets[0]["coords"]).shape[-1]
    family_names: list[str] = []
    max_parameters = 0
    max_fields = 0
    for index, dataset in enumerate(datasets):
        coords = _as_tensor(dataset["coords"])
        params = _as_tensor(dataset["params"])
        fields = _as_tensor(dataset["fields"])
        if coords.shape[1] != num_points or coords.shape[-1] != spatial_dim:
            raise ValueError("all families must share num_points and spatial_dim for batching")
        max_parameters = max(max_parameters, params.shape[-1])
        max_fields = max(max_fields, fields.shape[-1])
        family_names.append(str(dataset.get("family", f"family_{index}")))
    return MultiFamilySpec(
        max_parameters=max_parameters,
        max_fields=max_fields,
        num_points=num_points,
        spatial_dim=spatial_dim,
        family_names=tuple(family_names),
    )


def pad_operator_dataset(
    dataset: Mapping[str, Any],
    spec: MultiFamilySpec,
    family_id: int,
) -> dict[str, torch.Tensor]:
    """Pad one family to the common multi-family tensor protocol."""

    coords = _as_tensor(dataset["coords"])
    params = _as_tensor(dataset["params"])
    fields = _as_tensor(dataset["fields"])
    forcing = _as_tensor(dataset["forcing"])
    n_samples = params.shape[0]
    if coords.shape[1] != spec.num_points or coords.shape[-1] != spec.spatial_dim:
        raise ValueError("dataset coordinates do not match the multi-family spec")
    if fields.shape != forcing.shape:
        raise ValueError("fields and forcing must share shape")

    padded_params = params.new_zeros(n_samples, spec.max_parameters)
    padded_params[:, : params.shape[-1]] = params
    param_mask = params.new_zeros(n_samples, spec.max_parameters)
    param_mask[:, : params.shape[-1]] = 1.0

    padded_fields = fields.new_zeros(n_samples, spec.num_points, spec.max_fields)
    padded_fields[:, :, : fields.shape[-1]] = fields
    padded_forcing = forcing.new_zeros(n_samples, spec.num_points, spec.max_fields)
    padded_forcing[:, :, : forcing.shape[-1]] = forcing
    field_mask = fields.new_zeros(n_samples, 1, spec.max_fields)
    field_mask[:, :, : fields.shape[-1]] = 1.0

    return {
        "coords": coords,
        "params": padded_params,
        "fields": padded_fields,
        "forcing": padded_forcing,
        "param_mask": param_mask,
        "field_mask": field_mask,
        "family_id": torch.full((n_samples,), family_id, device=params.device, dtype=torch.long),
        "active_parameters": torch.full(
            (n_samples,), params.shape[-1], device=params.device, dtype=torch.long
        ),
        "active_fields": torch.full(
            (n_samples,), fields.shape[-1], device=params.device, dtype=torch.long
        ),
    }


def build_multifamily_tensors(
    datasets: Sequence[Mapping[str, Any]],
    spec: MultiFamilySpec | None = None,
) -> tuple[dict[str, torch.Tensor], MultiFamilySpec]:
    """Concatenate multiple benchmark families after parameter/field padding."""

    if spec is None:
        spec = infer_multifamily_spec(datasets)
    padded = [pad_operator_dataset(dataset, spec, family_id=i) for i, dataset in enumerate(datasets)]
    keys = padded[0].keys()
    tensors = {key: torch.cat([item[key] for item in padded], dim=0) for key in keys}
    return tensors, spec


def _as_tensor(value: Any) -> torch.Tensor:
    if not isinstance(value, torch.Tensor):
        raise TypeError("multi-family datasets must contain torch tensors")
    return value
