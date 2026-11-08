import numpy as np


class KerrSpacetimeEngine:
    """
    Boyer-Lindquist Kerr Metric & Critical Photon Geodesic Calculator (G = c = M = 1).
    Computes event horizons, ergosphere, prograde/retrograde ISCO, photon spheres,
    and Bardeen critical impact parameters (alpha, beta) for the black hole shadow.
    """

    def __init__(self, spin_a: float = 0.94):
        self.a = float(np.clip(spin_a, -0.998, 0.998))

    def horizon_radii(self) -> dict:
        """Outer event horizon r_+ and inner Cauchy horizon r_-."""
        disc = np.sqrt(max(0.0, 1.0 - self.a**2))
        return {
            "r_plus": float(1.0 + disc),
            "r_minus": float(1.0 - disc),
            "r_ergo_equator": 2.0,
        }

    def isco_radius(self, prograde: bool = True) -> float:
        """Bardeen-Press-Teukolsky (1972) exact ISCO radius."""
        a = abs(self.a)
        z1 = 1.0 + (1.0 - a**2) ** (1.0 / 3.0) * (
            (1.0 + a) ** (1.0 / 3.0) + (1.0 - a) ** (1.0 / 3.0)
        )
        z2 = np.sqrt(3.0 * a**2 + z1**2)
        sign = -1.0 if (self.a >= 0 and prograde) or (self.a < 0 and not prograde) else 1.0
        return float(3.0 + z2 + sign * np.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2)))

    def photon_sphere_radii(self) -> dict:
        """Equatorial circular photon orbit radii r_ph^- (prograde) and r_ph^+ (retrograde)."""
        a = abs(self.a)
        r_pro = 2.0 * (1.0 + np.cos((2.0 / 3.0) * np.arccos(-a)))
        r_ret = 2.0 * (1.0 + np.cos((2.0 / 3.0) * np.arccos(a)))
        return {"r_ph_prograde": float(r_pro), "r_ph_retrograde": float(r_ret)}

    def frame_dragging_omega(self, r: float, theta: float = np.pi / 2.0) -> float:
        """Relativistic Lense-Thirring frame-dragging angular velocity omega = -g_{t phi} / g_{phi phi}."""
        sin2 = np.sin(theta) ** 2
        sigma = r**2 + (self.a**2) * (np.cos(theta) ** 2)
        delta = r**2 - 2.0 * r + self.a**2
        A = (r**2 + self.a**2) ** 2 - (self.a**2) * delta * sin2
        return float((2.0 * self.a * r) / A)

    def shadow_contour(self, inclination_deg: float = 80.0, num_pts: int = 160) -> dict:
        """
        Computes Bardeen (1973) celestial coordinates (alpha, beta) of the unstable
        spherical photon shell delineating the Kerr black hole shadow boundary.
        """
        inc = np.deg2rad(np.clip(inclination_deg, 5.0, 89.9))
        a = self.a
        if abs(a) < 1e-4:
            # Schwarzschild exact circle of radius 3*sqrt(3) M ~ 5.196 M
            phi = np.linspace(0, 2 * np.pi, num_pts)
            r_crit = 3.0 * np.sqrt(3.0)
            return {
                "alpha": np.round(r_crit * np.cos(phi), 4).tolist(),
                "beta": np.round(r_crit * np.sin(phi), 4).tolist(),
            }

        ph = self.photon_sphere_radii()
        r_vals = np.linspace(ph["r_ph_prograde"] + 1e-4, ph["r_ph_retrograde"] - 1e-4, num_pts)

        alpha_list = []
        beta_pos = []
        for r in r_vals:
            delta = r**2 - 2.0 * r + a**2
            # Conserved Carter constants xi = L_z / E and eta = Q / E^2
            xi = (r**2 * (r - 3.0) + a**2 * (r + 1.0)) / (a * (r - 1.0))
            eta = (r**3 * (4.0 * a**2 - r * (r - 3.0) ** 2)) / (a**2 * (r - 1.0) ** 2)

            arg = eta + (a**2) * (np.cos(inc) ** 2) - (xi**2) * (np.cos(inc) / np.sin(inc)) ** 2
            if arg >= 0.0:
                alpha_val = -xi / np.sin(inc)
                beta_val = np.sqrt(arg)
                alpha_list.append(float(alpha_val))
                beta_pos.append(float(beta_val))

        # Mirror upper and lower halves for closed D-shaped curve
        full_alpha = alpha_list + alpha_list[::-1]
        full_beta = beta_pos + [-b for b in beta_pos[::-1]]
        return {
            "alpha": np.round(full_alpha, 4).tolist(),
            "beta": np.round(full_beta, 4).tolist(),
        }
