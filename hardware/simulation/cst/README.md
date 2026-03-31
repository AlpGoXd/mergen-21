# CST Studio Suite Simulations

Electromagnetic simulations of the pyramidal horn antenna at 1420.405 MHz (HI 21 cm line), performed in CST Studio Suite using the frequency-domain tetrahedral solver with lossy materials (aluminum horn body, copper annealed coax elements, lossy PTFE dielectric).

## Simulation Models

### `ideal_horn/` — Ideal Parametric Horn

The baseline parametric model of the horn antenna with coaxial-to-waveguide coupling probe. Geometry is perfectly symmetric and gap-free. This is the reference design used for all dimension optimization.

**Files:**
- `ideal_hornfrfr_creator.mcs.bas` — CST VBA macro that rebuilds the entire model from scratch (geometry, materials, ports, solver settings). Run this in any CST installation to recreate the project.
- `ideal_hornfrfr_all_parameters.txt` — All design parameters with values and expressions
- `ideal_hornfrfr.stp` — STEP export of the 3D geometry
- `ideal_hornfrfr.s1p` — S11 Touchstone data
- `ideal_hornfrfr_farfield_phi0.txt` — Farfield cut at Phi=0 (E-plane)
- `ideal_hornfrfr_farfield_phi90.txt` — Farfield cut at Phi=90 (H-plane)
- `ideal_hornfrfr.pptx` — CST auto-generated report with plots

**Key Results (ideal):**
- Peak directivity: 16.9 dBi at boresight
- 3 dB beamwidth: ~26° (E-plane), ~22° (H-plane)
- First SLL: -36.9 dB (E-plane), -17.2 dB (H-plane)

### `assembly_worstcase/` — Realistic Sheet Metal Assembly

A worst-case simulation of the actual fabricated horn. The real sheet-metal assembly does not close perfectly due to bending tolerances and compound angles, leaving small gaps at the seams. This model includes:

- **Gap fill blocks** — Extra metal blocks placed where the horn panels don't meet, simulating the worst-case leakage geometry
- **All screws** modeled individually (not simplified)
- **Asymmetric geometry** — The assembly is intentionally non-symmetric, matching the physical build

This simulation checks how much the imperfect construction degrades performance compared to the ideal model.

**Files:**
- `hornffrfr_assembly_worstcase.stp` — STEP export of the assembly geometry
- `hornffrfr_assembly_worstcase.s1p` — S11 Touchstone data
- `hornffrfr_assembly_worstcase_phi0.txt` — Farfield cut at Phi=0 (E-plane)
- `hornffrfr_assembly_worstcase_phi90.txt` — Farfield cut at Phi=90 (H-plane)
- `hornffrfr_assembly_worstcase.pptx` — CST auto-generated report with plots

## Solver Settings

Both models use:
- **Solver:** Frequency-domain, tetrahedral mesh with adaptive refinement
- **Materials:** Lossy — Aluminum (σ = 3.56×10⁷ S/m) for horn body, Copper annealed (σ = 5.8×10⁷ S/m) for coax, lossy PTFE (εᵣ = 2.1, tan δ = 0.0002) for dielectric
- **Frequency range:** 1–2 GHz
- **Port:** Discrete face port at coaxial feed, 50 Ω

## Farfield Data Format

All farfield `.txt` files are standard CST exports with columns:
`Theta [deg] | Phi [deg] | Abs(Dir.) [dBi] | Abs(Theta) [dBi] | Phase(Theta) [deg] | Abs(Phi) [dBi] | Phase(Phi) [deg] | Ax.Ratio [dB]`

360 points covering theta = 0°→180°→0° (full cut).
