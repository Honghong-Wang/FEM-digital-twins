from __future__ import annotations

import torch


def j2_fem_residual_energy(
    coords: torch.Tensor,
    params: torch.Tensor,
    fields: torch.Tensor,
    forcing: torch.Tensor,
    connectivity: torch.Tensor,
    plastic_strain: torch.Tensor,
    material_history: torch.Tensor,
    stress_qp: torch.Tensor | None = None,
    tangent_qp: torch.Tensor | None = None,
    correction_fields: torch.Tensor | None = None,
    assemble_tangent: bool = False,
    thickness: float = 1.0,
) -> dict[str, torch.Tensor]:
    """Matrix-free plane-strain J2 residual/energy audit for T3/T6 path snapshots.

    The callback prefers exported quadrature-point plastic strain/history when
    available. If only element-averaged arrays are present, it broadcasts the
    element state to all quadrature points. For T6 elements it uses a three-point
    triangular quadrature; for T3 it uses the one-point rule. It deliberately
    avoids dense tangent storage so 500-1000 node cases can be audited during
    training and evaluation.
    """

    if fields.ndim != 3:
        raise ValueError("fields must have shape [batch, nodes, fields]")
    if connectivity.ndim != 2 or connectivity.shape[1] not in {3, 6}:
        raise ValueError("connectivity must be T3 or T6 triangular connectivity")
    batch_size, n_nodes, n_fields = fields.shape
    if n_fields != 2:
        raise ValueError("J2 FEM audit expects two displacement components")
    residual = fields.new_zeros(batch_size, 2 * n_nodes)
    linearized_residual_increment = fields.new_zeros(batch_size, 2 * n_nodes)
    tangent_matrix = fields.new_zeros(batch_size, 2 * n_nodes, 2 * n_nodes) if assemble_tangent and tangent_qp is not None else None
    internal_energy = fields.new_zeros(batch_size)
    young = params[:, 0]
    poisson = params[:, 1]
    hardening = params[:, 3]
    shear = young / (2.0 * (1.0 + poisson))
    bulk = young / (3.0 * (1.0 - 2.0 * poisson))
    q_points, q_weights = _quadrature(connectivity.shape[1], fields.device, fields.dtype)
    conn = connectivity.to(device=fields.device, dtype=torch.long)

    n_elements, n_element_nodes = int(conn.shape[0]), int(conn.shape[1])
    flat_conn = conn.reshape(-1)
    element_dofs = torch.stack([2 * conn, 2 * conn + 1], dim=-1).reshape(n_elements, -1)
    scatter_dofs = element_dofs.reshape(1, -1).expand(batch_size, -1)

    element_coords = coords.index_select(dim=1, index=flat_conn).reshape(batch_size, n_elements, n_element_nodes, 2)
    element_disp = fields.index_select(dim=1, index=flat_conn).reshape(batch_size, n_elements, n_element_nodes, 2)
    element_disp_flat = element_disp.reshape(batch_size, n_elements, -1)
    if correction_fields is not None:
        element_correction = correction_fields.index_select(dim=1, index=flat_conn).reshape(
            batch_size, n_elements, n_element_nodes, 2
        )
        element_correction_flat = element_correction.reshape(batch_size, n_elements, -1)
    else:
        element_correction_flat = None
    flat_element_coords = element_coords.reshape(batch_size * n_elements, n_element_nodes, 2)
    identity = torch.eye(3, device=fields.device, dtype=fields.dtype)

    for qp_index, (point, weight) in enumerate(zip(q_points, q_weights)):
        b_matrix, volume = _b_matrix_and_volume(flat_element_coords, point, weight, thickness)
        b_matrix = b_matrix.reshape(batch_size, n_elements, 3, 2 * n_element_nodes)
        volume = volume.reshape(batch_size, n_elements)
        plastic_tensor = _plastic_strain_tensor(
            _select_quadrature_values(plastic_strain, qp_index),
            batch_size,
            n_elements,
            fields.dtype,
        )
        history_point = _select_quadrature_values(material_history, qp_index)
        eqp = history_point[..., 0] if history_point.shape[-1] > 0 else fields.new_zeros(batch_size, n_elements)
        strain_voigt = torch.einsum("beij,bej->bei", b_matrix, element_disp_flat)
        if stress_qp is None:
            strain_tensor = _strain_voigt_to_tensor(strain_voigt.reshape(batch_size * n_elements, -1)).reshape(
                batch_size, n_elements, 3, 3
            )
            elastic_strain = strain_tensor - plastic_tensor
            trace = elastic_strain[..., 0, 0] + elastic_strain[..., 1, 1] + elastic_strain[..., 2, 2]
            deviator = elastic_strain - trace[..., None, None] * identity / 3.0
            stress_tensor = bulk[:, None, None, None] * trace[..., None, None] * identity + 2.0 * shear[
                :, None, None, None
            ] * deviator
            stress_voigt = torch.stack(
                [stress_tensor[..., 0, 0], stress_tensor[..., 1, 1], stress_tensor[..., 0, 1]],
                dim=-1,
            )
            elastic_energy = 0.5 * (stress_tensor * elastic_strain).sum(dim=(-1, -2))
        else:
            stress_voigt = _select_quadrature_values(stress_qp, qp_index).to(dtype=fields.dtype)
            elastic_energy = 0.5 * (stress_voigt * strain_voigt).sum(dim=-1)
        element_residual = volume[..., None] * torch.einsum("beji,bej->bei", b_matrix, stress_voigt)
        residual.scatter_add_(1, scatter_dofs, element_residual.reshape(batch_size, -1))
        hardening_energy = 0.5 * hardening[:, None] * eqp.square()
        internal_energy = internal_energy + (volume * (elastic_energy + hardening_energy)).sum(dim=1)
        if tangent_qp is not None and element_correction_flat is not None:
            tangent = _select_quadrature_values(tangent_qp, qp_index).to(dtype=fields.dtype)
            strain_increment = torch.einsum("beij,bej->bei", b_matrix, element_correction_flat)
            stress_increment = torch.einsum("beij,bej->bei", tangent, strain_increment)
            residual_increment = volume[..., None] * torch.einsum("beji,bej->bei", b_matrix, stress_increment)
            linearized_residual_increment.scatter_add_(
                1,
                scatter_dofs,
                residual_increment.reshape(batch_size, -1),
            )
        if tangent_matrix is not None:
            tangent = _select_quadrature_values(tangent_qp, qp_index).to(dtype=fields.dtype)
            element_tangent = volume[..., None, None] * torch.einsum(
                "xeia,xeij,xejc->xeac",
                b_matrix,
                tangent,
                b_matrix,
            )
            _scatter_element_tangent(tangent_matrix, element_dofs, element_tangent)
    force_work = (forcing.reshape(batch_size, -1) * fields.reshape(batch_size, -1)).sum(dim=1)
    residual = _mask_left_edge(residual, coords, n_nodes).view_as(fields)
    linearized_residual_increment = _mask_left_edge(linearized_residual_increment, coords, n_nodes).view_as(fields)
    linearized_residual = residual + linearized_residual_increment
    if tangent_matrix is not None:
        tangent_matrix = _apply_left_edge_dirichlet_to_tangent(tangent_matrix, coords, n_nodes)
    energy = internal_energy - force_work
    result = {
        "residual": residual,
        "linearized_residual": linearized_residual,
        "energy": energy,
        "residual_rms": residual.square().mean(dim=(1, 2)).sqrt(),
        "linearized_residual_rms": linearized_residual.square().mean(dim=(1, 2)).sqrt(),
    }
    if tangent_matrix is not None:
        result["tangent_matrix"] = tangent_matrix
    return result


