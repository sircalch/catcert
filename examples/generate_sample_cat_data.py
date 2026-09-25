"""
Generates sample surface slab convergence CSV and 1D electrostatic potential profile.
"""

import os
import pandas as pd
import numpy as np


def generate_sample_cat_data(output_dir: str = "sample_surface_dataset"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Slab Layer Convergence CSV (Pt(111) 3 to 7 layers)
    layers = [3, 4, 5, 6, 7]
    atoms = [12, 16, 20, 24, 28]
    energies = [-67.200, -91.483, -115.732, -139.912, -164.092]
    areas = [27.60] * 5

    df = pd.DataFrame({
        "layers": layers,
        "n_atoms": atoms,
        "energy": energies,
        "area": areas
    })
    csv_p = os.path.join(output_dir, "pt111_layer_convergence.csv")
    df.to_csv(csv_p, index=False)

    # 2. Planar potential profile (VASP LOCPOT average format)
    z_pts = np.linspace(0, 26.0, 260)
    atom_z = [5.0, 7.5, 10.0, 12.5, 15.0]
    v_planar = np.zeros_like(z_pts)
    for z_at in atom_z:
        v_planar -= 18.0 * np.exp(-((z_pts - z_at) / 1.0)**2)

    pot_p = os.path.join(output_dir, "pt111_potential_1d.dat")
    with open(pot_p, "w", encoding="utf-8") as f:
        f.write("# z_coordinate_Angstrom  potential_eV\n")
        for z, v in zip(z_pts, v_planar):
            f.write(f"{z:10.4f}  {v:10.4f}\n")

    print(f"Generated sample surface dataset at: {os.path.abspath(output_dir)}/")


if __name__ == "__main__":
    generate_sample_cat_data()
