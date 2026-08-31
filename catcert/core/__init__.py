"""
Core surface science algorithms, potential profiles, and convergence metrics for CatCert.
"""

from catcert.core.surface_energy import calculate_surface_energy_convergence, SurfaceEnergyResult
from catcert.core.vacuum_potential import calculate_vacuum_potential_profile, VacuumPotentialResult
from catcert.core.dipole_correction import calculate_dipole_correction_audit, DipoleAuditResult
from catcert.core.adsorption_energy import calculate_adsorption_energy, AdsorptionEnergyResult
from catcert.core.scoring import assess_slab_quality, SlabQualityReport

__all__ = [
    "calculate_surface_energy_convergence",
    "SurfaceEnergyResult",
    "calculate_vacuum_potential_profile",
    "VacuumPotentialResult",
    "calculate_dipole_correction_audit",
    "DipoleAuditResult",
    "calculate_adsorption_energy",
    "AdsorptionEnergyResult",
    "assess_slab_quality",
    "SlabQualityReport"
]
