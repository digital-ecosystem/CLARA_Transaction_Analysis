"""
Überprüfe Trust_Score Werte in der analysierten CSV
"""
import pandas as pd
import numpy as np

# Lese analysierte CSV
csv_path = r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_20251110_172632.csv"
df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')

print("="*80)
print("TRUST_SCORE ANALYSE")
print("="*80)

print(f"\nGesamt Transaktionen: {len(df)}")
print(f"Gesamt Kunden: {df['Kundennummer'].nunique()}")

# Prüfe ob Trust_Score Spalte existiert
if 'Trust_Score' not in df.columns:
    print("\n[FEHLER] Trust_Score Spalte nicht gefunden!")
    print(f"Vorhandene Spalten: {list(df.columns)}")
    exit(1)

# Statistiken pro Kunde (nur erste Zeile pro Kunde)
df_customers = df.groupby('Kundennummer').first().reset_index()

print(f"\nKunden mit Trust_Score: {df_customers['Trust_Score'].notna().sum()}")
print(f"Kunden ohne Trust_Score: {df_customers['Trust_Score'].isna().sum()}")

# Statistiken
print("\n" + "="*80)
print("TRUST_SCORE STATISTIKEN")
print("="*80)

trust_scores = df_customers['Trust_Score'].dropna()
print(f"\nAnzahl gültiger Trust_Scores: {len(trust_scores)}")
print(f"Min: {trust_scores.min():.3f}")
print(f"Max: {trust_scores.max():.3f}")
print(f"Mean: {trust_scores.mean():.3f}")
print(f"Median: {trust_scores.median():.3f}")
print(f"Std: {trust_scores.std():.3f}")

# Verteilung
print("\n" + "="*80)
print("VERTEILUNG")
print("="*80)

print("\nTrust_Score Bereiche:")
print(f"  0.0 - 0.2: {(trust_scores < 0.2).sum()} Kunden ({(trust_scores < 0.2).sum()/len(trust_scores)*100:.1f}%)")
print(f"  0.2 - 0.3: {((trust_scores >= 0.2) & (trust_scores < 0.3)).sum()} Kunden ({((trust_scores >= 0.2) & (trust_scores < 0.3)).sum()/len(trust_scores)*100:.1f}%)")
print(f"  0.3 - 0.5: {((trust_scores >= 0.3) & (trust_scores < 0.5)).sum()} Kunden ({((trust_scores >= 0.3) & (trust_scores < 0.5)).sum()/len(trust_scores)*100:.1f}%)")
print(f"  0.5 - 0.7: {((trust_scores >= 0.5) & (trust_scores < 0.7)).sum()} Kunden ({((trust_scores >= 0.5) & (trust_scores < 0.7)).sum()/len(trust_scores)*100:.1f}%)")
print(f"  0.7 - 1.0: {(trust_scores >= 0.7).sum()} Kunden ({(trust_scores >= 0.7).sum()/len(trust_scores)*100:.1f}%)")

# Korrelation mit Risk_Level
print("\n" + "="*80)
print("KORRELATION MIT RISK_LEVEL")
print("="*80)

for risk_level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    risk_customers = df_customers[df_customers['Risk_Level'] == risk_level]
    if len(risk_customers) > 0:
        trust_avg = risk_customers['Trust_Score'].mean()
        trust_median = risk_customers['Trust_Score'].median()
        trust_min = risk_customers['Trust_Score'].min()
        trust_max = risk_customers['Trust_Score'].max()
        print(f"\n{risk_level}: {len(risk_customers)} Kunden")
        print(f"  Trust_Score Durchschnitt: {trust_avg:.3f}")
        print(f"  Trust_Score Median: {trust_median:.3f}")
        print(f"  Trust_Score Min: {trust_min:.3f}")
        print(f"  Trust_Score Max: {trust_max:.3f}")
        
        # Zähle niedrige Trust Scores (< 0.5)
        low_trust = (risk_customers['Trust_Score'] < 0.5).sum()
        print(f"  Kunden mit Trust_Score < 0.5: {low_trust} ({low_trust/len(risk_customers)*100:.1f}%)")

# Korrelation mit Suspicion_Score
print("\n" + "="*80)
print("KORRELATION MIT SUSPICION_SCORE")
print("="*80)

# Scatter-Plot Daten
low_suspicion = df_customers[df_customers['Suspicion_Score'] < 1.0]
medium_suspicion = df_customers[(df_customers['Suspicion_Score'] >= 1.0) & (df_customers['Suspicion_Score'] < 2.0)]
high_suspicion = df_customers[df_customers['Suspicion_Score'] >= 2.0]

print(f"\nNiedrige Suspicion (< 1.0): {len(low_suspicion)} Kunden")
if len(low_suspicion) > 0:
    print(f"  Trust_Score Durchschnitt: {low_suspicion['Trust_Score'].mean():.3f}")

print(f"\nMittlere Suspicion (1.0-2.0): {len(medium_suspicion)} Kunden")
if len(medium_suspicion) > 0:
    print(f"  Trust_Score Durchschnitt: {medium_suspicion['Trust_Score'].mean():.3f}")

print(f"\nHohe Suspicion (>= 2.0): {len(high_suspicion)} Kunden")
if len(high_suspicion) > 0:
    print(f"  Trust_Score Durchschnitt: {high_suspicion['Trust_Score'].mean():.3f}")

