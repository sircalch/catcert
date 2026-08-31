"""
Planar electrostatic potential profile V(z), vacuum thickness audit, flatness, and work function.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class VacuumPotentialResult:
    z_coordinates_ang: List[float]
    potential_ev: List[float]
    cell_height_c_ang: float
    slab_thickness_ang: float
    vacuum_thickness_ang: float
    vacuum_plateau_potential_ev: float
    vacuum_flatness_delta_ev: float
    e_fermi_ev: Optional[float]
    work_function_ev: Optional[float]
    status: str  # 'PASS', 'WARNING', 'FAIL'
    diagnostic_message: str


def calculate_vacuum_potential_profile(
    z_grid_ang: np.ndarray,
    v_planar_ev: np.ndarray,
    atomic_z_positions_ang: List[float],
    e_fermi_ev: Optional[float] = None,
    min_vacuum_thickness_ang: float = 12.0,
    max_vacuum_flatness_ev: float = 0.05
) -> VacuumPotentialResult:
    """
    Analyzes planar averaged electrostatic potential profile V(z), calculates
    vacuum thickness, checks vacuum potential flatness, and derives the work function Phi.

    Parameters
    ----------
    z_grid_ang : np.ndarray
        z coordinates along the surface normal (Å).
    v_planar_ev : np.ndarray
        Planar average electrostatic potential V(z) in eV.
    atomic_z_positions_ang : list of float
        z coordinates of all atoms in the slab to locate slab boundaries.
    e_fermi_ev : float, optional
        Fermi energy from DFT calculation (eV).
    min_vacuum_thickness_ang : float, default 12.0 Å
    max_vacuum_flatness_ev : float, default 0.05 eV

    Returns
    -------
    result : VacuumPotentialResult
    """
    z_arr = np.asarray(z_grid_ang, dtype=float)
    v_arr = np.asarray(v_planar_ev, dtype=float)
    c_length = float(np.max(z_arr) - np.min(z_arr))

    # Slab boundaries along z
    z_min_atom = float(np.min(atomic_z_positions_ang))
    z_max_atom = float(np.max(atomic_z_positions_ang))
    slab_thick = float(z_max_atom - z_min_atom)
    vac_thick = float(c_length - slab_thick)

    # Locate vacuum region: points sufficiently far from any atom (> 3.5 Å away)
    # or center of vacuum
    vac_mask = (z_arr < (z_min_atom - 2.5)) | (z_arr > (z_max_atom + 2.5))
    if np.sum(vac_mask) < 5:
        # Wrap-around boundary handling
        z_mid_vac = (z_max_atom + c_length + z_min_atom) / 2.0
        if z_mid_vac > c_length:
            z_mid_vac -= c_length
        vac_mask = np.abs(z_arr - z_mid_vac) < (vac_thick / 4.0)

    if np.sum(vac_mask) >= 3:
        v_vac_pts = v_arr[vac_mask]
        v_vac_level = float(np.median(v_vac_pts))
        # Flatness: peak-to-peak variation in the middle 50% of vacuum
        delta_v_vac = float(np.max(v_vac_pts) - np.min(v_vac_pts))
    else:
        v_vac_level = float(np.max(v_arr))
        delta_v_vac = 0.0

    # Work Function: Phi = V_vac - E_Fermi
    work_func = None
    if e_fermi_ev is not None:
        work_func = float(v_vac_level - e_fermi_ev)

    # Audit & certification decision
    if vac_thick < min_vacuum_thickness_ang:
        status = "FAIL"
        diag = f"Vacuum spacing is insufficient ({vac_thick:.1f} Å < {min_vacuum_thickness_ang:.1f} Å). High risk of periodic image interactions across the vacuum gap."
    elif delta_v_vac > max_vacuum_flatness_ev:
        status = "WARNING"
        diag = f"Vacuum potential has uncorrected slope/curvature (Delta V_vac = {delta_v_vac:.3f} eV > {max_vacuum_flatness_ev:.3f} eV). Dipole correction or larger vacuum recommended."
    else:
        status = "PASS"
        phi_str = f", Work Function Phi = {work_func:.2f} eV" if work_func is not None else ""
        diag = f"Vacuum region is well-isolated ({vac_thick:.1f} Å >= {min_vacuum_thickness_ang:.1f} Å) with flat plateau (Delta V_vac = {delta_v_vac:.4f} eV{phi_str})."

    return VacuumPotentialResult(
        z_coordinates_ang=z_arr.tolist(),
        potential_ev=v_arr.tolist(),
        cell_height_c_ang=c_length,
        slab_thickness_ang=slab_thick,
        vacuum_thickness_ang=vac_thick,
        vacuum_plateau_potential_ev=v_vac_level,
        vacuum_flatness_delta_ev=delta_v_vac,
        e_fermi_ev=e_fermi_ev,
        work_function_ev=work_func,
        status=status,
        diagnostic_message=diag
    )
