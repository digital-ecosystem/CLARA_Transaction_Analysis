"""
Entfernt unnötige/unbenutzte Dateien aus dem Projekt
"""
import os
from pathlib import Path

base = Path('.')

print("="*80)
print("BEREINIGUNG: UNNOETIGE DATEIEN")
print("="*80)

# Dateien die entfernt werden können
files_to_delete = []

# 1. Prüfe scripts/ auf alte/debug Scripts die nicht mehr benötigt werden
print("\n[1] PRUEFE SCRIPTS/")
print("-" * 80)
scripts_dir = base / 'scripts'

# Scripts die definitiv nicht mehr benötigt werden (alte Debug-Scripts)
unused_scripts = [
    # Alte Test-Scripts die durch neue ersetzt wurden
    'test_api.py',  # Wenn es neuere Versionen gibt
    'test_simple.py',
    'test_absolute_thresholds.py',
    'test_improved_smurfing.py',
    # Alte Debug-Scripts
    'debug_csv_parsing.py',
    'debug_launderer.py',
    'debug_launderer_direct.py',
    'debug_launderer_score.py',
    # Alte Check-Scripts
    'check_csv_results.py',
    'check_flags.py',
    'check_layering_scores.py',
    'check_detected_launderers.py',
    'compare_launderers.py',
    # Alte Analyse-Scripts die durch neue ersetzt wurden
    'analyze_smurfer_customer.py',
    'analyze_all_problem_types.py',
    'analyze_csv_problems.py',
]

deleted_scripts = 0
for script_name in unused_scripts:
    script_path = scripts_dir / script_name
    if script_path.exists():
        try:
            script_path.unlink()
            print(f"  [DELETED] {script_name}")
            deleted_scripts += 1
        except Exception as e:
            print(f"  [SKIP] {script_name} ({e})")

print(f"\n  {deleted_scripts} Scripts geloescht")

# 2. Prüfe docs/ auf alte/duplizierte Dokumentation
print("\n[2] PRUEFE DOCS/")
print("-" * 80)
docs_dir = base / 'docs'

# Alte Dokumentation die durch neuere Versionen ersetzt wurde
unused_docs = [
    # Alte System-Dokumentation
    'CLARA_System_Dokumentation.md',
    'CLARA_System_Dokumentation_v2.md',
    'SYSTEM_ERKLAERUNG.md',
    # Alte Quickstart (wenn README.md aktueller ist)
    'QUICKSTART.md',
    # Alte VBA-Dokumentation (wenn nicht mehr relevant)
    'VBA_FULL_FIX_PLAN.md',
    'VBA_IMPROVEMENTS_SUMMARY.md',
    # Alte Threshold-Dokumentation
    'ABSOLUTE_THRESHOLDS_CHANGES.md',
]

deleted_docs = 0
for doc_name in unused_docs:
    doc_path = docs_dir / doc_name
    if doc_path.exists():
        try:
            doc_path.unlink()
            print(f"  [DELETED] {doc_name}")
            deleted_docs += 1
        except Exception as e:
            print(f"  [SKIP] {doc_name} ({e})")

print(f"\n  {deleted_docs} Dokumente geloescht")

# 3. Prüfe output/ auf sehr alte Output-Dateien (optional - nur wenn gewünscht)
print("\n[3] PRUEFE OUTPUT/ (nur Info)")
print("-" * 80)
output_dir = base / 'output'
if output_dir.exists():
    csv_files = list(output_dir.glob('Analyzed_Trades_*.csv'))
    xlsx_files = list(output_dir.glob('Analyzed_Trades_*.xlsx'))
    print(f"  Gefunden: {len(csv_files)} CSV-Dateien, {len(xlsx_files)} Excel-Dateien")
    print(f"  (Alle Output-Dateien werden behalten)")

# 4. Zusammenfassung
print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)
print(f"  Scripts geloescht: {deleted_scripts}")
print(f"  Dokumente geloescht: {deleted_docs}")
print(f"  Gesamt geloescht: {deleted_scripts + deleted_docs}")
print("\n  Projekt ist jetzt aufgeraeumt!")

