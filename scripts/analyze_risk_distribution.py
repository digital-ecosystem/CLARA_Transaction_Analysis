"""
Analysiere Risk Level Verteilung und Suspicion Score Verteilung
"""
import pandas as pd
import numpy as np

csv_file = "Analyzed_Trades_20251112_172606.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("RISK LEVEL UND SUSPICION_SCORE ANALYSE")
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

print("\n4. SUSPICION_SCORE VERTEILUNG (Percentile):")
percentiles = [0, 10, 25, 50, 75, 90, 95, 99, 100]
for p in percentiles:
    val = np.percentile(df['Suspicion_Score'], p)
    print(f"  {p:3d}%: {val:.2f}")

print("\n5. PROBLEM-ANALYSE:")
print("   Laut Dokumentation sollten die Thresholds sein:")
print("   - GREEN: 0-150 SP (Unauffaellig)")
print("   - YELLOW: 150-300 SP (Leichte Auffaelligkeit)")
print("   - ORANGE: 300-500 SP (Erhoehtes Risiko)")
print("   - RED: 500-1000+ SP (Hoher Verdacht)")
print("\n   Aktuelle Verteilung:")
yellow_df = df[df['Risk_Level'] == 'YELLOW']
orange_df = df[df['Risk_Level'] == 'ORANGE']
red_df = df[df['Risk_Level'] == 'RED']

if len(yellow_df) > 0:
    print(f"   YELLOW: {len(yellow_df)} Kunden, Suspicion_Score {yellow_df['Suspicion_Score'].min():.2f}-{yellow_df['Suspicion_Score'].max():.2f}")
if len(orange_df) > 0:
    print(f"   ORANGE: {len(orange_df)} Kunden, Suspicion_Score {orange_df['Suspicion_Score'].min():.2f}-{orange_df['Suspicion_Score'].max():.2f}")
if len(red_df) > 0:
    print(f"   RED: {len(red_df)} Kunden, Suspicion_Score {red_df['Suspicion_Score'].min():.2f}-{red_df['Suspicion_Score'].max():.2f}")

print("\n6. EMPFOHLENE THRESHOLDS BASIEREND AUF PERCENTILEN:")
# Finde natürliche Clustering-Punkte
scores = df['Suspicion_Score'].values
scores_sorted = np.sort(scores)

# Finde größte Lücken
gaps = np.diff(scores_sorted)
large_gaps_idx = np.argsort(gaps)[-3:][::-1]
print("   Groesste Luecken in Suspicion_Score:")
for idx in large_gaps_idx:
    if idx < len(scores_sorted) - 1:
        gap_start = scores_sorted[idx]
        gap_end = scores_sorted[idx + 1]
        gap_size = gap_end - gap_start
        print(f"   Luecke bei {gap_start:.2f} - {gap_end:.2f} (Groesse: {gap_size:.2f})")

