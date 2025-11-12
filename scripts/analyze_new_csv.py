"""
Analysiere die neue CSV nach Threshold-Anpassung
"""
import pandas as pd
import numpy as np

csv_file = "Analyzed_Trades_20251112_172952.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("ANALYSE NACH THRESHOLD-ANPASSUNG")
print("=" * 70)

print("\n1. RISK LEVEL VERTEILUNG:")
risk_dist = df['Risk_Level'].value_counts()
print(risk_dist)
print("\nProzentual:")
print(df['Risk_Level'].value_counts(normalize=True) * 100)

print("\n2. SUSPICION_SCORE STATISTIKEN:")
print(df['Suspicion_Score'].describe())

print("\n3. SUSPICION_SCORE NACH RISK_LEVEL:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        print(f"\n{level:6s}:")
        print(f"  Anzahl: {len(level_df)}")
        print(f"  Min: {level_df['Suspicion_Score'].min():.2f}")
        print(f"  Max: {level_df['Suspicion_Score'].max():.2f}")
        print(f"  Mean: {level_df['Suspicion_Score'].mean():.2f}")
        print(f"  Median: {level_df['Suspicion_Score'].median():.2f}")

print("\n4. PROBLEM-ANALYSE:")
print("   Laut Dokumentation sollten die Thresholds sein:")
print("   - GREEN: 0-150 SP")
print("   - YELLOW: 150-300 SP")
print("   - ORANGE: 300-500 SP")
print("   - RED: 500-1000+ SP")
print("\n   Aktuelle Verteilung:")

yellow_df = df[df['Risk_Level'] == 'YELLOW']
orange_df = df[df['Risk_Level'] == 'ORANGE']
red_df = df[df['Risk_Level'] == 'RED']
green_df = df[df['Risk_Level'] == 'GREEN']

if len(green_df) > 0:
    green_max = green_df['Suspicion_Score'].max()
    print(f"   GREEN: {len(green_df)} Kunden, Suspicion_Score 0.00-{green_max:.2f}")
    if green_max >= 150:
        print(f"      [WARNUNG] GREEN hat Scores >= 150!")

if len(yellow_df) > 0:
    yellow_min = yellow_df['Suspicion_Score'].min()
    yellow_max = yellow_df['Suspicion_Score'].max()
    print(f"   YELLOW: {len(yellow_df)} Kunden, Suspicion_Score {yellow_min:.2f}-{yellow_max:.2f}")
    if yellow_min < 150 or yellow_max >= 300:
        print(f"      [WARNUNG] YELLOW sollte 150-300 SP sein!")

if len(orange_df) > 0:
    orange_min = orange_df['Suspicion_Score'].min()
    orange_max = orange_df['Suspicion_Score'].max()
    print(f"   ORANGE: {len(orange_df)} Kunden, Suspicion_Score {orange_min:.2f}-{orange_max:.2f}")
    if orange_min < 300 or orange_max >= 500:
        print(f"      [WARNUNG] ORANGE sollte 300-500 SP sein!")

if len(red_df) > 0:
    red_min = red_df['Suspicion_Score'].min()
    red_max = red_df['Suspicion_Score'].max()
    print(f"   RED: {len(red_df)} Kunden, Suspicion_Score {red_min:.2f}-{red_max:.2f}")
    if red_min < 500:
        print(f"      [WARNUNG] RED sollte >= 500 SP sein!")

print("\n5. SUSPICION_SCORE VERTEILUNG (Percentile):")
percentiles = [0, 10, 25, 50, 75, 90, 95, 99, 100]
for p in percentiles:
    val = np.percentile(df['Suspicion_Score'], p)
    print(f"  {p:3d}%: {val:.2f}")

print("\n6. VERGLEICH MIT VORHERIGEN WERTEN:")
print("   Vorher (172606.csv):")
print("      GREEN: 46.0%")
print("      YELLOW: 0.6%")
print("      ORANGE: 46.4%")
print("      RED: 6.9%")
print("\n   Jetzt:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        pct = len(level_df) / len(df) * 100
        print(f"      {level:6s}: {pct:.1f}%")

