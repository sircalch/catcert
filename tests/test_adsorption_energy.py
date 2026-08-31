"""
Tests for adsorption energy calculation and dispersion corrections.
"""

import numpy as np
import pytest
from catcert.core.adsorption_energy import calculate_adsorption_energy


def test_adsorption_energy_with_dispersion():
    res = calculate_adsorption_energy(
        adsorbate_name="CO*",
        e_slab_adsorbate_ev=-135.0,
        e_clean_slab_ev=-120.0,
        e_gas_ev=-13.5,
        zpe_correction_ev=0.10,
        dispersion_method="DFT-D3(BJ)"
    )

    assert np.isclose(res.e_adsorption_ev, -1.50)
    assert np.isclose(res.e_adsorption_zpe_ev, -1.40)
    assert res.is_dispersion_included is True
    assert res.status == "PASS"


def test_adsorption_energy_no_dispersion():
    res = calculate_adsorption_energy(
        adsorbate_name="CO*",
        e_slab_adsorbate_ev=-135.0,
        e_clean_slab_ev=-120.0,
        e_gas_ev=-13.5,
        dispersion_method=None
    )

    assert res.is_dispersion_included is False
    assert res.status == "WARNING"
