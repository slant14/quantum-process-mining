"""Load the merged QCM-Log event log for Paper 1 (issue #1).

    from load_log import load_log
    log = load_log()                 # version="raw"

The CSV is read with explicit types, so nothing is rounded or guessed:

- integer columns (start_unix_ns, duration_ns, event_index, ...) are pandas
  ``Int64``. Nanosecond Unix times (~1.8e18) do not fit exactly in float64,
  which is what pandas falls back to when a column has blanks; float64 would
  round 97 % of the start times (by up to 128 ns).
- ``opt_level``, ``seed``, ``topology`` and ``run`` (and every other text
  column) are strings: opt_level mixes "2" with "converge" and "default".
- ``is_container`` and ``ir_changed`` are nullable ``boolean``
  (ir_changed is blank on outcome events and on 96 Kirin events).
- only empty fields are missing values; strings such as "None" or "NA" are kept.

"raw" means only the types are set: no rows are dropped, renamed or derived.

On first use the log is written to paper1/data/event_log_raw.parquet, and
later calls read the Parquet copy. The copy is rebuilt when the CSV changes
(size or modification time differ from what the cache was built from).
Building the cache also writes paper1/data/CHECKSUMS.txt.

The CSV is found in this order: the ``csv_path`` argument, the QCM_LOG
environment variable, results/merged_v2/event_log.csv, data/QCM_event_log.csv.
"""
import hashlib
import json
import os
import warnings

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "paper1", "data")
CANDIDATES = [os.path.join(ROOT, "results", "merged_v2", "event_log.csv"),
              os.path.join(ROOT, "data", "QCM_event_log.csv")]

INT_COLS = ["event_index", "seq", "nesting_depth", "iteration", "start_unix_ns",
            "duration_ns", "size_before", "size_after", "mem_peak_bytes", "num_qubits", "rep"]
BOOL_COLS = ["is_container", "ir_changed"]
STR_COLS = ["case_id", "run_token", "toolchain", "phase", "activity", "activity_module",
            "pass_kind", "parent_activity", "changed_method", "circuit_id", "algorithm",
            "selection_tier", "portability_tier", "input_sha16", "topology", "run",
            "opt_level", "seed", "status", "error", "stage"]
COLUMNS = INT_COLS + BOOL_COLS + STR_COLS  # the 34 columns of event_log.csv
VERSIONS = ("raw",)


def find_csv(csv_path=None):
    for p in [csv_path, os.environ.get("QCM_LOG"), *CANDIDATES]:
        if p and os.path.exists(p):
            return os.path.abspath(p)
    raise FileNotFoundError("event log not found; pass csv_path, set QCM_LOG, or put it at "
                            + " or ".join(os.path.relpath(c, ROOT) for c in CANDIDATES))


def sha256(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    header = list(pd.read_csv(path, nrows=0).columns)
    if sorted(header) != sorted(COLUMNS):
        raise ValueError(f"unexpected columns in {path}: "
                         f"missing {sorted(set(COLUMNS) - set(header))}, "
                         f"extra {sorted(set(header) - set(COLUMNS))}")
    dtype = {**{c: "Int64" for c in INT_COLS}, **{c: "string" for c in STR_COLS + BOOL_COLS}}
    log = pd.read_csv(path, dtype=dtype, keep_default_na=False, na_values=[""])
    for c in BOOL_COLS:
        log[c] = log[c].map({"True": True, "False": False}).astype("boolean")
    return log[header]


def _source_id(path):
    st = os.stat(path)
    return {"csv": os.path.basename(path), "bytes": st.st_size, "mtime_ns": st.st_mtime_ns}


def load_log(version="raw", csv_path=None, cache=True):
    """Return the event log as a DataFrame (one row per event, file order)."""
    if version not in VERSIONS:
        raise ValueError(f"unknown version {version!r}; available: {VERSIONS}")
    src = find_csv(csv_path)
    pq = os.path.join(DATA, f"event_log_{version}.parquet")
    meta = pq + ".source.json"
    if cache and os.path.exists(pq) and os.path.exists(meta):
        with open(meta) as fh:
            if json.load(fh) == _source_id(src):
                try:
                    return pd.read_parquet(pq)
                except ImportError as e:  # no pyarrow / fastparquet: fall back to the CSV
                    warnings.warn(f"Parquet cache not read ({e}); reading the CSV")
                    return read_csv(src)
    log = read_csv(src)
    if cache:
        try:
            os.makedirs(DATA, exist_ok=True)
            log.to_parquet(pq, index=False)
        except ImportError as e:  # no pyarrow / fastparquet
            warnings.warn(f"Parquet cache not written ({e}); install paper1/requirements.txt")
            return log
        with open(meta, "w") as fh:
            json.dump(_source_id(src), fh)
        write_checksums(src, pq)
    return log


def write_checksums(csv_path, parquet_path):
    """SHA-256 of the source CSV and of the Parquet copy.

    The CSV hash identifies the dataset and must match across machines. The Parquet
    hash depends on the pyarrow version and is only a local record.
    """
    import pyarrow
    lines = [f"{sha256(csv_path)}  {os.path.basename(csv_path)}  "
             f"(source CSV, {os.path.getsize(csv_path):,} bytes)",
             f"{sha256(parquet_path)}  {os.path.basename(parquet_path)}  "
             f"(local cache, pandas {pd.__version__}, pyarrow {pyarrow.__version__}; "
             f"differs between machines)"]
    with open(os.path.join(DATA, "CHECKSUMS.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    log = load_log()
    print(f"{len(log):,} events, {log.case_id.nunique():,} cases")
    print(log.dtypes.to_string())
