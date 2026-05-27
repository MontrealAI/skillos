from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = ["index.html", "styles.css", "app.js", ".nojekyll", "data/demo.json", "data/wealth_proof.json", "assets/skillos-mark.svg"]


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    missing = [name for name in REQUIRED if not (target / name).exists()]
    if missing:
        raise SystemExit(f"Missing generated GitHub Pages files: {missing}")
    html = (target / "index.html").read_text(encoding="utf-8")
    if "Agent SkillOS" not in html:
        raise SystemExit("index.html does not contain Agent SkillOS")
    if "https://montrealai.github.io/skillos/" not in html:
        raise SystemExit("index.html does not contain the expected Pages URL")
    data = json.loads((target / "data" / "demo.json").read_text(encoding="utf-8"))
    for key in ["lessons", "candidate", "test_result", "release", "dashboard"]:
        if not data.get(key):
            raise SystemExit(f"demo.json missing {key}")
    wealth = json.loads((target / "data" / "wealth_proof.json").read_text(encoding="utf-8"))
    if not wealth.get("conclusion", {}).get("proved"):
        raise SystemExit("wealth_proof.json does not prove the workflow economics")
    checks = wealth.get("monotonic_checks", {})
    for key in ["every_job_created_approved_release", "cost_per_job_decreased_after_each_release", "minutes_per_job_decreased_after_each_release", "quality_score_increased_after_each_release", "accepted_rate_increased_after_each_release"]:
        if checks.get(key) is not True:
            raise SystemExit(f"wealth_proof.json failed monotonic check: {key}")
    print(f"✅ Verified GitHub Pages output at {target}")


if __name__ == "__main__":
    main()
