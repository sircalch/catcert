# Changelog

## 1.1.0 (unreleased)

### Fixed
- **Demo data and plausibility checks.** The demo Pt(111) slab energies gave γ = 0.084 J/m², 18 times below
  the documented 1.50 J/m², and were still certified PASS. The demo data are now physically consistent. The
  surface-energy audit now fails when γ ≤ 0 or when the bulk reference is missing, and warns when γ lies
  outside 0.05–5 J/m² or when only one thickness is given.
- **Quantum ESPRESSO support was not wired into the CLI.** The parsers were imported but never used; only a
  hand-made CSV was accepted. `catcert assess --qe-slabs a.out,b.out,... --qe-bulk bulk.out` now reads pw.x
  outputs directly. The number of atoms, the surface area from the cell vectors, the bulk energy per atom
  and the layer counts (atoms per layer from the gcd of the atom counts, or `--atoms-per-layer`) are all
  taken from the outputs.
- The QE parser also returns `n_atoms`, `cell_ang`, `surface_area_ang2` and `scf_converged`. The Ry→eV
  factor is updated to CODATA 2018 (13.605693122994 eV).
- The demo output is labelled as synthetic data.

### Validation (`validation/qe_runs/`, Quantum ESPRESSO 7.5, PBE, SSSP 1.3.0 efficiency, 30/240 Ry)
- fcc Al bulk and unrelaxed Al(111) 1×1 slabs of 3–7 layers. Per-thickness surface energies match an
  independent hand calculation from the raw Ry energies (0.805, 0.869, 0.864, … J/m²). γ converges to
  0.858 J/m² (Δγ between 6 and 7 layers = 0.0002 J/m²); the Fiorentini–Methfessel estimate is 0.804 J/m².

### Not yet validated
- VASP OUTCAR/LOCPOT parsers (VASP is not available).

## 1.0.0 (2026-08-31)

Initial release.
