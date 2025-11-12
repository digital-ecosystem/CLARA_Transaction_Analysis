"""
Detaillierte Analyse der neuesten Ergebnisse
"""

import pandas as pd
from pathlib import Path
import sys

print("="*80)
print("ANALYSE: Analyzed_Trades_20251112_153323.csv")
print("="*80)

# Lade CSV
csv_file = Path("output/Analyzed_Trades_20251112_153323.csv")
if not csv_file.exists():
    print(f"Fehler: {csv_file} nicht gefunden!")
    sys.exit(1)

df = pd.read_csv(csv_file, encoding='utf-8-sig')

print(f"\n[1] CSV geladen: {csv_file.name}")
print(f"    Transaktionen: {len(df)}")
print(f"    Kunden: {df['Kundennummer'].nunique()}")

# Gruppiere nach Kunde
customer_data = df.groupby('Kundennummer').agg({
    'Risk_Level': 'first',
    'Suspicion_Score': 'first',
    'Flags': lambda x: x.iloc[0] if pd.notna(x.iloc[0]) and x.iloc[0] != '' else '',
    'Threshold_Avoidance_Ratio_%': 'first',
    'Layering_Score': 'first',
    'Entropy_Complex': 'first',
    'Temporal_Density_Weeks': 'first',
    'Trust_Score': 'first',
}).reset_index()

# 1. Risk Level Verteilung
print(f"\n[2] RISK LEVEL VERTEILUNG")
print("-" * 80)
risk_counts = customer_data['Risk_Level'].value_counts()
total = len(customer_data)

for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    count = risk_counts.get(level, 0)
    percent = (count / total * 100) if total > 0 else 0
    print(f"    {level:<8}: {count:>3} ({percent:>5.1f}%)")

# 2. Score Statistik
print(f"\n[3] SUSPICION SCORE STATISTIK")
print("-" * 80)
print(f"    Min:    {customer_data['Suspicion_Score'].min():.2f}")
print(f"    Max:    {customer_data['Suspicion_Score'].max():.2f}")
print(f"    Mean:   {customer_data['Suspicion_Score'].mean():.2f}")
print(f"    Median: {customer_data['Suspicion_Score'].median():.2f}")

# Perzentile
print(f"\n    Perzentile:")
for p in [25, 50, 75, 90, 95, 99]:
    val = customer_data['Suspicion_Score'].quantile(p/100)
    print(f"      {p:>2}%: {val:>6.2f}")

# 3. Schwellen-Analyse
print(f"\n[4] SCHWELLEN-ANALYSE (1.6 / 2.8 / 5.0)")
print("-" * 80)

green_count = len(customer_data[customer_data['Suspicion_Score'] < 1.6])
yellow_count = len(customer_data[(customer_data['Suspicion_Score'] >= 1.6) & (customer_data['Suspicion_Score'] < 2.8)])
orange_count = len(customer_data[(customer_data['Suspicion_Score'] >= 2.8) & (customer_data['Suspicion_Score'] < 5.0)])
red_count = len(customer_data[customer_data['Suspicion_Score'] >= 5.0])

print(f"    < 1.6:     {green_count:>3} (GREEN)")
print(f"    1.6-2.8:   {yellow_count:>3} (YELLOW)")
print(f"    2.8-5.0:   {orange_count:>3} (ORANGE)")
print(f"    >= 5.0:    {red_count:>3} (RED)")

# 4. Score-Verteilung (Histogramm)
print(f"\n[5] SCORE-VERTEILUNG")
print("-" * 80)

# Nur aktive Kunden
active = customer_data[customer_data['Suspicion_Score'] > 0]
inactive = customer_data[customer_data['Suspicion_Score'] == 0]

print(f"    Inaktive (Score = 0): {len(inactive)} Kunden")
print(f"    Aktive (Score > 0):   {len(active)} Kunden")

if len(active) > 0:
    print(f"\n    Aktive Kunden - Score-Statistik:")
    print(f"      Min:    {active['Suspicion_Score'].min():.2f}")
    print(f"      Max:    {active['Suspicion_Score'].max():.2f}")
    print(f"      Mean:   {active['Suspicion_Score'].mean():.2f}")
    print(f"      Median: {active['Suspicion_Score'].median():.2f}")

# Detaillierte Verteilung
print(f"\n    Score-Bereiche (alle Kunden):")
ranges = [
    (0.0, 0.5, "GREEN"),
    (0.5, 1.0, "GREEN"),
    (1.0, 1.6, "GREEN"),
    (1.6, 2.0, "YELLOW"),
    (2.0, 2.8, "YELLOW"),
    (2.8, 3.5, "ORANGE"),
    (3.5, 5.0, "ORANGE"),
    (5.0, 10.0, "RED")
]

