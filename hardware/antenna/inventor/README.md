# Autodesk Inventor CAD Files

Horn antenna, waveguide flange, and tripod adapter.

## Note on Assembly

The full assembly will not constrain properly in Inventor due to compound angles at the horn-to-waveguide and waveguide-to-flange joints. Individual parts are dimensionally correct and assemble fine in real life — the CAD assembly is provided for reference only, not as a fully constrained model.

## Files

- `*.ipt` — Part files
- `*.iam` — Assembly files (partially constrained, see note above)
- Sheet metal parts: 1.5 mm aluminum

## Export Workflow

- STEP exports (`.stp`) for interchange — keep alongside source `.ipt`/`.iam` files
- DXF exports for laser cutting → `../dxf/`
- STL exports for 3D printing → `../stl/`
