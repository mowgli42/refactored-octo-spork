#!/usr/bin/env python3
"""Create a small synthetic DASHlink-style .mat for offline CI (no 800MB download)."""
from pathlib import Path
import numpy as np
from scipy.io import savemat

def main():
    out = Path("sample-data/dashlink_fixture")
    out.mkdir(parents=True, exist_ok=True)
    n_hi, n_mid, n_lo = 800, 400, 100
    params = {
        "ALT": (15000 + np.cumsum(np.random.randn(n_hi) * 2)).astype(np.float64),
        "CAS": (280 + 20 * np.sin(np.linspace(0, 8, n_hi)) + np.random.randn(n_hi)).astype(np.float64),
        "PTCH": (2 * np.sin(np.linspace(0, 6, n_mid)) + np.random.randn(n_mid) * 0.3).astype(np.float64),
        "ROLL": (5 * np.sin(np.linspace(0, 10, n_mid)) + np.random.randn(n_mid) * 0.5).astype(np.float64),
        "N1": (55 + 15 * np.sin(np.linspace(0, 4, n_lo)) + np.random.randn(n_lo)).astype(np.float64),
        "GLS": (np.random.randn(n_lo) * 0.2).astype(np.float64),
        "HYDG": np.zeros(n_lo, dtype=np.float64),
    }
    params["HYDG"][40:45] = 1.0
    path = out / "652201003041921.mat"
    savemat(str(path), params)
    print(f"Wrote {path} ({path.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
