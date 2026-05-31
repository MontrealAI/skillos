from __future__ import annotations
import json, sys
from pathlib import Path

SLUG = "rsi-blockchain-protocol-capital-frontier-proof"
REQUIRED = [
    Path(f"data/{SLUG}.json"),
    Path(f"docs/{SLUG}.md"),
    Path(f"site/{SLUG}.html"),
    Path(f"badges/{SLUG}.svg"),
    Path("site/index.html"),
    Path("site/proof-registry.json"),
    Path("site/sitemap.xml"),
    Path("site/robots.txt"),
]


def main() -> None:
    errors = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing required generated file: {path}")
    if not errors:
        index = Path("site/index.html").read_text(encoding="utf-8")
        page = Path(f"site/{SLUG}.html").read_text(encoding="utf-8")
        registry = json.loads(Path("site/proof-registry.json").read_text(encoding="utf-8"))
        if f"{SLUG}.html" not in index:
            errors.append("homepage does not link to proof page")
        if "Run / regenerate" not in page and "Run on GitHub" not in page:
            errors.append("proof page does not contain a user-friendly run/regenerate link")
        if not any(p.get("slug") == SLUG for p in registry.get("proofs", [])):
            errors.append("proof registry missing blockchain protocol capital frontier proof")
        if "investment advice" not in page.lower():
            errors.append("claim-boundary language missing from proof page")
    if errors:
        print("Site verification failed:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    print("Blockchain proof site verification passed")


if __name__ == "__main__":
    main()
