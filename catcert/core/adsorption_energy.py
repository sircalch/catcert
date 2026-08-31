"""
Adsorption energy calculation, zero-point energy (ZPE) correction, and dispersion audit.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class AdsorptionEnergyResult:
    adsorbate_name: str
    e_total_slab_adsorbate_ev: float
    e_clean_slab_ev: float
    e_gas_molecule_ev: float
    e_adsorption_ev: float
    e_adsorption_kcal_mol: float
    zpe_correction_ev: Optional[float]
    e_adsorption_zpe_ev: Optional[float]
    dispersion_method: Optional[str]
    is_dispersion_included: bool
    status: str  # 'PASS', 'WARNING', 'FAIL'
    diagnostic_message: str


EV_TO_KCAL_MOL = 23.06054887


def calculate_adsorption_energy(
    adsorbate_name: str,
    e_slab_adsorbate_ev: float,
    e_clean_slab_ev: float,
    e_gas_ev: float,
    zpe_correction_ev: Optional[float] = None,
    dispersion_method: Optional[str] = None
) -> AdsorptionEnergyResult:
    """
    Computes adsorption energy E_ads = E_total - (E_clean + E_gas),
    applies optional ZPE corrections, and checks dispersion corrections.

    Parameters
    ----------
    adsorbate_name : str (e.g. 'CO', 'OH*', 'H2O', 'O*')
    e_slab_adsorbate_ev : float
        Total energy of slab with adsorbate (eV).
    e_clean_slab_ev : float
        Total energy of clean bare surface slab (eV).
    e_gas_ev : float
        Energy of isolated gas-phase molecule / radical in box (eV).
    zpe_correction_ev : float, optional
        Delta ZPE = ZPE_ads - ZPE_gas (eV).
    dispersion_method : str, optional (e.g. 'D3-BJ', 'D4', 'vdW-DF2', 'None')

    Returns
    -------
    result : AdsorptionEnergyResult
    """
    e_ads_ev = float(e_slab_adsorbate_ev - (e_clean_slab_ev + e_gas_ev))
    e_ads_kcal = float(e_ads_ev * EV_TO_KCAL_MOL)

    e_ads_zpe = None
    if zpe_correction_ev is not None:
        e_ads_zpe = float(e_ads_ev + zpe_correction_ev)

    is_disp = False
    if dispersion_method and dispersion_method.lower() not in ["none", "false", "no", ""]:
        is_disp = True

    # Audit logic
    if not is_disp:
        status = "WARNING"
        diag = f"Adsorption energy calculated without dispersion correction (E_ads = {e_ads_ev:.3f} eV / {e_ads_kcal:.2f} kcal/mol). GGA functionals without vdW typically underbind physisorbed and weakly chemisorbed species by 0.2-0.6 eV."
    else:
        status = "PASS"
        disp_str = f"with {dispersion_method}"
        diag = f"Adsorption energy rigorously evaluated {disp_str} (E_ads = {e_ads_ev:.3f} eV / {e_ads_kcal:.2f} kcal/mol)."

    return AdsorptionEnergyResult(
        adsorbate_name=adsorbate_name,
        e_total_slab_adsorbate_ev=e_slab_adsorbate_ev,
        e_clean_slab_ev=e_clean_slab_ev,
        e_gas_molecule_ev=e_gas_ev,
        e_adsorption_ev=e_ads_ev,
        e_adsorption_kcal_mol=e_ads_kcal,
        zpe_correction_ev=zpe_correction_ev,
        e_adsorption_zpe_ev=e_ads_zpe,
        dispersion_method=dispersion_method,
        is_dispersion_included=is_disp,
        status=status,
        diagnostic_message=diag
    )
