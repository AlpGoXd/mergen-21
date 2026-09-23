# Simulations

Computational models and exported results for the Mergen-21 antenna and RF chain.

## Subdirectories

### [`cst/`](cst/) — Antenna EM Simulation

Frequency-domain EM simulation of the pyramidal horn antenna in CST Studio Suite.

Two simulation cases:
- `ideal_horn/` — Parametric model with perfect geometry. Includes a VBA macro (`ideal_hornfrfr_creator.mcs.bas`) that rebuilds the entire model from scratch in any CST installation.
- `assembly_worstcase/` — Realistic model with fabrication imperfections (panel gaps, all screws modelled) to bound the tolerance sensitivity.

Exported results: S1P (S11 reflection), STEP (3D geometry), far-field pattern text files, and PDF report.

### [`awr/`](awr/) — RF Cascade Analysis

Cascaded noise-figure and gain analysis of the three-stage RF front-end in AWR Microwave Office.

Inputs: Mini-Circuits manufacturer noise-figure data for each amplifier (`.txt` files).  
Outputs: Cascaded S2P, gain plot PNG.

These results can be reproduced from the S-parameter and noise-figure files without running AWR — see `docs/lab-manual-01-simulate.md` for a Python-based approach.
