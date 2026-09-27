"""
Regression tests on real Quantum ESPRESSO 7.5 outputs (PBE, SSSP 1.3.0 efficiency, 30/240 Ry):
fcc Al bulk and unrelaxed Al(111) 1x1 slabs, inputs in validation/qe_runs/.
"""
import os

import pytest

from catcert.core.surface_energy import calculate_surface_energy_convergence
from catcert.parsers.qe_parser import parse_qe_output

DATA = os.path.join(os.path.dirname(__file__), "data")
RY_TO_EV = 13.605693122994


def load(name):
    return parse_qe_output(os.path.join(DATA, name))


def test_parser_reads_energy_atoms_and_surface_area():
    d = load("al111_3L.out")
    assert d["final_energy_ev"] == pytest.approx(-118.45713474 * RY_TO_EV, rel=1e-10)
    assert d["n_atoms"] == 3
    assert d["surface_area_ang2"] == pytest.approx(7.0675, abs=1e-3)   # sqrt(3)/2 * (4.04/sqrt 2)^2
    assert d["e_fermi_ev"] == pytest.approx(0.3676)
    assert d["scf_converged"] is True


def test_surface_energy_matches_hand_calculation():
    bulk = load("al_bulk.out")
    slabs = [load(f"al111_{n}L.out") for n in (3, 4, 5)]
    res = calculate_surface_energy_convergence(
        [s["final_energy_ev"] for s in slabs], [s["n_atoms"] for s in slabs], [3, 4, 5],
        slabs[0]["surface_area_ang2"], bulk["final_energy_ev"] / bulk["n_atoms"])
    # gamma = (E_slab - n E_bulk) / (2 A), computed independently from the raw Ry energies
    assert [p.surface_energy_j_m2 for p in res.layer_points] == pytest.approx([0.8053, 0.8690, 0.8639], abs=2e-4)
    assert 0.5 < res.converged_gamma_j_m2 < 1.2
