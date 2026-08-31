"""
CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction,
and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs.
"""

__version__ = "1.0.0"
__author__ = "Andre Monreal-Hernández"
__license__ = "MIT"

from catcert.core.surface_energy import calculate_surface_energy_convergence, SurfaceEnergyResult
from catcert.core.vacuum_potential import calculate_vacuum_potential_profile, VacuumPotentialResult
from catcert.core.dipole_correction import calculate_dipole_correction_audit, DipoleAuditResult
from catcert.core.adsorption_energy import calculate_adsorption_energy, AdsorptionEnergyResult
from catcert.core.scoring import assess_slab_quality, SlabQualityReport

__all__ = [
    "__version__",
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