for low, high, expected_level in ranges:
    count = len(customer_data[(customer_data['Suspicion_Score'] >= low) & (customer_data['Suspicion_Score'] < high)])
    percent = (count / total * 100)
    if count > 0:
        print(f"      {low:.1f}-{high:.1f}: {count:>3} ({percent:>5.1f}%) -> {expected_level}")

# 5. Problem: Warum YELLOW = 0?
print(f"\n[6] PROBLEM-ANALYSE: YELLOW = 0")
print("-" * 80)

# Prüfe Kunden im YELLOW-Bereich (1.6-2.8)
yellow_range = customer_data[(customer_data['Suspicion_Score'] >= 1.6) & (customer_data['Suspicion_Score'] < 2.8)]
print(f"    Kunden im YELLOW-Bereich (1.6-2.8): {len(yellow_range)}")

if len(yellow_range) > 0:
    print(f"\n    Erste 10 Kunden im YELLOW-Bereich:")
    print(f"    {'Kunde':<10} {'Score':<8} {'Risk_Level':<12} {'Flags'}")
    print("-" * 80)
    for idx, row in yellow_range.head(10).iterrows():
        flags_short = str(row['Flags'])[:30] if pd.notna(row['Flags']) and row['Flags'] else "None"
        print(f"    {row['Kundennummer']:<10} {row['Suspicion_Score']:<8.2f} {row['Risk_Level']:<12} {flags_short}")

# Prüfe warum sie nicht YELLOW sind
if len(yellow_range) > 0:
    actual_yellow = yellow_range[yellow_range['Risk_Level'] == 'YELLOW']
    not_yellow = yellow_range[yellow_range['Risk_Level'] != 'YELLOW']
    
    print(f"\n    Tatsaechlich YELLOW: {len(actual_yellow)}")
    print(f"    NICHT YELLOW (aber im Bereich): {len(not_yellow)}")
    
    if len(not_yellow) > 0:
        print(f"\n    Kunden im YELLOW-Bereich, aber nicht YELLOW:")
        for level in ['GREEN', 'ORANGE', 'RED']:
            count = len(not_yellow[not_yellow['Risk_Level'] == level])
            if count > 0:
                print(f"      {level}: {count} Kunden")

# 6. Vergleich mit vorheriger Analyse
print(f"\n[7] VERGLEICH MIT VORHERIGER ANALYSE")
print("=" * 80)

print(f"\n    Vorher (152214.csv):")
print(f"      GREEN:  161 (65.4%)")
print(f"      YELLOW:  23 (9.3%)")
print(f"      ORANGE:  42 (17.1%)")
print(f"      RED:     20 (8.1%)")

print(f"\n    Jetzt (153323.csv):")
print(f"      GREEN:  {risk_counts.get('GREEN', 0):>3} ({risk_counts.get('GREEN', 0)/total*100:>5.1f}%)")
print(f"      YELLOW: {risk_counts.get('YELLOW', 0):>3} ({risk_counts.get('YELLOW', 0)/total*100:>5.1f}%)")
print(f"      ORANGE: {risk_counts.get('ORANGE', 0):>3} ({risk_counts.get('ORANGE', 0)/total*100:>5.1f}%)")
print(f"      RED:    {risk_counts.get('RED', 0):>3} ({risk_counts.get('RED', 0)/total*100:>5.1f}%)")

print(f"\n    Aenderung:")
print(f"      GREEN:  {risk_counts.get('GREEN', 0) - 161:>+4} Kunden")
print(f"      YELLOW: {risk_counts.get('YELLOW', 0) - 23:>+4} Kunden")
print(f"      ORANGE: {risk_counts.get('ORANGE', 0) - 42:>+4} Kunden")
print(f"      RED:    {risk_counts.get('RED', 0) - 20:>+4} Kunden")

# 7. Zusammenfassung
print(f"\n[8] ZUSAMMENFASSUNG")
print("=" * 80)

print(f"\n[PROBLEME]")
if risk_counts.get('YELLOW', 0) == 0:
    print(f"  KRITISCH: YELLOW = 0 Kunden!")
    print(f"  - {len(yellow_range)} Kunden im YELLOW-Bereich (1.6-2.8)")
    print(f"  - Aber alle haben andere Risk Levels")
    print(f"  - Schwellen-Logik funktioniert nicht!")

if risk_counts.get('ORANGE', 0) > 50:
    print(f"  WARNUNG: ORANGE zu hoch ({risk_counts.get('ORANGE', 0)} statt ~3)")

if risk_counts.get('RED', 0) < 15:
    print(f"  WARNUNG: RED zu niedrig ({risk_counts.get('RED', 0)} statt ~21)")

print("\n" + "=" * 80)

