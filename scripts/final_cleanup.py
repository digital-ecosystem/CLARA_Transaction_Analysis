"""Finale Bereinigung: Verschiebt alle verbleibenden Output-Dateien"""
import shutil
from pathlib import Path
import time

base = Path('.')
output = Path('output')

# Finde alle CSV/Excel-Dateien im Root
csv_files = list(base.glob('Analyzed_Trades_*.csv'))
xlsx_files = list(base.glob('Analyzed_Trades_*.xlsx'))

all_files = csv_files + xlsx_files

moved = 0
skipped = 0
already_exists = 0

print("="*80)
print("FINALE BEREINIGUNG - OUTPUT-DATEIEN")
print("="*80)

for file in all_files:
    dest = output / file.name
    if dest.exists():
        print(f"  [EXISTS] {file.name} (bereits in output/)")
        # Versuche die Datei im Root zu löschen, wenn sie identisch ist
        try:
            if file.stat().st_size == dest.stat().st_size:
                file.unlink()
                print(f"  [DELETED] {file.name} (dupliziert)")
                already_exists += 1
        except:
            pass
    else:
        try:
            shutil.move(str(file), str(dest))
            print(f"  -> {file.name}")
            moved += 1
        except (PermissionError, OSError) as e:
            print(f"  [SKIP] {file.name} (Datei geoeffnet oder gesperrt)")
            skipped += 1
            # Warte kurz und versuche es nochmal
            time.sleep(0.5)
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {file.name} (nach Wartezeit)")
                moved += 1
                skipped -= 1
            except:
                pass

print("\n" + "="*80)
print(f"ZUSAMMENFASSUNG:")
print(f"  Verschoben: {moved}")
print(f"  Bereits vorhanden: {already_exists}")
print(f"  Uebersprungen (geoeffnet): {skipped}")
print("="*80)

