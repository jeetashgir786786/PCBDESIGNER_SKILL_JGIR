#!/usr/bin/env python3
"""PCB engineering calculator (transparent first-order estimates).

Every result is an ESTIMATE from a published closed-form approximation.
Final impedance must come from a 2D field solver with the fab's stackup;
final current/thermal values from IPC-2152 data, simulation or measurement.

Units: lengths in mm unless the option name says otherwise; frequency in GHz;
voltage in V; current in A; temperature rise in degC.

Examples:
  pcb_calc.py microstrip --w 0.2 --h 0.1 --t 0.035 --er 4.2
  pcb_calc.py stripline  --w 0.1 --b 0.25 --t 0.018 --er 3.6
  pcb_calc.py diff-microstrip --w 0.12 --s 0.15 --h 0.1 --t 0.035 --er 4.2
  pcb_calc.py diff-stripline  --w 0.1 --s 0.15 --b 0.3 --t 0.018 --er 3.6
  pcb_calc.py delay --er-eff 3.7 --length 100
  pcb_calc.py critical-length --tr-ps 100 --er-eff 3.7
  pcb_calc.py stub --stub-mm 1.2 --er-eff 3.6 --nyquist-ghz 16
  pcb_calc.py trace-current --current 3 --dt 10 --oz 1 --layer external
  pcb_calc.py via-current --drill 0.25 --plating-um 25 --dt 10
  pcb_calc.py ztarget --v 0.8 --ripple-pct 2 --di 40
  pcb_calc.py plane-cap --area-mm2 10000 --d-mm 0.076 --er 4.2
  pcb_calc.py ipc2221-spacing --v 300 --col B2
  pcb_calc.py aspect --thickness 3.0 --drill 0.25
  pcb_calc.py loss --f-ghz 16 --df 0.004 --dk 3.6 --w-mil 5 --z0 50 --length-in 10 --rough 1.3
  pcb_calc.py bga-layers --signal-rows 12 --traces-per-channel 2
  pcb_calc.py via-thermal --length 1.6 --drill 0.3 --plating-um 25 --count 20
"""
import argparse
import math
import sys

C_IN_PER_NS = 11.8028  # speed of light, inches per ns
C_MM_PER_PS = 0.299792458
MM_PER_MIL = 0.0254
CU_RHO = 1.72e-8  # ohm*m at 20 C
K_CU = 390.0  # W/m/K

# IPC-2221B Table 6-1 (mm). Rows: upper voltage bound (V peak). Columns B1..A7.
IPC2221_COLS = ["B1", "B2", "B3", "B4", "A5", "A6", "A7"]
IPC2221_TABLE = [
    (15,  [0.05, 0.1, 0.1, 0.05, 0.13, 0.13, 0.13]),
    (30,  [0.05, 0.1, 0.1, 0.05, 0.13, 0.25, 0.13]),
    (50,  [0.1, 0.6, 0.6, 0.13, 0.13, 0.4, 0.13]),
    (100, [0.1, 0.6, 1.5, 0.13, 0.13, 0.5, 0.13]),
    (150, [0.2, 0.6, 3.2, 0.4, 0.4, 0.8, 0.4]),
    (170, [0.2, 1.25, 3.2, 0.4, 0.4, 0.8, 0.4]),
    (250, [0.2, 1.25, 6.4, 0.4, 0.4, 0.8, 0.4]),
    (300, [0.2, 2.5, 12.5, 0.4, 0.4, 0.8, 0.8]),
    (500, [0.25, 2.5, 12.5, 0.8, 0.8, 1.5, 0.8]),
]
IPC2221_PER_VOLT = [0.0025, 0.005, 0.025, 0.00305, 0.00305, 0.00305, 0.00305]


def warn(msg):
    print(f"  ! {msg}")


def z_microstrip(w, h, t, er):
    return 87.0 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def z_stripline(w, b, t, er):
    return 60.0 / math.sqrt(er) * math.log(4.0 * b / (0.67 * math.pi * (0.8 * w + t)))


def er_eff_microstrip(w, h, er):
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h / w) ** -0.5


def cmd_microstrip(a):
    z = z_microstrip(a.w, a.h, a.t, a.er)
    ee = er_eff_microstrip(a.w, a.h, a.er)
    print(f"IPC-2141 microstrip: Z0 = {z:.1f} ohm, er_eff ~ {ee:.2f}, tpd ~ {84.7*math.sqrt(ee):.0f} ps/in")
    if not 0.1 <= a.w / a.h <= 2.0:
        warn("w/h outside 0.1..2.0 validity range")
    warn("Excludes solder mask (typically -1..-3 ohm), etch trapezoid, roughness. Use a field solver.")


