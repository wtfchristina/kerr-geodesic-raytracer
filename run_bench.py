import time
from kerr_core.metric import KerrSpacetimeEngine
from kerr_core.radiative_disk import NovikovThorneDisk

spins = [0.0, 0.5, 0.85, 0.94, 0.998]
print(f"{'Spin a/M':<10} | {'r_+ (M)':<9} | {'r_ISCO (M)':<11} | {'r_ph^- (M)':<11} | {'Max g_blue':<11} | {'Beaming Ratio':<14}")
print("-" * 78)

for a in spins:
    t0 = time.perf_counter()
    kerr = KerrSpacetimeEngine(spin_a=a)
    disk = NovikovThorneDisk(spin_a=a)
    horiz = kerr.horizon_radii()
    ph = kerr.photon_sphere_radii()
    prof = disk.radial_profile(inclination_deg=78.0)
    print(
        f"{a:<10.3f} | {horiz['r_plus']:<9.4f} | {kerr.isco_radius():<11.4f} | "
        f"{ph['r_ph_prograde']:<11.4f} | {prof['peak_g_approaching']:<11.4f} | "
        f"{prof['doppler_asymmetry_ratio']:<13.1f}x"
    )
