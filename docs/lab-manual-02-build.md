# Lab Manual 2: Build

**Topic:** Fabricating and assembling the Mergen-21 horn antenna and LDO power supply  
**Estimated time:** 4–6 hours (plus external fabrication lead time)  
**Prerequisites:** Basic hand-tool skills; access to a laser or waterjet cutting service; soldering capability

---

## Learning Objectives

After completing this lab, students will be able to:

1. Prepare DXF files for laser or waterjet cutting of sheet-metal antenna panels.
2. Assemble a pyramidal horn antenna from flat sheet-metal parts.
3. Fabricate a waveguide-to-coax transition using a standard N-type connector.
4. Solder the probe feed element and verify continuity.
5. Order a simple two-layer PCB from a fabrication service using Gerber files.

---

## Safety Notes

- **Laser cutting:** Wear appropriate eye protection. All cuts generate aluminum dust; use a filtered mask and ensure adequate ventilation.
- **Soldering:** Work in a ventilated area. Allow the soldering iron and workpiece to cool before handling.
- **Sheet metal edges:** Cut aluminum edges are sharp. Deburr all edges with a file or sandpaper before handling.

---

## Part A: Horn Antenna Fabrication

### Files Needed

| File | Location | Purpose |
|---|---|---|
| E-plane DXF | `hardware/antenna/dxf/eplane_v0.3.dxf` | Laser cutting template |
| H-plane DXF | `hardware/antenna/dxf/hplane_v0.3.dxf` | Laser cutting template |
| Backshort DXF | `hardware/antenna/dxf/backshort_0.1.dxf` | Laser cutting template |
| Waveguide DXF | `hardware/antenna/dxf/wave_0.1.dxf` | Laser cutting template |
| E-plane drawing (PDF) | `hardware/antenna/drawings/eplane_v0.3.pdf` | Dimensioned reference |
| H-plane drawing (PDF) | `hardware/antenna/drawings/hplane_v0.3.pdf` | Dimensioned reference |
| Backshort drawing (PDF) | `hardware/antenna/drawings/backshort_0.1-1.pdf` | Dimensioned reference |
| Waveguide drawing (PDF) | `hardware/antenna/drawings/wave_0.1.pdf` | Dimensioned reference |
| Assembly instructions | `hardware/antenna/ASSEMBLY.md` | Step-by-step assembly |

### Materials

| Item | Specification | Quantity |
|---|---|---|
| Aluminum sheet | Alloy 5754-H22, 1.5 mm thick | Approximately 400 × 400 mm |
| N-type female chassis connector | Amphenol RF 000-49000-SRFX (or equivalent) | 1 |
| Copper wire | 1.0 mm diameter, bare (not insulated) | ~50 mm |
| M3 × 30 mm bolts (DIN 965TX, stainless A2-304) | — | 12 |
| M3 × 8 mm bolts (DIN 7985TX, stainless A2-304) | — | 12 |
| M3 flat washers (DIN 125, stainless) | — | 24 |
| M3 spring washers (DIN 127, stainless) | — | 24 |
| M3 hex nuts (DIN 934, stainless A2-304) | — | 24 |

### Procedure

#### A1: Order laser-cut parts

Send the four DXF files in `hardware/antenna/dxf/` to a sheet-metal fabrication service with the following instructions:

- **Material:** Aluminum alloy 5754-H22, **1.5 mm thick** (not thicker; the tolerance stack matters for the waveguide fit)
- **Process:** Laser or waterjet cutting
- **Flatness:** ≤ 0.5 mm deviation over any 200 mm span; specify this explicitly. Poor flatness is the most common problem.
- **Bending (if applicable):** The waveguide and backshort parts may require bending. Provide PDF drawings with explicit bend angles. **Verify angles with the shop before production**; the original build encountered 90° bending errors.

> **Tolerance note:** The DXF files encode the nominal geometry. The backshort-to-probe distance is the most sensitive dimension (affects resonance frequency). Allow ±0.5 mm on this dimension; all other dimensions can be ±1 mm.

Allow **5–10 business days** for cutting and shipping.

#### A2: Prepare the N-type connector and feed probe

While waiting for parts:

1. Cut a 38 mm length of 1.0 mm copper wire. The wire must be **pure copper** (not copper-clad steel) and completely bare (no insulation).
2. Tin the inner contact of the N-type connector with a small amount of solder.
3. Solder the copper wire perpendicular to the connector contact, centered and straight.
4. Inspect under magnification: the joint must be shiny and mechanically rigid. A cold or cracked joint will cause poor S11.
5. Allow to cool. Do not bend the wire after soldering.

#### A3: Deburr and inspect parts

When parts arrive:

1. Inspect each panel for flatness using a steel straightedge. Reject panels with more than 0.5 mm deviation.
2. Deburr all cut edges with a fine file or 320-grit sandpaper. Remove any sharp burrs around bolt holes.
3. Check that bolt holes are clean and correctly positioned; compare to the PDF drawings.

#### A4: Mechanical assembly

Follow the step-by-step instructions in `hardware/antenna/ASSEMBLY.md`. Key points:

