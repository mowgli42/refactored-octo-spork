"""Extended test: DASHlink fixture convert + verify (no 800MB download required)."""
from pathlib import Path
import subprocess
import sys
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent


def test_fixture_convert_and_verify():
    r = subprocess.run([sys.executable, str(SCRIPTS / "create_dashlink_fixture.py")], cwd=str(REPO))
    assert r.returncode == 0
    mat = REPO / "sample-data" / "dashlink_fixture" / "652201003041921.mat"
    assert mat.exists()
    out = REPO / "sample-data" / "dashlink_converted"
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "convert_dashlink.py"), "--mat", str(mat), "--out-dir", str(out), "--hz", "2"],
        cwd=str(REPO),
    )
    assert r.returncode == 0
    csv = out / "652201003041921_aligned.csv"
    assert csv.exists()
    df = pd.read_csv(csv)
    assert len(df) >= 50
    assert "altitude_ft" in df.columns
    assert "core_speed_pct" in df.columns
    assert "timestamp" in df.columns
    assert (df["hyd_low_green"] > 0.5).sum() > 0
