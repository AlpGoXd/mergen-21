# Pluto-terminated captures (band-center artifact and SDR noise floor)

Recorded on 2026-10-08 as a re-measurement, not during the April 2026 first-light session. The receiver chain was no longer available, so only the ADALM-Pluto was measured: a 50 ohm termination on its RX port and nothing else connected. The same Pluto, laptop and flowgraph (`software/gnuradio/receiver.grc`) were used as for first light: 2.048 MS/s, rx_gain 30 dB (manual), RF bandwidth 2 MHz, integration_time 1000 (1 s rows), 2048 channels at 1 kHz.

| File | LO (MHz) | Rows |
|---|---|---|
| `mergen21_spec_20261008_142108_pluto_term_LO1420405.dat` | 1420.405 | 112 |
| `mergen21_spec_20261008_142350_pluto_term_LO1420705.dat` | 1420.705 | 84 |
| `mergen21_spec_20261008_142618_pluto_term_LO1420105.dat` | 1420.105 | 103 |

What they show:
- **Band-center artifact.** With nothing connected, the narrow peak is present in all three files and sits at 0 kHz offset from whichever LO was set (about 73 to 76 times the 450–880 kHz noise floor in the center channel). It therefore follows the LO and originates in the SDR, not in the analog chain or the sky. Its absolute level is similar to the artifact in the April sky records (about 0.8 to 0.9 x 10^-9 here versus 1.1 x 10^-9 there, in the same arbitrary units).
- **SDR noise floor.** At LO 1420.405 MHz, the terminated-Pluto level in the line-free channels (450 to 880 kHz from the LO on both sides) is 4.0 % of the level in the April first-light sky records (W, S, E, both east records and the sweep: 3.9 to 4.1 %), taken with the same Pluto, gain and flowgraph scaling. The SDR therefore raises the system noise during observation by about 4 %, or 0.18 dB. This is a comparison across days and assumes the Pluto gain was unchanged; the original April comparison with the receiver connected was not archived.
- **April spur.** Nothing appears at +406 kHz with the input terminated at LO 1420.405 MHz, so the +406 kHz spur in the April east records entered through the antenna and receiver path, not from the Pluto itself.
- **Synthesizer spur at 1420.580 MHz.** The LO 1420.105 MHz file shows a steady single-channel spur at +475 kHz (RF 1420.580 MHz, about 7 times the floor, present in every row). The LO 1420.405 and 1420.705 MHz files cover the same RF frequency and show nothing there, and the spur is not at a fixed baseband offset, so it depends on the LO setting. With the input terminated, no other SDR running and 1400-1427 MHz closed to transmissions, it is a spur of the Pluto's fractional-N RF synthesizer at that LO setting. It does not affect the band-center result. Choosing the LO so that no spur falls on the line, and checking each LO setting with a terminated capture like these, avoids it.
