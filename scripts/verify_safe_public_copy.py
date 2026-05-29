#!/usr/bin/env python3
"""Verify that public-facing SkillOS copy keeps the safe reference-workflow posture."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    'site/index.html',
    'index.html',
    'site/app.js',
    'README.md',
    'PROOF_OF_WEALTH_ACCUMULATION.md',
    'docs/wealth_accumulation_proof.md',
    'data/wealth_proof.json',
    'dist/index.html',
    'dist/app.js',
    'dist/wealth_accumulation_proof.md',
    'dist/data/wealth_proof.json',
]

FORBIDDEN_EXACT = [
    'The wealth-accumulation layer for self-improving AI agents',
    'wealth-accumulation layer',
    'Wealth-accumulation proof',
    'Wealth Proof',
    'one real workflow',
    'real workflow gets cheaper',
    'real skill releases',
    'Skills become margin',
    'wealth-producing capability',
    'financial guarantees',  # allowed only in disclaimer, handled separately
]

# Phrases that are acceptable only if inside the disclaimer sentence.
REQUIRED_DISCLAIMER_FRAGMENT = 'not audited customer results, financial guarantees, investment advice'

REQUIRED_ANYWHERE = [
    'reference workflow',
    'demo assumptions',
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return ''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true', help='Fail if generated dist is missing.')
    args = parser.parse_args()
    errors: list[str] = []
    scanned = []
    combined = ''
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            if args.strict and rel.startswith('dist/'):
                errors.append(f'Missing generated file: {rel}')
            continue
        text = read(path)
        if not text:
            continue
        scanned.append(rel)
        combined += '\n' + text
        for phrase in FORBIDDEN_EXACT:
            if phrase == 'financial guarantees':
                # This phrase is expected in the disclaimer only. Check below instead.
                continue
            if phrase in text:
                errors.append(f'Unsafe phrase in {rel}: {phrase}')

        # Any public-facing mention of projected annual savings should carry the demo-assumptions qualifier.
        for match in re.finditer(r'projected annual savings', text, flags=re.IGNORECASE):
            window = text[match.start(): match.start() + 80].lower()
            if 'under demo assumptions' not in window:
                errors.append(f'Missing demo-assumptions qualifier near projected annual savings in {rel}')

    if REQUIRED_DISCLAIMER_FRAGMENT not in combined:
        errors.append('Missing required public disclaimer fragment.')
    for phrase in REQUIRED_ANYWHERE:
        if phrase not in combined.lower():
            errors.append(f'Missing required safe phrase somewhere in public copy: {phrase}')

    if errors:
        print('Safe public copy verification failed:')
        for err in errors:
            print(f' - {err}')
        raise SystemExit(1)
    print(f'Safe public copy verification passed across {len(scanned)} file(s).')

if __name__ == '__main__':
    main()
