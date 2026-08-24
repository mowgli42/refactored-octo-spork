#!/usr/bin/env python3
"""
Convert NASA DASHlink-style MATLAB flight segments to aligned CSV / Parquet.

Supports:
  - Real DASHlink .mat files (parameter arrays at heterogeneous rates)
  - Fixture .mat produced by create_dashlink_fixture.py

Usage:
  python scripts/convert_dashlink.py --mat path/to/file.mat --out-dir sample-data/dashlink_converted/ --hz 2
  python scripts/convert_dashlink.py --mat-dir sample-data/dashlink_fixture --out-dir sample-data/dashlink_converted/
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat

DEFAULT_NAME_MAP = {
    "ALT": "altitude_ft",
    "CAS": "airspeed_kt",
    "IAS": "airspeed_kt",
    "PTCH": "pitch_deg",
    "ROLL": "roll_deg",
    "HDG": "heading_deg",
    "N1": "core_speed_pct",
    "GLS": "glideslope_dev_pct",
    "LOC": "localizer_dev_pct",
    "HYDG": "hyd_low_green",
    "HYDY": "hyd_low_yellow",
    "APUF": "apu_fire_warning",
    "AOA": "aoa_deg",
    "VRTG": "g_force",
    "WS": "wind_speed_kt",
    "WD": "wind_dir_deg",
}


def _find_arrays(mat: dict) -> dict[str, np.ndarray]:
    skip = {"__header__", "__version__", "__globals__"}
    out = {}
    for k, v in mat.items():
        if k in skip or k.startswith("_"):
            continue
        arr = np.asarray(v).ravel()
        if arr.size == 0:
            continue
        if np.issubdtype(arr.dtype, np.number) or arr.dtype == object:
            try:
                out[k] = arr.astype(float)
            except (ValueError, TypeError):
                continue
    return out


def _guess_rate(n: int, rates_hint: dict[str, float], key: str) -> float:
    if key in rates_hint:
        return rates_hint[key]
    if n >= 500:
        return 16.0
    if n >= 200:
        return 8.0
    if n >= 50:
        return 2.0
    return 1.0


def convert_mat(
    mat_path: Path,
    out_dir: Path,
    target_hz: float = 2.0,
    name_map: dict[str, str] | None = None,
    rates_hint: dict[str, float] | None = None,
    start_time: datetime | None = None,
) -> Path:
    name_map = name_map or DEFAULT_NAME_MAP
    rates_hint = rates_hint or {}
    mat = loadmat(str(mat_path), squeeze_me=True, struct_as_record=False)
    arrays = _find_arrays(mat)
    if not arrays:
        raise SystemExit(f"No numeric arrays found in {mat_path}")

    durations = []
    for k, arr in arrays.items():
        rate = _guess_rate(len(arr), rates_hint, k)
        durations.append(len(arr) / rate)
    duration_s = max(durations)
    n_out = max(2, int(duration_s * target_hz))
    t_out = np.linspace(0, duration_s, n_out, endpoint=False)

    rows: dict[str, np.ndarray] = {}
    used = []
    for src, arr in arrays.items():
        dst = name_map.get(src, src.lower())
        rate = _guess_rate(len(arr), rates_hint, src)
        t_src = np.arange(len(arr)) / rate
        rows[dst] = np.interp(t_out, t_src, arr.astype(float))
        used.append({"source": src, "dest": dst, "n": int(len(arr)), "rate_hz": rate})

    start = start_time or datetime(2010, 1, 1, 12, 0, tzinfo=timezone.utc)
    stem = mat_path.stem
    if len(stem) >= 15 and stem[-12:].isdigit():
        try:
            y, mo, d = int(stem[-12:-8]), int(stem[-8:-6]), int(stem[-6:-4])
            hh, mm = int(stem[-4:-2]), int(stem[-2:])
            start = datetime(y, mo, d, hh, mm, tzinfo=timezone.utc)
        except ValueError:
            pass

    df = pd.DataFrame(rows)
    df.insert(
        0,
        "timestamp",
        [(start + timedelta(seconds=float(s))).isoformat() for s in t_out],
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    base = mat_path.stem
    csv_path = out_dir / f"{base}_aligned.csv"
    pq_path = out_dir / f"{base}_aligned.parquet"
    meta_path = out_dir / f"{base}_conversion_meta.json"

    df.to_csv(csv_path, index=False)
    df.to_parquet(pq_path, index=False)
    meta = {
        "source_mat": str(mat_path),
        "rows": len(df),
        "columns": list(df.columns),
        "target_hz": target_hz,
        "duration_s": duration_s,
        "parameters": used,
        "start_time": start.isoformat(),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"Wrote {csv_path} ({csv_path.stat().st_size} bytes)")
    print(f"Wrote {pq_path} ({pq_path.stat().st_size} bytes)")
    print(f"Wrote {meta_path}")
    return pq_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mat", type=Path, help="Single .mat file")
    ap.add_argument("--mat-dir", type=Path, help="Directory of .mat files")
    ap.add_argument("--out-dir", type=Path, default=Path("sample-data/dashlink_converted"))
    ap.add_argument("--hz", type=float, default=2.0)
    args = ap.parse_args()

    files: list[Path] = []
    if args.mat:
        files.append(args.mat)
    if args.mat_dir:
        files.extend(sorted(args.mat_dir.glob("*.mat")))
    if not files:
        raise SystemExit("Provide --mat or --mat-dir")

    rates = {"ALT": 16, "CAS": 16, "PTCH": 8, "ROLL": 8, "N1": 2, "GLS": 2, "HYDG": 1}
    for f in files:
        convert_mat(f, args.out_dir, target_hz=args.hz, rates_hint=rates)


if __name__ == "__main__":
    main()
