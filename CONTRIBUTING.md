# Contributing to Mergen-21

This project is a graduation research effort at Ozyegin University. **Open-source contributions are welcome.**

## Current Status

- **Public repository** (owned by Alp Gokalp, Ozyegin University)
- First-light observations complete (2026-04-29); science-grade analysis in progress

## Code of Conduct

Be respectful, constructive, and collaborative. Discrimination, harassment, or bad-faith arguments are not tolerated.

## For Future Contributors (After Public Release)

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r software/requirements.txt`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make changes; test locally (especially GNU Radio flowgraphs)
5. Commit with descriptive messages: `[category] Description`
   - Categories: `[docs]`, `[software]`, `[hardware]`, `[measurement]`, `[fix]`
6. Push & create a pull request

### Areas for Contribution

- **Software:** GNU Radio improvements, Python analysis enhancements
- **Hardware:** RFI mitigation, dual-pol receiver design, tracking mount firmware
- **Documentation:** Clarifications, tutorials, translation to other languages
- **Science:** Calibration improvements, rotation curve extraction algorithms

### Licensing

All contributions must be compatible with:
- **Hardware:** CERN-OHL-S v2 (reciprocal, share-alike)
- **Software:** GPL-3.0 (copyleft, share-alike)
- **Documentation:** CC-BY-SA 4.0 (attribution, share-alike)

By submitting a pull request, you agree to license your contribution under these terms.

## Questions or Suggestions?

Open a GitHub issue for discussion. Please include:
- Problem/idea description
- Relevant context (hardware config, software version, measurements if applicable)
- Proposed solution (if you have one)
