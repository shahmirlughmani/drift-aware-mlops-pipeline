"""Build a clean submission zip of the project.

Excludes caches, MLflow runs, large raw data, and model joblib artefacts.
The output filename encodes the team roll numbers.
"""
from __future__ import annotations

import fnmatch
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT.parent  # one level up from mlops-project/
ZIP_NAME = "i221883_i221934_MLOps_Project.zip"

EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "mlruns",
    "mlartifacts",
    "node_modules",
    ".git",
    "htmlcov",
    "build",
    "dist",
}
EXCLUDE_GLOBS = [
    "*.pyc", "*.pyo", "*.pyd",
    "*.joblib", "*.pkl",
    "*.log",
    ".coverage", ".coverage.*",
    "*.egg-info",
    "data/raw/elec2.csv",
    "data/processed/*.npy",
]


def is_excluded(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & EXCLUDE_DIRS:
        return True
    rel_str = str(rel).replace("\\", "/")
    return any(fnmatch.fnmatch(rel_str, pat) or fnmatch.fnmatch(rel.name, pat)
               for pat in EXCLUDE_GLOBS)


def main() -> int:
    out = OUT_DIR / ZIP_NAME
    if out.exists():
        out.unlink()

    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if is_excluded(rel):
                continue
            arcname = Path("mlops-project") / rel
            zf.write(path, arcname.as_posix())
            n += 1

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"Wrote {out}")
    print(f"  files : {n}")
    print(f"  size  : {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
