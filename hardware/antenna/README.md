# Horn Antenna

Pyramidal horn antenna for 1420.405 MHz (21 cm hydrogen line), fabricated from 1.5 mm aluminium sheet (alloy 5754-H22) by laser cutting and riveting.

## Directory Contents

| Path | What's in it |
|---|---|
| [`drawings/`](drawings/) | Dimensioned PDF drawings for each panel — use these as fabrication reference |
| [`dxf/`](dxf/) | DXF laser-cutting files — send these directly to a cutting service |
| [`inventor/`](inventor/) | Autodesk Inventor source files (.ipt parts, .iam assembly) |
| [`stl/`](stl/) | STL export of 3D-printed tripod mount parts |
| [`3d-print/`](3d-print/) | 3MF print file for the tripod adapter |
| [`assembly-photos/`](assembly-photos/) | Photographs from fabrication and assembly |
| [`ASSEMBLY.md`](ASSEMBLY.md) | Step-by-step assembly guide with photos |

## Key Performance (Measured)

| Parameter | Value |
|---|---|
| S11 at 1420.4 MHz | −42 dB |
| Design frequency | 1420.405 MHz (HI line) |
| Simulated directivity | 16.9 dBi |
| Simulated 3 dB beamwidth | 26° (E-plane), 22° (H-plane) |
| Material | Aluminium 5754-H22, 1.5 mm |
| Connector | N-type (Amphenol RF 000-49000-SRFX) |

## To Reproduce

1. Send the four DXF files from `dxf/` to a laser-cutting service. Specify: aluminium alloy 5754-H22, 1.5 mm thick, flatness ≤ 0.5 mm over 200 mm span.
2. Order the N-type connector (DigiKey: see `ASSEMBLY.md`).
3. Follow `ASSEMBLY.md` for assembly.
4. Verify with VNA — expected S11 < −20 dB at 1420.4 MHz.

EM simulation files are in [`../../simulation/cst/`](../../simulation/cst/).
