"""
Command Line Interface (CLI) for CatCert.
"""

import sys
import os
import argparse
import numpy as np

from catcert import __version__
from catcert.parsers.vasp_parser import parse_vasp_outcar, parse_vasp_locpot_average
from catcert.parsers.qe_parser import parse_qe_output, parse_qe_planar_average
from catcert.parsers.generic_slab_csv import parse_slab_convergence_csv, parse_potential_profile_csv

from catcert.core.surface_energy import calculate_surface_energy_convergence
from catcert.core.vacuum_potential import calculate_vacuum_potential_profile
from catcert.core.dipole_correction import calculate_dipole_correction_audit
from catcert.core.adsorption_energy import calculate_adsorption_energy
from catcert.core.scoring import assess_slab_quality

from catcert.reporters.plot_generator import generate_catcert_figures
from catcert.reporters.manuscript_prep import generate_catcert_manuscript_assets
from catcert.reporters.html_report import generate_catcert_html_report


def print_banner():
    banner = rf"""
   _____       _    _____          _   
  / ____|     | |  / ____|        | |  
 | |     __ _ | |_| |     ___ _ __| |_ 
 | |    / _` || __| |    / _ \ '__| __|
 | |___| (_| || |_| |___|  __/ |  | |_ 
  \_____\__,_| \__|\_____\___|_|   \__| v{__version__}

 Heterogeneous Catalysis & DFT Surface Slab Convergence Toolkit
 Monreal-Hernández et al., 2026
"""
    print(banner)


