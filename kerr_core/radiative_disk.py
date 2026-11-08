import numpy as np
from kerr_core.metric import KerrSpacetimeEngine


class NovikovThorneDisk:
    """
    Relativistic thin accretion disk radiative transfer model (Page & Thorne 1974).
    Computes Keplerian angular velocity Omega_K, gravitational redshift + Doppler
    beaming factor g = nu_obs / nu_emit, and observed bolometric intensity I_obs = g^4 I_emit.
    """

    def __init__(self, spin_a: float = 0.94):
        self.kerr = KerrSpacetimeEngine(spin_a=spin_a)
        self.a = self.kerr.a
        self.r_isco = self.kerr.isco_radius(prograde=True)

    def radial_profile(self, inclination_deg: float = 78.0, num_r: int = 80) -> dict:
        inc = np.deg2rad(inclination_deg)
        r_grid = np.linspace(self.r_isco + 0.05, 18.0, num_r)

        # Keplerian prograde angular frequency Omega_K = 1 / (r^(3/2) + a)
        omega_k = 1.0 / (r_grid**1.5 + self.a)

        # Metric components in equatorial plane (theta = pi/2)
        g_tt = -(1.0 - 2.0 / r_grid)
        g_tphi = -2.0 * self.a / r_grid
        g_phiphi = r_grid**2 + self.a**2 + (2.0 * self.a**2) / r_grid

        # Emitter 4-velocity normalization u^t = 1 / sqrt(-g_tt - 2*Omega*g_tphi - Omega^2*g_phiphi)
        denom = -g_tt - 2.0 * omega_k * g_tphi - (omega_k**2) * g_phiphi
        u_t = 1.0 / np.sqrt(np.maximum(1e-6, denom))

        # Impact parameter b = -L_z / E for approaching (-R sin i) and receding (+R sin i) limbs
        b_app = -r_grid * np.sin(inc)
        b_rec = +r_grid * np.sin(inc)

        g_approaching = 1.0 / (u_t * (1.0 - omega_k * b_app))
        g_receding = 1.0 / (u_t * (1.0 - omega_k * b_rec))

        # Intrinsic Novikov-Thorne thermal emissivity F(r) ~ (r^-3) * [1 - sqrt(r_isco / r)]
        x = np.sqrt(r_grid)
        x0 = np.sqrt(self.r_isco)
        intrinsic_flux = (3.0 / (r_grid**3)) * np.maximum(0.0, 1.0 - x0 / x)
        intrinsic_flux = intrinsic_flux / (np.max(intrinsic_flux) + 1e-12)

        # Liouville theorem invariant: I_obs = g^4 * I_emit
        flux_approaching = intrinsic_flux * (g_approaching**4)
        flux_receding = intrinsic_flux * (g_receding**4)

        return {
            "radii": np.round(r_grid, 3).tolist(),
            "intrinsic_flux": np.round(intrinsic_flux, 4).tolist(),
            "flux_approaching": np.round(flux_approaching, 4).tolist(),
            "flux_receding": np.round(flux_receding, 4).tolist(),
            "peak_g_approaching": float(np.max(g_approaching)),
            "min_g_receding": float(np.min(g_receding)),
            "doppler_asymmetry_ratio": float(np.max(flux_approaching) / (np.max(flux_receding) + 1e-8)),
        }
