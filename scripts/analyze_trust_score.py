"""
Analysiert Trust_Score Werte in der CSV-Datei
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_163712.csv"

df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 60)
print("TRUST_SCORE ANALYSE")
print("=" * 60)

print("\n1. Trust_Score = 0.0 Analyse:")
zero_trust = df[df['Trust_Score'] == 0.0]
print(f"   Anzahl: {len(zero_trust)} Zeilen")
print(f"   Risk_Level Verteilung:")
print(zero_trust['Risk_Level'].value_counts())
print(f"\n   Suspicion_Score Durchschnitt: {zero_trust['Suspicion_Score'].mean():.2f}")
print(f"   Suspicion_Score Min: {zero_trust['Suspicion_Score'].min():.2f}")
print(f"   Suspicion_Score Max: {zero_trust['Suspicion_Score'].max():.2f}")

print("\n2. Trust_Score > 0.7 Analyse:")
high_trust = df[df['Trust_Score'] > 0.7]
print(f"   Anzahl: {len(high_trust)} Zeilen")
print(f"   Risk_Level Verteilung:")
print(high_trust['Risk_Level'].value_counts())
print(f"\n   Suspicion_Score Durchschnitt: {high_trust['Suspicion_Score'].mean():.2f}")

print("\n3. Widersprüchliche Fälle:")
print("   YELLOW/ORANGE/RED mit hohem Trust_Score (> 0.7):")
suspicious_high_trust = df[(df['Risk_Level'].isin(['YELLOW', 'ORANGE', 'RED'])) & (df['Trust_Score'] > 0.7)]
print(f"   Anzahl: {len(suspicious_high_trust)} Zeilen")
if len(suspicious_high_trust) > 0:
    print(f"   Trust_Score Durchschnitt: {suspicious_high_trust['Trust_Score'].mean():.2f}")
    print(f"   Suspicion_Score Durchschnitt: {suspicious_high_trust['Suspicion_Score'].mean():.2f}")
    print(f"\n   Beispiele (erste 5):")
    examples = suspicious_high_trust[['Kundennummer', 'Risk_Level', 'Suspicion_Score', 'Trust_Score']].drop_duplicates().head(5)
    for idx, row in examples.iterrows():
        print(f"      Kunde {row['Kundennummer']}: Risk={row['Risk_Level']}, Suspicion={row['Suspicion_Score']:.2f}, Trust={row['Trust_Score']:.2f}")

print("\n4. GREEN mit niedrigem Trust_Score (< 0.3):")
green_low_trust = df[(df['Risk_Level'] == 'GREEN') & (df['Trust_Score'] < 0.3)]
print(f"   Anzahl: {len(green_low_trust)} Zeilen")
if len(green_low_trust) > 0:
    print(f"   Trust_Score Durchschnitt: {green_low_trust['Trust_Score'].mean():.2f}")
    print(f"   Suspicion_Score Durchschnitt: {green_low_trust['Suspicion_Score'].mean():.2f}")

print("\n5. Trust_Score Verteilung nach Risk_Level:")
print(df.groupby('Risk_Level')['Trust_Score'].agg(['count', 'mean', 'min', 'max', 'std']))

print("\n6. Erwartete vs. Tatsaechliche Korrelation:")
print("   Erwartung: Hoeheres Risk_Level -> Niedrigerer Trust_Score")
print("   Tatsaechlich:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        avg_suspicion = level_df['Suspicion_Score'].mean()
        print(f"      {level:6s}: Trust_Score={avg_trust:.3f}, Suspicion_Score={avg_suspicion:.2f}")

print("\n7. Problem-Analyse:")
print("   - Trust_Score sollte umgekehrt zu Suspicion_Score korrelieren")
print("   - YELLOW/ORANGE/RED sollten niedrigere Trust_Scores haben")
print("   - Viele 0.0 Werte bei GREEN Kunden (könnte OK sein, wenn wenig Daten)")

