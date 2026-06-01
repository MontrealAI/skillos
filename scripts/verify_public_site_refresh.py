#!/usr/bin/env python3
from pathlib import Path
import runpy, sys
ROOT=Path(__file__).resolve().parents[1]
sys.argv=[str(ROOT/'scripts/verify_skillos_public_command_center_v7.py'),'--out','dist']
runpy.run_path(str(ROOT/'scripts/verify_skillos_public_command_center_v7.py'), run_name='__main__')