def j2_fem_audit_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    connectivity: torch.Tensor,
    residual_weight: float = 1.0,
    energy_weight: float = 0.0,
    solver_weight: float = 0.0,
    solver_mode: str = "linearized",
    newton_damping: float = 1.0,
    newton_steps: int = 1,
    newton_line_search: bool = False,
    newton_line_search_dampings: tuple[float, ...] | None = None,
    newton_convergence_tol: float = 1.0e-3,
    tangent_regularization: float = 1.0e-6,
    every_step: bool = False,
    step_policy: str | None = None,
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    prediction = outputs["mean_sequence"]
    target = batch["fields_sequence"]
    forcing = batch["forcing_sequence"]
    plastic_key = "plastic_strain_qp_sequence" if "plastic_strain_qp_sequence" in batch else "plastic_strain_sequence"
    history_key = "material_history_qp_sequence" if "material_history_qp_sequence" in batch else "material_history_sequence"
    target_plastic = batch[plastic_key]
    target_history = batch[history_key]
    pred_plastic = _predicted_sequence(
        outputs,
        qp_key="plastic_strain_qp_sequence",
        element_key="plastic_strain_sequence",
        fallback=target_plastic,
    )
    pred_history = _predicted_sequence(
        outputs,
        qp_key="history_qp_sequence",
        element_key="history_sequence",
        fallback=target_history,
    )
    pred_stress = outputs.get("j2_qp_stress_sequence")
    pred_tangent = outputs.get("j2_qp_algorithmic_tangent_sequence")
    target_stress = batch.get("stress_sequence")
    solver_mode = solver_mode.lower().strip()
    if solver_mode not in {"linearized", "dense_newton"}:
        raise ValueError("solver_mode must be 'linearized' or 'dense_newton'")
    step_indices = _audit_step_indices(forcing, every_step=every_step, step_policy=step_policy)
    residual_terms = []
    energy_terms = []
    solver_terms = []
    newton_initial_residual_terms = []
    newton_final_residual_terms = []
    newton_residual_ratio_terms = []
    newton_residual_decrease_terms = []
    newton_step_decrease_terms = []
    newton_step_ratio_terms: dict[int, list[torch.Tensor]] = {}
    newton_step_residual_decrease_terms: dict[int, list[torch.Tensor]] = {}
    newton_correction_norm_terms = []
    newton_accepted_damping_terms = []
    newton_convergence_terms = []
    newton_failure_terms = []
    target_residual_terms = []
    path_force_scale = forcing.square().mean(dim=(1, 2, 3)).sqrt().clamp_min(eps)
    for step in step_indices:
        pred_audit = j2_fem_residual_energy(
            batch["coords"],
            batch["params"],
            prediction[:, step],
            forcing[:, step],
            connectivity,
            pred_plastic[:, step],
            pred_history[:, step],
            stress_qp=_step_value(pred_stress, step),
            tangent_qp=_step_value(pred_tangent, step),
            correction_fields=target[:, step] - prediction[:, step],
            assemble_tangent=solver_weight > 0.0 and solver_mode == "dense_newton",
        )
        target_audit = j2_fem_residual_energy(
            batch["coords"],
            batch["params"],
            target[:, step],
            forcing[:, step],
            connectivity,
            target_plastic[:, step],
            target_history[:, step],
            stress_qp=_step_value(target_stress, step),
        )
        residual_terms.append((pred_audit["residual_rms"] / path_force_scale).square().mean())
        if solver_mode == "dense_newton" and "tangent_matrix" in pred_audit:
            newton = _dense_newton_update_loss(
                pred_audit["tangent_matrix"],
                pred_audit["residual"],
                prediction[:, step],
                target[:, step],
                damping=newton_damping,
                steps=newton_steps,
                line_search=newton_line_search,
                line_search_dampings=newton_line_search_dampings,
                convergence_tol=newton_convergence_tol,
                regularization=tangent_regularization,
                eps=eps,
            )
            solver_terms.append(newton["loss"])
            newton_initial_residual_terms.append((newton["initial_residual_norm"] / path_force_scale).mean())
            newton_final_residual_terms.append((newton["final_residual_norm"] / path_force_scale).mean())
            newton_residual_ratio_terms.append(newton["residual_ratio"].mean())
            newton_residual_decrease_terms.append(newton["residual_decrease_fraction"].mean())
            newton_step_decrease_terms.append(newton["mean_step_residual_decrease_fraction"].mean())
            for step_index, value in enumerate(newton["residual_ratio_by_step"], start=1):
                newton_step_ratio_terms.setdefault(step_index, []).append(value.mean())
            for step_index, value in enumerate(newton["residual_decrease_by_step"], start=1):
                newton_step_residual_decrease_terms.setdefault(step_index, []).append(value.mean())
            newton_correction_norm_terms.append(newton["correction_relative_norm"].mean())
            newton_accepted_damping_terms.append(newton["accepted_damping"].mean())
            newton_convergence_terms.append(newton["converged"].mean())
            newton_failure_terms.append(newton["failed"].mean())
        else:
            solver_terms.append((pred_audit["linearized_residual_rms"] / path_force_scale).square().mean())
        target_residual_terms.append((target_audit["residual_rms"] / path_force_scale).mean())
        energy_scale = target_audit["energy"].detach().abs().clamp_min(eps)
        energy_terms.append(((pred_audit["energy"] - target_audit["energy"]) / energy_scale).square().mean())
    residual_loss = torch.stack(residual_terms).mean()
    energy_loss = torch.stack(energy_terms).mean()
    solver_loss = torch.stack(solver_terms).mean()
    result = {
        "fem_residual": residual_loss,
        "fem_energy": energy_loss,
        "fem_solver_linearized_residual": solver_loss,
        "target_fem_residual": torch.stack(target_residual_terms).mean(),
        "total": residual_weight * residual_loss + energy_weight * energy_loss + solver_weight * solver_loss,
    }
    if newton_initial_residual_terms:
        result.update(
            {
                "fem_newton_initial_residual": torch.stack(newton_initial_residual_terms).mean(),
                "fem_newton_final_residual": torch.stack(newton_final_residual_terms).mean(),
                "fem_newton_residual_ratio": torch.stack(newton_residual_ratio_terms).mean(),
                "fem_newton_residual_decrease_fraction": torch.stack(newton_residual_decrease_terms).mean(),
                "fem_newton_step_residual_decrease_fraction": torch.stack(newton_step_decrease_terms).mean(),
                "fem_newton_correction_relative_norm": torch.stack(newton_correction_norm_terms).mean(),
                "fem_newton_accepted_damping": torch.stack(newton_accepted_damping_terms).mean(),
                "fem_newton_convergence_rate": torch.stack(newton_convergence_terms).mean(),
                "fem_newton_failure_rate": torch.stack(newton_failure_terms).mean(),
            }
        )
        for step_index, values in sorted(newton_step_ratio_terms.items()):
            result[f"fem_newton_step{step_index}_residual_ratio"] = torch.stack(values).mean()
        for step_index, values in sorted(newton_step_residual_decrease_terms.items()):
            result[f"fem_newton_step{step_index}_residual_decrease_fraction"] = torch.stack(values).mean()
    return result


