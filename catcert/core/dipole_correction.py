"""
Asymmetric slab electrostatic dipole audit, work function offset Delta Phi, and correction verification.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class DipoleAuditResult:
    is_dipole_correction_enabled: bool
    is_asymmetric_slab: bool
    dipole_moment_debye: Optional[float]
    top_vacuum_potential_ev: float
    bottom_vacuum_potential_ev: float
    work_function_top_ev: Optional[float]
    work_function_bottom_ev: Optional[float]
    delta_work_function_ev: float  # |Phi_top - Phi_bottom|
    status: str  # 'PASS', 'WARNING', 'FAIL'
    diagnostic_message: str


def calculate_dipole_correction_audit(
    top_v_vac_ev: float,
    bottom_v_vac_ev: float,
    e_fermi_ev: Optional[float] = None,
    dipole_moment_debye: Optional[float] = None,
    is_dipole_correction_enabled: bool = False,
    is_asymmetric_slab: bool = True,
    max_tolerated_delta_phi_ev: float = 0.10
) -> DipoleAuditResult:
    """
    Audits work function asymmetry and verifies dipole correction for asymmetric surface slabs.

    Parameters
    ----------
    top_v_vac_ev : float
        Electrostatic potential at the top vacuum boundary (eV).
    bottom_v_vac_ev : float
        Electrostatic potential at the bottom vacuum boundary (eV).
    e_fermi_ev : float, optional
        Fermi energy from DFT calculation (eV).
    dipole_moment_debye : float, optional
        Total dipole moment along z in Debye (or e*Å).
    is_dipole_correction_enabled : bool, default False
        Whether dipole correction (e.g. LDIPOL=TRUE in VASP, dipfield=true in QE) was activated.
    is_asymmetric_slab : bool, default True
    max_tolerated_delta_phi_ev : float, default 0.10 eV

    Returns
    -------
    result : DipoleAuditResult
    """
    delta_phi = float(abs(top_v_vac_ev - bottom_v_vac_ev))

    phi_top = float(top_v_vac_ev - e_fermi_ev) if e_fermi_ev is not None else None
    phi_bot = float(bottom_v_vac_ev - e_fermi_ev) if e_fermi_ev is not None else None

    # Audit logic
    if not is_asymmetric_slab:
        status = "PASS"
        diag = f"Symmetric slab geometry: top/bottom vacuum potentials match (|Delta Phi| = {delta_phi:.3f} eV). Dipole correction is not required."
    elif is_dipole_correction_enabled:
        if delta_phi <= max_tolerated_delta_phi_ev:
            status = "PASS"
            diag = f"Dipole correction active: electrostatic step compensated (|Delta Phi| = {delta_phi:.3f} eV <= {max_tolerated_delta_phi_ev:.2f} eV). Validated work functions."
        else:
            status = "WARNING"
            diag = f"Dipole correction active, but residual potential step observed (|Delta Phi| = {delta_phi:.3f} eV). Check dipole center placement (DIPOL)."
    else:
        # Asymmetric slab without dipole correction
        if delta_phi > max_tolerated_delta_phi_ev:
            status = "FAIL"
            diag = f"Spurious dipole field detected! Asymmetric slab without dipole correction shows |Delta Phi| = {delta_phi:.3f} eV > {max_tolerated_delta_phi_ev:.2f} eV. Adsorption energies and barrier heights may have severe periodic artifact errors."
        else:
            status = "PASS"
            diag = f"Asymmetric slab with negligible dipole moment (|Delta Phi| = {delta_phi:.3f} eV <= {max_tolerated_delta_phi_ev:.2f} eV)."

    return DipoleAuditResult(
        is_dipole_correction_enabled=is_dipole_correction_enabled,
        is_asymmetric_slab=is_asymmetric_slab,
        dipole_moment_debye=dipole_moment_debye,
        top_vacuum_potential_ev=top_v_vac_ev,
        bottom_vacuum_potential_ev=bottom_v_vac_ev,
        work_function_top_ev=phi_top,
        work_function_bottom_ev=phi_bot,
        delta_work_function_ev=delta_phi,
        status=status,
        diagnostic_message=diag
    )