- Use M3×30 bolts initially to align panels, then swap to M3×8 bolts for final tightening.
- Tighten in a cross-pattern. Recommended torque: 0.5–1.0 Nm (finger-tight plus ~1/8 turn).
- Install the N-type connector and feed probe **last**, after the outer structure is assembled.
- **Check the feed probe depth** against the drawing (`backshort_0.1-1.pdf`). The probe depth above the waveguide floor is a critical dimension.

#### A5: Visual inspection before electrical test

Before any RF measurement, verify:

- [ ] All panels are flush with no visible gaps at seams
- [ ] Feed probe is vertical and centered in the waveguide aperture
- [ ] N-type connector body is fully seated and the retaining nut is tight
- [ ] No metal chips or debris inside the waveguide (use a torch and mirror to inspect)
- [ ] The center conductor of the N-type connector is not shorted to the body (check with a multimeter; it should be open circuit, not 0 Ω)

---

## Part B: LDO Power Supply Board

The LDO board provides clean, low-noise DC power to the two RF amplifiers (ZX60-P162LN+ and ZX60-V63+). Both amplifiers require +5 V. The board uses two TPS7A4701RGWT ultra-low-noise LDO regulators.

### Files Needed

| File | Location |
|---|---|
| Gerber files (PCB fabrication) | `hardware/ldo-regulator/gerbers/` |
| Pick-and-place file | `hardware/ldo-regulator/pick-and-place/Pick Place for PCB1.txt` |
| Bill of materials | `hardware/ldo-regulator/bom.pdf` |
| Schematic | `hardware/ldo-regulator/schematic.pdf` |
| PCB layout | `hardware/ldo-regulator/pcb.pdf` |
| 3D STEP model (mechanical reference) | `hardware/ldo-regulator/PCB1.step` |

### Procedure

#### B1: Order the PCB

Send the entire contents of `hardware/ldo-regulator/gerbers/` to a PCB fabrication service (JLC PCB, OSH Park, PCBWay, etc.) with the following specification:

- **Layers:** 2 (double-sided)
- **Thickness:** 1.6 mm FR4
- **Copper weight:** 1 oz
- **Surface finish:** HASL or ENIG
- **Color:** Any (green is cheapest)

Allow 5–10 business days for fabrication and shipping. Cost is typically $15–30 for 5 boards.

#### B2: Assemble the board

Components are listed in `bom.pdf`. Use the pick-and-place file as a reference for component positions.

1. Apply solder paste to all SMD pads using a stencil or manually.
2. Place the TPS7A4701RGWT ICs first (they are QFN packages; use tweezers and a microscope or magnifier).
3. Place passive components (resistors, capacitors).
4. Reflow-solder (preferred) or hand-solder with a fine-tip iron.
5. Inspect all joints under magnification.

#### B3: Initial power-on and verification

Before connecting any RF components:

1. Set a bench power supply to 7–12 V input (within the TPS7A4701RGWT input range).
2. Connect to the board input with current limiting set to 100 mA.
3. Power on and verify:
   - Input current should be < 20 mA at no load
   - Output voltage should be 5.0 V ±0.1 V at each output
   - No excessive heat from any component

If the output voltage is incorrect, check the resistor divider values against `schematic.pdf`. The TPS7A4701 output is set by an external resistor network.

---

## Mechanical Tolerances

These are the critical dimensions and their allowed deviations, derived from the simulation tolerance study (see `hardware/simulation/cst/assembly_worstcase/`):

| Dimension | Nominal | Max allowed deviation | Effect of exceedance |
|---|---|---|---|
| Backshort-to-probe distance | Per drawing | ±0.5 mm | Shifts resonance frequency, degrades S11 |
| Probe wire length above waveguide floor | 38 mm | ±0.5 mm | Changes coupling depth, affects S11 depth |
| Panel flatness | 0 mm deflection | ±0.5 mm over 200 mm | Gap-induced current leakage, pattern distortion |
| Panel seam gaps | 0 mm | <0.3 mm | Allows RF leakage at seams |
| Aluminum sheet thickness | 1.5 mm | ±0.1 mm | Affects internal waveguide dimensions |
| Bolt hole diameter | 3.2 mm (for M3) | ±0.1 mm | If too large, panel alignment is poor |

**The most consequential dimensions** are the probe depth and backshort distance. These directly control the impedance matching at 1420 MHz. If S11 is worse than −15 dB, start by checking these two.

---

## Common Problems and Solutions

| Problem | Likely Cause | Solution |
|---|---|---|
| S11 poor (> −10 dB) at 1420 MHz | Probe depth or backshort incorrect | Re-measure probe length; compare to drawings |
| S11 resonance is offset in frequency | Sheet thickness different from 1.5 mm | Check material spec; re-order if needed |
| Antenna feels mechanically unstable | Bolts undertightened or wrong size | Re-tighten in cross-pattern; verify M3 specification |
| LDO board output is wrong voltage | Wrong resistor values | Check schematic, verify with ohmmeter before soldering |
| Feed probe shorts to waveguide body | Wire bent during assembly | Straighten probe; verify clearance with multimeter |

---

## Next Steps

After successfully assembling and visually inspecting the antenna and LDO board, proceed to **Lab 3: Measure** to characterize the antenna S11 and RF chain performance with a VNA.