def j2_fem_training_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    connectivity: torch.Tensor,
    residual_weight: float = 1.0,
    energy_weight: float = 0.0,
    solver_weight: float = 0.0,
    solver_mode: str = "linearized",
    newton_damping: float = 1.0,
    newton_steps: int = 1,
    newton_line_search: bool = False,
    newton_line_search_dampings: tuple[float, ...] | None = None,
    newton_convergence_tol: float = 1.0e-3,
    tangent_regularization: float = 1.0e-6,
    step_policy: str = "all",
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    """Differentiable FEM residual/energy loss for path-operator training.

    This is the training-loop counterpart of :func:`j2_fem_audit_loss`.  It defaults to
    all rollout steps so residual and potential-energy consistency are optimized along
    the whole path rather than inspected only after training at selected audit steps.
    """

    return j2_fem_audit_loss(
        outputs,
        batch,
        connectivity,
        residual_weight=residual_weight,
        energy_weight=energy_weight,
        solver_weight=solver_weight,
        solver_mode=solver_mode,
        newton_damping=newton_damping,
        newton_steps=newton_steps,
        newton_line_search=newton_line_search,
        newton_line_search_dampings=newton_line_search_dampings,
        newton_convergence_tol=newton_convergence_tol,
        tangent_regularization=tangent_regularization,
        every_step=False,
        step_policy=step_policy,
        eps=eps,
    )


