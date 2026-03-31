#!/usr/bin/env python3
"""
Sanitize VNA serial numbers from .s2p (and .sNp) Touchstone files.
 
Replaces the serial number in the *IDN?-style comment line with "REDACTED".
Handles Rohde & Schwarz, Keysight, Agilent, and similar VNA formats.
 
Usage:
    python sanitize_s2p.py <file_or_folder> [--in-place]
 
Examples:
    python sanitize_s2p.py measurements/           # preview changes
    python sanitize_s2p.py measurements/ --in-place # apply changes
    python sanitize_s2p.py my_file.s2p --in-place   # single file

    Vibecoded with claude opus 4.6

"""
 
import argparse
import re
from pathlib import Path
 
# Matches lines like: ! Rohde-Schwarz,ZNB8-4Port,XXXXXXX,X.XX
# Captures: prefix (manufacturer,model,) + serial + suffix (,firmware)
IDN_PATTERN = re.compile(
    r"^(!\s*"
    r"(?:Rohde[\s&-]*Schwarz|Keysight|Agilent|Anritsu|Copper\s*Mountain)"  # manufacturer
    r"\s*,\s*"
    r"[^,]+"           # model
    r"\s*,\s*)"
    r"([A-Za-z0-9]+)"  # serial number
    r"(\s*,\s*.*)$",   # firmware version etc.
    re.IGNORECASE,
)
 
 
def sanitize_file(path: Path, in_place: bool = False) -> bool:
    """Sanitize a single file. Returns True if a serial was found."""
    text = path.read_text(encoding="utf-8", errors="replace")
    new_lines = []
    found = False
 
    for line in text.splitlines(keepends=True):
        m = IDN_PATTERN.match(line.rstrip("\r\n"))
        if m:
            found = True
            original_serial = m.group(2)
            sanitized = m.group(1) + "REDACTED" + m.group(3)
            # preserve original line ending
            ending = line[len(line.rstrip("\r\n")):]
            new_lines.append(sanitized + ending)
            print(f"  {path.name}: {original_serial} -> REDACTED")
        else:
            new_lines.append(line)
 
    if found and in_place:
        path.write_text("".join(new_lines), encoding="utf-8")
        print(f"  ✓ Saved {path.name}")
 
    return found
 
 
def main():
    parser = argparse.ArgumentParser(description="Strip VNA serial numbers from Touchstone files.")
    parser.add_argument("target", help="File or folder to process")
    parser.add_argument("--in-place", action="store_true", help="Modify files (default is dry-run preview)")
    args = parser.parse_args()
 
    target = Path(args.target)
    snp_pattern = re.compile(r"\.s\d+p$", re.IGNORECASE)
 
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(f for f in target.rglob("*") if snp_pattern.search(f.suffix.lower()))
    else:
        print(f"Error: '{target}' not found.")
        return
 
    if not files:
        print("No Touchstone files found.")
        return
 
    if not args.in_place:
        print("DRY RUN (use --in-place to apply changes)\n")
 
    count = 0
    for f in files:
        if sanitize_file(f, in_place=args.in_place):
            count += 1
 
    print(f"\n{'Modified' if args.in_place else 'Would modify'} {count}/{len(files)} file(s).")
 
 
if __name__ == "__main__":
    main()