#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path
from urllib.parse import urlparse

PROOF_ID = "proof-gradient-agent-evolution-protocol"
ROOT_MARKER = "SKILLOS_PROOF_GRADIENT_COMMAND_CENTER_V1"
RECEIPT_MARKER = "SKILLOS_PROOF_GRADIENT_AGENT_EVOLUTION_PROTOCOL_V1"
BANNED_ROOT = ["Autonomous Proof Command Center", "SkillOS Proof Command Center", "SkillOS Public Command Center v2", "SkillOS Public Command Center v3", "SkillOS Sovereign Command Center v5"]

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Cannot read JSON {path}: {e}")

def hrefs(html_text):
    return re.findall(r'href=["\']([^"\']+)["\']', html_text)

def local_target(href):
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return None
    if href.startswith("/"):
        return None
    h = href.split("#",1)[0].split("?",1)[0]
    if not h:
        return None
    return h

def verify_links(out):
    missing = []
    for html_path in out.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        for href in hrefs(text):
            target = local_target(href)
            if not target:
                continue
            dest = (html_path.parent / target).resolve()
            try:
                dest.relative_to(out.resolve())
            except ValueError:
                missing.append(f"{html_path.relative_to(out)} -> {href} escapes root")
                continue
            if not dest.exists():
                missing.append(f"{html_path.relative_to(out)} -> {href}")
    if missing:
        fail("Missing internal links:\n" + "\n".join(missing[:80]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    out = Path(args.out)
    if not out.exists():
        fail(f"Output directory does not exist: {out}")
    root = out / "index.html"
    proof = out / f"{PROOF_ID}.html"
    skills = out / "skills.html"
    manifest_path = out / "data" / "command-center-manifest.json"
    receipt_path = out / "data" / f"{PROOF_ID}.json"
    for p in [root, proof, skills, manifest_path, receipt_path, out / "proof-registry.json"]:
        if not p.exists():
            fail(f"Missing required artifact: {p}")
    root_text = root.read_text(encoding="utf-8", errors="ignore")
    if "Public SkillOS Command Center" not in root_text:
        fail("Root does not identify itself as Public SkillOS Command Center")
    for phrase in BANNED_ROOT:
        if phrase in root_text:
            fail(f"Root contains legacy/banned phrase: {phrase}")
    # Proof Gradient may be featured on the root, but must not be the h1 root title.
    if re.search(r"<h1[^>]*>\s*Proof Gradient", root_text, re.I):
        fail("Root h1 is Proof Gradient; root must be the Command Center")
    manifest = load_json(manifest_path)
    if manifest.get("marker") != ROOT_MARKER:
        fail(f"Manifest marker mismatch: {manifest.get('marker')}")
    receipt = load_json(receipt_path)
    if receipt.get("marker") != RECEIPT_MARKER:
        fail(f"Receipt marker mismatch: {receipt.get('marker')}")
    if receipt.get("status") != "PASSED":
        fail(f"Receipt status is not PASSED: {receipt.get('status')}")
    gates = receipt.get("proof_gates") or []
    if not gates or not all(g.get("passed") for g in gates):
        fail("One or more proof gates failed")
    skills_used = receipt.get("skills_used") or []
    if len(skills_used) < 6:
        fail("Expected at least 6 Skills Used cards")
    skills_text = skills.read_text(encoding="utf-8", errors="ignore")
    for required in ["Skills Used", "Verifier", "Input", "Output", "Proof-Gated Selection", "Gradient Scoring"]:
        if required not in skills_text:
            fail(f"Skills page missing: {required}")
    proof_text = proof.read_text(encoding="utf-8", errors="ignore")
    for required in ["One agent tries", "Proof decides", "The network evolves", "Proof Gradient release curve", "Baseline comparison", "Public boundary"]:
        if required not in proof_text:
            fail(f"Proof page missing: {required}")
    verify_links(out)
    print(json.dumps({"status":"verified", "out":str(out), "proof_id":PROOF_ID, "root_marker":ROOT_MARKER, "skills_used":len(skills_used)}, indent=2))

if __name__ == "__main__":
    main()
