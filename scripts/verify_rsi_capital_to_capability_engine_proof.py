#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(path: str, phrase: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f'Missing {path}')
    text = p.read_text(encoding='utf-8', errors='ignore')
    if phrase not in text:
        raise SystemExit(f'Missing {phrase!r} in {path}')


def main() -> None:
    require('site/index.html', 'rsi-capital-to-capability-engine-proof.html')
    require('site/index.html', 'Autonomous RSI Capital-to-Capability Engine')
    require('site/rsi-capital-to-capability-engine-proof.html', 'Autonomous RSI Capital-to-Capability Engine')
    require('site/rsi-capital-to-capability-engine-proof.html', 'Safe Kardashev-scale operationalization')
    require('docs/rsi_capital_to_capability_engine_proof.md', 'Large-scale multi-agent coordination')
    require('docs/rsi_capital_to_capability_engine_proof.md', 'Proof receipts')
    require('data/rsi_capital_to_capability_engine_proof.json', 'PASSED_AUTONOMOUS_RSI_CAPITAL_TO_CAPABILITY_ENGINE_PROOF')
    data = json.loads((ROOT / 'data/rsi_capital_to_capability_engine_proof.json').read_text(encoding='utf-8'))
    if not data.get('proved'):
        raise SystemExit('Proof JSON did not pass.')
    failed = [name for name, ok in data.get('gates', {}).items() if not ok]
    if failed:
        raise SystemExit('Failed proof gates: ' + ', '.join(failed))
    print('RSI capital-to-capability proof visibility and gate verification passed.')


if __name__ == '__main__':
    main()
