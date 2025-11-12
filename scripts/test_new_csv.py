"""
Test für die neue CSV-Datei mit 3 Jahren Transaktionsdaten
"""
import requests
import json
import sys
import io

# Setze UTF-8 Encoding für Windows Console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API-URL
BASE_URL = "http://localhost:8000"

def test_new_csv():
    """Testet die neue CSV-Datei"""
    print("=" * 80)
    print("🚀 Test: Neue CSV-Datei (3 Jahre Daten)")
    print("=" * 80)
    
    # Pfad zur neuen CSV
    csv_path = r"D:\My Progs\CLARA\2\Kunden CSV Generator\Trades_20251109_174429.csv"
    
    print(f"\n📂 Lade CSV: {csv_path}")
    
    # Für historische Daten (2021-2023) verwenden wir ein großes Zeitfenster
    recent_days = 3650  # ~10 Jahre (alle Daten als "recent")
    historical_days = 1095  # 3 Jahre für Baseline
    
    print(f"⚙️  Analyse-Parameter:")
    print(f"   recent_days: {recent_days} (analysiere alle Transaktionen)")
    print(f"   historical_days: {historical_days} (Baseline)")
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('transactions.csv', f, 'text/csv')}
            data = {
                'recent_days': recent_days,
                'historical_days': historical_days
            }
            response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Analyse erfolgreich!")
            print(f"\n📊 Zusammenfassung:")
            print(f"   Kunden analysiert: {result['analyzed_customers']}")
            print(f"   🟢 GREEN:  {result['summary']['green']:3d}")
            print(f"   🟡 YELLOW: {result['summary']['yellow']:3d}")
            print(f"   🟠 ORANGE: {result['summary']['orange']:3d}")
            print(f"   🔴 RED:    {result['summary']['red']:3d}")
            print(f"   ⚠️  Flagged: {len(result['flagged_customers'])}")
            
            # Zeige die ersten 5 auffälligen Kunden
            if result['flagged_customers']:
                print(f"\n🚨 Top {min(5, len(result['flagged_customers']))} auffällige Kunden:")
                print("-" * 80)
                
                for i, customer in enumerate(result['flagged_customers'][:5], 1):
                    print(f"\n{i}. {customer['customer_name']} ({customer['customer_id']})")
                    print(f"   Risk Level: {customer['risk_level']}")
                    print(f"   Suspicion Score: {customer['suspicion_score']:.2f}")
                    print(f"   Transaktionen (recent): {customer['transaction_count']}")
                    
                    # Zeige Flags
                    if customer.get('flags'):
                        print(f"   Flags:")
                        for flag in customer['flags'][:3]:  # Erste 3 Flags
                            print(f"      {flag}")
                    
                    # Zeige Weight-Analyse
                    weight = customer['analyses']['weight_analysis']
                    print(f"   Anti-Smurfing:")
                    print(f"      Weight 7d:  {weight['weight_7d']:.2f} (Z: {weight['z_score_7d']:.2f})")
                    print(f"      Weight 30d: {weight['weight_30d']:.2f} (Z: {weight['z_score_30d']:.2f})")
                    
                    # Zeige Layering
                    stats = customer['analyses']['statistical_analysis']
                    print(f"   Layering Score: {stats['layering_score']:.2f}")
            
            # Info über grüne Kunden
            green_count = result['summary']['green']
            if green_count > 0:
                print(f"\n\n✅ {green_count} Kunden sind unauffällig (GREEN)")
            
        else:
            print(f"\n❌ Fehler: {response.status_code}")
            print(response.text)
    
    except FileNotFoundError:
        print(f"\n❌ CSV-Datei nicht gefunden: {csv_path}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Verbindung fehlgeschlagen. Ist der Server gestartet?")
        print(f"   Starte ihn mit: python main.py")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_csv()

