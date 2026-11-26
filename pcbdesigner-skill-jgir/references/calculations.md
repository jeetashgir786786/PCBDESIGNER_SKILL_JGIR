# Engineering calculations

Show: equation, inputs with units and source, result, margin vs requirement, assumptions/validity range. Use `scripts/pcb_calc.py` for deterministic arithmetic and state which subcommand was run. Closed-form PCB formulas are estimates (±5–20 %); final impedance/current/thermal values come from field solvers, IPC-2152 charts, simulation or measurement.

## 1. Basics
- V = I·R; P = V·I = I²R = V²/R. Divider Vout = Vin·R2/(R1+R2), loaded: R2 → R2‖R_load. Include tolerance worst case.
- RC: τ = RC; first-order fc = 1/(2πRC). LC resonance f = 1/(2π√LC).
- Energy: E_C = ½CV², E_L = ½LI².
- Copper resistance: R = ρL/(W·t), ρ_Cu = 1.72e-8 Ω·m at 20 °C, α = 0.00393/°C. Sheet resistance 1 oz ≈ 0.49 mΩ/□. Include both supply and return paths for voltage drop.

## 2. Conductor current (estimate)
- IPC-2221 (legacy): I = k·ΔT^0.44·A^0.725 with A in mil², k = 0.048 external, 0.024 internal. Conservative for internal layers; IPC-2152 shows internal conductors near planes carry as much as or more than external ones.
- IPC-2152: use its charts with modifiers (board thickness, copper plane presence/distance, copper thickness) or a calculator implementing them (Saturn PCB Toolkit, UltraCAD). Adjacent planes reduce temperature rise substantially.
- Always also check voltage drop and fusing/fault current (fuse rating, short-circuit duration).
- 1 oz = 35 µm = 1.378 mil; ½ oz = 17.5 µm; 2 oz = 70 µm. Width(mil) = A(mil²)/thickness(mil).

## 3. Timing & SI
- tpd ≈ 84.7 ps/in·√Dk_eff; microstrip Dk_eff ≈ (εr+1)/2 + (εr−1)/2·(1+12h/w)^−0.5.
- f_knee = 0.5/tr; critical length ≈ tr/(6·tpd).
- Stub resonance f = c/(4·L·√Dk_eff).
- Wavelength in dielectric λ = c/(f·√Dk_eff); stitching via pitch ≤ λ/20.
- Skin depth δ = √(ρ/(π f μ)) ≈ 66 µm/√f[MHz] for copper (2.1 µm at 1 GHz).
- Loss estimates: α_d ≈ 2.3·f[GHz]·Df·√Dk dB/in; α_c ≈ 36·√f[GHz]/(w[mil]·Z0) dB/in (smooth).
- Impedance: IPC-2141 formulas in `signal-integrity.md` §2.
- Delay mismatch → length: ΔL = Δt / tpd (e.g. 1 ps ≈ 6 mil in FR-4 stripline).

## 4. PDN
- Ztarget = V·ripple% / ΔI.
- Plane capacitance C = ε0·εr·A/d.
- Capacitor impedance |Z| = √(ESR² + (2πf·ESL − 1/(2πf·C))²); SRF = 1/(2π√(ESL·C)).

## 5. Thermal
- ΔT = P·θ; T_j = T_a + P·θ_JA (JEDEC board only) — prefer Ψ_JB/Ψ_JT with measured board temperature.
- Via thermal resistance ≈ L/(k_Cu·π·d·t), k_Cu ≈ 390 W/m·K.

## 6. Spacing
- IPC-2221B Table 6-1 lookup (functional) → `pcb_calc.py ipc2221-spacing`. Safety creepage/clearance → product standard (see `high-voltage-safety.md`).

## 7. Aspect ratio & thickness
- AR = board (or span) thickness / finished drill; microvia AR = dielectric depth / laser diameter (≤ 1:1, target ≤ 0.8:1).
- Stack thickness = Σ pressed dielectric + Σ finished copper (inner copper partially embeds in prepreg: pressed PP thickness ≈ nominal − (1 − copper residual ratio)·copper thickness on each side).
