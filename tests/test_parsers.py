"""
Tests for parsers (VASP, QE, CSV) in CatCert.
"""

import os
import tempfile
import numpy as np
import pytest
from catcert.parsers.vasp_parser import parse_vasp_outcar, parse_vasp_locpot_average
from catcert.parsers.qe_parser import parse_qe_output, parse_qe_planar_average
from catcert.parsers.generic_slab_csv import parse_slab_convergence_csv, parse_potential_profile_csv


def test_vasp_outcar_parser():
    content = """
 free energy    TOTEN  =      -120.61234567 eV
 energy  without entropy =      -120.61234567
 E-fermi :      -5.7000     QC(all comp.) =       0.0000
 dipolmoment          0.000000      0.000000      0.450123 electrons x Angstroem
 LDIPOL =      T
 IDIPOL =      3
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        f_path = f.name

    try:
        data = parse_vasp_outcar(f_path)
        assert np.isclose(data["final_energy_ev"], -120.61234567)
        assert np.isclose(data["e_fermi_ev"], -5.70)
        assert data["is_dipole_correction_enabled"] is True
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_generic_slab_csv_parser():
    content = """layers,energy,n_atoms,area
3,-72.22,12,27.60
4,-96.42,16,27.60
5,-120.61,20,27.60
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        f_path = f.name

    try:
        c_data = parse_slab_convergence_csv(f_path)
        assert len(c_data["layer_counts"]) == 3
        assert c_data["layer_counts"] == [3, 4, 5]
        assert c_data["surface_area_ang2"] == 27.60
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)
