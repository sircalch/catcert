"""
Generates and runs Quantum ESPRESSO (pw.x 7.5, SSSP 1.3.0 PBE efficiency) calculations for the
surface energy of Al(111): fcc bulk and unrelaxed 1x1 slabs of 3-7 layers with 15 A of vacuum.

Run inside WSL:  python3 make_and_run.py
"""
import math
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PSEUDO = "/home/andres/pseudo/SSSP_1.3.0_PBE_efficiency"
A0 = 4.04            # fcc lattice constant (Angstrom), close to the PBE value
VAC = 15.0           # vacuum (Angstrom)
NP = 8

COMMON = f"""  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  smearing = 'mv'
  degauss = 0.02
/
&electrons
  conv_thr = 1.0d-9
  mixing_beta = 0.3
/
ATOMIC_SPECIES
  Al 26.9815 Al.pbe-n-kjpaw_psl.1.0.0.UPF
"""


def write_bulk():
    txt = f"""&control
  calculation = 'scf'
  prefix = 'al_bulk'
  pseudo_dir = '{PSEUDO}'
  outdir = './tmp_bulk'
/
&system
  ibrav = 2
  celldm(1) = {A0 / 0.529177210903:.8f}
  nat = 1
  ntyp = 1
{COMMON}ATOMIC_POSITIONS crystal
  Al 0.0 0.0 0.0
K_POINTS automatic
  16 16 16 0 0 0
"""
    open(os.path.join(HERE, "al_bulk.in"), "w").write(txt)
    return "al_bulk"


def write_slab(n):
    a = A0 / math.sqrt(2.0)          # in-plane hexagonal lattice constant
    d = A0 / math.sqrt(3.0)          # (111) interlayer spacing
    c = (n - 1) * d + VAC
    shifts = [(0.0, 0.0), (1 / 3, 2 / 3), (2 / 3, 1 / 3)]     # ABC stacking, crystal coordinates
    pos = []
    for i in range(n):
        x, y = shifts[i % 3]
        pos.append(f"  Al {x:.10f} {y:.10f} {(i * d) / c:.10f}")
    txt = f"""&control
  calculation = 'scf'
  prefix = 'al111_{n}L'
  pseudo_dir = '{PSEUDO}'
  outdir = './tmp_{n}L'
/
&system
  ibrav = 4
  A = {a:.8f}
  C = {c:.8f}
  nat = {n}
  ntyp = 1
{COMMON}ATOMIC_POSITIONS crystal
""" + "\n".join(pos) + """
K_POINTS automatic
  16 16 1 0 0 0
"""
    name = f"al111_{n}L"
    open(os.path.join(HERE, name + ".in"), "w").write(txt)
    return name


def main():
    names = [write_bulk()] + [write_slab(n) for n in (3, 4, 5, 6, 7)]
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/miniforge3/envs/qe/bin") + ":" + env["PATH"]
    env["OMP_NUM_THREADS"] = "1"
    for name in names:
        out = os.path.join(HERE, name + ".out")
        if os.path.exists(out) and "JOB DONE" in open(out, errors="ignore").read():
            print("skip", name)
            continue
        with open(out, "w") as fh:
            subprocess.run(["mpirun", "--oversubscribe", "-np", str(NP), "pw.x", "-in", name + ".in"],
                           cwd=HERE, stdout=fh, stderr=subprocess.STDOUT, env=env, check=False)
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
