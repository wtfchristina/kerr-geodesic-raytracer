import time
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from kerr_core.metric import KerrSpacetimeEngine
from kerr_core.radiative_disk import NovikovThorneDisk

app = FastAPI(
    title="Kerr Geodesic Ray Tracer & Radiative Transfer Engine",
    description="Boyer-Lindquist Kerr spacetime solver and GLSL null-geodesic ray marcher.",
    version="1.0.0",
)


@app.get("/api/v1/kerr-telemetry")
def get_kerr_telemetry(
    spin_a: float = Query(0.94, ge=0.0, le=0.998),
    inclination: float = Query(78.0, ge=5.0, le=89.0),
):
    t0 = time.perf_counter()
    kerr = KerrSpacetimeEngine(spin_a=spin_a)
    disk = NovikovThorneDisk(spin_a=spin_a)

    horiz = kerr.horizon_radii()
    ph = kerr.photon_sphere_radii()
    isco = kerr.isco_radius(prograde=True)
    omega_h = kerr.frame_dragging_omega(horiz["r_plus"])
    shadow = kerr.shadow_contour(inclination_deg=inclination)
    profile = disk.radial_profile(inclination_deg=inclination)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return {
        "spin_a": round(spin_a, 3),
        "inclination_deg": round(inclination, 1),
        "r_plus": round(horiz["r_plus"], 4),
        "r_isco": round(isco, 4),
        "r_ph_prograde": round(ph["r_ph_prograde"], 4),
        "r_ph_retrograde": round(ph["r_ph_retrograde"], 4),
        "omega_horizon": round(omega_h, 4),
        "peak_g_factor": round(profile["peak_g_approaching"], 3),
        "doppler_asymmetry": round(profile["doppler_asymmetry_ratio"], 1),
        "latency_ms": round(elapsed_ms, 2),
        "shadow": shadow,
        "profile": profile,
    }


@app.get("/", response_class=HTMLResponse)
def serve_grrt_visualizer():
    with open("api/index.html", "r") as f:
        return f.read()