def cmd_stripline(a):
    z = z_stripline(a.w, a.b, a.t, a.er)
    print(f"IPC-2141 symmetric stripline: Z0 = {z:.1f} ohm, tpd ~ {84.7*math.sqrt(a.er):.0f} ps/in")
    if a.w / a.b >= 0.35 or a.t / a.b >= 0.25:
        warn("outside validity (w/b < 0.35, t/b < 0.25)")
    warn("b = plane-to-plane spacing. Asymmetric stripline needs a field solver.")


def cmd_diff_microstrip(a):
    z0 = z_microstrip(a.w, a.h, a.t, a.er)
    zd = 2 * z0 * (1 - 0.48 * math.exp(-0.96 * a.s / a.h))
    print(f"Edge-coupled microstrip: Z0(single) = {z0:.1f} ohm, Zdiff ~ {zd:.1f} ohm")
    warn("Approximation +/-10%. Confirm with field solver.")


def cmd_diff_stripline(a):
    z0 = z_stripline(a.w, a.b, a.t, a.er)
    zd = 2 * z0 * (1 - 0.347 * math.exp(-2.9 * a.s / a.b))
    print(f"Edge-coupled stripline: Z0(single) = {z0:.1f} ohm, Zdiff ~ {zd:.1f} ohm")
    warn("Approximation +/-10%. Confirm with field solver.")


def cmd_delay(a):
    tpd_ps_mm = math.sqrt(a.er_eff) / C_MM_PER_PS
    print(f"tpd = {tpd_ps_mm:.3f} ps/mm ({tpd_ps_mm*25.4:.1f} ps/in); delay over {a.length} mm = {tpd_ps_mm*a.length:.1f} ps")
    print(f"1 ps of skew = {1/tpd_ps_mm:.3f} mm ({1/tpd_ps_mm/MM_PER_MIL:.1f} mil)")


def cmd_critical(a):
    tpd_ps_mm = math.sqrt(a.er_eff) / C_MM_PER_PS
    lc = a.tr_ps / (6 * tpd_ps_mm)
    print(f"f_knee ~ {0.5/(a.tr_ps*1e-3):.2f} GHz; critical length (tr/6tpd) ~ {lc:.1f} mm ({lc/25.4:.2f} in)")
    print(f"Reflections unavoidable without termination above ~ {a.tr_ps/(2*tpd_ps_mm):.1f} mm")


def cmd_stub(a):
    f = C_MM_PER_PS * 1e3 / (4 * a.stub_mm * math.sqrt(a.er_eff))  # GHz (mm/ps * 1e3 = mm/ns)
    print(f"Quarter-wave stub resonance ~ {f:.1f} GHz for {a.stub_mm} mm ({a.stub_mm/MM_PER_MIL:.0f} mil) stub")
    if a.nyquist_ghz:
        ratio = f / a.nyquist_ghz
        print(f"f_res / Nyquist = {ratio:.2f}  ->  {'OK (>=3x)' if ratio >= 3 else 'RISK: back-drill / blind via / re-layer, then simulate'}")
    max_stub = C_MM_PER_PS * 1e3 / (4 * math.sqrt(a.er_eff) * 3 * a.nyquist_ghz) if a.nyquist_ghz else None
    if max_stub:
        print(f"Max stub for f_res >= 3x Nyquist ~ {max_stub:.2f} mm ({max_stub/MM_PER_MIL:.0f} mil)")


def oz_to_mil(oz):
    return oz * 1.378


def cmd_trace_current(a):
    k = 0.048 if a.layer == "external" else 0.024
    t_mil = oz_to_mil(a.oz)
    area = (a.current / (k * a.dt ** 0.44)) ** (1 / 0.725)  # mil^2
    w_mil = area / t_mil
    print(f"IPC-2221 ({a.layer}, {a.oz} oz, dT={a.dt} C, I={a.current} A): area {area:.1f} mil^2 -> width {w_mil:.1f} mil ({w_mil*MM_PER_MIL:.3f} mm)")
    if a.length:
        r = CU_RHO * (a.length * 1e-3) / (w_mil * MM_PER_MIL * 1e-3 * t_mil * MM_PER_MIL * 1e-3)
        print(f"DC resistance over {a.length} mm ~ {r*1e3:.2f} mOhm at 20 C; drop {a.current*r*1e3:.1f} mV; loss {a.current**2*r*1e3:.1f} mW")
    warn("IPC-2221 is legacy and conservative for internal layers; check IPC-2152 (planes reduce dT).")