def _dense_newton_update_loss(
    tangent_matrix: torch.Tensor,
    residual: torch.Tensor,
    prediction: torch.Tensor,
    target: torch.Tensor,
    damping: float,
    steps: int,
    line_search: bool = False,
    line_search_dampings: tuple[float, ...] | None = None,
    convergence_tol: float = 1.0e-3,
    regularization: float = 1.0e-6,
    eps: float = 1.0e-12,
) -> dict[str, torch.Tensor]:
    batch_size = int(prediction.shape[0])
    residual_flat = residual.reshape(batch_size, -1)
    dofs = int(residual_flat.shape[-1])
    identity = torch.eye(dofs, device=tangent_matrix.device, dtype=tangent_matrix.dtype).unsqueeze(0)
    diag_scale = tangent_matrix.diagonal(dim1=-2, dim2=-1).detach().abs().mean(dim=-1).clamp_min(eps)
    regularized = tangent_matrix + float(regularization) * diag_scale[:, None, None] * identity
    residual_iter = residual_flat
    correction_total = torch.zeros_like(residual_flat)
    n_steps = max(int(steps), 1)
    initial_residual_norm = _vector_rms(residual_flat, eps)
    step_decreases = []
    step_residual_ratios = []
    step_residual_decreases = []
    correction_norms = []
    accepted_dampings = []
    damping_candidates = _newton_damping_candidates(damping, line_search, line_search_dampings, residual_flat)
    for _ in range(n_steps):
        previous_norm = _vector_rms(residual_iter, eps)
        correction = torch.linalg.solve(regularized, -residual_iter.unsqueeze(-1)).squeeze(-1)
        if line_search:
            candidate_corrections = damping_candidates[:, None, :] * correction[:, :, None]
            candidate_residuals = residual_iter[:, :, None] + torch.einsum(
                "bij,bjk->bik", tangent_matrix, candidate_corrections
            )
            candidate_norms = _vector_rms(candidate_residuals.transpose(1, 2), eps)
            best = candidate_norms.argmin(dim=-1)
            selected_damping = damping_candidates.gather(1, best[:, None]).squeeze(1)
            damped_correction = selected_damping[:, None] * correction
        else:
            selected_damping = residual_flat.new_full((batch_size,), float(damping))
            damped_correction = selected_damping[:, None] * correction
        correction_total = correction_total + damped_correction
        residual_next = residual_iter + torch.einsum("bij,bj->bi", tangent_matrix, damped_correction)
        next_norm = _vector_rms(residual_next, eps)
        step_decreases.append((previous_norm - next_norm) / previous_norm.clamp_min(eps))
        step_residual_ratios.append(next_norm / initial_residual_norm.clamp_min(eps))
        step_residual_decreases.append((initial_residual_norm - next_norm) / initial_residual_norm.clamp_min(eps))
        correction_norms.append(_vector_rms(damped_correction, eps))
        accepted_dampings.append(selected_damping)
        residual_iter = residual_next
    corrected = prediction + correction_total.reshape_as(prediction)
    error = corrected - target
    scale = target.detach().square().mean(dim=(1, 2)).sqrt().clamp_min(eps)
    final_residual_norm = _vector_rms(residual_iter, eps)
    residual_ratio = final_residual_norm / initial_residual_norm.clamp_min(eps)
    residual_decrease = (initial_residual_norm - final_residual_norm) / initial_residual_norm.clamp_min(eps)
    correction_relative_norm = _vector_rms(correction_total, eps) / scale
    return {
        "loss": (error.square().mean(dim=(1, 2)) / scale.square()).mean(),
        "initial_residual_norm": initial_residual_norm,
        "final_residual_norm": final_residual_norm,
        "residual_ratio": residual_ratio,
        "residual_decrease_fraction": residual_decrease,
        "mean_step_residual_decrease_fraction": torch.stack(step_decreases, dim=0).mean(dim=0),
        "residual_ratio_by_step": torch.stack(step_residual_ratios, dim=0),
        "residual_decrease_by_step": torch.stack(step_residual_decreases, dim=0),
        "correction_relative_norm": correction_relative_norm,
        "accepted_damping": torch.stack(accepted_dampings, dim=0).mean(dim=0),
        "converged": (residual_ratio <= float(convergence_tol)).to(dtype=prediction.dtype),
        "failed": (final_residual_norm > initial_residual_norm).to(dtype=prediction.dtype),
        "mean_step_correction_norm": torch.stack(correction_norms, dim=0).mean(dim=0),
    }


