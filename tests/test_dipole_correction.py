"""
Tests for dipole correction and work function asymmetry audit.
"""

import numpy as np
import pytest
from catcert.core.dipole_correction import calculate_dipole_correction_audit


def test_dipole_correction_symmetric():
    res = calculate_dipole_correction_audit(
        top_v_vac_ev=0.0,
        bottom_v_vac_ev=0.0,
        e_fermi_ev=-5.0,
        is_asymmetric_slab=False
    )
    assert res.status == "PASS"
    assert res.delta_work_function_ev == 0.0


def test_dipole_correction_asymmetric_uncorrected():
    res = calculate_dipole_correction_audit(
        top_v_vac_ev=0.5,
        bottom_v_vac_ev=-0.2,
        e_fermi_ev=-5.0,
        is_dipole_correction_enabled=False,
        is_asymmetric_slab=True
    )
    assert res.status == "FAIL"
    assert res.delta_work_function_ev == 0.70
