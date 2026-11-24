#!/usr/bin/env python3
"""Recompute synthetic results only. Real-photo comparison requires user-supplied images."""
from pathlib import Path
import subprocess, sys
here=Path(__file__).resolve().parent
for script in ['faiza_lab_v10.py','test_chaine_complete.py','vector_structure.py']:
    print(f'\n--- Running {script} ---',flush=True)
    subprocess.run([sys.executable,str(here/script)],cwd=here,check=True)
print('\nComplete: see CSV results and figures; all thresholds are provisional.',flush=True)