def _newton_damping_candidates(
    damping: float,
    line_search: bool,
    line_search_dampings: tuple[float, ...] | None,
    like: torch.Tensor,
) -> torch.Tensor:
    if not line_search:
        values = (float(damping),)
    elif line_search_dampings:
        values = tuple(float(value) for value in line_search_dampings)
    else:
        values = (float(damping), 0.5 * float(damping), 0.25 * float(damping), 0.125 * float(damping))
    values = tuple(value for value in values if value > 0.0)
    if not values:
        values = (float(damping),)
    return like.new_tensor(values).reshape(1, -1).expand(like.shape[0], -1)


def _vector_rms(value: torch.Tensor, eps: float) -> torch.Tensor:
    return value.square().mean(dim=-1).sqrt().clamp_min(eps)


def _step_value(value: torch.Tensor | None, step: int) -> torch.Tensor | None:
    if value is None:
        return None
    if value.ndim < 2:
        raise ValueError("path sequence tensors must include a step dimension")
    return value[:, step]


def _predicted_sequence(
    outputs: dict[str, torch.Tensor],
    qp_key: str,
    element_key: str,
    fallback: torch.Tensor,
) -> torch.Tensor:
    value = outputs.get(qp_key)
    if value is None:
        value = outputs.get(element_key)
    if value is None:
        return fallback
    return value


