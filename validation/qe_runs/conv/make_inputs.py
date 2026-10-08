"""
Inputs for the slab-side convergence tests of CatCert 1.2.0 (Quantum ESPRESSO 7.5, PBE, SSSP 1.3.0,
30/240 Ry, Marzari-Vanderbilt smearing 0.02 Ry, unrelaxed fcc(111) 1x1 Al slabs, same stacking and
vacuum convention as validation/qe_runs/al111_{3,5,7}L.in).

    python make_inputs.py

Writes:
  al111_9L.in, al111_11L.in   thickness series, 16x16x1 in-plane k-mesh (as the 3-7 layer runs)
  al111_5L_k24.in, al111_5L_k32.in   in-plane k-mesh test on the 5-layer slab
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "al111_5L.in")
TEMPLATE_TEXT = open(TEMPLATE, encoding="utf-8").read()
C3, C5 = 19.66499018, 24.32998035
STEP_C = (C5 - C3) / 2.0                 # cell height added per layer
D_LAYER = 0.0958691727 * C5 - 0.0 * 0   # layer spacing in angstrom (from the 5L file)
STACK = [(0.0, 0.0), (1 / 3, 2 / 3), (2 / 3, 1 / 3)]


def positions(n, c):
    rows = []
    for i in range(n):
        x, y = STACK[i % 3]
        rows.append(f"  Al {x:.10f} {y:.10f} {i * D_LAYER / c:.10f}")
    return "\n".join(rows)


def make(name, n, kmesh="16 16 1 0 0 0", c=None):
    c = C3 + (n - 3) * STEP_C if c is None else c
    text = TEMPLATE_TEXT
    text = text.replace("prefix = 'al111_5L'", f"prefix = '{name}'")
    text = text.replace("outdir = './tmp_5L'", f"outdir = './tmp_{name}'")
    text = text.replace(f"C = {C5:.8f}", f"C = {c:.8f}").replace(f"C = {C5}", f"C = {c:.8f}")
    text = text.replace("nat = 5", f"nat = {n}")
    head, _ = text.split("ATOMIC_POSITIONS crystal\n")
    _, tail = text.split("K_POINTS automatic\n")
    body = f"{head}ATOMIC_POSITIONS crystal\n{positions(n, c)}\nK_POINTS automatic\n  {kmesh}\n"
    with open(os.path.join(HERE, f"{name}.in"), "w", encoding="utf-8") as fh:
        fh.write(body)
    print(name, "C =", round(c, 4), "atoms", n)


if __name__ == "__main__":
    make("al111_9L", 9)
    make("al111_11L", 11)
    make("al111_5L_k24", 5, kmesh="24 24 1 0 0 0", c=C5)
    make("al111_5L_k32", 5, kmesh="32 32 1 0 0 0", c=C5)
