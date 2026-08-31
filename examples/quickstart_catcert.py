"""
Quickstart API tutorial for CatCert.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from catcert import (
    calculate_surface_energy_convergence,
    calculate_vacuum_potential_profile,
    calculate_dipole_correction_audit,
    calculate_adsorption_energy,
    assess_slab_quality
)
from catcert.parsers import parse_slab_convergence_csv, parse_potential_profile_csv
from catcert.reporters import (
    generate_catcert_figures,
    generate_catcert_manuscript_assets,
    generate_catcert_html_report
)
from generate_sample_cat_data import generate_sample_cat_data


def main():
    print("Running CatCert Python API quickstart tutorial...")
    raw_dir = "sample_surface_dataset"
    generate_sample_cat_data(raw_dir)

    out_dir = "quickstart_catcert_output"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Parse slab convergence CSV
    c_data = parse_slab_convergence_csv(os.path.join(raw_dir, "pt111_layer_convergence.csv"))
    se_res = calculate_surface_energy_convergence(
        slab_energies_ev=c_data["slab_energies_ev"],
        n_atoms_list=c_data["n_atoms_list"],
        layer_counts=c_data["layer_counts"],
        surface_area_ang2=c_data["surface_area_ang2"],
        bulk_energy_per_atom_ev=-6.045
    )

    # 2. Parse potential profile
    z_pts, v_pts = parse_potential_profile_csv(os.path.join(raw_dir, "pt111_potential_1d.dat"))
    vac_res = calculate_vacuum_potential_profile(
        z_grid_ang=z_pts,
        v_planar_ev=v_pts,
        atomic_z_positions_ang=[5.0, 7.5, 10.0, 12.5, 15.0],
        e_fermi_ev=-5.70
    )

    # 3. Assess overall slab quality
    report = assess_slab_quality(
        metadata={"surface": "Pt(111)", "functional": "PBE-D3", "software": "VASP"},
        surface_energy_res=se_res,
        vacuum_res=vac_res
    )

    print(f"\nOverall Slab Certification Status: {report.overall_status}")
    print(f"Converged Surface Energy: {report.surface_energy.converged_gamma_j_m2:.3f} J/m^2")
    print(f"Vacuum Thickness: {report.vacuum_potential.vacuum_thickness_ang:.1f} Å")
    print(f"Work Function: {report.vacuum_potential.work_function_ev:.2f} eV")

    # 4. Export deliverables
    generate_catcert_figures(report, out_dir)
    assets = generate_catcert_manuscript_assets(report, out_dir)
    with open(assets["methods_text"], "r", encoding="utf-8") as f:
        methods_txt = f.read()
    with open(assets["citation_bib"], "r", encoding="utf-8") as f:
        bib_txt = f.read()

    html_p = os.path.join(out_dir, "report.html")
    generate_catcert_html_report(report, html_p, methods_text=methods_txt, citation_bib=bib_txt)

    print(f"\nCompleted! HTML report available at: {os.path.abspath(html_p)}")


if __name__ == "__main__":
    main()