def _audit_step_indices(
    forcing: torch.Tensor,
    every_step: bool = False,
    step_policy: str | None = None,
) -> tuple[int, ...]:
    n_steps = int(forcing.shape[1])
    if n_steps <= 0:
        raise ValueError("forcing sequence must contain at least one step")
    if every_step:
        return tuple(range(n_steps))
    policy = (step_policy or "final").lower().strip()
    if policy == "final":
        return (n_steps - 1,)
    if policy == "all":
        return tuple(range(n_steps))
    if policy not in {"reversal", "reversal_final"}:
        raise ValueError("step_policy must be final, all, reversal, or reversal_final")
    steps = set(_reversal_step_indices(forcing))
    if policy == "reversal_final" or not steps:
        steps.add(n_steps - 1)
    return tuple(sorted(steps))


def _reversal_step_indices(forcing: torch.Tensor) -> tuple[int, ...]:
    if forcing.shape[1] < 3:
        return ()
    net_force = forcing.detach().sum(dim=(0, 2))
    dominant = int(net_force.abs().sum(dim=0).argmax().item())
    signal = net_force[:, dominant]
    increments = signal[1:] - signal[:-1]
    signs = torch.sign(increments)
    reversal_steps = []
    for idx in range(1, int(signs.numel())):
        previous = float(signs[idx - 1])
        current = float(signs[idx])
        if previous == 0.0 or current == 0.0:
            continue
        if previous * current < 0.0:
            reversal_steps.append(idx)
    return tuple(reversal_steps)


def _quadrature(n_nodes_per_element: int, device: torch.device, dtype: torch.dtype) -> tuple[torch.Tensor, torch.Tensor]:
    if n_nodes_per_element == 3:
        return (
            torch.tensor([[1.0 / 3.0, 1.0 / 3.0]], device=device, dtype=dtype),
            torch.tensor([0.5], device=device, dtype=dtype),
        )
    return (
        torch.tensor(
            [[1.0 / 6.0, 1.0 / 6.0], [2.0 / 3.0, 1.0 / 6.0], [1.0 / 6.0, 2.0 / 3.0]],
            device=device,
            dtype=dtype,
        ),
        torch.tensor([1.0 / 6.0, 1.0 / 6.0, 1.0 / 6.0], device=device, dtype=dtype),
    )


