# Changelog

## Unreleased

### Slab convergence tests (validation/results/slab_convergence.csv)
- Surface energy of unrelaxed Al(111) with the converged bulk reference (32x32x32), PBE, 30/240 Ry:
  thickness 3-11 layers gives 0.788, 0.846, 0.835, 0.823, 0.818, 0.796, 0.852 J/m^2 (no plateau).
- Vacuum (+4 and +8 A) changes nothing at 7, 9 or 11 layers (to 0.0001 J/m^2): the spread is not a cell-height effect.
- In-plane k-mesh of the 5-layer slab: 16x16 0.8353, 24x24 0.8409, 32x32 0.8410 J/m^2; 16x16 is within 0.006 J/m^2.
- Two 11-layer runs did not converge the SCF at 1e-9 Ry; they were rerun at 1e-8 and 1e-6 Ry (energies agree to 0.3 meV).
- Not yet tested: smearing, relaxation, and the choice of fit. No converged surface energy is quoted.

## 1.2.0 (2026-10-07)

### Correction
- **The Al(111) surface energy of 0.858 J/m^2 in 1.1.0 is withdrawn.** It was computed against a bulk energy from a
  16x16x16 k-mesh, which is not converged (bulk energy per atom: 16^3 -537.4673, 24^3 -537.4612, 32^3 -537.4622 eV;
  the 16^3 value was off by about 8 meV). With the converged bulk (32^3), the pointwise surface energies of 3-7
  layers are 0.788, 0.846, 0.835, 0.823 and 0.818 J/m^2: no plateau, and the 6-to-7-layer change is 0.0055 J/m^2,
  not 0.0002. The Fiorentini-Methfessel fit gives 0.804 J/m^2. The claim "converges to 0.858 J/m^2" should not be
  used. Release 1.1.0 was not published (no GitHub release, no Zenodo record); this entry corrects its commit history.
- **The convergence test cannot detect this kind of drift.** The layer-to-layer check (threshold 0.015 J/m^2)
  accepts a monotone drift of a few hundredths of a J/m^2 per layer. A plateau has to be shown explicitly; the
  package does not yet do that. Slab-side k-point and smearing convergence is not tested.

### Fixed
- **Dispersion was recognised from any text.** `calculate_adsorption_energy` returned PASS ("rigorously evaluated")
  for any non-empty dispersion label, e.g. 'xyz'. Only recognised methods (names normalised: 'DFT-D3(BJ)' -> 'd3bj')
  now pass; anything else gives WARNING.
- **Functional and van der Waals treatment are read from the pw.x output** (`parse_qe_dispersion`), not typed in.
- **Wording.** Reports say "checked", not "certified"; the version and citation come from `catcert.__version__`.

### Validation
- `validation/ase_emt_check.py`: the surface-energy bookkeeping (areas, factor 2, thickness fit) agrees with ASE
  to machine precision for Al(111) slabs with the EMT potential. This tests conventions only: EMT slabs have the same
  energy per layer at every thickness, so it cannot test convergence.
- `validation/qe_runs/kconv/`: bulk fcc Al at 16^3, 24^3 and 32^3 (Quantum ESPRESSO 7.5, PBE, SSSP 1.3.0).

### Not validated
- The slab series: its thickness and k-mesh convergence are open. The VASP parsers are not validated.

## 1.1.0 (committed, never released; see the correction in 1.2.0)

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
