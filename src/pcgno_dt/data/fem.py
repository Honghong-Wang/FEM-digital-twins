from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import inspect
from pathlib import Path
from typing import Any

import numpy as np
import torch


TensorDict = dict[str, torch.Tensor]
ResidualCallback = Callable[..., torch.Tensor]
BoundaryCallback = Callable[..., torch.Tensor]
EnergyCallback = Callable[..., torch.Tensor]
ThermodynamicCallback = Callable[..., torch.Tensor]
_PATH_SEQUENCE_KEYS = (
    "fields_sequence",
    "forcing_sequence",
    "tangent_stiffness_sequence",
    "newton_residual_sequence",
    "reference_energy_sequence",
    "material_history_sequence",
    "material_history_qp_sequence",
    "plastic_strain_sequence",
    "plastic_strain_qp_sequence",
    "stress_sequence",
    "strain_sequence",
)


@dataclass(frozen=True)
class FEMSnapshotSchema:
    """Schema for FEM data exported into the operator-learning tensor protocol."""

    coords: str = "coords"
    params: str = "params"
    fields: str = "fields"
    forcing: str = "forcing"
    residual: str = "residual"
    sample_id: str = "sample_id"
    parameter_names: str = "parameter_names"
    field_names: str = "field_names"


def load_fem_snapshots(
    path: str | Path,
    schema: FEMSnapshotSchema = FEMSnapshotSchema(),
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> dict[str, Any]:
    """Load FEM snapshots from `.npz` or `.h5/.hdf5` into the common tensor protocol.

    Required arrays:

    - `coords`: `[n_samples, n_nodes, spatial_dim]` or `[n_nodes, spatial_dim]`
    - `params`: `[n_samples, n_parameters]`
    - `fields`: `[n_samples, n_nodes, n_fields]`
    - `forcing`: `[n_samples, n_nodes, n_fields]`

    Optional arrays such as `residual`, `connectivity`, `mass`, `stiffness`, `parameter_names`,
    and `field_names` are preserved when present.
    """

    path = Path(path)
    if path.suffix.lower() == ".npz":
        raw = _load_npz(path)
    elif path.suffix.lower() in {".h5", ".hdf5"}:
        raw = _load_hdf5(path)
    else:
        raise ValueError("FEM snapshots must be stored as .npz, .h5, or .hdf5")

    tensors: TensorDict = {}
    for key in (schema.coords, schema.params, schema.fields, schema.forcing, schema.residual):
        if key in raw:
            tensors[key] = _as_tensor(raw[key], device=device, dtype=dtype)

    _validate_required_tensors(tensors, schema)
    if tensors[schema.coords].ndim == 2:
        coords = tensors[schema.coords].unsqueeze(0).expand(tensors[schema.params].shape[0], -1, -1)
        tensors[schema.coords] = coords.contiguous()
    if schema.sample_id in raw:
        sample_id = torch.as_tensor(raw[schema.sample_id], device=device, dtype=torch.long).reshape(-1)
    else:
        sample_id = torch.arange(tensors[schema.params].shape[0], device=device, dtype=torch.long)
    if sample_id.numel() != tensors[schema.params].shape[0]:
        raise ValueError("sample_id must have one entry per FEM snapshot")
    tensors[schema.sample_id] = sample_id

    metadata = {
        "path": str(path),
        "parameter_names": _decode_names(raw.get(schema.parameter_names)),
        "field_names": _decode_names(raw.get(schema.field_names)),
        "available_keys": tuple(sorted(raw)),
    }
    extra = {
        key: value
        for key, value in raw.items()
        if key not in tensors and key not in {schema.parameter_names, schema.field_names}
    }
    return {"tensors": tensors, "metadata": metadata, "extra": extra}


def load_fem_path_snapshots(
    path: str | Path,
    schema: FEMSnapshotSchema = FEMSnapshotSchema(),
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> dict[str, Any]:
    """Load FEM snapshots and promote path-dependent sequence arrays into tensors."""

    loaded = load_fem_snapshots(path, schema=schema, device=device, dtype=dtype)
    tensors = loaded["tensors"]
    extra = loaded["extra"]
    n_samples = int(tensors["params"].shape[0])
    for key in _PATH_SEQUENCE_KEYS:
        if key not in extra:
            continue
        value = extra[key]
        shape = _shape_tuple(value)
        if not shape or shape[0] != n_samples:
            continue
        tensors[key] = _as_tensor(value, device=device, dtype=dtype)
    return loaded


def save_fem_npz(
    path: str | Path,
    tensors: Mapping[str, torch.Tensor],
    parameter_names: tuple[str, ...] = (),
    field_names: tuple[str, ...] = (),
    **extra: Any,
) -> None:
    """Save tensors in the FEM adapter format for smoke tests or external solver export."""

    arrays = {key: value.detach().cpu().numpy() for key, value in tensors.items()}
    if parameter_names:
        arrays["parameter_names"] = np.asarray(parameter_names)
    if field_names:
        arrays["field_names"] = np.asarray(field_names)
    arrays.update(extra)
    np.savez(Path(path), **arrays)


@dataclass
class FEMProblemAdapter:
    """FEM-backed problem wrapper using the same residual/energy/boundary methods.

    For a real FEM solver, pass callbacks that evaluate assembled residuals, boundary residuals,
    and energies on predicted fields. Without callbacks, the adapter remains usable for data-only
    training and baseline comparison; physics residual terms are zero by construction.
    """

    coords: torch.Tensor
    num_parameters: int
    num_fields: int
    parameter_names: tuple[str, ...] = ()
    field_names: tuple[str, ...] = ()
    residual_callback: ResidualCallback | None = None
    boundary_callback: BoundaryCallback | None = None
    energy_callback: EnergyCallback | None = None
    thermodynamic_callback: ThermodynamicCallback | None = None
    use_full_residual: bool = True
    batch_context: Mapping[str, torch.Tensor] | None = None

    @property
    def num_points(self) -> int:
        return self.coords.shape[1] if self.coords.ndim == 3 else self.coords.shape[0]

    def grid(self, batch_size: int | None = None) -> torch.Tensor:
        coords = self.coords
        if coords.ndim == 2:
            coords = coords.unsqueeze(0)
        if batch_size is None:
            return coords[:1]
        if coords.shape[0] == batch_size:
            return coords
        return coords[:1].expand(batch_size, -1, -1).contiguous()

    def residual(
        self,
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None = None,
        use_finite_difference: bool = True,
    ) -> torch.Tensor:
        del use_finite_difference
        if self.residual_callback is not None:
            return _call_residual_callback(self.residual_callback, params, fields, forcing, self.batch_context)
        return torch.zeros_like(fields)

    def boundary_residual(self, params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        if self.boundary_callback is not None:
            return _call_boundary_callback(self.boundary_callback, params, fields, self.batch_context)
        return torch.stack([fields[:, 0, :], fields[:, -1, :]], dim=1).new_zeros(
            fields.shape[0], 2, fields.shape[-1]
        )

    def energy(
        self, params: torch.Tensor, fields: torch.Tensor, forcing: torch.Tensor | None = None
    ) -> torch.Tensor:
        if self.energy_callback is not None:
            return _call_energy_callback(self.energy_callback, params, fields, forcing, self.batch_context)
        if forcing is None:
            forcing = torch.zeros_like(fields)
        return -(forcing * fields).mean(dim=(1, 2))

    def thermodynamic_penalty(self, params: torch.Tensor) -> torch.Tensor:
        if self.thermodynamic_callback is not None:
            return _call_thermodynamic_callback(self.thermodynamic_callback, params, self.batch_context)
        return params.new_tensor(0.0)

    def set_batch_context(self, batch: Mapping[str, torch.Tensor] | None) -> None:
        if batch is None:
            self.batch_context = None
            return
        self.batch_context = {key: value for key, value in batch.items() if isinstance(value, torch.Tensor)}

    def clear_batch_context(self) -> None:
        self.batch_context = None


def make_fem_problem_adapter(
    tensors: Mapping[str, torch.Tensor],
    metadata: Mapping[str, Any] | None = None,
    residual_callback: ResidualCallback | None = None,
    boundary_callback: BoundaryCallback | None = None,
    energy_callback: EnergyCallback | None = None,
    thermodynamic_callback: ThermodynamicCallback | None = None,
) -> FEMProblemAdapter:
    metadata = metadata or {}
    params = tensors["params"]
    fields = tensors["fields"]
    return FEMProblemAdapter(
        coords=tensors["coords"],
        num_parameters=params.shape[-1],
        num_fields=fields.shape[-1],
        parameter_names=tuple(metadata.get("parameter_names") or ()),
        field_names=tuple(metadata.get("field_names") or ()),
        residual_callback=residual_callback,
        boundary_callback=boundary_callback,
        energy_callback=energy_callback,
        thermodynamic_callback=thermodynamic_callback,
    )


def has_assembled_linear_fem_data(extra: Mapping[str, Any]) -> bool:
    """Return whether loaded FEM extras contain a reusable assembled stiffness matrix."""

    if "stiffness" not in extra:
        return False
    stiffness_shape = _shape_tuple(extra["stiffness"])
    return len(stiffness_shape) == 2 or (len(stiffness_shape) == 3 and stiffness_shape[0] == 1)


def has_stateful_nonlinear_fem_data(
    tensors: Mapping[str, torch.Tensor],
    extra: Mapping[str, Any],
    tangent_key: str = "tangent_stiffness",
    stiffness_key: str = "stiffness",
) -> bool:
    """Return whether FEM extras contain per-sample tangent/Newton data."""

    n_samples = int(tensors["fields"].shape[0])
    if tangent_key in extra:
        tangent_shape = _shape_tuple(extra[tangent_key])
        return len(tangent_shape) == 3 and tangent_shape[0] == n_samples
    if stiffness_key in extra:
        stiffness_shape = _shape_tuple(extra[stiffness_key])
        return len(stiffness_shape) == 3 and stiffness_shape[0] == n_samples
    return False


def make_assembled_linear_fem_callbacks(
    tensors: Mapping[str, torch.Tensor],
    extra: Mapping[str, Any],
    stiffness_key: str = "stiffness",
    fixed_dofs_key: str = "fixed_dofs",
    fixed_nodes_key: str = "fixed_nodes",
) -> tuple[ResidualCallback, BoundaryCallback, EnergyCallback]:
    """Create callbacks from externally exported assembled linear FEM operators.

    Expected export arrays:

    ```text
    stiffness:  [n_dofs, n_dofs] or [1, n_dofs, n_dofs]
    fixed_dofs: optional [n_fixed_dofs]
    fixed_nodes: optional [n_fixed_nodes]
    ```

    The callbacks evaluate `K u - f`, boundary displacement on fixed DOFs/nodes, and
    `0.5 u^T K u - f^T u`. Sample-dependent `K_i` tensors are intentionally rejected here
    because the stateless callback API cannot safely infer dataset indices from shuffled batches.
    For nonlinear/sample-dependent external solvers, export a solver-side callback or include a
    stateful adapter that receives sample IDs.
    """

    if stiffness_key not in extra:
        raise KeyError(f"missing assembled stiffness array: {stiffness_key}")
    n_nodes = tensors["fields"].shape[1]
    n_fields = tensors["fields"].shape[2]
    n_dofs = n_nodes * n_fields
    stiffness = _shared_stiffness_tensor(extra[stiffness_key], n_dofs)
    fixed_dofs = _fixed_dofs_from_extra(extra, fixed_dofs_key, fixed_nodes_key, n_fields)

    def residual_callback(
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None,
    ) -> torch.Tensor:
        del params
        stiffness_local = stiffness.to(device=fields.device, dtype=fields.dtype)
        displacement = fields.reshape(fields.shape[0], -1)
        if forcing is None:
            force = torch.zeros_like(displacement)
        else:
            force = forcing.reshape(forcing.shape[0], -1).to(device=fields.device, dtype=fields.dtype)
        residual_flat = displacement @ stiffness_local.T - force
        if fixed_dofs.numel() > 0:
            residual_flat = residual_flat.clone()
            residual_flat[:, fixed_dofs.to(device=fields.device)] = 0.0
        return residual_flat.view_as(fields)

    def boundary_callback(params: torch.Tensor, fields: torch.Tensor) -> torch.Tensor:
        del params
        if fixed_dofs.numel() == 0:
            return fields[:, :1, :].new_zeros(fields.shape[0], 1, fields.shape[-1])
        values = fields.reshape(fields.shape[0], -1).index_select(
            dim=1,
            index=fixed_dofs.to(device=fields.device),
        )
        return values.unsqueeze(-1)

    def energy_callback(
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None,
    ) -> torch.Tensor:
        del params
        stiffness_local = stiffness.to(device=fields.device, dtype=fields.dtype)
        displacement = fields.reshape(fields.shape[0], -1)
        if forcing is None:
            force = torch.zeros_like(displacement)
        else:
            force = forcing.reshape(forcing.shape[0], -1).to(device=fields.device, dtype=fields.dtype)
        elastic = 0.5 * torch.einsum("bi,ij,bj->b", displacement, stiffness_local, displacement)
        work = (force * displacement).sum(dim=1)
        return elastic - work

    return residual_callback, boundary_callback, energy_callback


def make_stateful_nonlinear_fem_callbacks(
    tensors: Mapping[str, torch.Tensor],
    extra: Mapping[str, Any],
    tangent_key: str = "tangent_stiffness",
    stiffness_key: str = "stiffness",
    reference_fields_key: str = "reference_fields",
    newton_residual_key: str = "newton_residual",
    reference_energy_key: str = "reference_energy",
    history_key: str = "material_history",
    history_alias_key: str = "history",
    fixed_dofs_key: str = "fixed_dofs",
    fixed_nodes_key: str = "fixed_nodes",
) -> tuple[ResidualCallback, BoundaryCallback, EnergyCallback, ThermodynamicCallback]:
    """Create stateful callbacks for nonlinear FEM snapshots with per-sample tangent data.

    The callback evaluates a Newton-linearized residual around each exported converged state:

    ```text
    R_i(u) ~= R_i(u_ref) + K_tangent_i (u - u_ref_i)
    ```

    Batch/sample alignment is driven by `sample_id`, so the callbacks remain correct under
    shuffled DataLoader batches and mesh-transfer evaluation.
    """

    n_samples = int(tensors["fields"].shape[0])
    n_nodes = int(tensors["fields"].shape[1])
    n_fields = int(tensors["fields"].shape[2])
    n_dofs = n_nodes * n_fields
    sample_ids = tensors.get("sample_id")
    if sample_ids is None:
        sample_ids = torch.arange(n_samples, dtype=torch.long)
    sample_ids = torch.as_tensor(sample_ids, dtype=torch.long).reshape(-1)
    if sample_ids.numel() != n_samples:
        raise ValueError("stateful FEM callbacks require one sample_id per snapshot")

    tangent = _sample_matrix_tensor(
        extra[tangent_key] if tangent_key in extra else extra[stiffness_key],
        n_samples=n_samples,
        n_dofs=n_dofs,
        name=tangent_key if tangent_key in extra else stiffness_key,
    )
    reference_fields = _sample_field_tensor(
        extra.get(reference_fields_key, tensors["fields"]),
        n_samples=n_samples,
        n_nodes=n_nodes,
        n_fields=n_fields,
        name=reference_fields_key,
    )
    if newton_residual_key in extra:
        reference_residual = _sample_flat_tensor(
            extra[newton_residual_key],
            n_samples=n_samples,
            n_dofs=n_dofs,
            name=newton_residual_key,
        )
    elif "residual" in tensors:
        reference_residual = _sample_flat_tensor(
            tensors["residual"],
            n_samples=n_samples,
            n_dofs=n_dofs,
            name="residual",
        )
    else:
        reference_residual = torch.zeros(n_samples, n_dofs, dtype=reference_fields.dtype)
    if reference_energy_key in extra:
        reference_energy = torch.as_tensor(extra[reference_energy_key])
        if not reference_energy.is_floating_point():
            reference_energy = reference_energy.float()
        reference_energy = reference_energy.reshape(-1)
        if reference_energy.numel() != n_samples:
            raise ValueError(f"{reference_energy_key} must have one value per snapshot")
        reference_energy = reference_energy.detach().cpu()
    else:
        reference_energy = torch.zeros(n_samples, dtype=reference_fields.dtype)
    history_value = extra.get(history_key, extra.get(history_alias_key))
    history = None if history_value is None else _sample_history_tensor(history_value, n_samples)
    fixed_dofs = _fixed_dofs_from_extra(extra, fixed_dofs_key, fixed_nodes_key, n_fields)
    id_to_row = {int(sample_id): row for row, sample_id in enumerate(sample_ids.cpu().tolist())}

    def residual_callback(
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None,
        batch_context: Mapping[str, torch.Tensor] | None = None,
    ) -> torch.Tensor:
        del params, forcing
        rows = _stateful_row_indices(batch_context, fields.shape[0], id_to_row, n_samples, fields.device)
        tangent_local = tangent.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        reference = reference_fields.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        residual_ref = reference_residual.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        delta = fields.reshape(fields.shape[0], -1) - reference.reshape(fields.shape[0], -1)
        residual_flat = residual_ref + torch.bmm(tangent_local, delta.unsqueeze(-1)).squeeze(-1)
        residual_flat = _mask_fixed_dofs(residual_flat, fixed_dofs, rows, fields.device)
        return residual_flat.view_as(fields)

    def boundary_callback(
        params: torch.Tensor,
        fields: torch.Tensor,
        batch_context: Mapping[str, torch.Tensor] | None = None,
    ) -> torch.Tensor:
        del params
        rows = _stateful_row_indices(batch_context, fields.shape[0], id_to_row, n_samples, fields.device)
        return _gather_fixed_dof_values(fields, fixed_dofs, rows)

    def energy_callback(
        params: torch.Tensor,
        fields: torch.Tensor,
        forcing: torch.Tensor | None,
        batch_context: Mapping[str, torch.Tensor] | None = None,
    ) -> torch.Tensor:
        del params, forcing
        rows = _stateful_row_indices(batch_context, fields.shape[0], id_to_row, n_samples, fields.device)
        tangent_local = tangent.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        reference = reference_fields.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        residual_ref = reference_residual.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        energy_ref = reference_energy.index_select(0, rows.cpu()).to(device=fields.device, dtype=fields.dtype)
        delta = fields.reshape(fields.shape[0], -1) - reference.reshape(fields.shape[0], -1)
        quadratic = 0.5 * torch.bmm(delta.unsqueeze(1), torch.bmm(tangent_local, delta.unsqueeze(-1))).flatten()
        linear = (residual_ref * delta).sum(dim=1)
        return energy_ref + linear + quadratic

    def thermodynamic_callback(
        params: torch.Tensor,
        batch_context: Mapping[str, torch.Tensor] | None = None,
    ) -> torch.Tensor:
        if history is None:
            return params.new_tensor(0.0)
        rows = _stateful_row_indices(batch_context, params.shape[0], id_to_row, n_samples, params.device)
        history_local = history.index_select(0, rows.cpu()).to(device=params.device, dtype=params.dtype)
        return torch.relu(-history_local).square().mean()

    return residual_callback, boundary_callback, energy_callback, thermodynamic_callback


def _load_npz(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def _load_hdf5(path: Path) -> dict[str, Any]:
    try:
        import h5py
    except ImportError as exc:
        raise ImportError("h5py is required to load .h5/.hdf5 FEM snapshots") from exc

    raw: dict[str, Any] = {}
    with h5py.File(path, "r") as handle:
        for key in handle.keys():
            raw[key] = handle[key][()]
    return raw


def _as_tensor(value: Any, device: str, dtype: torch.dtype) -> torch.Tensor:
    tensor = torch.as_tensor(value)
    if not tensor.is_floating_point():
        tensor = tensor.float()
    return tensor.to(device=device, dtype=dtype)


def _validate_required_tensors(tensors: Mapping[str, torch.Tensor], schema: FEMSnapshotSchema) -> None:
    required = {schema.coords, schema.params, schema.fields, schema.forcing}
    missing = required.difference(tensors)
    if missing:
        raise KeyError(f"FEM snapshot is missing required arrays: {sorted(missing)}")

    coords = tensors[schema.coords]
    params = tensors[schema.params]
    fields = tensors[schema.fields]
    forcing = tensors[schema.forcing]
    if coords.ndim not in {2, 3}:
        raise ValueError("coords must have shape [nodes, dim] or [samples, nodes, dim]")
    if params.ndim != 2:
        raise ValueError("params must have shape [samples, parameters]")
    if fields.ndim != 3 or forcing.ndim != 3:
        raise ValueError("fields and forcing must have shape [samples, nodes, fields]")
    if fields.shape != forcing.shape:
        raise ValueError("fields and forcing must share shape")
    if params.shape[0] != fields.shape[0]:
        raise ValueError("params and fields must share sample count")
    if coords.ndim == 3 and coords.shape[0] != fields.shape[0]:
        raise ValueError("batched coords must share sample count with fields")
    if coords.shape[-2] != fields.shape[1]:
        raise ValueError("coords and fields must share node count")


def _decode_names(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    array = np.asarray(value)
    names: list[str] = []
    for item in array.reshape(-1):
        if isinstance(item, bytes):
            names.append(item.decode("utf-8"))
        else:
            names.append(str(item))
    return tuple(names)


def _shared_stiffness_tensor(value: Any, n_dofs: int) -> torch.Tensor:
    stiffness = torch.as_tensor(value)
    if not stiffness.is_floating_point():
        stiffness = stiffness.float()
    if stiffness.ndim == 3 and stiffness.shape[0] == 1:
        stiffness = stiffness[0]
    if stiffness.ndim != 2:
        raise ValueError(
            "assembled callbacks currently require a shared stiffness [n_dofs, n_dofs]; "
            "sample-dependent stiffness tensors need a stateful solver callback"
        )
    if tuple(stiffness.shape) != (n_dofs, n_dofs):
        raise ValueError(f"stiffness shape {tuple(stiffness.shape)} does not match n_dofs={n_dofs}")
    return stiffness


def _shape_tuple(value: Any) -> tuple[int, ...]:
    if isinstance(value, torch.Tensor):
        return tuple(int(dim) for dim in value.shape)
    return tuple(int(dim) for dim in np.asarray(value).shape)


def _fixed_dofs_from_extra(
    extra: Mapping[str, Any],
    fixed_dofs_key: str,
    fixed_nodes_key: str,
    n_fields: int,
) -> torch.Tensor:
    if fixed_dofs_key in extra:
        fixed_dofs = torch.as_tensor(extra[fixed_dofs_key], dtype=torch.long)
        return fixed_dofs.reshape(-1) if fixed_dofs.ndim <= 1 else fixed_dofs
    if fixed_nodes_key in extra:
        fixed_nodes = torch.as_tensor(extra[fixed_nodes_key], dtype=torch.long)
        if fixed_nodes.ndim <= 1:
            fixed_nodes = fixed_nodes.reshape(-1)
            return torch.stack([n_fields * fixed_nodes + field for field in range(n_fields)], dim=-1).reshape(-1)
        return torch.stack([n_fields * fixed_nodes + field for field in range(n_fields)], dim=-1).reshape(
            fixed_nodes.shape[0], -1
        )
    return torch.empty(0, dtype=torch.long)


def _call_residual_callback(
    callback: ResidualCallback,
    params: torch.Tensor,
    fields: torch.Tensor,
    forcing: torch.Tensor | None,
    batch_context: Mapping[str, torch.Tensor] | None,
) -> torch.Tensor:
    if _callback_accepts_context(callback, positional_count=4):
        return callback(params, fields, forcing, batch_context)
    return callback(params, fields, forcing)


def _call_boundary_callback(
    callback: BoundaryCallback,
    params: torch.Tensor,
    fields: torch.Tensor,
    batch_context: Mapping[str, torch.Tensor] | None,
) -> torch.Tensor:
    if _callback_accepts_context(callback, positional_count=3):
        return callback(params, fields, batch_context)
    return callback(params, fields)


def _call_energy_callback(
    callback: EnergyCallback,
    params: torch.Tensor,
    fields: torch.Tensor,
    forcing: torch.Tensor | None,
    batch_context: Mapping[str, torch.Tensor] | None,
) -> torch.Tensor:
    if _callback_accepts_context(callback, positional_count=4):
        return callback(params, fields, forcing, batch_context)
    return callback(params, fields, forcing)


def _call_thermodynamic_callback(
    callback: ThermodynamicCallback,
    params: torch.Tensor,
    batch_context: Mapping[str, torch.Tensor] | None,
) -> torch.Tensor:
    if _callback_accepts_context(callback, positional_count=2):
        return callback(params, batch_context)
    return callback(params)


def _callback_accepts_context(callback: Callable[..., torch.Tensor], positional_count: int) -> bool:
    try:
        signature = inspect.signature(callback)
    except (TypeError, ValueError):
        return False
    parameters = list(signature.parameters.values())
    if any(parameter.kind == inspect.Parameter.VAR_POSITIONAL for parameter in parameters):
        return True
    if any(parameter.name == "batch_context" for parameter in parameters):
        return True
    positional = [
        parameter
        for parameter in parameters
        if parameter.kind in {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}
    ]
    return len(positional) >= positional_count


def _sample_matrix_tensor(value: Any, n_samples: int, n_dofs: int, name: str) -> torch.Tensor:
    tensor = torch.as_tensor(value)
    if not tensor.is_floating_point():
        tensor = tensor.float()
    if tuple(tensor.shape) != (n_samples, n_dofs, n_dofs):
        raise ValueError(f"{name} must have shape [{n_samples}, {n_dofs}, {n_dofs}], got {tuple(tensor.shape)}")
    return tensor.detach().cpu()


def _sample_field_tensor(
    value: Any,
    n_samples: int,
    n_nodes: int,
    n_fields: int,
    name: str,
) -> torch.Tensor:
    tensor = torch.as_tensor(value)
    if not tensor.is_floating_point():
        tensor = tensor.float()
    if tuple(tensor.shape) != (n_samples, n_nodes, n_fields):
        raise ValueError(
            f"{name} must have shape [{n_samples}, {n_nodes}, {n_fields}], got {tuple(tensor.shape)}"
        )
    return tensor.detach().cpu()


def _sample_flat_tensor(value: Any, n_samples: int, n_dofs: int, name: str) -> torch.Tensor:
    tensor = torch.as_tensor(value)
    if not tensor.is_floating_point():
        tensor = tensor.float()
    if tensor.ndim == 3:
        tensor = tensor.reshape(tensor.shape[0], -1)
    if tuple(tensor.shape) != (n_samples, n_dofs):
        raise ValueError(f"{name} must have shape [{n_samples}, {n_dofs}] or field shape, got {tuple(tensor.shape)}")
    return tensor.detach().cpu()


def _sample_history_tensor(value: Any, n_samples: int) -> torch.Tensor:
    tensor = torch.as_tensor(value)
    if not tensor.is_floating_point():
        tensor = tensor.float()
    if tensor.shape[0] != n_samples:
        raise ValueError(f"material history must have first dimension n_samples={n_samples}")
    return tensor.detach().cpu()


def _stateful_row_indices(
    batch_context: Mapping[str, torch.Tensor] | None,
    batch_size: int,
    id_to_row: Mapping[int, int],
    n_samples: int,
    device: torch.device,
) -> torch.Tensor:
    if batch_context is not None and "sample_id" in batch_context:
        sample_ids = batch_context["sample_id"].reshape(-1).detach().cpu().tolist()
        if len(sample_ids) != batch_size:
            raise ValueError("batch sample_id count does not match fields batch size")
        try:
            rows = [id_to_row[int(sample_id)] for sample_id in sample_ids]
        except KeyError as exc:
            raise KeyError(f"unknown FEM sample_id in batch: {exc}") from exc
        return torch.as_tensor(rows, dtype=torch.long, device=device)
    if batch_size == n_samples:
        return torch.arange(n_samples, dtype=torch.long, device=device)
    raise ValueError(
        "stateful FEM callbacks require sample_id in the batch context for shuffled or partial batches"
    )


def _mask_fixed_dofs(
    residual_flat: torch.Tensor,
    fixed_dofs: torch.Tensor,
    rows: torch.Tensor,
    device: torch.device,
) -> torch.Tensor:
    if fixed_dofs.numel() == 0:
        return residual_flat
    residual_flat = residual_flat.clone()
    if fixed_dofs.ndim == 1:
        residual_flat[:, fixed_dofs.to(device=device)] = 0.0
        return residual_flat
    dofs = fixed_dofs.index_select(0, rows.cpu()).to(device=device)
    return residual_flat.scatter(1, dofs, torch.zeros_like(dofs, dtype=residual_flat.dtype))


def _gather_fixed_dof_values(fields: torch.Tensor, fixed_dofs: torch.Tensor, rows: torch.Tensor) -> torch.Tensor:
    if fixed_dofs.numel() == 0:
        return fields[:, :1, :].new_zeros(fields.shape[0], 1, fields.shape[-1])
    flat = fields.reshape(fields.shape[0], -1)
    if fixed_dofs.ndim == 1:
        return flat.index_select(dim=1, index=fixed_dofs.to(device=fields.device)).unsqueeze(-1)
    dofs = fixed_dofs.index_select(0, rows.cpu()).to(device=fields.device)
    return torch.gather(flat, dim=1, index=dofs).unsqueeze(-1)
