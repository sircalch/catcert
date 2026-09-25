"""
Surface energy calculation, layer thickness convergence, and Fiorentini-Methfessel regression.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# Physical constants
EV_PER_ANG2_TO_J_PER_M2 = 16.02176634  # 1 eV/Å^2 = 16.02176634 J/m^2
EV_TO_MEV = 1000.0
# Typical range of surface energies for solid surfaces (soft/molecular crystals ~0.05, refractory metals ~4-5 J/m^2)
GAMMA_PLAUSIBLE_MIN_J_M2 = 0.05
GAMMA_PLAUSIBLE_MAX_J_M2 = 5.0


@dataclass
class SlabLayerPoint:
    n_layers: int
    n_atoms: int
    energy_ev: float
    surface_energy_j_m2: float
    surface_energy_mev_ang2: float
    delta_gamma_j_m2: Optional[float]


@dataclass
class SurfaceEnergyResult:
    is_symmetric: bool
    surface_area_ang2: float
    bulk_energy_per_atom_ev: float
    converged_gamma_j_m2: float
    converged_gamma_mev_ang2: float
    fiorentini_methfessel_gamma_j_m2: Optional[float]
    fiorentini_methfessel_e_bulk_ev: Optional[float]
    layer_points: List[SlabLayerPoint]
    is_converged: bool
    final_delta_gamma_j_m2: float
    status: str  # 'PASS', 'WARNING', 'FAIL'
    diagnostic_message: str


def calculate_surface_energy_convergence(
    slab_energies_ev: List[float],
    n_atoms_list: List[int],
    layer_counts: List[int],
    surface_area_ang2: float,
    bulk_energy_per_atom_ev: Optional[float] = None,
    is_symmetric: bool = True,
    convergence_threshold_j_m2: float = 0.015,  # ~1 meV/Å^2
    warning_threshold_j_m2: float = 0.035
) -> SurfaceEnergyResult:
    """
    Computes surface energy gamma and audits slab thickness convergence as a function of layer count.
    Also fits the Fiorentini-Methfessel linear regression E_slab(N) = 2*A*gamma + N*E_bulk.

    Parameters
    ----------
    slab_energies_ev : list of float
        Total energies of slabs with varying layer counts (eV).
    n_atoms_list : list of int
        Number of atoms / formula units in each slab.
    layer_counts : list of int
        Number of layers for each calculation (e.g. [3, 4, 5, 6]).
    surface_area_ang2 : float
        Surface cross-sectional area (A = |a x b|) in Å^2.
    bulk_energy_per_atom_ev : float, optional
        Reference energy per atom from bulk crystal calculation (eV).
    is_symmetric : bool, default True
        Whether the slab has two identical relaxed top and bottom surfaces (factor 2).
    convergence_threshold_j_m2 : float, default 0.015 J/m^2
    warning_threshold_j_m2 : float, default 0.035 J/m^2

    Returns
    -------
    result : SurfaceEnergyResult
    """
    if len(slab_energies_ev) != len(n_atoms_list) or len(slab_energies_ev) != len(layer_counts):
        raise ValueError("Lengths of slab_energies_ev, n_atoms_list, and layer_counts must match.")

    n_slabs = len(slab_energies_ev)
    surface_factor = 2.0 if is_symmetric else 1.0

    # 1. Fiorentini-Methfessel Linear Fit: E_slab(N) = Intercept + Slope * N
    # Slope = E_bulk, Intercept = surface_factor * A * gamma_FM
    fm_gamma_j = None
    fm_e_bulk = None
    if n_slabs >= 3:
        n_arr = np.asarray(n_atoms_list, dtype=float)
        e_arr = np.asarray(slab_energies_ev, dtype=float)
        # Linear regression
        poly = np.polyfit(n_arr, e_arr, 1)
        fm_e_bulk = float(poly[0])
        intercept = float(poly[1])
        # gamma_FM in eV/Å^2
        fm_gamma_ev = intercept / (surface_factor * surface_area_ang2)
        fm_gamma_j = float(fm_gamma_ev * EV_PER_ANG2_TO_J_PER_M2)

    # Use provided bulk energy if given, else use FM fitted bulk energy
    e_bulk_ref = bulk_energy_per_atom_ev if bulk_energy_per_atom_ev is not None else (fm_e_bulk if fm_e_bulk is not None else 0.0)

    # 2. Pointwise Surface Energy: gamma = (E_slab - N * E_bulk) / (surface_factor * A)
    layer_points: List[SlabLayerPoint] = []
    prev_gamma = None
    final_delta = 0.0

    for i in range(n_slabs):
        e_slab = slab_energies_ev[i]
        n_at = n_atoms_list[i]
        n_lay = layer_counts[i]

        gamma_ev_ang2 = (e_slab - n_at * e_bulk_ref) / (surface_factor * surface_area_ang2)
        gamma_j_m2 = float(gamma_ev_ang2 * EV_PER_ANG2_TO_J_PER_M2)
        gamma_mev_ang2 = float(gamma_ev_ang2 * EV_TO_MEV)

        delta_g = None
        if prev_gamma is not None:
            delta_g = float(abs(gamma_j_m2 - prev_gamma))
            final_delta = delta_g

        layer_points.append(SlabLayerPoint(
            n_layers=n_lay,
            n_atoms=n_at,
            energy_ev=e_slab,
            surface_energy_j_m2=gamma_j_m2,
            surface_energy_mev_ang2=gamma_mev_ang2,
            delta_gamma_j_m2=delta_g
        ))
        prev_gamma = gamma_j_m2

    converged_gamma_j = layer_points[-1].surface_energy_j_m2
    converged_gamma_mev = layer_points[-1].surface_energy_mev_ang2

    # 3. Decision
    if bulk_energy_per_atom_ev is None and fm_e_bulk is None:
        is_conv = False
        status = "FAIL"
        diag = "No bulk reference energy available (provide bulk_energy_per_atom_ev or >= 3 slab thicknesses for the Fiorentini-Methfessel fit); surface energy is undefined."
    elif converged_gamma_j <= 0.0:
        is_conv = False
        status = "FAIL"
        diag = f"Non-physical surface energy (gamma = {converged_gamma_j:.3f} J/m^2 <= 0). Check the bulk reference energy and that slab/bulk use identical settings."
    elif not (GAMMA_PLAUSIBLE_MIN_J_M2 <= converged_gamma_j <= GAMMA_PLAUSIBLE_MAX_J_M2):
        is_conv = False
        status = "WARNING"
        diag = f"Surface energy gamma = {converged_gamma_j:.3f} J/m^2 lies outside the typical range for solid surfaces ({GAMMA_PLAUSIBLE_MIN_J_M2}-{GAMMA_PLAUSIBLE_MAX_J_M2} J/m^2). Verify the bulk reference, surface area, and symmetric/asymmetric slab factor."
    elif n_slabs < 2:
        is_conv = False
        status = "WARNING"
        diag = f"Single slab thickness evaluated: gamma = {converged_gamma_j:.3f} J/m^2 ({converged_gamma_mev:.1f} meV/Å^2). Layer convergence cannot be assessed from one thickness."
    elif final_delta <= convergence_threshold_j_m2:
        is_conv = True
        status = "PASS"
        diag = f"Surface energy well-converged with respect to slab thickness (|Delta gamma| = {final_delta:.4f} <= {convergence_threshold_j_m2:.3f} J/m^2). Final gamma = {converged_gamma_j:.3f} J/m^2."
    elif final_delta <= warning_threshold_j_m2:
        is_conv = False
        status = "WARNING"
        diag = f"Surface energy moderately oscillating (|Delta gamma| = {final_delta:.4f} J/m^2). Additional atomic layers recommended for high-precision kinetics."
    else:
        is_conv = False
        status = "FAIL"
        diag = f"Surface energy NOT converged across tested slab layers (|Delta gamma| = {final_delta:.4f} > {warning_threshold_j_m2:.3f} J/m^2). Slab is too thin (quantum confinement or top/bottom coupling)."

    return SurfaceEnergyResult(
        is_symmetric=is_symmetric,
        surface_area_ang2=surface_area_ang2,
        bulk_energy_per_atom_ev=e_bulk_ref,
        converged_gamma_j_m2=converged_gamma_j,
        converged_gamma_mev_ang2=converged_gamma_mev,
        fiorentini_methfessel_gamma_j_m2=fm_gamma_j,
        fiorentini_methfessel_e_bulk_ev=fm_e_bulk,
        layer_points=layer_points,
        is_converged=is_conv,
        final_delta_gamma_j_m2=final_delta,
        status=status,
        diagnostic_message=diag
    )