def _b_matrix_and_volume(
    element_coords: torch.Tensor,
    point: torch.Tensor,
    weight: torch.Tensor,
    thickness: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    if element_coords.shape[1] == 3:
        return _t3_b_matrix_and_volume(element_coords, weight, thickness)
    return _t6_b_matrix_and_volume(element_coords, point, weight, thickness)


def _t3_b_matrix_and_volume(
    element_coords: torch.Tensor,
    weight: torch.Tensor,
    thickness: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    x1, y1 = element_coords[:, 0, 0], element_coords[:, 0, 1]
    x2, y2 = element_coords[:, 1, 0], element_coords[:, 1, 1]
    x3, y3 = element_coords[:, 2, 0], element_coords[:, 2, 1]
    twice_area = ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)).clamp_min(1.0e-12)
    b = torch.stack([y2 - y3, y3 - y1, y1 - y2], dim=-1)
    c = torch.stack([x3 - x2, x1 - x3, x2 - x1], dim=-1)
    b_matrix = _make_b_matrix(b / twice_area.unsqueeze(-1), c / twice_area.unsqueeze(-1))
    return b_matrix, twice_area * weight * thickness


def _t6_b_matrix_and_volume(
    element_coords: torch.Tensor,
    point: torch.Tensor,
    weight: torch.Tensor,
    thickness: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    d_shape_ref = _t6_shape_gradients(point, element_coords.dtype, element_coords.device)
    jacobian = torch.einsum("na,bnd->bad", d_shape_ref, element_coords)
    det_j = torch.linalg.det(jacobian).clamp_min(1.0e-12)
    grad = torch.einsum("na,bad->bnd", d_shape_ref, torch.linalg.inv(jacobian))
    b_matrix = _make_b_matrix(grad[..., 0], grad[..., 1])
    return b_matrix, det_j * weight * thickness


def _t6_shape_gradients(point: torch.Tensor, dtype: torch.dtype, device: torch.device) -> torch.Tensor:
    r, s = point[0], point[1]
    l1 = 1.0 - r - s
    l2 = r
    l3 = s
    return torch.stack(
        [
            torch.stack([-(4.0 * l1 - 1.0), -(4.0 * l1 - 1.0)]),
            torch.stack([4.0 * l2 - 1.0, torch.zeros((), device=device, dtype=dtype)]),
            torch.stack([torch.zeros((), device=device, dtype=dtype), 4.0 * l3 - 1.0]),
            torch.stack([4.0 * (l1 - l2), -4.0 * l2]),
            torch.stack([4.0 * l3, 4.0 * l2]),
            torch.stack([-4.0 * l3, 4.0 * (l1 - l3)]),
        ]
    ).to(device=device, dtype=dtype)


def _make_b_matrix(dnx: torch.Tensor, dny: torch.Tensor) -> torch.Tensor:
    batch_size, n_elem_nodes = dnx.shape
    b_matrix = dnx.new_zeros(batch_size, 3, 2 * n_elem_nodes)
    b_matrix[:, 0, 0::2] = dnx
    b_matrix[:, 1, 1::2] = dny
    b_matrix[:, 2, 0::2] = dny
    b_matrix[:, 2, 1::2] = dnx
    return b_matrix


def _element_dofs(tri: torch.Tensor) -> torch.Tensor:
    return torch.stack([2 * tri, 2 * tri + 1], dim=-1).reshape(-1)


def _scatter_element_tangent(
    tangent_matrix: torch.Tensor,
    element_dofs: torch.Tensor,
    element_tangent: torch.Tensor,
) -> None:
    for element_index in range(int(element_dofs.shape[0])):
        dofs = element_dofs[element_index]
        tangent_matrix[:, dofs[:, None], dofs[None, :]] += element_tangent[:, element_index]


def _mask_left_edge(residual: torch.Tensor, coords: torch.Tensor, n_nodes: int) -> torch.Tensor:
    min_x = coords[:, :, 0].amin(dim=1, keepdim=True)
    fixed = (coords[:, :, 0] - min_x).abs() <= 1.0e-6
    mask = torch.stack([fixed, fixed], dim=-1).reshape(coords.shape[0], 2 * n_nodes)
    return residual.masked_fill(mask, 0.0)


def _apply_left_edge_dirichlet_to_tangent(
    tangent_matrix: torch.Tensor,
    coords: torch.Tensor,
    n_nodes: int,
) -> torch.Tensor:
    min_x = coords[:, :, 0].amin(dim=1, keepdim=True)
    fixed_nodes = (coords[:, :, 0] - min_x).abs() <= 1.0e-6
    fixed = torch.stack([fixed_nodes, fixed_nodes], dim=-1).reshape(coords.shape[0], 2 * n_nodes)
    constrained = fixed[:, :, None] | fixed[:, None, :]
    tangent_matrix = tangent_matrix.masked_fill(constrained, 0.0)
    diag = torch.arange(2 * n_nodes, device=tangent_matrix.device)
    tangent_matrix[:, diag, diag] = torch.where(
        fixed,
        torch.ones_like(tangent_matrix[:, diag, diag]),
        tangent_matrix[:, diag, diag],
    )
    return tangent_matrix


def _select_quadrature_value(value: torch.Tensor, qp_index: int) -> torch.Tensor:
    if value.ndim == 3:
        return value[:, min(qp_index, value.shape[1] - 1)]
    if value.ndim == 2:
        return value
    raise ValueError("quadrature history must have shape [batch, channels] or [batch, q_points, channels]")


def _select_quadrature_values(value: torch.Tensor, qp_index: int) -> torch.Tensor:
    if value.ndim == 5:
        return value[:, :, min(qp_index, value.shape[2] - 1)]
    if value.ndim == 4:
        return value[:, :, min(qp_index, value.shape[2] - 1)]
    if value.ndim == 3:
        return value
    raise ValueError("quadrature history must have shape [batch, elements, channels] or [batch, elements, q_points, channels]")


def _plastic_strain_tensor(
    value: torch.Tensor,
    batch_size: int,
    n_elements: int,
    dtype: torch.dtype,
) -> torch.Tensor:
    if value.ndim >= 4 and value.shape[-2:] == (3, 3):
        return value.to(dtype=dtype)
    return _history_voigt_to_tensor(value.reshape(batch_size * n_elements, -1), dtype).reshape(
        batch_size, n_elements, 3, 3
    )


def _history_voigt_to_tensor(plastic_strain: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
    value = plastic_strain.to(dtype=dtype)
    tensor = value.new_zeros(value.shape[0], 3, 3)
    tensor[:, 0, 0] = value[:, 0]
    tensor[:, 1, 1] = value[:, 1]
    if value.shape[-1] >= 3:
        tensor[:, 2, 2] = value[:, 2]
    if value.shape[-1] >= 4:
        tensor[:, 0, 1] = value[:, 3]
        tensor[:, 1, 0] = value[:, 3]
    return tensor


def _strain_voigt_to_tensor(strain: torch.Tensor) -> torch.Tensor:
    tensor = strain.new_zeros(strain.shape[0], 3, 3)
    tensor[:, 0, 0] = strain[:, 0]
    tensor[:, 1, 1] = strain[:, 1]
    tensor[:, 0, 1] = 0.5 * strain[:, 2]
    tensor[:, 1, 0] = 0.5 * strain[:, 2]
    return tensor


def _trace(tensor: torch.Tensor) -> torch.Tensor:
    return tensor[:, 0, 0] + tensor[:, 1, 1] + tensor[:, 2, 2]


def _deviator(tensor: torch.Tensor) -> torch.Tensor:
    identity = torch.eye(3, device=tensor.device, dtype=tensor.dtype)
    return tensor - _trace(tensor).view(-1, 1, 1) * identity / 3.0