def cmd_via_current(a):
    d = a.drill
    t = a.plating_um / 1000.0
    area_mm2 = math.pi * ((d / 2 + t) ** 2 - (d / 2) ** 2)
    area_mil2 = area_mm2 / (MM_PER_MIL ** 2)
    i_ext = 0.048 * a.dt ** 0.44 * area_mil2 ** 0.725
    i_int = 0.024 * a.dt ** 0.44 * area_mil2 ** 0.725
    print(f"Barrel area {area_mm2*1e3:.1f} x1e-3 mm^2 ({area_mil2:.1f} mil^2); IPC-2221 estimate: {i_int:.2f} A (internal k) .. {i_ext:.2f} A (external k) for dT={a.dt} C")
    if a.length:
        r = CU_RHO * (a.length * 1e-3) / (area_mm2 * 1e-6)
        print(f"Via resistance over {a.length} mm ~ {r*1e3:.2f} mOhm")
    warn("Rule of thumb only; vias are short and heat-sunk by planes. Use many vias and IR-drop simulation for high current.")


def cmd_ztarget(a):
    z = a.v * a.ripple_pct / 100 / a.di
    print(f"Ztarget = {a.v} V x {a.ripple_pct}% / {a.di} A = {z*1e3:.3f} mOhm")


def cmd_plane_cap(a):
    c = 8.854e-12 * a.er * (a.area_mm2 * 1e-6) / (a.d_mm * 1e-3)
    print(f"Plane capacitance ~ {c*1e12:.0f} pF ({c*1e12/(a.area_mm2/645.16):.0f} pF/in^2)")


def cmd_spacing(a):
    col = a.col.upper()
    if col not in IPC2221_COLS:
        sys.exit(f"col must be one of {IPC2221_COLS}")
    i = IPC2221_COLS.index(col)
    if a.v <= 500:
        for vmax, row in IPC2221_TABLE:
            if a.v <= vmax:
                s = row[i]
                break
    else:
        s = IPC2221_TABLE[-1][1][i] + (a.v - 500) * IPC2221_PER_VOLT[i]
    print(f"IPC-2221B Table 6-1 {col} @ {a.v} V peak: min spacing {s:.3f} mm ({s/MM_PER_MIL:.1f} mil)")
    warn("Functional spacing only. Safety creepage/clearance comes from the product standard (IEC 62368-1/60664-1 etc.). Verify against your licensed IPC-2221 revision.")


def cmd_aspect(a):
    ar = a.thickness / a.drill
    tier = "mainstream (<=10:1)" if ar <= 10 else "advanced (10-16:1)" if ar <= 16 else "backplane-class (>16:1) - confirm with fab"
    print(f"Aspect ratio {ar:.1f}:1 -> {tier}")


def cmd_loss(a):
    ad = 2.3 * a.f_ghz * a.df * math.sqrt(a.dk)
    ac = 36 * math.sqrt(a.f_ghz) / (a.w_mil * a.z0) * a.rough
    tot = ad + ac
    print(f"@ {a.f_ghz} GHz: dielectric ~ {ad:.3f} dB/in, conductor ~ {ac:.3f} dB/in (roughness x{a.rough}), total ~ {tot:.3f} dB/in")
    if a.length_in:
        print(f"Over {a.length_in} in: ~ {tot*a.length_in:.1f} dB (trace only; add vias, connectors, packages, margin)")
    warn("Rule-of-thumb (Bogatin-style) estimates; use vendor/simulated loss for budgets.")


def cmd_bga(a):
    n = 1 + math.ceil(max(a.signal_rows - 2, 0) / a.traces_per_channel)
    print(f"Estimated signal routing layers ~ {n} (outer escapes 2 rows; each inner ~{a.traces_per_channel} rows)")
    print("Add reference planes (one per signal layer side) and power planes per rail group; verify with a trial fan-out.")


