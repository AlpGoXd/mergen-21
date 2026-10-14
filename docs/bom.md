# Bill of Materials

Complete component list for the Mergen-21 21 cm radio telescope.

> **Part number notes:** Mini-Circuits parts can be ordered directly from
> [minicircuits.com](https://www.minicircuits.com) using the model number as the
> ordering code, or through Mouser Electronics (manufacturer prefix **723-**).
> Distributor part numbers marked † should be verified at checkout; they are
> correct as of mid-2026 but stock codes occasionally change.

> **Costs:** Approximate 2026 costs; prices change. These match Table III of
> the IEEE AP Magazine article. Exact per-item prices are not listed because
> they drift; check the distributor at the time of purchase.

---

## RF Front-End

| Qty | Description | Manufacturer | Mfr Part No. | Mouser P/N |
|-----|-------------|--------------|--------------|------------|
| 1 | Low-noise amplifier, 50–1600 MHz, NF 0.7 dB, G 19.7 dB | Mini-Circuits | ZX60-P162LN+ | 723-ZX60-P162LN+ † |
| 1 | Bandpass filter, 1450 MHz center, ~50 MHz BW | Mini-Circuits | ZX75BP-1450-S+ | 723-ZX75BP-1450-S+ † |
| 1 | Amplifier, 50–6000 MHz, G 20.8 dB | Mini-Circuits | ZX60-V63+ | 723-ZX60-V63+ † |

**RF amplifiers and filter: about $344**

---

## SDR Backend

| Qty | Description | Manufacturer | Mfr Part No. | Digi-Key P/N |
|-----|-------------|--------------|--------------|--------------|
| 1 | Software-defined radio, 70 MHz–6 GHz, 12-bit ADC | Analog Devices | ADALM-PLUTO | ADALM-PLUTO-ND † |

**ADALM-Pluto: about $230**

---

## LDO Power Supply PCB

The PCB gerbers are in `hardware/ldo-regulator/gerbers/`. Fabricate at any PCB house (JLC, OSH Park, etc.): 2-layer, no special stack-up required.

| Qty | Description | Manufacturer | Mfr Part No. | Digi-Key P/N |
|-----|-------------|--------------|--------------|--------------|
| 2 | Ultra-low-noise LDO regulator, 1 A, adjustable | Texas Instruments | TPS7A4701RGWT | 296-TPS7A4701RGWT-ND † |
| — | Resistors, capacitors (per schematic `hardware/ldo-regulator/schematic.pdf`) | Various | See BOM PDF | — |
| 1 | PCB fabrication (double-sided, 2-layer) | — | — | — |

**Regulator PCB and components: about $38**

---

## Horn Antenna

Horn (1.5 mm aluminum, laser cutting and bending): **about $175**, an estimated
replacement cost. The prototype horn was provided in kind. The parts it is
assembled from:

| Qty | Description | Specification | Supplier |
|-----|-------------|---------------|----------|
| 1 set | Aluminum sheet for horn panels | Alloy 5754-H22, 1.5 mm thick, ~400 × 400 mm | Local metal supplier or online |
| 1 | N-type female chassis connector (waveguide feed) | Amphenol RF 000-49000-SRFX | [Digi-Key](https://www.digikey.com/en/products/detail/amphenol-rf/000-49000-SRFX/4746416) |
| 1 | Copper wire 1.0 mm diameter, ~50 mm | Pure copper | Electronics supplier |
| 1 pkg | M3 × 30 mm stainless steel bolts (DIN 965TX), M3 × 8 mm (DIN 7985TX), M3 nuts (DIN 934), M3 flat + spring washers | A2-304 stainless steel | Hardware store |

---

## Cables and Adapters

| Qty | Description |
|-----|-------------|
| 1 | SMA male – N-type male coaxial cable, ~0.3 m, 50 Ω |
| 1–2 | SMA male–male adapter (as needed) |

**Cables and adapters: about $17**

---

## Optional / Not Required for Basic Operation

| Qty | Description | Notes |
|-----|-------------|-------|
| 1 set | 3D-printed tripod mount | STL files in `hardware/antenna/stl/`; mount was prototyped but not used in final observations |

---

## Total System Cost

| Category | Approx. cost (USD, 2026) |
|---|---|
| Horn (1.5 mm aluminum, laser cutting and bending; prototype provided in kind) | about $175, estimated replacement cost |
| RF amplifiers and filter | about $344 |
| ADALM-Pluto | about $230 |
| Regulator PCB and components | about $38 |
| Cables and adapters | about $17 |
| **Total dedicated hardware** | **about $804** |

Approximate 2026 costs; prices change. These match Table III of the IEEE AP Magazine article.

The total excludes the host computer, the cart and shared laboratory
instruments. The main cost drivers are the RF amplifiers and filter and the
ADALM-Pluto SDR; the bandpass filter and the SDR can be substituted with
cheaper alternatives at the cost of increased out-of-band interference.

---

## Not Included (lab equipment)

The following items are assumed to be available in a university laboratory and are not included in the cost above:

- Vector network analyzer (for antenna and RF chain characterization): e.g. R&S ZNB8
- Spectrum analyzer with noise figure option (for NF and IP3 measurements)
- DC bench power supply (for LDO board)
- Soldering station
- Host computer and cart (also excluded from the total above)

These instruments are only needed for the characterization labs (Lab 3). Labs 1, 2, and 4 do not require them.
