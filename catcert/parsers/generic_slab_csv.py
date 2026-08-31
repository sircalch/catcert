"""
Parser for generic tabular slab convergence CSV/TSV files and 1D potential profiles.
"""

from typing import Dict, Any, List, Tuple
import os
import pandas as pd
import numpy as np


def parse_slab_convergence_csv(filepath: str) -> Dict[str, Any]:
    """
    Parses a CSV containing slab thickness convergence series.
    Required columns: 'layers' (or 'n_layers'), 'energy' (eV), 'n_atoms' (or 'atoms').
    Optional columns: 'area' (surface area in Å^2).

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    sep = r"\s+" if filepath.endswith(".dat") else ("," if filepath.endswith(".csv") else None)
    df = pd.read_csv(filepath, sep=sep, engine="python" if sep is None else None)

    col_map = {}
    for c in df.columns:
        c_low = str(c).lower().strip()
        if c_low in ["layers", "n_layers", "layer", "thickness"]:
            col_map[c] = "layers"
        elif c_low in ["energy", "energy_ev", "e_slab", "toten", "e_tot"]:
            col_map[c] = "energy"
        elif c_low in ["n_atoms", "atoms", "natoms", "n_units", "nat"]:
            col_map[c] = "n_atoms"
        elif c_low in ["area", "surface_area", "area_ang2", "a"]:
            col_map[c] = "area"

    df = df.rename(columns=col_map)

    if "layers" not in df.columns or "energy" not in df.columns or "n_atoms" not in df.columns:
        raise ValueError(f"Slab convergence CSV must contain 'layers', 'energy', and 'n_atoms'. Found: {list(df.columns)}")

    df = df.sort_values(by="layers")

    return {
        "layer_counts": df["layers"].astype(int).tolist(),
        "slab_energies_ev": df["energy"].astype(float).tolist(),
        "n_atoms_list": df["n_atoms"].astype(int).tolist(),
        "surface_area_ang2": float(df["area"].iloc[0]) if "area" in df.columns else None
    }


def parse_potential_profile_csv(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Parses a 2-column CSV/DAT file containing z_coordinates and electrostatic potential.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    data = np.loadtxt(filepath, comments="#")
    z = data[:, 0]
    v = data[:, 1]
    return z, v
