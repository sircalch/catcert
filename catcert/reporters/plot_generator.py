"""
Publication-ready vector figures for surface energy convergence, potential profiles, and work functions.
"""

from typing import List, Optional
import os
import numpy as np
import matplotlib.pyplot as plt
from catcert.core.scoring import SlabQualityReport

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'figure.dpi': 300,
    'lines.linewidth': 2.0,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
})


def generate_catcert_figures(
    report: SlabQualityReport,
    output_dir: str,
    formats: List[str] = ("png", "svg", "pdf")
) -> List[str]:
    """
    Generates publication figures: surface energy convergence vs layers and planar potential profile V(z).

    Parameters
    ----------
    report : SlabQualityReport
    output_dir : str
    formats : list of str

    Returns
    -------
    saved_paths : list of str
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files = []

    # 1. Surface Energy Convergence Plot
    if report.surface_energy is not None:
        se = report.surface_energy
        layers = [pt.n_layers for pt in se.layer_points]
        gammas = [pt.surface_energy_j_m2 for pt in se.layer_points]

        fig, ax = plt.subplots(figsize=(6.5, 5))
        ax.plot(layers, gammas, marker="o", markersize=8, color="#0284c7", linewidth=2.0, label=r"Pointwise $\gamma(L)$")

        if se.fiorentini_methfessel_gamma_j_m2 is not None:
            ax.axhline(se.fiorentini_methfessel_gamma_j_m2, color="#dc2626", linestyle="--", linewidth=1.5, label=rf"Fiorentini-Methfessel $\gamma_\infty = {se.fiorentini_methfessel_gamma_j_m2:.3f}\ \mathrm{{J/m}}^2$")
            ax.fill_between([min(layers)-0.5, max(layers)+0.5], se.fiorentini_methfessel_gamma_j_m2 - 0.015, se.fiorentini_methfessel_gamma_j_m2 + 0.015, color="#dc2626", alpha=0.1, label=r"$\pm 0.015\ \mathrm{J/m}^2$ Convergence Zone")

        ax.set_xlim(min(layers) - 0.5, max(layers) + 0.5)
        ax.set_xlabel("Slab Thickness (Number of Atomic Layers)")
        ax.set_ylabel(r"Surface Energy $\gamma\ (\mathrm{J/m}^2)$")
        facet = report.metadata.get("surface", "Surface Slab")
        ax.set_title(rf"{facet} — Surface Energy Convergence ($\gamma = {se.converged_gamma_j_m2:.3f}\ \mathrm{{J/m}}^2$)")
        ax.grid(True)
        ax.legend(loc="upper right", frameon=True, fontsize=9)

        plt.tight_layout()
        for fmt in formats:
            p = os.path.join(output_dir, f"catcert_surface_energy_convergence.{fmt}")
            plt.savefig(p, dpi=300, bbox_inches="tight")
            saved_files.append(p)
        plt.close()

    # 2. Planar Potential Profile V(z) & Work Function Diagram
    if report.vacuum_potential is not None:
        vp = report.vacuum_potential
        z_arr = np.asarray(vp.z_coordinates_ang)
        v_arr = np.asarray(vp.potential_ev)

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(z_arr, v_arr, color="#0f172a", linewidth=1.8, label=r"Planar Average $\bar{V}(z)$")

        # Vacuum level
        ax.axhline(vp.vacuum_plateau_potential_ev, color="#0284c7", linestyle="--", linewidth=1.5, label=rf"Vacuum Level $V_{{\mathrm{{vac}}}} = {vp.vacuum_plateau_potential_ev:.2f}\ \mathrm{{eV}}$")

        # Fermi energy
        if vp.e_fermi_ev is not None:
            ax.axhline(vp.e_fermi_ev, color="#16a34a", linestyle=":", linewidth=1.5, label=rf"Fermi Level $E_F = {vp.e_fermi_ev:.2f}\ \mathrm{{eV}}$")
            if vp.work_function_ev is not None:
                # Annotation for work function Phi
                z_mid = float(np.median(z_arr))
                wf_str = rf"Work Function $\Phi = {vp.work_function_ev:.2f}\ \mathrm{{eV}}$"
                ax.annotate(
                    wf_str,
                    xy=(z_mid, (vp.vacuum_plateau_potential_ev + vp.e_fermi_ev) / 2.0),
                    xytext=(z_mid + 2.0, (vp.vacuum_plateau_potential_ev + vp.e_fermi_ev) / 2.0),
                    arrowprops=dict(arrowstyle="<->", color="#c084fc", lw=1.5),
                    color="#c084fc",
                    fontweight="bold",
                    fontsize=10
                )

        ax.set_xlabel(r"$z$-Coordinate along Surface Normal ($\mathrm{\AA}$)")
        ax.set_ylabel(r"Electrostatic Potential (eV)")
        ax.set_title(f"Planar Electrostatic Potential Profile — Vacuum Gap = {vp.vacuum_thickness_ang:.1f} Å")
        ax.grid(True)
        ax.legend(loc="lower right", frameon=True, fontsize=9)

        plt.tight_layout()
        for fmt in formats:
            p = os.path.join(output_dir, f"catcert_potential_profile.{fmt}")
            plt.savefig(p, dpi=300, bbox_inches="tight")
            saved_files.append(p)
        plt.close()

    return saved_files
