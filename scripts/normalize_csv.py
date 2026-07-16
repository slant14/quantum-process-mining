#!/usr/bin/env python3
"""Validate + normalize the exported SLR sheet into a deterministic CSV."""
import csv, os, sys

SRC, OUT = sys.argv[1], sys.argv[2]
SORT_KEY = os.environ.get("SORT_KEY", "")
REQUIRED = [c.strip() for c in os.environ.get("REQUIRED_COLS", "").split(",") if c.strip()]

with open(SRC, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))

if not rows:
    sys.exit("FATAL: empty export — refusing to commit.")

header = [h.strip() for h in rows[0]]
width = len(header)

data = []
for r in rows[1:]:
    r = [c.strip() for c in r] + [""] * (width - len(r))
    if any(r[:width]):
        data.append(r[:width])

errors = []
for col in REQUIRED:
    if col not in header:
        errors.append(f"missing column: {col}")
if not errors:
    for col in REQUIRED:
        i = header.index(col)
        for n, r in enumerate(data, start=2):
            if not r[i]:
                errors.append(f"row {n}: empty required '{col}'")
    if SORT_KEY and SORT_KEY in header:
        i = header.index(SORT_KEY)
        seen = {}
        for n, r in enumerate(data, start=2):
            if r[i] in seen:
                errors.append(f"row {n}: duplicate {SORT_KEY} '{r[i]}' (also row {seen[r[i]]})")
            seen[r[i]] = n
if errors:
    for e in errors[:25]:
        print("  " + e, file=sys.stderr)
    sys.exit(f"FATAL: {len(errors)} validation error(s).")

if SORT_KEY and SORT_KEY in header:
    i = header.index(SORT_KEY)
    data.sort(key=lambda r: (r[i].lower(), r))

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(header)
    w.writerows(data)
print(f"OK: {len(data)} rows -> {OUT}", file=sys.stderr)
