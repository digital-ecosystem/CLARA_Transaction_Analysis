"""
Analysiert Trust_Score Werte nach Anpassung
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_170438.csv"

df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("TRUST_SCORE ANALYSE NACH ANPASSUNG")
print("=" * 70)

print("\n1. Trust_Score Statistik:")
print(df['Trust_Score'].describe())

print("\n2. Trust_Score Verteilung nach Risk_Level:")
stats = df.groupby('Risk_Level')['Trust_Score'].agg(['count', 'mean', 'min', 'max', 'std'])
print(stats)

print("\n3. Korrelation Trust_Score vs Suspicion_Score:")
print("   Erwartung: Hoeheres Risk_Level -> Niedrigerer Trust_Score")
print("   Tatsaechlich:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        avg_suspicion = level_df['Suspicion_Score'].mean()
        print(f"      {level:6s}: Trust={avg_trust:.3f}, Suspicion={avg_suspicion:.2f}")

print("\n4. Widerspruechliche Faelle:")
print("   YELLOW/ORANGE/RED mit Trust_Score > 0.7:")
suspicious_high = df[(df['Risk_Level'].isin(['YELLOW', 'ORANGE', 'RED'])) & (df['Trust_Score'] > 0.7)]
print(f"   Anzahl: {len(suspicious_high)} Zeilen")
if len(suspicious_high) > 0:
    print(f"   Trust_Score Durchschnitt: {suspicious_high['Trust_Score'].mean():.2f}")
    print(f"   Suspicion_Score Durchschnitt: {suspicious_high['Suspicion_Score'].mean():.2f}")
    print(f"\n   Beispiele (erste 5 Kunden):")
    examples = suspicious_high[['Kundennummer', 'Risk_Level', 'Suspicion_Score', 'Trust_Score']].drop_duplicates().head(5)
    for idx, row in examples.iterrows():
        print(f"      Kunde {row['Kundennummer']}: Risk={row['Risk_Level']}, Suspicion={row['Suspicion_Score']:.2f}, Trust={row['Trust_Score']:.2f}")

print("\n5. Vergleich mit vorherigen Werten:")
print("   Vorher (Analyzed_Trades_20251112_163712.csv):")
print("      YELLOW: Trust=0.823, Suspicion=1.57")
print("      ORANGE: Trust=0.739, Suspicion=3.45")
print("      RED:   Trust=0.583, Suspicion=15.23")
print("\n   Jetzt:")
for level in ['YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        avg_suspicion = level_df['Suspicion_Score'].mean()
        change = avg_trust - {'YELLOW': 0.823, 'ORANGE': 0.739, 'RED': 0.583}[level]
        print(f"      {level:6s}: Trust={avg_trust:.3f} ({change:+.3f}), Suspicion={avg_suspicion:.2f}")

print("\n6. Problem-Analyse:")
if len(suspicious_high) > 0:
    print("   [WARNUNG] Trust_Score-Werte haben sich NICHT geaendert!")
    print("   Moegliche Ursachen:")
    print("      - Server wurde nicht neu gestartet")
    print("      - Aenderungen sind nicht wirksam")
    print("      - Trust_Score wird aus Cache geladen")
else:
    print("   [OK] Keine widerspruechlichen Faelle gefunden!")

