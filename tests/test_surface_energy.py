"""
Tests for surface energy calculation and slab layer convergence.
"""

import numpy as np
import pytest
from catcert.core.surface_energy import calculate_surface_energy_convergence


def test_surface_energy_convergence_pass():
    # 3, 4, 5, 6 layer slabs with perfect asymptotic slope
    e_bulk = -6.00
    area = 25.0
    layers = [3, 4, 5, 6]
    n_atoms = [12, 16, 20, 24]
    
    # 2*A*gamma = 5.0 eV (gamma = 5.0 / (2*25) = 0.1 eV/Å^2 = 1.602 J/m^2)
    slab_energies = [
        12 * e_bulk + 5.000,
        16 * e_bulk + 5.002,
        20 * e_bulk + 5.001,
        24 * e_bulk + 5.000
    ]

    res = calculate_surface_energy_convergence(
        slab_energies_ev=slab_energies,
        n_atoms_list=n_atoms,
        layer_counts=layers,
        surface_area_ang2=area,
        bulk_energy_per_atom_ev=e_bulk,
        is_symmetric=True
    )

    assert res.is_converged is True
    assert res.status == "PASS"
    assert np.isclose(res.converged_gamma_j_m2, 1.602, atol=0.01)
    assert res.final_delta_gamma_j_m2 < 0.015


def test_surface_energy_convergence_fail():
    e_bulk = -6.00
    area = 25.0
    layers = [3, 4, 5]
    n_atoms = [12, 16, 20]
    
    # Severe oscillation
    slab_energies = [
        12 * e_bulk + 2.0,
        16 * e_bulk + 8.0,
        20 * e_bulk + 1.0
    ]

    res = calculate_surface_energy_convergence(
        slab_energies_ev=slab_energies,
        n_atoms_list=n_atoms,
        layer_counts=layers,
        surface_area_ang2=area,
        bulk_energy_per_atom_ev=e_bulk,
        is_symmetric=True
    )

    assert res.is_converged is False
    assert res.status == "FAIL"