# Prüfe auf Auffälligkeiten
print("\n" + "="*80)
print("AUFFÄLLIGKEITEN")
print("="*80)

# 1. Trust_Score außerhalb 0-1 Bereich
out_of_range = df_customers[(df_customers['Trust_Score'] < 0) | (df_customers['Trust_Score'] > 1)]
if len(out_of_range) > 0:
    print(f"\n[WARNUNG] {len(out_of_range)} Kunden mit Trust_Score außerhalb 0-1:")
    for idx, row in out_of_range.iterrows():
        print(f"  Kunde {row['Kundennummer']}: Trust_Score = {row['Trust_Score']}")
else:
    print("\n[OK] Alle Trust_Scores im Bereich 0-1")

# 2. Hoher Risk_Level aber hoher Trust_Score (widersprüchlich)
high_risk_high_trust = df_customers[
    (df_customers['Risk_Level'].isin(['ORANGE', 'RED'])) & 
    (df_customers['Trust_Score'] >= 0.7)
]
if len(high_risk_high_trust) > 0:
    print(f"\n[INFO] {len(high_risk_high_trust)} Kunden mit hohem Risk aber hohem Trust_Score:")
    for idx, row in high_risk_high_trust.head(10).iterrows():
        print(f"  Kunde {row['Kundennummer']}: Risk={row['Risk_Level']}, Trust={row['Trust_Score']:.3f}, Suspicion={row['Suspicion_Score']:.2f}")

# 3. Niedriger Risk_Level aber niedriger Trust_Score (widersprüchlich)
low_risk_low_trust = df_customers[
    (df_customers['Risk_Level'] == 'GREEN') & 
    (df_customers['Trust_Score'] < 0.3)
]
if len(low_risk_low_trust) > 0:
    print(f"\n[INFO] {len(low_risk_low_trust)} GREEN Kunden mit sehr niedrigem Trust_Score:")
    for idx, row in low_risk_low_trust.head(10).iterrows():
        print(f"  Kunde {row['Kundennummer']}: Trust={row['Trust_Score']:.3f}, Suspicion={row['Suspicion_Score']:.2f}")

# 4. Konsistenz pro Kunde
print("\n" + "="*80)
print("KONSISTENZ-PRÜFUNG")
print("="*80)

inconsistent = 0
for customer_id in df['Kundennummer'].unique():
    customer_data = df[df['Kundennummer'] == customer_id]
    unique_trust_scores = customer_data['Trust_Score'].nunique()
    if unique_trust_scores > 1:
        inconsistent += 1
        if inconsistent <= 5:  # Zeige nur erste 5
            print(f"  [WARNUNG] Kunde {customer_id} hat {unique_trust_scores} verschiedene Trust_Scores:")
            print(f"    {customer_data['Trust_Score'].unique()}")

if inconsistent == 0:
    print("\n[OK] Alle Kunden haben konsistente Trust_Scores")
else:
    print(f"\n[WARNUNG] {inconsistent} Kunden haben inkonsistente Trust_Scores")

# Beispiele
print("\n" + "="*80)
print("BEISPIELE")
print("="*80)

# Top 10 niedrigste Trust_Scores
print("\nTop 10 niedrigste Trust_Scores:")
lowest_trust = df_customers.nsmallest(10, 'Trust_Score')[['Kundennummer', 'Risk_Level', 'Suspicion_Score', 'Trust_Score']]
for idx, row in lowest_trust.iterrows():
    print(f"  Kunde {row['Kundennummer']}: Trust={row['Trust_Score']:.3f}, Risk={row['Risk_Level']}, Suspicion={row['Suspicion_Score']:.2f}")

# Top 10 höchste Trust_Scores
print("\nTop 10 höchste Trust_Scores:")
highest_trust = df_customers.nlargest(10, 'Trust_Score')[['Kundennummer', 'Risk_Level', 'Suspicion_Score', 'Trust_Score']]
for idx, row in highest_trust.iterrows():
    print(f"  Kunde {row['Kundennummer']}: Trust={row['Trust_Score']:.3f}, Risk={row['Risk_Level']}, Suspicion={row['Suspicion_Score']:.2f}")

print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)

print(f"\n[OK] Trust_Score Analyse abgeschlossen")
print(f"[OK] {len(trust_scores)} gültige Trust_Scores gefunden")
print(f"[OK] Durchschnitt: {trust_scores.mean():.3f}, Median: {trust_scores.median():.3f}")

# Prüfe ob die Verteilung sinnvoll ist
if trust_scores.mean() < 0.3:
    print(f"\n[WARNUNG] Sehr niedriger durchschnittlicher Trust_Score ({trust_scores.mean():.3f})")
    print("  -> Möglicherweise zu viele verdächtige Kunden oder Berechnungsfehler")
elif trust_scores.mean() > 0.8:
    print(f"\n[WARNUNG] Sehr hoher durchschnittlicher Trust_Score ({trust_scores.mean():.3f})")
    print("  -> Möglicherweise zu konservativ oder Berechnungsfehler")
else:
    print(f"\n[OK] Durchschnittlicher Trust_Score ({trust_scores.mean():.3f}) ist im erwarteten Bereich")



