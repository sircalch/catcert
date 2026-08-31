"""
Multi-metric certification scoring, slab quality assessment, and report aggregation for CatCert.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import numpy as np

from catcert.core.surface_energy import SurfaceEnergyResult, calculate_surface_energy_convergence
from catcert.core.vacuum_potential import VacuumPotentialResult, calculate_vacuum_potential_profile
from catcert.core.dipole_correction import DipoleAuditResult, calculate_dipole_correction_audit
from catcert.core.adsorption_energy import AdsorptionEnergyResult, calculate_adsorption_energy


@dataclass
class SlabQualityReport:
    overall_status: str  # 'PASS', 'WARNING', 'FAIL'
    validation_score: str
    metadata: Dict[str, Any]
    surface_energy: Optional[SurfaceEnergyResult]
    vacuum_potential: Optional[VacuumPotentialResult]
    dipole_audit: Optional[DipoleAuditResult]
    adsorption_energy: Optional[AdsorptionEnergyResult]
    recommendations: List[str]
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def assess_slab_quality(
    metadata: Dict[str, Any],
    surface_energy_res: Optional[SurfaceEnergyResult] = None,
    vacuum_res: Optional[VacuumPotentialResult] = None,
    dipole_res: Optional[DipoleAuditResult] = None,
    adsorption_res: Optional[AdsorptionEnergyResult] = None
) -> SlabQualityReport:
    """
    Consolidates heterogeneous catalysis and DFT surface slab validation results.

    Parameters
    ----------
    metadata : dict
        Surface facet (e.g. Pt(111), TiO2(101)), functional (PBE-D3), software (VASP, QE).
    surface_energy_res : SurfaceEnergyResult, optional
    vacuum_res : VacuumPotentialResult, optional
    dipole_res : DipoleAuditResult, optional
    adsorption_res : AdsorptionEnergyResult, optional

    Returns
    -------
    report : SlabQualityReport
    """
    statuses = []
    recommendations = []

    if surface_energy_res is not None:
        statuses.append(surface_energy_res.status)
        if surface_energy_res.status != "PASS":
            recommendations.append(surface_energy_res.diagnostic_message)

    if vacuum_res is not None:
        statuses.append(vacuum_res.status)
        if vacuum_res.status != "PASS":
            recommendations.append(vacuum_res.diagnostic_message)

    if dipole_res is not None:
        statuses.append(dipole_res.status)
        if dipole_res.status != "PASS":
            recommendations.append(dipole_res.diagnostic_message)

    if adsorption_res is not None:
        statuses.append(adsorption_res.status)
        if adsorption_res.status != "PASS":
            recommendations.append(adsorption_res.diagnostic_message)

    if not statuses:
        overall_status = "PASS"
        validation_score = "SURFACE SLAB AUDIT = UNVERIFIED"
    elif "FAIL" in statuses:
        overall_status = "FAIL"
        validation_score = "SURFACE SLAB AUDIT = FAILED / CRITICAL ARTIFACTS DETECTED"
    elif "WARNING" in statuses:
        overall_status = "WARNING"
        validation_score = "SURFACE SLAB AUDIT = ACCEPTABLE WITH METHODOLOGICAL WARNINGS"
    else:
        overall_status = "PASS"
        validation_score = "SURFACE SLAB AUDIT = FULLY CONVERGED (PUBLICATION GRADE)"

    return SlabQualityReport(
        overall_status=overall_status,
        validation_score=validation_score,
        metadata=metadata,
        surface_energy=surface_energy_res,
        vacuum_potential=vacuum_res,
        dipole_audit=dipole_res,
        adsorption_energy=adsorption_res,
        recommendations=recommendations,
        provenance={
            "tool": "CatCert",
            "version": "1.0.0",
            "citation": "Monreal-Hernández, A. (2026). CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs."
        }
    )
