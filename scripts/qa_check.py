from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)


def remove_generated() -> None:
    for name in ("dist", ".skillos"):
        path = ROOT / name
        if path.exists():
            shutil.rmtree(path)
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
    for path in ROOT.rglob("*.py[co]"):
        path.unlink(missing_ok=True)


def main() -> None:
    remove_generated()
    run([sys.executable, "scripts/verify_repo.py"])
    run([sys.executable, "scripts/prove_wealth_loop.py"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    with tempfile.TemporaryDirectory() as tmp:
        run([sys.executable, "-m", "skillos.cli", "--db", str(Path(tmp) / "skillos-verify.db"), "verify"])
    run([sys.executable, "scripts/build_pages.py"])
    run([sys.executable, "scripts/verify_pages.py", "dist"])
    print("✅ Repository QA passed")


if __name__ == "__main__":
    main()
