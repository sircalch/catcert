"""
Parsers for VASP calculations: OUTCAR, LOCPOT planar averages, and dipole settings.
"""

from typing import Dict, Any, Optional, List, Tuple
import os
import re
import numpy as np


def parse_vasp_outcar(filepath: str) -> Dict[str, Any]:
    """
    Parses key quantities from a VASP OUTCAR: total energy, Fermi energy,
    dipole moment, and dipole correction flags.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    energy_free = None
    energy_without_entropy = None
    e_fermi = None
    dipole_moment_z = None
    ldipol = False
    idipol = 0

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "free energy    TOTEN  =" in line:
                m = re.search(r"TOTEN\s*=\s*([-\d\.]+)", line)
                if m:
                    energy_free = float(m.group(1))
            elif "energy  without entropy =" in line:
                m = re.search(r"energy\s+without\s+entropy\s*=\s*([-\d\.]+)", line)
                if m:
                    energy_without_entropy = float(m.group(1))
            elif "E-fermi :" in line:
                m = re.search(r"E-fermi\s*:\s*([-\d\.]+)", line)
                if m:
                    e_fermi = float(m.group(1))
            elif "dipolmoment" in line:
                # e.g. dipolmoment          0.000000      0.000000      0.450123 electrons x Angstroem
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        dipole_moment_z = float(parts[3])
                    except ValueError:
                        pass
            elif "LDIPOL" in line and "=" in line:
                if "T" in line.upper():
                    ldipol = True
            elif "IDIPOL" in line and "=" in line:
                m = re.search(r"IDIPOL\s*=\s*(\d+)", line)
                if m:
                    idipol = int(m.group(1))

    final_energy = energy_without_entropy if energy_without_entropy is not None else energy_free

    return {
        "final_energy_ev": final_energy,
        "e_fermi_ev": e_fermi,
        "dipole_moment_z": dipole_moment_z,
        "is_dipole_correction_enabled": ldipol and (idipol == 3),
        "idipol": idipol
    }


def parse_vasp_locpot_average(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Parses a 1D planar average potential file (e.g. generated from LOCPOT via macro_density or vaspkit).
    Expected format: 2 columns [z_coordinate_Ang, potential_eV].

    Parameters
    ----------
    filepath : str

    Returns
    -------
    z_coords : np.ndarray
    potential : np.ndarray
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    z_vals = []
    v_vals = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_s = line.strip()
            if not line_s or line_s.startswith("#") or line_s.startswith("&"):
                continue
            parts = line_s.split()
            if len(parts) >= 2:
                try:
                    z = float(parts[0])
                    v = float(parts[1])
                    z_vals.append(z)
                    v_vals.append(v)
                except ValueError:
                    continue

    if not z_vals:
        raise ValueError(f"No numeric potential data parsed from {filepath}")

    return np.asarray(z_vals, dtype=float), np.asarray(v_vals, dtype=float)
