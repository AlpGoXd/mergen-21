# Bill of Materials

Complete component list for the Mergen-21 21 cm radio telescope.

> **Part number notes:** Mini-Circuits parts can be ordered directly from
> [minicircuits.com](https://www.minicircuits.com) using the model number as the
> ordering code, or through Mouser Electronics (manufacturer prefix **723-**).
> Distributor part numbers marked † should be verified at checkout; they are
> correct as of mid-2026 but stock codes occasionally change.

> **Currency:** USD prices are the reference (Mini-Circuits, Digi-Key, and
> Mouser price in USD). TRY figures are converted at **1 USD ≈ 47.35 TRY**
> (27 July 2026, exchange-rates.org / tradingeconomics.com) and will drift with
> the exchange rate; use the USD column for ordering, TRY for budgeting.

---

## RF Front-End

| Qty | Description | Manufacturer | Mfr Part No. | Mouser P/N | Approx. Price (USD) | Approx. Price (TRY) |
|-----|-------------|--------------|--------------|------------|---------------------|----------------------|
| 1 | Low-noise amplifier, 50–1600 MHz, NF 0.7 dB, G 19.7 dB | Mini-Circuits | ZX60-P162LN+ | 723-ZX60-P162LN+ † | $49.95 | ₺2,365 |
| 1 | Bandpass filter, 1450 MHz center, ~50 MHz BW | Mini-Circuits | ZX75BP-1450-S+ | 723-ZX75BP-1450-S+ † | $89.95 | ₺4,259 |
| 1 | Amplifier, 50–6000 MHz, G 20.8 dB | Mini-Circuits | ZX60-V63+ | 723-ZX60-V63+ † | $39.95 | ₺1,892 |

**Sub-total RF chain: ~$180 / ~₺8,523**

---

## SDR Backend

| Qty | Description | Manufacturer | Mfr Part No. | Digi-Key P/N | Approx. Price (USD) | Approx. Price (TRY) |
|-----|-------------|--------------|--------------|--------------|---------------------|----------------------|
| 1 | Software-defined radio, 70 MHz–6 GHz, 12-bit ADC | Analog Devices | ADALM-PLUTO | ADALM-PLUTO-ND † | $149–$249 | ₺7,055–₺11,790 |

---

## LDO Power Supply PCB

The PCB gerbers are in `hardware/ldo-regulator/gerbers/`. Fabricate at any PCB house (JLC, OSH Park, etc.): 2-layer, no special stack-up required.

| Qty | Description | Manufacturer | Mfr Part No. | Digi-Key P/N | Approx. Price (USD) | Approx. Price (TRY) |
|-----|-------------|--------------|--------------|--------------|---------------------|----------------------|
| 2 | Ultra-low-noise LDO regulator, 1 A, adjustable | Texas Instruments | TPS7A4701RGWT | 296-TPS7A4701RGWT-ND † | $3.50 each | ₺166 each |
| — | Resistors, capacitors (per schematic `hardware/ldo-regulator/schematic.pdf`) | Various | See BOM PDF | — | ~$5 total | ~₺237 total |
| 1 | PCB fabrication (double-sided, 2-layer) | — | — | — | ~$15–30 | ~₺710–₺1,420 |

**Sub-total LDO board: ~$30 / ~₺1,420**

---

## Antenna Structure

| Qty | Description | Specification | Supplier | Approx. Price (USD) | Approx. Price (TRY) |
|-----|-------------|---------------|----------|---------------------|----------------------|
| 1 set | Aluminum sheet for horn panels | Alloy 5754-H22, 1.5 mm thick, ~400 × 400 mm | Local metal supplier or online | ~$20 | ~₺947 |
| 1 | N-type female chassis connector (waveguide feed) | Amphenol RF 000-49000-SRFX | [Digi-Key](https://www.digikey.com/en/products/detail/amphenol-rf/000-49000-SRFX/4746416) | ~$8 | ~₺379 |
| 1 | Copper wire 1.0 mm diameter, ~50 mm | Pure copper | Electronics supplier | ~$1 | ~₺47 |
| 1 pkg | M3 × 30 mm stainless steel bolts (DIN 965TX), M3 × 8 mm (DIN 7985TX), M3 nuts (DIN 934), M3 flat + spring washers | A2-304 stainless steel | Hardware store | ~$8 | ~₺379 |

**Sub-total antenna: ~$37 / ~₺1,752**

---

## Cables and Adapters

| Qty | Description | Approx. Price (USD) | Approx. Price (TRY) |
|-----|-------------|---------------------|----------------------|
| 1 | SMA male – N-type male coaxial cable, ~0.3 m, 50 Ω | ~$12 | ~₺568 |
| 1–2 | SMA male–male adapter (as needed) | ~$5 | ~₺237 |

**Sub-total cables: ~$17 / ~₺805**

---

## Optional / Not Required for Basic Operation

| Qty | Description | Notes |
|-----|-------------|-------|
| 1 set | 3D-printed tripod mount | STL files in `hardware/antenna/stl/`; mount was prototyped but not used in final observations |

---

## Total System Cost

| Subsystem | Approx. Cost (USD) | Approx. Cost (TRY) |
|---|---|---|
| RF front-end | $180 | ₺8,523 |
| SDR (ADALM-PLUTO) | $149–$249 | ₺7,055–₺11,790 |
| LDO power supply board | $30 | ₺1,420 |
| Antenna structure | $37 | ₺1,752 |
| Cables and adapters | $17 | ₺805 |
| **Total** | **~$413–$513** | **~₺19,556–₺24,291** |

> The lower bound (~$413 / ~₺19,556) applies when the PlutoSDR is purchased at
> the student price or on sale. The main cost driver is the ADALM-PLUTO SDR and
> the ZX75BP-1450-S+ bandpass filter. Both can be substituted with cheaper
> alternatives at the cost of increased out-of-band interference. TRY figures
> use 1 USD ≈ 47.35 TRY (27 July 2026) and should be re-checked at time of
> purchase.

---

## Not Included (lab equipment)

The following items are assumed to be available in a university laboratory and are not included in the cost above:

- Vector network analyzer (for antenna and RF chain characterization): e.g. R&S ZNB8
- Spectrum analyzer with noise figure option (for NF and IP3 measurements)
- DC bench power supply (for LDO board)
- Soldering station

These instruments are only needed for the characterization labs (Lab 3). Labs 1, 2, and 4 do not require them.
