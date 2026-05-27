from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://montrealai.github.io/skillos/"
REQUIRED = [
    "README.md",
    "README_FIRST_GITHUB_WEB_USERS.md",
    "GITHUB_UPLOAD_GUIDE.md",
    "START_HERE.html",
    "PROOF_OF_WEALTH_ACCUMULATION.md",
    ".github/workflows/pages.yml",
    ".github/workflows/tests.yml",
    "COPY_PASTE_GITHUB_ACTIONS/pages.yml",
    "COPY_PASTE_GITHUB_ACTIONS/tests.yml",
    "scripts/build_pages.py",
    "scripts/qa_check.py",
    "scripts/prove_wealth_loop.py",
    "scripts/verify_pages.py",
    "site/index.html",
    "site/styles.css",
    "site/app.js",
    "site/assets/skillos-mark.svg",
    "skillos/cli.py",
    "skillos/wealth_proof.py",
    "tests/test_end_to_end.py",
    "tests/test_pages_build.py",
    "tests/test_storage.py",
    "tests/test_wealth_proof.py",
    "docs/wealth_accumulation_proof.md",
]
FORBIDDEN_PARTS = {".skillos", "dist"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def tracked_or_packaged_files() -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True)
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if files:
            return files
    except Exception:
        pass
    return [str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix not in FORBIDDEN_SUFFIXES]


def main() -> None:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))

    offenders = []
    for rel in tracked_or_packaged_files():
        parts = set(Path(rel).parts)
        if parts & FORBIDDEN_PARTS or Path(rel).suffix in FORBIDDEN_SUFFIXES:
            offenders.append(rel)
    if offenders:
        fail("Remove generated files before uploading: " + ", ".join(offenders[:20]))

    pages = read(".github/workflows/pages.yml")
    for snippet in [
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v4",
        "actions/deploy-pages@v4",
        "pages: write",
        "id-token: write",
        "path: dist",
    ]:
        if snippet not in pages:
            fail(f"Pages workflow is missing `{snippet}`")

    for rel in ["README.md", "README_FIRST_GITHUB_WEB_USERS.md", "GITHUB_UPLOAD_GUIDE.md", "site/index.html", "scripts/build_pages.py"]:
        if TARGET_URL not in read(rel):
            fail(f"{rel} does not mention the target GitHub Pages URL")

    app = read("site/app.js")
    if "data/demo.json" not in app:
        fail("site/app.js must load generated demo data from data/demo.json")
    if "wealth_proof" not in app:
        fail("site/app.js must render the generated wealth_proof from demo.json")
    for snippet in ["fallbackSnapshot", "initial_agent_metrics", "final_skillos_metrics", "proof_steps", "Cheaper", "Faster", "Better"]:
        if snippet not in app:
            fail(f"site/app.js must render the wealth proof: missing {snippet}")

    html = read("site/index.html")
    for text in ["The wealth-accumulation layer", "GitHub Actions", "MontrealAI/skillos", "Wealth-accumulation proof", "cheaper", "faster", "better", "data/wealth_proof.json"]:
        if text not in html:
            fail(f"site/index.html is missing expected text: {text}")

    print("✅ Repository file verification passed")


if __name__ == "__main__":
    main()
