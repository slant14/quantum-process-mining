#!/usr/bin/env python3
"""Validate + normalize the exported survey sheet into a deterministic CSV.

Handles a two-row banded header: if the export begins with a group-band row
(few populated cells, e.g. "A. Screening & Scope"), the real field-name row
directly below it is detected and used. Config contract is unchanged:
  SORT_KEY, REQUIRED_COLS (comma list), SKIP_ID_PREFIX  (all via env)
"""
import csv, os, sys

SRC, OUT = sys.argv[1], sys.argv[2]
SORT_KEY = os.environ.get("SORT_KEY", "")
REQUIRED = [c.strip() for c in os.environ.get("REQUIRED_COLS", "").split(",") if c.strip()]
SKIP_PREFIX = os.environ.get("SKIP_ID_PREFIX", "")
MAX_HEADER_SCAN = 5  # look at most this many top rows for the field-name row

with open(SRC, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))
if not rows:
    sys.exit("FATAL: empty export — refusing to commit.")


def trimmed(row):
    """Row copy with trailing empties dropped."""
    r = [c.strip() for c in row]
    while r and not r[-1]:
        r.pop()
    return r


# ---- locate the real header (field-name) row ----------------------------
# Anchor tokens we expect to find in the true header. SORT_KEY + REQUIRED are
# the columns the pipeline actually depends on, so the header is the first
# scanned row that contains them (all of them if any are configured).
anchors = [c for c in ([SORT_KEY] if SORT_KEY else []) + REQUIRED if c]
header_idx = None
if anchors:
    for i in range(min(MAX_HEADER_SCAN, len(rows))):
        cells = {c.strip() for c in rows[i]}
        if all(a in cells for a in anchors):
            header_idx = i
            break
    if header_idx is None:
        sys.exit(
            "FATAL: no row in the first "
            f"{MAX_HEADER_SCAN} contains all anchor columns {anchors} — "
            "check the export range / gid."
        )
else:
    # No anchors configured: pick the densest of the first few rows.
    header_idx = max(
        range(min(MAX_HEADER_SCAN, len(rows))),
        key=lambda i: len(trimmed(rows[i])),
    )

header = trimmed(rows[header_idx])
if not header:
    sys.exit("FATAL: detected header row is empty — check the gid.")
width = len(header)

# ---- collect data rows (everything below the header) --------------------
data = []
for r in rows[header_idx + 1:]:
    r = [c.strip() for c in r] + [""] * (width - len(r))
    if any(r[:width]):
        data.append(r[:width])

# drop template/example rows by ID prefix
if SKIP_PREFIX and SORT_KEY in header:
    i = header.index(SORT_KEY)
    data = [r for r in data if not r[i].startswith(SKIP_PREFIX)]

# ---- validation ---------------------------------------------------------
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
                errors.append(
                    f"row {n}: duplicate {SORT_KEY} '{r[i]}' (also row {seen[r[i]]})"
                )
            seen[r[i]] = n
if errors:
    for e in errors[:25]:
        print("  " + e, file=sys.stderr)
    sys.exit(f"FATAL: {len(errors)} validation error(s).")

# ---- deterministic sort + write ----------------------------------------
if SORT_KEY and SORT_KEY in header:
    i = header.index(SORT_KEY)
    data.sort(key=lambda r: (r[i].lower(), r))

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(header)
    w.writerows(data)

note = "" if header_idx == 0 else f" (skipped {header_idx} band row(s))"
print(f"OK: {len(data)} rows, {width} cols -> {OUT}{note}", file=sys.stderr)