def cmd_via_thermal(a):
    t = a.plating_um * 1e-6
    d = a.drill * 1e-3
    area = math.pi * ((d / 2 + t) ** 2 - (d / 2) ** 2)
    r = (a.length * 1e-3) / (K_CU * area)
    print(f"Single via (unfilled) ~ {r:.0f} K/W; {a.count} in parallel ~ {r/a.count:.1f} K/W")
    warn("Ignores spreading resistance and fill; copper-filled vias are much lower.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("microstrip"); s.add_argument("--w", type=float, required=True); s.add_argument("--h", type=float, required=True); s.add_argument("--t", type=float, default=0.035); s.add_argument("--er", type=float, required=True); s.set_defaults(f=cmd_microstrip)
    s = sp.add_parser("stripline"); s.add_argument("--w", type=float, required=True); s.add_argument("--b", type=float, required=True); s.add_argument("--t", type=float, default=0.018); s.add_argument("--er", type=float, required=True); s.set_defaults(f=cmd_stripline)
    s = sp.add_parser("diff-microstrip"); [s.add_argument(f"--{k}", type=float, required=True) for k in ("w", "s", "h", "er")]; s.add_argument("--t", type=float, default=0.035); s.set_defaults(f=cmd_diff_microstrip)
    s = sp.add_parser("diff-stripline"); [s.add_argument(f"--{k}", type=float, required=True) for k in ("w", "s", "b", "er")]; s.add_argument("--t", type=float, default=0.018); s.set_defaults(f=cmd_diff_stripline)
    s = sp.add_parser("delay"); s.add_argument("--er-eff", type=float, required=True); s.add_argument("--length", type=float, default=100.0, help="mm"); s.set_defaults(f=cmd_delay)
    s = sp.add_parser("critical-length"); s.add_argument("--tr-ps", type=float, required=True); s.add_argument("--er-eff", type=float, default=4.0); s.set_defaults(f=cmd_critical)
    s = sp.add_parser("stub"); s.add_argument("--stub-mm", type=float, required=True); s.add_argument("--er-eff", type=float, default=3.8); s.add_argument("--nyquist-ghz", type=float); s.set_defaults(f=cmd_stub)
    s = sp.add_parser("trace-current"); s.add_argument("--current", type=float, required=True); s.add_argument("--dt", type=float, default=10.0); s.add_argument("--oz", type=float, default=1.0); s.add_argument("--layer", choices=["external", "internal"], default="external"); s.add_argument("--length", type=float, help="mm, for resistance/drop"); s.set_defaults(f=cmd_trace_current)
    s = sp.add_parser("via-current"); s.add_argument("--drill", type=float, required=True, help="finished hole mm"); s.add_argument("--plating-um", type=float, default=25.0); s.add_argument("--dt", type=float, default=10.0); s.add_argument("--length", type=float, help="mm"); s.set_defaults(f=cmd_via_current)
    s = sp.add_parser("ztarget"); s.add_argument("--v", type=float, required=True); s.add_argument("--ripple-pct", type=float, required=True); s.add_argument("--di", type=float, required=True); s.set_defaults(f=cmd_ztarget)
    s = sp.add_parser("plane-cap"); s.add_argument("--area-mm2", type=float, required=True); s.add_argument("--d-mm", type=float, required=True); s.add_argument("--er", type=float, default=4.2); s.set_defaults(f=cmd_plane_cap)
    s = sp.add_parser("ipc2221-spacing"); s.add_argument("--v", type=float, required=True, help="peak V"); s.add_argument("--col", default="B2", help="B1 B2 B3 B4 A5 A6 A7"); s.set_defaults(f=cmd_spacing)
    s = sp.add_parser("aspect"); s.add_argument("--thickness", type=float, required=True); s.add_argument("--drill", type=float, required=True); s.set_defaults(f=cmd_aspect)
    s = sp.add_parser("loss"); s.add_argument("--f-ghz", type=float, required=True); s.add_argument("--df", type=float, required=True); s.add_argument("--dk", type=float, required=True); s.add_argument("--w-mil", type=float, default=5.0); s.add_argument("--z0", type=float, default=50.0); s.add_argument("--rough", type=float, default=1.0); s.add_argument("--length-in", type=float); s.set_defaults(f=cmd_loss)
    s = sp.add_parser("bga-layers"); s.add_argument("--signal-rows", type=int, required=True); s.add_argument("--traces-per-channel", type=int, default=1); s.set_defaults(f=cmd_bga)
    s = sp.add_parser("via-thermal"); s.add_argument("--length", type=float, default=1.6); s.add_argument("--drill", type=float, default=0.3); s.add_argument("--plating-um", type=float, default=25.0); s.add_argument("--count", type=int, default=1); s.set_defaults(f=cmd_via_thermal)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
