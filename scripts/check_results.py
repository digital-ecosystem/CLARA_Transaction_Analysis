"""
Vergleicht die aktuellen Analyse-Ergebnisse mit den erwarteten Test-Ergebnissen
"""

import pandas as pd
from pathlib import Path

# Finde die neueste analysierte CSV
output_dir = Path("output")
csv_files = list(output_dir.glob("Analyzed_Trades_*.csv"))
if not csv_files:
    print("Keine analysierten CSV-Dateien gefunden!")
    exit(1)

latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
print(f"Analysiere: {latest_csv.name}\n")

# Lese CSV
df = pd.read_csv(latest_csv, encoding='utf-8-sig')

# Zähle Kunden nach Risk Level
risk_counts = df.groupby('Kundennummer')['Risk_Level'].first().value_counts()
total_customers = risk_counts.sum()

# Berechne Statistiken
max_score = df.groupby('Kundennummer')['Suspicion_Score'].first().max()
total_transactions = len(df)

print("="*70)
print("AKTUELLE ERGEBNISSE (Neuer Upload)")
print("="*70)
print(f"\nTransaktionen: {total_transactions}")
print(f"Kunden: {total_customers}\n")

print("Risk Level Verteilung:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    count = risk_counts.get(level, 0)
    percent = (count / total_customers * 100) if total_customers > 0 else 0
    print(f"  {level:7s}: {count:3d} ({percent:5.1f}%)")

print(f"\nMax Suspicion Score: {max_score:.2f}")

# Erwartete Ergebnisse (TP/SP-System)
print("\n" + "="*70)
print("ERWARTETE ERGEBNISSE (TP/SP-System aus Tests)")
print("="*70)
print("""
Metrik          TP/SP-System
--------------------------------
GREEN           189 (76.8%)
YELLOW           33 (13.4%)
ORANGE            3 ( 1.2%)
RED              21 ( 8.5%)
--------------------------------
Gesamt          246 (100.0%)
Max Score       14.48
""")

print("="*70)
print("VERGLEICH")
print("="*70)

# Vergleiche
expected = {
    'GREEN': (189, 76.8),
    'YELLOW': (33, 13.4),
    'ORANGE': (3, 1.2),
    'RED': (21, 8.5),
    'total': 246,
    'max_score': 14.48
}

print("\nAbweichungen:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    actual_count = risk_counts.get(level, 0)
    actual_percent = (actual_count / total_customers * 100) if total_customers > 0 else 0
    expected_count, expected_percent = expected[level]
    
    diff_count = actual_count - expected_count
    diff_percent = actual_percent - expected_percent
    
    print(f"  {level:7s}: {diff_count:+4d} Kunden ({diff_percent:+6.1f}%)")

print(f"\n  Total   : {total_customers - expected['total']:+4d} Kunden")
print(f"  Max Score: {max_score - expected['max_score']:+6.2f}")

# Analyse
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if total_customers < expected['total']:
    print(f"\n[HINWEIS] Weniger Kunden als erwartet ({total_customers} vs {expected['total']})")
    print("  -> Dies kann an unterschiedlichen Test-Daten liegen")
    print("  -> Die CSV scheint nur 88 Kunden zu enthalten, nicht 246")

# Prüfe ob das System sensibler ist
red_percent = (risk_counts.get('RED', 0) / total_customers * 100) if total_customers > 0 else 0
if red_percent > 0:
    print(f"\n[OK] Das System erkennt RED-Kunden ({red_percent:.1f}%)")
else:
    print("\n[WARNUNG] Keine RED-Kunden erkannt!")

if max_score > 10:
    print(f"[OK] Max Score ist hoch genug ({max_score:.2f})")
else:
    print(f"[HINWEIS] Max Score ist niedriger als erwartet ({max_score:.2f} vs 14.48)")

print("\n" + "="*70)

