"""
Test-Script für die neue Web-UI und API
"""

import requests
import time
from pathlib import Path

def test_ui_api():
    """Testet die neue UI-API mit CSV-Upload"""
    
    base_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("CLARA WEB-UI API TEST")
    print("="*70 + "\n")
    
    # 1. Health Check
    print("[1/4] Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("  [OK] Server laeuft")
        else:
            print(f"  [FEHLER] Server antwortet mit Status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("  [FEHLER] Server nicht erreichbar. Bitte starten Sie: python main.py")
        return
    except Exception as e:
        print(f"  [FEHLER] Fehler: {e}")
        return
    
    # 2. UI erreichbar?
    print("\n[2/4] Web-UI Check...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200 and "CLARA" in response.text:
            print("  [OK] Web-UI erreichbar")
        else:
            print(f"  [WARN] Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"  [FEHLER] Fehler: {e}")
    
    # 3. CSV-Upload & Analyse
    print("\n[3/4] CSV-Upload & Analyse...")
    
    # Suche nach vorhandener CSV
    csv_files = list(Path(".").glob("Trades_*.csv"))
    if not csv_files:
        print("  [WARN] Keine Test-CSV gefunden (Trades_*.csv)")
        print("  Bitte VBA-Makro ausfuehren oder CSV bereitstellen")
        return
    
    test_csv = csv_files[0]
    print(f"  Verwende: {test_csv.name}")
    
    try:
        with open(test_csv, 'rb') as f:
            files = {'file': (test_csv.name, f, 'text/csv')}
            
            print("  Uploading...")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/analyze/csv-upload",
                files=files,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"  [OK] Analyse erfolgreich ({elapsed:.2f}s)")
                print(f"\n  Ergebnisse:")
                print(f"    - Analysierte Kunden: {result['analyzed_customers']}")
                print(f"    - GREEN: {result['summary']['green']}")
                print(f"    - YELLOW: {result['summary']['yellow']}")
                print(f"    - ORANGE: {result['summary']['orange']}")
                print(f"    - RED: {result['summary']['red']}")
                print(f"    - CSV-Datei: {result['csv_filename']}")
                
                csv_filename = result['csv_filename']
                
                # 4. CSV-Download
                print("\n[4/4] CSV-Download...")
                download_response = requests.get(
                    f"{base_url}/api/download/{csv_filename}",
                    timeout=30
                )
                
                if download_response.status_code == 200:
                    print(f"  [OK] CSV erfolgreich heruntergeladen")
                    print(f"  Groesse: {len(download_response.content)} Bytes")
                    
                    # Prüfe ob Datei auch im output/ Verzeichnis ist
                    output_path = Path("output") / csv_filename
                    if output_path.exists():
                        print(f"  [OK] Datei gespeichert: {output_path}")
                    else:
                        print(f"  [WARN] Datei nicht in output/ gefunden")
                else:
                    print(f"  [FEHLER] Download fehlgeschlagen: {download_response.status_code}")
                
            else:
                print(f"  [FEHLER] Analyse fehlgeschlagen: {response.status_code}")
                print(f"  Response: {response.text}")
                
    except Exception as e:
        print(f"  [FEHLER] Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    # Log-Check
    print("\n[LOGS] Pruefe Log-Dateien...")
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("clara_*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"  [OK] Log-Datei gefunden: {latest_log.name}")
            
            # Zeige letzte 5 Zeilen
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("\n  Letzte Eintraege:")
                    for line in lines[-5:]:
                        print(f"    {line.rstrip()}")
        else:
            print("  [WARN] Keine Log-Dateien gefunden")
    else:
        print("  [WARN] logs/ Verzeichnis nicht gefunden")
    
    print("\n" + "="*70)
    print("TEST ABGESCHLOSSEN")
    print("="*70)
    print("\nOeffne im Browser: http://localhost:8000")
    print()


if __name__ == "__main__":
    test_ui_api()

