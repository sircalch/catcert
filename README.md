# CatCert

[![CI](https://github.com/amonreal/catcert/actions/workflows/test.yml/badge.svg)](https://github.com/amonreal/catcert/actions)
[![PyPI version](https://img.shields.io/pypi/v/catcert.svg?color=blue)](https://pypi.org/project/catcert/)
[![Python versions](https://img.shields.io/pypi/pyversions/catcert.svg)](https://pypi.org/project/catcert/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234590.svg)](https://doi.org/10.5281/zenodo.1234590)

> **Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs (VASP, Quantum ESPRESSO).**

---

## Overview

**CatCert** is an open-source scientific software package designed to standardize, audit, and certify periodic DFT surface slab calculations and adsorption energetics in heterogeneous catalysis, 2D materials, electrochemistry, and surface science.

Surface slab modeling in VASP, Quantum ESPRESSO, and ASE requires rigorous convergence of slab geometry and periodic boundary conditions:

- 🧱 **Surface Energy ($\gamma$) & Slab Layer Convergence**:
  - Pointwise surface energy: $\gamma = \frac{E_{\text{slab}}(N) - N \cdot E_{\text{bulk}}}{2 A}$ (for symmetric slabs).
  - Fiorentini-Methfessel asymptotic regression: $E_{\text{slab}}(N) = 2 A \gamma + N \cdot E_{\text{bulk}}$.
  - Layer-by-layer delta convergence criterion: $\Delta\gamma \le 0.015\text{ J/m}^2$ ($\approx 1\text{ meV/\AA}^2$).
- 🌌 **Vacuum Thickness & Planar Electrostatic Potential $\bar{V}(z)$**:
  - Automatically isolates the vacuum gap (verifying $\ge 12-15\text{ \AA}$ to eliminate periodic image interactions).
  - Checks vacuum plateau flatness: $\Delta V_{\text{vac}} \le 0.05\text{ eV}$.
  - Computes the physical work function: $\Phi = V_{\text{vac}} - E_{\text{Fermi}}$.
- ⚡ **Electrostatic Dipole Moment & Asymmetry Audit**:
  - Quantifies potential steps $|\Delta \Phi| = |\Phi_{\text{top}} - \Phi_{\text{bottom}}|$ in asymmetric slabs (adsorbates on one side, polar facets).
  - Audits dipole corrections (`LDIPOL = .TRUE.` in VASP, `dipfield = .true.` in QE) to prevent artificial electric field artifacts.
- 🔬 **Adsorption Energy ($E_{\text{ads}}$) & Dispersion Check**:
  - $E_{\text{ads}} = E_{\text{slab+adsorbate}} - (E_{\text{clean}} + E_{\text{gas}})$.
  - Verifies presence of van der Waals / dispersion corrections (D3-BJ, D4, vdW-DF2) and ZPE corrections.
- 📑 **Publication Deliverables**:
  - Interactive self-contained `report.html` dashboard.
  - Publication vector figures ($\gamma$ vs layer count, $\bar{V}(z)$ potential profile) in SVG, PDF, PNG (300 DPI).
  - Ready-to-compile LaTeX summary tables (`.tex`).
  - Draft **Methods** text snippet and BibTeX citation (`citation.bib`).

```
       DFT Outputs (OUTCAR, LOCPOT, QE log, Convergence CSV)
                               │
                               ▼
  ┌───────────────────────────────────────────────────────────┐
  │                          CatCert                          │
  │  ├── Surface Energy & Fiorentini-Methfessel Regression    │
  │  ├── Vacuum Gap Spacing & Potential Profile Flatness V(z) │
  │  ├── Work Function (Phi = V_vac - E_Fermi)                │
  │  ├── Asymmetric Dipole Correction Verification           │
  │  └── Adsorption Energy & vdW Dispersion Audit             │
  └───────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌───────────────────────────────────────────────────────────┐
  │                   Publication Deliverables                │
  │  ├── report.html (Interactive Dashboard & Badges)         │
  │  ├── catcert_surface_energy_convergence.pdf/svg/png       │
  │  ├── catcert_potential_profile.pdf/svg/png                │
  │  ├── catcert_summary_table.tex / .csv                     │
  │  ├── methods_snippet.txt (Ready for Manuscript)           │
  │  └── citation.bib (BibTeX Reference)                      │
  └───────────────────────────────────────────────────────────┘
```

---

## Installation

### From PyPI
```bash
pip install catcert
```

### From Source
```bash
git clone https://github.com/amonreal/catcert.git
cd catcert
pip install -e .[dev]
```

---

## Quickstart (CLI)

### 1. Run Benchmark Demo (Pt(111) 3-7 Layers + CO* Adsorption)
```bash
catcert demo -o my_slab_audit/
```
Open `my_slab_audit/report.html` in your browser!

### 2. Assess Slab Convergence CSV & Potential Profile
```bash
catcert assess --layers-csv pt_layers.csv --area 27.60 --potential potential_1d.dat --e-fermi -5.70 -o slab_report/
```

---

## Python API Usage

```python
from catcert import (
    calculate_surface_energy_convergence,
    calculate_vacuum_potential_profile,
    calculate_dipole_correction_audit,
    calculate_adsorption_energy,
    assess_slab_quality
)
from catcert.reporters import (
    generate_catcert_figures,
    generate_catcert_manuscript_assets,
    generate_catcert_html_report
)

# 1. Surface energy convergence
se_res = calculate_surface_energy_convergence(
    slab_energies_ev=[-72.22, -96.42, -120.61, -144.79, -168.97],
    n_atoms_list=[12, 16, 20, 24, 28],
    layer_counts=[3, 4, 5, 6, 7],
    surface_area_ang2=27.60,
    bulk_energy_per_atom_ev=-6.045
)

# 2. Consolidate slab quality
report = assess_slab_quality(
    metadata={"surface": "Pt(111)", "functional": "PBE-D3", "software": "VASP"},
    surface_energy_res=se_res
)

print(f"Overall Certification: {report.overall_status}")
print(f"Converged gamma: {report.surface_energy.converged_gamma_j_m2:.3f} J/m^2")

# 3. Export manuscript deliverables
generate_catcert_figures(report, "output_dir/")
generate_catcert_manuscript_assets(report, "output_dir/")
generate_catcert_html_report(report, "output_dir/report.html")
```

---

## Citation

If you use CatCert in your research, please cite:

```bibtex
@software{monreal2026catcert,
  author = {Monreal-Hern{\'a}ndez, Andre},
  title = {{CatCert: Automated Quality-Control, Vacuum Thickness, Dipole Correction, and Surface Energy Convergence Certification for Heterogeneous Catalysis & DFT Surface Slabs}},
  year = {2026},
  version = {1.0.0},
  publisher = {Zenodo},
  url = {https://github.com/amonreal/catcert}
}
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
