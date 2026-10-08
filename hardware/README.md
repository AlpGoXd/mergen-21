# Hardware

All hardware design files for the Mergen-21 21 cm radio telescope.

## Directory Structure

```
hardware/
├── antenna/            Horn antenna: CAD, drawings, DXF files, assembly photos
├── rf-chain/           RF front-end components: datasheets and S-parameter files
├── ldo-regulator/      Dual LDO power supply PCB (Altium, Gerbers, BOM, STEP)
└── simulation/
    ├── cst/            CST Studio Suite antenna EM simulations
    └── awr/            AWR Microwave Office RF cascade analysis
```

## Quick Overview

### Antenna (`antenna/`)

Pyramidal horn antenna fabricated from 1.5 mm aluminum sheet (alloy 5754-H22), laser-cut and bolted (M3, see [ASSEMBLY.md](antenna/ASSEMBLY.md)). Waveguide-to-coax transition uses an N-type connector with a copper probe.

| Subdirectory | Contents |
|---|---|
| `drawings/` | Dimensioned PDF drawings for each panel (E-plane, H-plane, backshort, waveguide) |
| `dxf/` | DXF laser-cutting files: send directly to a laser/waterjet cutter |
| `inventor/` | Autodesk Inventor parametric source files (.ipt, .iam) |
| `stl/` | STL exports of 3D-printed tripod mount parts |
| `3d-print/` | 3MF print file for the tripod adapter |
| `assembly-photos/` | Photographs from the fabrication and assembly process |
| `ASSEMBLY.md` | Step-by-step assembly instructions with photos |

Key numbers: S11 better than −30 dB from 1410 to 1440 MHz (ZNB8, 10 MHz grid; −41.8 dB at the 1420.000 MHz sample, so the null depth is not resolved); directivity 16.9 dBi (simulated).

### RF Chain (`rf-chain/`)

Three-stage front-end: LNA → bandpass filter → second amplifier. All Mini-Circuits SMA-connectorized modules.

| Stage | Component | Function |
|---|---|---|
| 1 | ZX60-P162LN+ | Low-noise amplifier |
| 2 | ZX75BP-1450-S+ | Bandpass filter (datasheet: 1 dB passband 1254–1625 MHz, 3 dB passband 1230–1645 MHz) |
| 3 | ZX60-V63+ | Second-stage amplifier |

`datasheets/` contains manufacturer PDFs. `datasheet-s-parameters/` contains Touchstone S2P files at three temperatures. See `COMPONENTS.md` for the cross-reference between datasheets, S-parameter files, and lab measurements.

### LDO Regulator (`ldo-regulator/`)

Custom dual-rail LDO PCB supplying clean DC to the two amplifiers. Two TPS7A4701RGWT ultra-low-noise LDOs. Designed in Altium Designer.

Fabrication-ready outputs: `gerbers/` (Gerber layers `PCB1_*.gbr` + NC drill file `PCB1.TXT`), `pick-and-place/` (assembly coordinates), `schematic.pdf`, `pcb.pdf`, `bom.pdf`, `PCB1.step`.

### Simulations (`simulation/`)

- `cst/`: Frequency-domain EM simulation of the horn antenna in CST Studio Suite. Includes a VBA macro (`ideal_hornfrfr_creator.mcs.bas`) that rebuilds the parametric model from scratch.
- `awr/`: Cascaded noise-figure and gain analysis of the RF chain in AWR Microwave Office. Exported results (S2P, PNG) are included so the plots can be reproduced with any S-parameter tool.

## Reproducing Designs

- **Horn antenna:** Send DXF files from `antenna/dxf/` to any laser or waterjet cutting service. Material: 1.5 mm aluminum sheet. Follow `antenna/ASSEMBLY.md`.
- **LDO PCB:** Send `ldo-regulator/gerbers/` to any PCB fabrication house. Components are listed in `ldo-regulator/bom.pdf`.
- **Simulations:** CST project can be rebuilt from the VBA macro. AWR exported S-parameter files can be re-analysed in any RF simulator or Python script.
