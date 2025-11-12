"""Verschiebt verbleibende Output-Dateien ins output/ Verzeichnis"""
import shutil
from pathlib import Path

base = Path('.')
output = Path('output')

# Finde alle CSV/Excel-Dateien
files = list(base.glob('Analyzed_Trades_*.csv')) + list(base.glob('Analyzed_Trades_*.xlsx'))

moved = 0
skipped = 0

for file in files:
    if file.name.startswith('Analyzed_Trades_'):
        dest = output / file.name
        if not dest.exists():
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {file.name}")
                moved += 1
            except (PermissionError, OSError) as e:
                print(f"  [SKIP] {file.name}")
                skipped += 1

print(f"\nVerschoben: {moved}, Uebersprungen: {skipped}")

