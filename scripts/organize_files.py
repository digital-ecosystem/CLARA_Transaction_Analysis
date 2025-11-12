"""
Organisiert die Dateien im Black Box Ordner in eine logische Struktur
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

# Definiere Ordnerstruktur
FOLDER_STRUCTURE = {
    'docs': [
        '*.md',
        '*.docx',
    ],
    'scripts': [
        '*.py',
    ],
    'output': [
        'Analyzed_Trades_*.csv',
        'Analyzed_Trades_*.xlsx',
        'Trades_*.csv',
    ],
    'logs': [
        # Logs bleiben im logs/ Ordner
    ],
    'templates': [
        # Templates bleiben im templates/ Ordner
    ],
    'backup': [
        # Alte/Backup-Dateien
    ],
    '__pycache__': [
        # Python Cache bleibt
    ],
}

# Dateien die NICHT verschoben werden sollen
KEEP_IN_ROOT = [
    'main.py',
    'analyzer.py',
    'models.py',
    'weight_detector.py',
    'entropy_detector.py',
    'predictability_detector.py',
    'trust_score.py',
    'statistical_methods.py',
    '.gitignore',
    'README.md',
    'requirements.txt',
]

# Dateien die gelöscht werden können (temporäre/Backup)
TEMP_FILES = [
    '~$*.xlsx',
    '*.pyc',
    '__pycache__',
]

def organize_files():
    """Organisiert Dateien in logische Ordner"""
    base_path = Path('.')
    
    print("="*80)
    print("DATEI-ORGANISATION")
    print("="*80)
    
    # Erstelle Ordner
    folders = {
        'docs': base_path / 'docs',
        'scripts': base_path / 'scripts',
        'output': base_path / 'output',
        'backup': base_path / 'backup',
    }
    
    for folder_name, folder_path in folders.items():
        if not folder_path.exists():
            folder_path.mkdir()
            print(f"Ordner erstellt: {folder_name}/")
    
    # Verschiebe Dokumentation
    print("\n[1] DOKUMENTATION")
    print("-" * 80)
    doc_files = list(base_path.glob('*.md')) + list(base_path.glob('*.docx'))
    moved_docs = 0
    skipped_docs = 0
    for file in doc_files:
        if file.name not in KEEP_IN_ROOT:
            dest = folders['docs'] / file.name
            if not dest.exists():
                try:
                    shutil.move(str(file), str(dest))
                    print(f"  -> {file.name}")
                    moved_docs += 1
                except (PermissionError, OSError) as e:
                    print(f"  [SKIP] {file.name} (Datei geoeffnet oder gesperrt)")
                    skipped_docs += 1
    print(f"  {moved_docs} Dateien verschoben, {skipped_docs} uebersprungen")
    
    # Verschiebe Scripts (außer Haupt-Module)
    print("\n[2] SCRIPTS")
    print("-" * 80)
    script_files = list(base_path.glob('*.py'))
    moved_scripts = 0
    skipped_scripts = 0
    for file in script_files:
        if file.name not in KEEP_IN_ROOT:
            dest = folders['scripts'] / file.name
            if not dest.exists():
                try:
                    shutil.move(str(file), str(dest))
                    print(f"  -> {file.name}")
                    moved_scripts += 1
                except (PermissionError, OSError) as e:
                    print(f"  [SKIP] {file.name} (Datei geoeffnet oder gesperrt)")
                    skipped_scripts += 1
    print(f"  {moved_scripts} Dateien verschoben, {skipped_scripts} uebersprungen")
    
    # Verschiebe Output-Dateien
    print("\n[3] OUTPUT-DATEIEN")
    print("-" * 80)
    output_files = list(base_path.glob('Analyzed_Trades_*.csv')) + \
                   list(base_path.glob('Analyzed_Trades_*.xlsx')) + \
                   list(base_path.glob('Trades_*.csv'))
    moved_output = 0
    skipped_output = 0
    for file in output_files:
        dest = folders['output'] / file.name
        if not dest.exists():
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {file.name}")
                moved_output += 1
            except (PermissionError, OSError) as e:
                print(f"  [SKIP] {file.name} (Datei geoeffnet oder gesperrt)")
                skipped_output += 1
    print(f"  {moved_output} Dateien verschoben, {skipped_output} uebersprungen")
    
    # Verschiebe temporäre/Backup-Dateien
    print("\n[4] BACKUP/TEMPORAERE DATEIEN")
    print("-" * 80)
    backup_files = list(base_path.glob('~$*'))
    moved_backup = 0
    skipped_backup = 0
    for file in backup_files:
        dest = folders['backup'] / file.name
        if not dest.exists():
            try:
                shutil.move(str(file), str(dest))
                print(f"  -> {file.name}")
                moved_backup += 1
            except (PermissionError, OSError) as e:
                print(f"  [SKIP] {file.name} (Datei geoeffnet oder gesperrt)")
                skipped_backup += 1
    print(f"  {moved_backup} Dateien verschoben, {skipped_backup} uebersprungen")
    
    # Zeige verbleibende Dateien im Root
    print("\n[5] VERBLEIBENDE DATEIEN IM ROOT")
    print("-" * 80)
    remaining = []
    for file in base_path.iterdir():
        if file.is_file() and file.name not in ['.gitignore', 'README.md', 'requirements.txt']:
            remaining.append(file.name)
    
    if remaining:
        print("  Haupt-Module (bleiben im Root):")
        for name in sorted(remaining):
            if name.endswith('.py'):
                print(f"    - {name}")
        print("\n  Andere Dateien:")
        for name in sorted(remaining):
            if not name.endswith('.py'):
                print(f"    - {name}")
    else:
        print("  Keine weiteren Dateien")
    
    print("\n" + "="*80)
    print("ORGANISATION ABGESCHLOSSEN")
    print("="*80)
    print("\nNeue Struktur:")
    print("  docs/          - Dokumentation (.md, .docx)")
    print("  scripts/       - Analyse- und Tool-Scripts (.py)")
    print("  output/        - Analysierte CSV/Excel-Dateien")
    print("  backup/        - Temporäre/Backup-Dateien")
    print("  logs/          - Log-Dateien")
    print("  templates/     - HTML-Templates")
    print("\n  Root/         - Haupt-Module (main.py, analyzer.py, etc.)")

if __name__ == '__main__':
    try:
        organize_files()
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

