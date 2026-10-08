"""
Inputs for the adsorption-energy test of CatCert (Quantum ESPRESSO 7.5, PBE, SSSP 1.3.0 efficiency, 30/240 Ry,
Marzari-Vanderbilt smearing 0.02 Ry, same convention as the 1x1 Al(111) slabs):

  clean_2x2   Al(111) 2x2, 5 layers, clean
  H_2x2       the same with one H atom in the fcc hollow, 1.0 A above the top layer (coverage 1/4 ML)
  H2_box      H2 molecule, bond 0.74 A, in a 10 A cubic box, Gamma point
Each in PBE and in PBE + Grimme-D3 (vdw_corr = 'grimme-d3'), so that the dispersion contribution to E_ads
is computed, not assumed. The 2x2 cell uses an 8x8x1 k-mesh, the same k density as the 16x16x1 1x1 cell.

    python make_ads.py
"""
import os

from ase.build import fcc111, molecule, add_adsorbate

HERE = os.path.dirname(os.path.abspath(__file__))
A_FCC = 2.85671140 * 2 ** 0.5     # fcc lattice constant from the 1x1 Al(111) runs (hexagonal a = 2.85671 A)
C_SLAB = 24.32998035              # cell height of the 5-layer 1x1 slab
PSEUDO = "/home/andres/pseudo/SSSP_1.3.0_PBE_efficiency"


def header(prefix, outdir, calc, nat, ntyp, species, extra_sys=""):
    return f"""&control
  calculation = '{calc}'
  prefix = '{prefix}'
  pseudo_dir = '{PSEUDO}'
  outdir = './{outdir}'
/
&system
  ibrav = 0
  nat = {nat}
  ntyp = {ntyp}
  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  smearing = 'mv'
  degauss = 0.02
{extra_sys}/
&electrons
  conv_thr = 1.0d-7
  mixing_beta = 0.2
/
ATOMIC_SPECIES
{species}
"""


def cell_block(cell):
    rows = "\n".join(f"  {v[0]:.8f} {v[1]:.8f} {v[2]:.8f}" for v in cell)
    return f"CELL_PARAMETERS angstrom\n{rows}\n"


def pos_block(atoms):
    rows = "\n".join(f"  {s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}" for s, p in zip(atoms.get_chemical_symbols(), atoms.positions))
    return f"ATOMIC_POSITIONS angstrom\n{rows}\n"


def write(name, atoms, kmesh, prefix, vdw=None, species=None):
    sys_extra = f"  vdw_corr = '{vdw}'\n" if vdw else ""
    text = header(prefix, f"tmp_{prefix}", "scf", len(atoms), len(set(atoms.get_chemical_symbols())),
                  species, sys_extra)
    text += cell_block(atoms.cell) + pos_block(atoms) + f"K_POINTS automatic\n  {kmesh}\n"
    with open(os.path.join(HERE, name + ".in"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(name, len(atoms), "atoms")


AL_SPECIES = "  Al 26.9815 Al.pbe-n-kjpaw_psl.1.0.0.UPF"
H_SPECIES = "  H 1.00794 H.pbe-rrkjus_psl.1.0.0.UPF"
SPECIES_SLAB = AL_SPECIES
SPECIES_H = AL_SPECIES + "\n" + H_SPECIES


def build_slab():
    slab = fcc111("Al", size=(2, 2, 5), a=A_FCC, vacuum=None)
    slab.set_cell([slab.cell[0], slab.cell[1], [0.0, 0.0, C_SLAB]], scale_atoms=False)
    slab.pbc = True
    return slab


def build_h_slab():
    slab = build_slab()
    add_adsorbate(slab, "H", height=1.0, position="fcc")
    return slab


def build_h2():
    h2 = molecule("H2")
    h2.set_cell([10.0, 10.0, 10.0])
    h2.center()
    h2.pbc = False
    return h2


if __name__ == "__main__":
    for tag, vdw in (("", None), ("_d3", "grimme-d3")):
        write(f"clean_2x2{tag}", build_slab(), "8 8 1 0 0 0", f"clean2x2{tag.replace('_', '')}", vdw, SPECIES_SLAB)
        write(f"H_2x2{tag}", build_h_slab(), "8 8 1 0 0 0", f"H2x2{tag.replace('_', '')}", vdw, SPECIES_H)
        write(f"H2_box{tag}", build_h2(), "1 1 1 0 0 0", f"H2box{tag.replace('_', '')}", vdw, H_SPECIES)
