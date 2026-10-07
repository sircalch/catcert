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


def test_unrecognised_dispersion_label_is_not_a_pass():
    from catcert.core.adsorption_energy import calculate_adsorption_energy
    r = calculate_adsorption_energy("CO", -100.0, -95.0, -5.1, dispersion_method="xyz")
    assert r.status == "WARNING"
    assert r.is_dispersion_included is False
    assert calculate_adsorption_energy("CO", -100.0, -95.0, -5.1, dispersion_method="D3-BJ").status == "PASS"


def test_qe_dispersion_parser_reads_functional_from_real_output():
    import os
    from catcert.parsers.qe_dispersion import parse_qe_dispersion
    path = os.path.join(os.path.dirname(__file__), "..", "validation", "qe_runs", "al111_3L.out")
    d = parse_qe_dispersion(path)
    assert d["xc"].startswith("SLA")       # PBE, no van der Waals line in this run
    assert d["dispersion"] is None
