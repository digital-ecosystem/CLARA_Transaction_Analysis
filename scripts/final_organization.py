"""
Finale Organisation: Sortiert verbleibende Dateien und entfernt Unnötiges
"""
import shutil
from pathlib import Path
import os

base = Path('.')
output = Path('output')
docs = Path('docs')
scripts = Path('scripts')

print("="*80)
print("FINALE ORGANISATION & BEREINIGUNG")
print("="*80)

# 1. Verschiebe verbleibende Output-Dateien
print("\n[1] OUTPUT-DATEIEN")
print("-" * 80)
output_files = [
    'Analyzed_Trades_20251112_160142.xlsx',
]

for filename in output_files:
    file = base / filename
    if file.exists():
        dest = output / filename
        if not dest.exists():
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {filename}")
            except (PermissionError, OSError) as e:
                print(f"  [SKIP] {filename} (geoeffnet)")
        else:
            try:
                file.unlink()
                print(f"  [DELETED] {filename} (dupliziert)")
            except:
                print(f"  [SKIP] {filename} (geoeffnet)")

# 2. Verschiebe Dokumentation
print("\n[2] DOKUMENTATION")
print("-" * 80)
doc_files = [
    'CSV_SPALTEN_ERKLAERUNG.docx',
]

for filename in doc_files:
    file = base / filename
    if file.exists():
        dest = docs / filename
        if not dest.exists():
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {filename}")
            except (PermissionError, OSError) as e:
                print(f"  [SKIP] {filename} (geoeffnet)")

# 3. Entferne unnötige Test-Dateien
print("\n[3] UNNOETIGE TEST-DATEIEN")
print("-" * 80)
test_files = [
    'example_transactions.csv',
    'example_transactions_enhanced.csv',
    'example_transactions_with_history.csv',
    'markings_check_result.txt',
    'package-lock.json',  # Nicht benötigt für Python-Projekt
]

deleted = 0
for filename in test_files:
    file = base / filename
    if file.exists():
        try:
            file.unlink()
            print(f"  [DELETED] {filename}")
            deleted += 1
        except (PermissionError, OSError) as e:
            print(f"  [SKIP] {filename} (geoeffnet)")

print(f"\n  {deleted} Dateien geloescht")

# 4. Prüfe auf weitere unnötige Dateien
print("\n[4] PRUEFUNG AUF WEITERE UNNOETIGE DATEIEN")
print("-" * 80)

# Finde alle .py Dateien im Root (außer Haupt-Module)
main_modules = {
    'main.py', 'analyzer.py', 'models.py', 'weight_detector.py',
    'entropy_detector.py', 'predictability_detector.py',
    'statistical_methods.py', 'trust_score.py'
}

root_py_files = [f for f in base.glob('*.py') if f.name not in main_modules]
if root_py_files:
    print(f"  Gefunden: {len(root_py_files)} .py Dateien im Root")
    for f in root_py_files:
        print(f"    - {f.name}")
        try:
            shutil.move(str(f), str(scripts / f.name))
            print(f"      -> nach scripts/ verschoben")
        except:
            print(f"      [SKIP] (Fehler)")

# 5. Zusammenfassung
print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)
print("\nRoot-Verzeichnis sollte jetzt nur noch enthalten:")
print("  - Haupt-Module (.py)")
print("  - README.md")
print("  - requirements.txt")
print("  - .gitignore")
print("\nAlle anderen Dateien wurden sortiert oder entfernt.")

