"""
Parsers for Quantum ESPRESSO calculations: pw.x output and pp.x average.dat.
"""

from typing import Dict, Any, Optional, Tuple
import os
import re
import numpy as np

# QE Ry to eV conversion
RY_TO_EV = 13.605693009


def parse_qe_output(filepath: str) -> Dict[str, Any]:
    """
    Parses total energy, Fermi energy, and dipole flags from Quantum ESPRESSO pw.x log.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    data : dict
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    total_energy_ry = None
    e_fermi_ev = None
    dipfield = False

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "!    total energy" in line:
                m = re.search(r"=\s*([-\d\.]+)\s*Ry", line)
                if m:
                    total_energy_ry = float(m.group(1))
            elif "the Fermi energy is" in line:
                m = re.search(r"is\s*([-\d\.]+)\s*ev", line, re.IGNORECASE)
                if m:
                    e_fermi_ev = float(m.group(1))
            elif "dipfield" in line and ".true." in line.lower():
                dipfield = True

    total_energy_ev = float(total_energy_ry * RY_TO_EV) if total_energy_ry is not None else None

    return {
        "final_energy_ev": total_energy_ev,
        "e_fermi_ev": e_fermi_ev,
        "is_dipole_correction_enabled": dipfield
    }


def parse_qe_planar_average(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Parses 1D planar average file from Quantum ESPRESSO pp.x / average.x (.dat).
    Expected format: 2 columns [z_coordinate, potential].
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    z_vals = []
    v_vals = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_s = line.strip()
            if not line_s or line_s.startswith("#"):
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

    return np.asarray(z_vals, dtype=float), np.asarray(v_vals, dtype=float)
