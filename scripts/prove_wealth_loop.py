from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skillos.wealth_proof import markdown_report, write_wealth_proof


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "wealth_proof.json"
    report = write_wealth_proof(output)
    md_path = ROOT / "docs" / "wealth_accumulation_proof.md"
    md_path.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({
        "proved": report["conclusion"]["proved"],
        "workflow": report["workflow"]["name"],
        "final_skill_version": report["conclusion"]["final_skill_version"],
        "cost_reduction_percent_vs_initial_agent": report["conclusion"]["cost_reduction_percent_vs_initial_agent"],
        "speed_gain_percent_vs_initial_agent": report["conclusion"]["speed_gain_percent_vs_initial_agent"],
        "quality_gain_points_vs_initial_agent": report["conclusion"]["quality_gain_points_vs_initial_agent"],
        "output": str(output),
        "markdown_report": str(md_path),
    }, indent=2))
    if not report["conclusion"]["proved"]:
        raise SystemExit("SkillOS wealth proof failed")


if __name__ == "__main__":
    main()
