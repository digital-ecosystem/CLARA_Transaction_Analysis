"""
Test mit historischen Daten - vergleiche letzte 6 Monate mit früheren Daten
"""
import requests
import json
import sys
import io

# Windows UTF-8 Fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API-URL
BASE_URL = "http://localhost:8000"

csv_path = r"D:\My Progs\CLARA\2\Kunden CSV Generator\Trades_20251109_174429.csv"

print("=" * 80)
print("🚀 Test: Historische Daten-Analyse (letzte 6 Monate vs. früher)")
print("=" * 80)

# Für 3-Jahres-Daten (2021-2023):
# - Recent: Letzte 180 Tage (6 Monate) der Daten
# - Historical: 540 Tage (18 Monate) davor als Baseline
recent_days = 180  # 6 Monate
historical_days = 540  # 18 Monate

print(f"\n⚙️  Analyse-Strategie für historische Daten:")
print(f"   recent_days: {recent_days} Tage (letzte 6 Monate der Daten)")
print(f"   historical_days: {historical_days} Tage (18 Monate als Baseline)")
print(f"\n📂 Lade CSV: {csv_path}")

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
        
        # Zeige auffällige Kunden
        if result['flagged_customers']:
            print(f"\n🚨 Auffällige Kunden (sortiert nach Suspicion Score):")
            print("=" * 80)
            
            # Sortiere nach Suspicion Score
            flagged_sorted = sorted(
                result['flagged_customers'],
                key=lambda x: x['suspicion_score'],
                reverse=True
            )
            
            for i, customer in enumerate(flagged_sorted[:10], 1):
                print(f"\n{i}. {customer['customer_name']} ({customer['customer_id']})")
                print(f"   🎯 Risk Level: {customer['risk_level']}")
                print(f"   📊 Suspicion Score: {customer['suspicion_score']:.2f}")
                
                # Anti-Smurfing Details
                weight = customer['analyses']['weight_analysis']
                print(f"\n   🔍 Anti-Smurfing (Weight-Variable):")
                print(f"      Weight 7d:  {weight['weight_7d']:8.2f} (Z-Score: {weight['z_score_7d']:6.2f})")
                print(f"      Weight 30d: {weight['weight_30d']:8.2f} (Z-Score: {weight['z_score_30d']:6.2f})")
                print(f"      Weight 90d: {weight['weight_90d']:8.2f} (Z-Score: {weight['z_score_90d']:6.2f})")
                
                # Entropie
                entropy = customer['analyses']['entropy_analysis']
                print(f"\n   📉 Shannon-Entropie (Komplexität):")
                print(f"      Aktuelle Entropie: {entropy['current_entropy']:.3f}")
                print(f"      Baseline Entropie: {entropy['baseline_entropy']:.3f}")
                print(f"      Z-Score: {entropy['z_score']:.2f}")
                
                # Trust Score
                trust = customer['analyses']['trust_analysis']
                print(f"\n   🎯 Dynamic Trust Score:")
                print(f"      Aktuell: {trust['current_score']:.3f}")
                print(f"      Vorhersagbarkeit: {trust['predictability']:.3f}")
                
                # Statistische Analysen
                stats = customer['analyses']['statistical_analysis']
                print(f"\n   📊 Statistische Signale:")
                print(f"      Benford's Law: {stats['benford_score']:.3f}")
                print(f"      Velocity: {stats['velocity_score']:.3f}")
                print(f"      Time Anomaly: {stats['time_anomaly_score']:.3f}")
                print(f"      Layering (Geldwäsche): {stats['layering_score']:.3f}")
                
                # Flags
                if customer.get('flags'):
                    print(f"\n   🚩 Flags:")
                    for flag in customer['flags'][:5]:
                        print(f"      {flag}")
                
                # Empfehlungen
                if customer.get('recommendations'):
                    print(f"\n   💡 Empfehlungen:")
                    for rec in customer['recommendations'][:3]:
                        print(f"      {rec}")
                
                print("\n" + "-" * 80)
        
        else:
            print(f"\n✅ Keine auffälligen Muster gefunden")
            print(f"   Alle Kunden zeigen normales Verhalten innerhalb ihrer Baseline")
    
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