def run_demo(output_dir: str = "catcert_demo_output"):
    """
    Executes a benchmark demonstration evaluating Pt(111) surface slab calculations:
    3 to 7 layer thickness convergence, 16 Å vacuum gap with planar potential profile,
    work function Phi = 5.70 eV, dipole audit, and CO* adsorption with PBE-D3.
    """
    print(f"\n[CatCert] Running demonstration benchmark on Heterogeneous Catalyst Slab (Pt(111) / CO*)...")
    os.makedirs(output_dir, exist_ok=True)

    metadata = {
        "surface": "Pt(111) (p(2x2) 4-atom/layer slab)",
        "functional": "GGA-PBE-D3(BJ)",
        "software": "SYNTHETIC DEMO DATA (VASP-like settings: PAW-PBE, 450 eV, 6x6x1 k-mesh; not a real calculation)"
    }

    # 1. Surface energy convergence series (3, 4, 5, 6, 7 layers of Pt(111))
    layer_counts = [3, 4, 5, 6, 7]
    n_atoms = [12, 16, 20, 24, 28]  # 4 atoms per layer in 2x2 supercell
    # Pt bulk energy = -6.045 eV/atom, surface area A = 27.60 Å^2, gamma ~ 1.50 J/m^2 (~ 93.6 meV/Å^2)
    surface_area = 27.60
    e_bulk_pt = -6.045
    # Simulated total energies converging
    slab_energies = [
        -67.200,  # 3 layers: gamma ~ 1.55 J/m^2
        -91.483,  # 4 layers: gamma ~ 1.52 J/m^2
        -115.732, # 5 layers: gamma ~ 1.50 J/m^2
        -139.912, # 6 layers: gamma ~ 1.50 J/m^2
        -164.092  # 7 layers: gamma ~ 1.50 J/m^2
    ]

    print("  -> Calculating surface energy gamma & layer convergence (Fiorentini-Methfessel regression)...")
    surf_res = calculate_surface_energy_convergence(
        slab_energies_ev=slab_energies,
        n_atoms_list=n_atoms,
        layer_counts=layer_counts,
        surface_area_ang2=surface_area,
        bulk_energy_per_atom_ev=e_bulk_pt,
        is_symmetric=True
    )

    # 2. Planar potential profile V(z) with 16 Å vacuum gap
    print("  -> Generating planar electrostatic potential profile V(z) & work function Phi...")
    c_height = 26.0  # Å
    z_pts = np.linspace(0, c_height, 200)
    # Slab from z=5 to z=15 Å (10 Å slab thickness, 16 Å vacuum from 15 to 26 and 0 to 5)
    atom_z = [5.0, 7.5, 10.0, 12.5, 15.0]
    
    # Electrostatic potential profile: deep wells at atomic layers (~ -20 eV), plateau at 0 eV in vacuum
    v_planar = np.zeros_like(z_pts)
    for z_at in atom_z:
        v_planar -= 18.0 * np.exp(-((z_pts - z_at) / 1.0)**2)
    # Add baseline vacuum level at 0.0 eV
    e_fermi = -5.70  # Fermi level in eV

    vac_res = calculate_vacuum_potential_profile(
        z_grid_ang=z_pts,
        v_planar_ev=v_planar,
        atomic_z_positions_ang=atom_z,
        e_fermi_ev=e_fermi,
        min_vacuum_thickness_ang=12.0
    )

    # 3. Dipole correction audit
    print("  -> Auditing electrostatic dipole step across vacuum normal...")
    dip_res = calculate_dipole_correction_audit(
        top_v_vac_ev=0.0,
        bottom_v_vac_ev=0.0,
        e_fermi_ev=e_fermi,
        is_dipole_correction_enabled=True,
        is_asymmetric_slab=False
    )

    # 4. Adsorption Energy (CO on Pt(111) atop site)
    print("  -> Calculating adsorption energy E_ads for CO* atop site (PBE-D3)...")
    # Clean 5-layer Pt slab = -115.732 eV, gas CO = -14.80 eV, Pt(111)+CO = -132.182 eV
    ads_res = calculate_adsorption_energy(
        adsorbate_name="CO*",
        e_slab_adsorbate_ev=-132.182,
        e_clean_slab_ev=-115.732,
        e_gas_ev=-14.80,
        zpe_correction_ev=0.12,
        dispersion_method="DFT-D3(BJ)"
    )

    report = assess_slab_quality(
        metadata=metadata,
        surface_energy_res=surf_res,
        vacuum_res=vac_res,
        dipole_res=dip_res,
        adsorption_res=ads_res
    )

    print("  -> Generating publication-ready vector figures (Surface Energy vs Layers & Potential V(z))...")
    generate_catcert_figures(report, output_dir)

    print("  -> Drafting manuscript Methods text snippet, summary LaTeX tables, and BibTeX citations...")
    assets = generate_catcert_manuscript_assets(report, output_dir)

    with open(assets["methods_text"], "r", encoding="utf-8") as f:
        methods_txt = f.read()
    with open(assets["citation_bib"], "r", encoding="utf-8") as f:
        bib_txt = f.read()

    html_p = os.path.join(output_dir, "report.html")
    print(f"  -> Writing interactive report to {html_p}...")
    generate_catcert_html_report(report, html_p, methods_text=methods_txt, citation_bib=bib_txt)

    print("\n" + "="*70)
    print(f" [RESULT] Overall Slab Certification Status: {report.overall_status}")
    print(f" [SCORE]  {report.validation_score}")
    print("="*70)
    print(f" * Target Surface   : {report.metadata['surface']}")
    print(f" * Surface Energy   : gamma = {report.surface_energy.converged_gamma_j_m2:.3f} J/m^2 ({report.surface_energy.converged_gamma_mev_ang2:.1f} meV/A^2) | Delta gamma = {report.surface_energy.final_delta_gamma_j_m2:.4f} J/m^2 (PASS)")
    print(f" * Vacuum Spacing   : {report.vacuum_potential.vacuum_thickness_ang:.1f} A (Delta V = {report.vacuum_potential.vacuum_flatness_delta_ev:.4f} eV) | Status: {report.vacuum_potential.status}")
    print(f" * Work Function    : Phi = {report.vacuum_potential.work_function_ev:.2f} eV (E_Fermi = {report.vacuum_potential.e_fermi_ev:.2f} eV)")
    print(f" * Adsorption Energy: E_ads(CO*) = {report.adsorption_energy.e_adsorption_ev:.3f} eV ({report.adsorption_energy.e_adsorption_kcal_mol:.2f} kcal/mol) with {report.adsorption_energy.dispersion_method}")
    print("="*70)
    print(f"\nAll outputs successfully saved to: {os.path.abspath(output_dir)}/")
    print(f"Open {os.path.abspath(html_p)} in your browser to inspect the full report.\n")


