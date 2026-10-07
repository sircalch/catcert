"""
Exchange-correlation functional and van der Waals (dispersion) correction of a Quantum ESPRESSO pw.x run,
read from the output file itself rather than from a label typed by the user.
"""

import os
import re
from typing import Dict, Optional

# substrings of pw.x output lines that identify a van der Waals treatment (QE 7.x wording)
_DISPERSION_PATTERNS = [
    (re.compile(r"Grimme-D2|DFT-D2|Grimme D2", re.I), "Grimme-D2"),
    (re.compile(r"DFT-D3|Grimme-D3|D3\(BJ\)|DFT-D3\(BJ\)|Becke-Johnson", re.I), "Grimme-D3"),
    (re.compile(r"Tkatchenko|TS-vdW|Tkatchenko-Scheffler", re.I), "Tkatchenko-Scheffler"),
    (re.compile(r"\bXDM\b|exchange-hole dipole", re.I), "XDM"),
    (re.compile(r"vdW-DF|rVV10|Dion|vdW-DF2", re.I), "vdW-DF"),
]


def parse_qe_dispersion(filepath: str) -> Dict[str, Optional[str]]:
    """
    Returns the functional string and the dispersion correction found in a pw.x output.

    Keys: xc (the 'Exchange-correlation=' line, e.g. 'SLA PW PBX PBC' for PBE), dispersion (one of
    Grimme-D2, Grimme-D3, Tkatchenko-Scheffler, XDM, vdW-DF, or None when no such line is printed).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    xc = None
    dispersion = None
    with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if xc is None and "Exchange-correlation=" in line:
                xc = line.split("Exchange-correlation=", 1)[1].strip()
            if dispersion is None and ("Dispersion" in line or "dispersion" in line or "vdW" in line or "Van der Waals" in line):
                for pat, name in _DISPERSION_PATTERNS:
                    if pat.search(line):
                        dispersion = name
                        break
    return {"xc": xc, "dispersion": dispersion}
