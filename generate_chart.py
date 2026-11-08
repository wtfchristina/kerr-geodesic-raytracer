import numpy as np
import matplotlib.pyplot as plt
from kerr_core.metric import KerrSpacetimeEngine
from kerr_core.radiative_disk import NovikovThorneDisk

plt.style.use("dark_background")
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
fig.suptitle(
    "General Relativistic Ray Tracer (GRRT): Kerr Spacetime Shadow, ISCO & Doppler Beaming (g^4)",
    fontsize=13,
    fontweight="bold",
    color="#38bdf8",
    y=0.98,
)

# Panel 1: Bardeen Black Hole Shadow Deformation across Spins
for a, col in [(0.0, "#64748b"), (0.75, "#38bdf8"), (0.998, "#f43f5e")]:
    kerr = KerrSpacetimeEngine(spin_a=a)
    sh = kerr.shadow_contour(inclination_deg=82.0)
    axes[0].plot(sh["alpha"], sh["beta"], label=f"a/M = {a}", color=col, linewidth=2.0)
axes[0].set_title("Bardeen Photon Shadow (θ_obs = 82°)", fontsize=11)
axes[0].set_xlabel("Celestial α (M)")
axes[0].set_ylabel("Celestial β (M)")
axes[0].set_aspect("equal")
axes[0].grid(alpha=0.15)
axes[0].legend(loc="upper right", fontsize=9)

# Panel 2: Relativistic Doppler Beaming (Approaching vs Receding Disk Limb, a/M = 0.94)
disk = NovikovThorneDisk(spin_a=0.94)
prof = disk.radial_profile(inclination_deg=78.0)
axes[1].plot(prof["radii"], prof["flux_approaching"], color="#38bdf8", lw=2.2, label="Approaching Limb (g^4 Blue)")
axes[1].plot(prof["radii"], prof["intrinsic_flux"], color="#fbbf24", lw=1.6, ls="--", label="Rest-Frame Emissivity")
axes[1].plot(prof["radii"], prof["flux_receding"], color="#f43f5e", lw=2.0, label="Receding Limb (g^4 Red)")
axes[1].set_title("Novikov-Thorne Relativistic Flux (a/M = 0.94)", fontsize=11)
axes[1].set_xlabel("Boyer-Lindquist Radius r/M")
axes[1].set_ylabel("Observed Specific Intensity I_obs")
axes[1].grid(alpha=0.15)
axes[1].legend(fontsize=8.5)

# Panel 3: Horizon, Photon Sphere & ISCO Scaling vs Spin a/M
a_grid = np.linspace(0.0, 0.998, 60)
r_isco = [KerrSpacetimeEngine(a).isco_radius() for a in a_grid]
r_ph = [KerrSpacetimeEngine(a).photon_sphere_radii()["r_ph_prograde"] for a in a_grid]
r_hor = [KerrSpacetimeEngine(a).horizon_radii()["r_plus"] for a in a_grid]

axes[2].plot(a_grid, r_isco, color="#10b981", lw=2.2, label="Prograde r_ISCO")
axes[2].plot(a_grid, r_ph, color="#a855f7", lw=2.0, label="Prograde Photon Orbit r_ph^-")
axes[2].plot(a_grid, r_hor, color="#f43f5e", lw=2.0, label="Event Horizon r_+")
axes[2].set_title("Critical Kerr Radii vs Spin Parameter a/M", fontsize=11)
axes[2].set_xlabel("Dimensionless Spin a/M")
axes[2].set_ylabel("Radius (r/M)")
axes[2].grid(alpha=0.15)
axes[2].legend(fontsize=8.5)

plt.tight_layout()
plt.savefig("kerr_grrt_telemetry.png", dpi=300)
print("Saved high-resolution relativistic telemetry plot: kerr_grrt_telemetry.png")
