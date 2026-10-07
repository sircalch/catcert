"""
Independent bookkeeping check of CatCert's surface-energy convention with ASE (independent code) and the EMT
potential (a model potential for Al, not DFT; the check tests conventions, not physical accuracy).

    python validation/ase_emt_check.py

Slabs: fcc Al(111), 1x1 cell, 3-9 layers, lattice constant 4.05 A, fixed geometry (no relaxation: EMT energies
are compared with the same geometry in ASE). Bulk: fcc Al, same lattice constant, 4 atoms in the conventional
cell. Reference surface energy computed independently with ASE, gamma = (E_slab - N*E_bulk/atom)/(2A), and
with the Fiorentini-Methfessel fit E(N) = N*E_bulk + 2*A*gamma. Output: validation/results/ase_emt_check.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from ase.build import bulk, fcc111
from ase.calculators.emt import EMT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from catcert.core.surface_energy import calculate_surface_energy_convergence  # noqa: E402

A_LAT = 4.05


def main():
    bulk_at = bulk("Al", "fcc", a=A_LAT, cubic=False)
    bulk_at.calc = EMT()
    e_bulk = bulk_at.get_potential_energy() / len(bulk_at)

    rows, energies, natoms, layers = [], [], [], []
    for n in range(3, 10):
        slab = fcc111("Al", size=(1, 1, n), a=A_LAT, vacuum=None)
        slab.calc = EMT()
        e = slab.get_potential_energy()
        area = np.linalg.norm(np.cross(slab.cell[0], slab.cell[1]))
        gamma_ase = (e - len(slab) * e_bulk) / (2 * area) * 16.02176634
        energies.append(e)
        natoms.append(len(slab))
        layers.append(n)
        rows.append({"layers": n, "n_atoms": len(slab), "area_A2": area, "gamma_ase_J_m2": gamma_ase})

    # CatCert: convergence (pointwise, with the ASE bulk energy) and FM fit (bulk energy from the fit)
    res = calculate_surface_energy_convergence(energies, natoms, layers, area, bulk_energy_per_atom_ev=e_bulk)
    pw = {p.n_layers: p.surface_energy_j_m2 for p in res.layer_points}
    fm = calculate_surface_energy_convergence(energies, natoms, layers, area)
    df = pd.DataFrame(rows)
    df["gamma_catcert_J_m2"] = df.layers.map(pw)
    df["rel_diff"] = df.gamma_catcert_J_m2 / df.gamma_ase_J_m2 - 1
    df.to_csv(os.path.join(HERE, "results", "ase_emt_check.csv"), index=False)
    print(df.to_string(index=False))
    gamma_fm = fm.fiorentini_methfessel_gamma_j_m2
    print(f"max |rel diff| CatCert vs ASE (pointwise, given bulk): {df.rel_diff.abs().max():.2e}")
    print(f"Fiorentini-Methfessel fit: gamma = {gamma_fm:.4f} J/m^2; ASE at 9 layers: {df.gamma_ase_J_m2.iloc[-1]:.4f}")


if __name__ == "__main__":
    main()
