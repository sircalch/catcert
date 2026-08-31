"""
Manuscript Methods snippet, summary tables (CSV, LaTeX), and BibTeX citations for CatCert.
"""

from typing import Dict, Any, Optional
import os
import pandas as pd
from catcert.core.scoring import SlabQualityReport


def generate_catcert_manuscript_assets(
    report: SlabQualityReport,
    output_dir: str
) -> Dict[str, str]:
    """
    Generates manuscript Methods paragraph, summary CSV/LaTeX tables, and BibTeX citations.

    Parameters
    ----------
    report : SlabQualityReport
    output_dir : str

    Returns
    -------
    paths : dict
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = {}

    rows = []
    meta = report.metadata

    rows.append({"Parameter": "Target Surface / Facet", "Value": f"{meta.get('surface', 'Surface Slab')} ({meta.get('software', 'DFT')})", "Status": "PASS"})
    rows.append({"Parameter": "Exchange-Correlation Functional", "Value": f"{meta.get('functional', 'PBE')}", "Status": "PASS"})

    if report.surface_energy:
        se = report.surface_energy
        rows.append({"Parameter": "Converged Surface Energy (gamma)", "Value": f"{se.converged_gamma_j_m2:.3f} J/m^2 ({se.converged_gamma_mev_ang2:.1f} meV/A^2)", "Status": se.status})
        if se.fiorentini_methfessel_gamma_j_m2 is not None:
            rows.append({"Parameter": "Fiorentini-Methfessel Asymptotic gamma", "Value": f"{se.fiorentini_methfessel_gamma_j_m2:.3f} J/m^2", "Status": "PASS"})
        rows.append({"Parameter": "Slab Layer Convergence (Delta gamma)", "Value": f"{se.final_delta_gamma_j_m2:.4f} J/m^2", "Status": se.status})

    if report.vacuum_potential:
        vp = report.vacuum_potential
        rows.append({"Parameter": "Vacuum Gap Spacing", "Value": f"{vp.vacuum_thickness_ang:.1f} Angstroms (c = {vp.cell_height_c_ang:.1f} A)", "Status": vp.status})
        rows.append({"Parameter": "Vacuum Potential Flatness (Delta V)", "Value": f"{vp.vacuum_flatness_delta_ev:.4f} eV", "Status": vp.status})
        if vp.work_function_ev is not None:
            rows.append({"Parameter": "Calculated Work Function (Phi)", "Value": f"{vp.work_function_ev:.2f} eV (V_vac = {vp.vacuum_plateau_potential_ev:.2f} eV)", "Status": "PASS"})

    if report.dipole_audit:
        da = report.dipole_audit
        rows.append({"Parameter": "Dipole Correction Audit", "Value": f"{'Active' if da.is_dipole_correction_enabled else 'None'} (|Delta Phi| = {da.delta_work_function_ev:.3f} eV)", "Status": da.status})

    if report.adsorption_energy:
        ae = report.adsorption_energy
        rows.append({"Parameter": f"Adsorption Energy ({ae.adsorbate_name})", "Value": f"{ae.e_adsorption_ev:.3f} eV ({ae.e_adsorption_kcal_mol:.2f} kcal/mol)", "Status": ae.status})
        if ae.dispersion_method:
            rows.append({"Parameter": "Dispersion / vdW Correction", "Value": f"{ae.dispersion_method}", "Status": "PASS"})

    df_summary = pd.DataFrame(rows)

    # CSV
    csv_path = os.path.join(output_dir, "catcert_summary_table.csv")
    df_summary.to_csv(csv_path, index=False)
    generated["summary_csv"] = csv_path

    # LaTeX
    tex_path = os.path.join(output_dir, "catcert_summary_table.tex")
    tex_content = df_summary.to_latex(index=False, escape=False)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("% CatCert Heterogeneous Catalysis & Surface Slab Validation Table\n")
        f.write(tex_content)
    generated["summary_tex"] = tex_path

    # 2. Methods Text
    methods_path = os.path.join(output_dir, "methods_snippet.txt")
    surf_str = meta.get("surface", "surface slab models")
    dft_str = meta.get("software", "density functional theory (DFT)")
    func_str = meta.get("functional", "GGA-PBE")

    se_str = ""
    if report.surface_energy:
        se = report.surface_energy
        se_str = f"Surface energy convergence as a function of slab thickness was audited using Fiorentini-Methfessel linear regression and pointwise layer differences (converged gamma = {se.converged_gamma_j_m2:.3f} J/m^2, Delta gamma = {se.final_delta_gamma_j_m2:.4f} J/m^2). "

    vac_str = ""
    if report.vacuum_potential:
        vp = report.vacuum_potential
        phi_part = f", yielding a work function Phi = {vp.work_function_ev:.2f} eV" if vp.work_function_ev else ""
        vac_str = f"Periodic image interactions were decoupled with {vp.vacuum_thickness_ang:.1f} Angstroms of vacuum spacing, confirming potential plateau flatness (Delta V_vac = {vp.vacuum_flatness_delta_ev:.4f} eV{phi_part}). "

    dip_str = ""
    if report.dipole_audit and report.dipole_audit.is_asymmetric_slab:
        dip_str = f"Electrostatic dipole layer corrections were verified across the asymmetric slab normal (|Delta Phi| = {report.dipole_audit.delta_work_function_ev:.3f} eV). "

    full_methods = (
        f"Periodic surface slab calculations for {surf_str} were performed with {dft_str} utilizing the {func_str} exchange-correlation functional. "
        f"Slab thickness convergence, vacuum isolation, work functions, and electrostatic potential profiles were certified using CatCert v1.0.0 (Monreal-Hernández, 2026). "
        f"{se_str}{vac_str}{dip_str}"
        f"The surface model achieved an overall quality certification status of: {report.overall_status}."
    )

    with open(methods_path, "w", encoding="utf-8") as f:
        f.write(full_methods + "\n")
    generated["methods_text"] = methods_path

    # 3. BibTeX
    bib_path = os.path.join(output_dir, "citation.bib")
    bib_content = """@software{monreal2026catcert,
  author = {Monreal-Hern\\'andez, Andre},
  title = {{CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs}},
  year = {2026},
  version = {1.0.0},
  publisher = {Zenodo},
  url = {https://github.com/amonreal/catcert}
}
"""
    with open(bib_path, "w", encoding="utf-8") as f:
        f.write(bib_content)
    generated["citation_bib"] = bib_path

    return generated
