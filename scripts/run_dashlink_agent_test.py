#!/usr/bin/env python3
"""
Extended agent test: DASHlink download (lightweight assets) → convert → verify.

Full 800MB flight zips are optional (DASHLINK_FULL_ZIP=url). By default:
  1. Downloads official parameter list + anomaly docs from NASA DASHlink
  2. Builds synthetic DASHlink-structure .mat fixture
  3. Converts to aligned CSV/Parquet
  4. Verifies schema, rates alignment, discrete events
  5. Writes a markdown report under sample-data/dashlink_reports/
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent

RAW = ROOT / "sample-data" / "dashlink_raw"
FIX = ROOT / "sample-data" / "dashlink_fixture"
CONV = ROOT / "sample-data" / "dashlink_converted"
REPORTS = ROOT / "sample-data" / "dashlink_reports"

ASSETS = {
    "parameters.txt": "https://c3.ndc.nasa.gov/dashlink/static/media/project/670200106231735_parameters.txt",
    "DASHlink_full_data_documentation.pdf": "https://c3.ndc.nasa.gov/dashlink/static/media/dataset/DASHlink_full_data_documentation.pdf",
}


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"GET {url}")
        urllib.request.urlretrieve(url, dest)
        print(f"  -> {dest} ({dest.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    results = {"started": datetime.now(timezone.utc).isoformat(), "steps": []}

    ok_dl = True
    for name, url in ASSETS.items():
        dest = RAW / name
        success = download(url, dest)
        results["steps"].append({"step": f"download:{name}", "ok": success, "bytes": dest.stat().st_size if success else 0})
        ok_dl = ok_dl and success

    full = os.environ.get("DASHLINK_FULL_ZIP")
    if full:
        zpath = RAW / "tail_full.zip"
        results["steps"].append({"step": "download:full_zip", "ok": download(full, zpath)})

    r = subprocess.run([sys.executable, str(SCRIPTS / "create_dashlink_fixture.py")], cwd=str(ROOT))
    results["steps"].append({"step": "create_fixture", "ok": r.returncode == 0})

    mat = FIX / "652201003041921.mat"
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "convert_dashlink.py"), "--mat", str(mat), "--out-dir", str(CONV), "--hz", "2"],
        cwd=str(ROOT),
    )
    results["steps"].append({"step": "convert", "ok": r.returncode == 0})

    import pandas as pd

    pq = CONV / "652201003041921_aligned.parquet"
    csv = CONV / "652201003041921_aligned.csv"
    verify = {"parquet_exists": pq.exists() and pq.stat().st_size > 0, "csv_exists": csv.exists()}
    if csv.exists():
        df = pd.read_csv(csv)
        verify["rows"] = len(df)
        verify["columns"] = list(df.columns)
        verify["has_altitude"] = "altitude_ft" in df.columns
        verify["has_core_speed"] = "core_speed_pct" in df.columns
        verify["hyd_events"] = int((df.get("hyd_low_green", 0) > 0.5).sum()) if "hyd_low_green" in df.columns else 0
        verify["ok"] = (
            verify["rows"] >= 50
            and verify["has_altitude"]
            and verify["has_core_speed"]
            and verify["hyd_events"] > 0
        )
    else:
        verify["ok"] = False
    results["steps"].append({"step": "verify", **verify})

    params_file = RAW / "parameters.txt"
    if params_file.exists():
        lines = [ln for ln in params_file.read_text(errors="ignore").splitlines() if ln.strip().startswith('"')]
        results["steps"].append({"step": "param_catalog", "ok": len(lines) > 50, "entries": len(lines)})

    results["finished"] = datetime.now(timezone.utc).isoformat()
    results["passed"] = all(s.get("ok") for s in results["steps"])

    report = REPORTS / "dashlink_agent_report.md"
    lines = [
        "# DASHlink agent test report",
        "",
        f"- Started: `{results['started']}`",
        f"- Finished: `{results['finished']}`",
        f"- **Passed: {results['passed']}**",
        "",
        "## Steps",
        "",
    ]
    for s in results["steps"]:
        status = "PASS" if s.get("ok") else "FAIL"
        detail = {k: v for k, v in s.items() if k != "step"}
        lines.append(f"- **{status}** `{s.get('step')}` — `{json.dumps(detail)}`")
    lines += [
        "",
        "## Notes",
        "",
        "- Full Tail_652_*.zip files are ~800MB each; set `DASHLINK_FULL_ZIP=<url>` to exercise a real download.",
        "- Fixture `.mat` validates conversion without NASA bandwidth.",
        "- UI screenshots: run frontend with converted Parquet and capture (Playwright or manual).",
        "",
        "## Outputs",
        "",
        f"- Raw assets: `{RAW}`",
        f"- Fixture: `{FIX}`",
        f"- Converted: `{CONV}`",
    ]
    report.write_text("\n".join(lines))
    (REPORTS / "dashlink_agent_report.json").write_text(json.dumps(results, indent=2))
    print(report.read_text())
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