def run_assess(args):
    """
    Evaluates user-provided slab data files.
    """
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    surf_res = None
    vac_res = None
    dip_res = None
    ads_res = None

    # 1. Parse Slab Convergence CSV
    if args.layers_csv:
        print(f"\n[CatCert] Parsing layer convergence CSV from: {args.layers_csv}...")
        c_data = parse_slab_convergence_csv(args.layers_csv)
        area = args.area or c_data.get("surface_area_ang2")
        if not area:
            raise ValueError("Surface area in Å^2 (--area) is required to compute surface energy gamma.")

        surf_res = calculate_surface_energy_convergence(
            slab_energies_ev=c_data["slab_energies_ev"],
            n_atoms_list=c_data["n_atoms_list"],
            layer_counts=c_data["layer_counts"],
            surface_area_ang2=float(area),
            bulk_energy_per_atom_ev=float(args.e_bulk) if args.e_bulk is not None else None,
            is_symmetric=not args.asymmetric
        )

    # 2. Parse Potential Profile
    if args.potential:
        print(f"  -> Parsing electrostatic potential profile from: {args.potential}...")
        z_pts, v_pts = parse_potential_profile_csv(args.potential)
        atom_pos = [float(z) for z in args.atom_z.split(",")] if args.atom_z else [float(np.min(z_pts) + 3.0), float(np.max(z_pts) - 3.0)]
        e_f = float(args.e_fermi) if args.e_fermi is not None else None

        vac_res = calculate_vacuum_potential_profile(
            z_grid_ang=z_pts,
            v_planar_ev=v_pts,
            atomic_z_positions_ang=atom_pos,
            e_fermi_ev=e_f
        )

    # 3. Adsorption calculation
    if args.e_adsorbate and args.e_clean and args.e_gas:
        print("  -> Calculating adsorption energy...")
        ads_res = calculate_adsorption_energy(
            adsorbate_name=args.adsorbate_name or "Adsorbate*",
            e_slab_adsorbate_ev=float(args.e_adsorbate),
            e_clean_slab_ev=float(args.e_clean),
            e_gas_ev=float(args.e_gas),
            dispersion_method=args.dispersion
        )

    meta = {
        "surface": args.surface or "Surface Slab",
        "functional": args.functional or "DFT-GGA",
        "software": args.software or "VASP / Quantum ESPRESSO"
    }

    report = assess_slab_quality(
        metadata=meta,
        surface_energy_res=surf_res,
        vacuum_res=vac_res,
        dipole_res=dip_res,
        adsorption_res=ads_res
    )

    print("  -> Generating publication figures...")
    generate_catcert_figures(report, output_dir)

    print("  -> Generating manuscript text, LaTeX summary table, and BibTeX citations...")
    assets = generate_catcert_manuscript_assets(report, output_dir)

    with open(assets["methods_text"], "r", encoding="utf-8") as f:
        methods_txt = f.read()
    with open(assets["citation_bib"], "r", encoding="utf-8") as f:
        bib_txt = f.read()

    html_p = os.path.join(output_dir, "report.html")
    print(f"  -> Writing HTML quality report to {html_p}...")
    generate_catcert_html_report(report, html_p, methods_text=methods_txt, citation_bib=bib_txt)

    print("\n" + "="*70)
    print(f" [RESULT] Overall Quality Certification: {report.overall_status}")
    print(f" [SCORE]  {report.validation_score}")
    print("="*70)
    if report.surface_energy:
        print(f" * Surface Energy : gamma = {report.surface_energy.converged_gamma_j_m2:.3f} J/m^2 | Status: {report.surface_energy.status}")
    if report.vacuum_potential:
        print(f" * Vacuum Gap     : {report.vacuum_potential.vacuum_thickness_ang:.1f} A | Status: {report.vacuum_potential.status}")
    print("="*70)
    print(f"\nReport ready at: {os.path.abspath(html_p)}\n")


