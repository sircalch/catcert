"""
Tests for vacuum potential profile V(z) and work function calculation.
"""

import numpy as np
import pytest
from catcert.core.vacuum_potential import calculate_vacuum_potential_profile


def test_vacuum_potential_profile_pass():
    z_pts = np.linspace(0, 24.0, 100)
    # Atoms at 6, 8, 10, 12 (slab thickness = 6 Å, vacuum = 18 Å)
    atom_z = [6.0, 8.0, 10.0, 12.0]
    
    # Potential: deep wells at slab, flat at 0 in vacuum
    v_planar = np.zeros_like(z_pts)
    for z_at in atom_z:
        v_planar -= 15.0 * np.exp(-((z_pts - z_at) / 1.0)**2)

    res = calculate_vacuum_potential_profile(
        z_grid_ang=z_pts,
        v_planar_ev=v_planar,
        atomic_z_positions_ang=atom_z,
        e_fermi_ev=-5.20,
        min_vacuum_thickness_ang=12.0
    )

    assert res.status == "PASS"
    assert res.vacuum_thickness_ang >= 15.0
    assert np.isclose(res.work_function_ev, 5.20, atol=0.1)


def test_vacuum_potential_profile_insufficient_vacuum():
    z_pts = np.linspace(0, 12.0, 100)
    # Atoms from 2 to 10 (slab thickness = 8 Å, vacuum = 4 Å)
    atom_z = [2.0, 4.0, 6.0, 8.0, 10.0]
    v_planar = np.zeros_like(z_pts)

    res = calculate_vacuum_potential_profile(
        z_grid_ang=z_pts,
        v_planar_ev=v_planar,
        atomic_z_positions_ang=atom_z,
        min_vacuum_thickness_ang=12.0
    )

    assert res.status == "FAIL"
    assert res.vacuum_thickness_ang < 12.0
