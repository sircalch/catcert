"""
Tests for scoring, manuscript reporting, and CLI demo execution in CatCert.
"""

import os
import tempfile
import numpy as np
import pytest
from catcert.core.surface_energy import calculate_surface_energy_convergence
from catcert.core.vacuum_potential import calculate_vacuum_potential_profile
from catcert.core.dipole_correction import calculate_dipole_correction_audit
from catcert.core.adsorption_energy import calculate_adsorption_energy
from catcert.core.scoring import assess_slab_quality
from catcert.reporters.plot_generator import generate_catcert_figures
from catcert.reporters.manuscript_prep import generate_catcert_manuscript_assets
from catcert.reporters.html_report import generate_catcert_html_report
from catcert.cli import run_demo


def test_full_catcert_validation_pipeline():
    meta = {
        "surface": "Pd(111)",
        "functional": "PBE-D3",
        "software": "VASP"
    }

    # Surface energy
    surf_res = calculate_surface_energy_convergence(
        slab_energies_ev=[-60.0, -80.0, -100.0],
        n_atoms_list=[12, 16, 20],
        layer_counts=[3, 4, 5],
        surface_area_ang2=25.0,
        bulk_energy_per_atom_ev=-5.0,
        is_symmetric=True
    )

    # Vacuum potential
    z_pts = np.linspace(0, 20.0, 50)
    v_pts = np.zeros_like(z_pts)
    v_pts[10:30] = -10.0
    vac_res = calculate_vacuum_potential_profile(
        z_grid_ang=z_pts,
        v_planar_ev=v_pts,
        atomic_z_positions_ang=[6.0, 8.0, 10.0],
        e_fermi_ev=-5.0
    )

    # Dipole
    dip_res = calculate_dipole_correction_audit(
        top_v_vac_ev=0.0,
        bottom_v_vac_ev=0.0,
        e_fermi_ev=-5.0,
        is_asymmetric_slab=False
    )

    # Adsorption
    ads_res = calculate_adsorption_energy(
        adsorbate_name="O*",
        e_slab_adsorbate_ev=-105.0,
        e_clean_slab_ev=-100.0,
        e_gas_ev=-4.0,
        dispersion_method="D3-BJ"
    )

    report = assess_slab_quality(
        metadata=meta,
        surface_energy_res=surf_res,
        vacuum_res=vac_res,
        dipole_res=dip_res,
        adsorption_res=ads_res
    )

    assert report.overall_status == "PASS"

    with tempfile.TemporaryDirectory() as tmpdir:
        plots = generate_catcert_figures(report, tmpdir, formats=["png", "svg"])
        assert len(plots) > 0
        for p in plots:
            assert os.path.exists(p)

        assets = generate_catcert_manuscript_assets(report, tmpdir)
        assert os.path.exists(assets["summary_csv"])
        assert os.path.exists(assets["summary_tex"])
        assert os.path.exists(assets["methods_text"])
        assert os.path.exists(assets["citation_bib"])

        html_p = os.path.join(tmpdir, "report.html")
        generate_catcert_html_report(report, html_p, methods_text="Sample methods", citation_bib="@software{}")
        assert os.path.exists(html_p)
        assert os.path.getsize(html_p) > 500


def test_cli_demo_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        run_demo(output_dir=tmpdir)
        assert os.path.exists(os.path.join(tmpdir, "report.html"))
        assert os.path.exists(os.path.join(tmpdir, "catcert_summary_table.csv"))
        assert os.path.exists(os.path.join(tmpdir, "citation.bib"))
