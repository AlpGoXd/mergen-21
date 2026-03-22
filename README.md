# Mergen-21: Low-Cost 21 cm Hydrogen Line Radio Telescope

A low-cost radio telescope system for observing the 21 cm hydrogen emission line (1420.405 MHz), designed and built as an EE401 graduation project at Özyeğin University.

**Primary science goal:** Mapping the Milky Way's galactic rotation curve via the tangent-point method from Istanbul, Turkey.

## System Overview

### Antenna
- **Type:** Pyramidal horn antenna
- **Design frequency:** 1420.405 MHz (HI 21 cm line)
- **Material:** Sheet-metal aluminum (1.5 mm)
- **Simulation:** CST Studio Suite (full-wave EM)

### RF Chain
| Stage | Component | Function |
|-------|-----------|----------|
| 1 | ZX60-P162LN+ | Low-noise amplifier (LNA) |
| 2 | ZX75BP-1450-S+ | Bandpass filter (1450 MHz center) |
| 3 | ZX60-V63+ | Second-stage amplifier |

### Backend
- **SDR:** RTL-SDR / other SDR receiver
- **Software:** GNU Radio for signal acquisition and processing
- **Analysis:** Python (NumPy, SciPy, Matplotlib, Astropy)

### Mechanical
- Horn antenna fabricated from laser-cut aluminum sheet metal
- Waveguide-to-coax transition with N-type connector
- 3D-printed tripod adapter (ASA filament) for HLYPRO HPR-404 tripod
- CAD: Autodesk Inventor

## Repository Structure

```
mergen-21/
├── simulation/
│   ├── cst/              # CST Studio Suite project files & results
│   └── awr/              # AWR Microwave Office cascade/matching sims
├── mechanical/
│   ├── inventor/          # Autodesk Inventor source files (.ipt, .iam)
│   ├── drawings/          # 2D engineering drawings (PDF, dimensioned views)
│   ├── dxf/              # Laser-cutting DXF exports
│   ├── stl/              # 3D print STL files
│   └── 3d-print/         # Print profiles & settings
├── rf-chain/
│   ├── datasheets/        # Component datasheets
│   ├── docs/              # RF chain documentation & cascade analysis
│   └── schematics/        # Schematic diagrams
├── software/
│   ├── gnuradio/          # GNU Radio flowgraphs (.grc)
│   └── analysis/          # Python observation analysis scripts
├── observations/
│   ├── data/              # Raw observation data files
│   └── plots/             # Generated plots & figures
└── docs/
    ├── build-log/         # Build progress notes & diary
    └── photos/            # Build photos & documentation
```

## Getting Started

### Prerequisites
- **GNU Radio** (with RTL-SDR source block)
- **Python 3.8+** with: `numpy`, `scipy`, `matplotlib`, `astropy`
- **CST Studio Suite** (for antenna simulation files)
- **AWR Microwave Office** (for RF chain simulations)
- **Autodesk Inventor** (for mechanical CAD files)

### Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/mergen-21.git
cd mergen-21
pip install -r software/requirements.txt
```

## Observation Site
- **Location:** Istanbul, Turkey (~41.0°N, 29.0°E)
- **Target:** Galactic plane HI emission at various galactic longitudes
- **Method:** Tangent-point method for rotation curve extraction

## Licensing
- **Hardware** (antenna, mechanical, RF chain designs): [CERN Open Hardware Licence Version 2 — Strongly Reciprocal (CERN-OHL-S v2)](LICENSE-HARDWARE)
- **Software** (GNU Radio flowgraphs, Python scripts): [GNU General Public License v3.0 (GPL-3.0)](LICENSE-SOFTWARE)
- **Documentation & Photos:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Acknowledgments
- **Supervisors:** Prof. Mohammed Elamassie & Prof. Ahmed Akgiray — Özyeğin University
- **Inspired by:** Open-source radio astronomy projects and the amateur radio community

## Author
**Alp Gökalp** — Electrical & Electronics Engineering, Özyeğin University (Class of 2026)