def print_citation():
    bib = """@software{monreal2026catcert,
  author = {Monreal-Hern\\'andez, Andre},
  title = {{CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs}},
  year = {2026},
  version = {1.0.0},
  publisher = {Zenodo},
  url = {https://github.com/sircalch/catcert}
}"""
    print("\nIf you use CatCert in your publications, please cite:\n")
    print("APA Style:")
    print("Monreal-Hernández, A. (2026). CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs (v1.0.0). Zenodo. https://github.com/sircalch/catcert\n")
    print("BibTeX:")
    print(bib)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="catcert",
        description="CatCert: Automated Quality-Control & Convergence Certification for Heterogeneous Catalysis & DFT Slabs."
    )
    parser.add_argument("-v", "--version", action="version", version=f"catcert {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Assess command
    assess_parser = subparsers.add_parser("assess", help="Assess slab thickness convergence, potential profile, or adsorption")
    assess_parser.add_argument("--layers-csv", default=None, help="Path to slab layer convergence CSV (layers, energy, n_atoms)")
    assess_parser.add_argument("--area", type=float, default=None, help="Surface cross-sectional area (A = |a x b|) in Å^2")
    assess_parser.add_argument("--e-bulk", type=float, default=None, help="Bulk reference energy per atom (eV)")
    assess_parser.add_argument("--asymmetric", action="store_true", help="Flag if slab is asymmetric (factor 1 instead of 2)")
    assess_parser.add_argument("--potential", default=None, help="Path to 1D planar average potential file (z, V)")
    assess_parser.add_argument("--atom-z", default=None, help="Comma-separated z coordinates of atoms (e.g. '5.0,7.5,10.0,12.5')")
    assess_parser.add_argument("--e-fermi", type=float, default=None, help="Fermi energy (eV) to compute work function Phi")
    assess_parser.add_argument("--e-adsorbate", type=float, default=None, help="Total energy of slab + adsorbate (eV)")
    assess_parser.add_argument("--e-clean", type=float, default=None, help="Total energy of clean bare slab (eV)")
    assess_parser.add_argument("--e-gas", type=float, default=None, help="Energy of isolated gas molecule (eV)")
    assess_parser.add_argument("--adsorbate-name", default="Adsorbate*", help="Adsorbate name (e.g. 'CO*', 'OH*')")
    assess_parser.add_argument("--dispersion", default=None, help="Dispersion method (e.g. 'D3-BJ', 'D4', 'vdW-DF2')")
    assess_parser.add_argument("-o", "--output", default="catcert_output", help="Directory for output report (default: catcert_output)")
    assess_parser.add_argument("--surface", default=None, help="Surface facet description (e.g. 'Pt(111)')")
    assess_parser.add_argument("--functional", default=None, help="DFT functional description (e.g. 'PBE-D3')")
    assess_parser.add_argument("--software", default=None, help="Software code (e.g. 'VASP', 'Quantum ESPRESSO')")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run benchmark demonstration (Pt(111) 3-7 layer slab + CO* adsorption + V(z))")
    demo_parser.add_argument("-o", "--output", default="catcert_demo_output", help="Output directory (default: catcert_demo_output)")

    # Cite command
    subparsers.add_parser("cite", help="Display BibTeX and APA citation details")

    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "assess":
        print_banner()
        run_assess(args)
    elif args.command == "demo":
        print_banner()
        run_demo(args.output)
    elif args.command == "cite":
        print_banner()
        print_citation()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

