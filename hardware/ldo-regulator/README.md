# LDO Regulator Board

Dual LDO power supply board for the RF chain amplifiers (ZX60-P162LN+ and ZX60-V63+). Provides clean, low-noise DC rails using two TPS7A4701RGWT ultralow-noise regulators.

Designed in Altium Designer.

## Contents

| Path | Description |
|------|-------------|
| `altium/` | Altium Designer source files (schematic + PCB project) |
| `gerbers/` | Fabrication-ready Gerber and NC drill files |
| `pick-and-place/` | Assembly pick-and-place coordinates (Altium export) |
| `schematic.pdf` | Circuit schematic (PDF export) |
| `pcb.pdf` | PCB layout (PDF export) |
| `bom.pdf` | Bill of materials |
| `PCB1.step` | 3D STEP model for mechanical integration |

## Board Details

- **Regulator IC:** TPS7A4701RGWT (x2) — ultralow-noise, 1 A LDO
- **Purpose:** Supply clean DC power to RF chain amplifiers
- **Protection:** PTC fuse, LED power indicator
- **Design tool:** Altium Designer
