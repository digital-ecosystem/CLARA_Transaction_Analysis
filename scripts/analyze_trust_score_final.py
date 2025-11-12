"""
Finale Analyse der Trust_Score-Werte nach Anpassung
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_171055.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("TRUST_SCORE FINALE ANALYSE")
print("=" * 70)

print("\n1. Trust_Score Statistik:")
stats = df['Trust_Score'].describe()
print(stats)

print("\n2. Trust_Score Verteilung nach Risk_Level:")
level_stats = df.groupby('Risk_Level')['Trust_Score'].agg(['count', 'mean', 'min', 'max', 'std'])
print(level_stats)

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
print(f"   Anzahl: {len(suspicious_high)} Zeilen ({len(suspicious_high)/len(df)*100:.1f}%)")
if len(suspicious_high) > 0:
    print(f"   Trust_Score Durchschnitt: {suspicious_high['Trust_Score'].mean():.2f}")
    print(f"   Suspicion_Score Durchschnitt: {suspicious_high['Suspicion_Score'].mean():.2f}")

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
        old_trust = {'YELLOW': 0.823, 'ORANGE': 0.739, 'RED': 0.583}[level]
        change = avg_trust - old_trust
        status = "VERSCHLECHERT" if change > 0 else "VERBESSERT" if change < -0.05 else "UNVERAENDERT"
        print(f"      {level:6s}: Trust={avg_trust:.3f} ({change:+.3f}) [{status}], Suspicion={avg_suspicion:.2f}")

print("\n6. Problem-Analyse:")
if len(suspicious_high) > 0:
    print("   [KRITISCH] Trust_Score-Werte haben sich NICHT verbessert!")
    print("   Moegliche Ursachen:")
    print("      1. Abweichungen sind zu niedrig (z.B. 0.28)")
    print("      2. Selbst mit ^2.0 Bestrafung bleibt Trust_Score hoch")
    print("      3. Predictability ist zu hoch (z.B. 0.57)")
    print("      4. Peer Deviation = 0.0 (keine Peers gefunden)")
    print("\n   Empfehlung:")
    print("      - Direkte Verknuepfung mit verdaechtigen Indikatoren")
    print("      - Wenn Suspicion_Score > 1.0, Trust_Score reduzieren")
    print("      - Wenn Smurfing/Layering erkannt, Trust_Score reduzieren")
else:
    print("   [OK] Keine widerspruechlichen Faelle gefunden!")

print("\n7. Trust_Score Verteilung:")
print("   < 0.3: ", len(df[df['Trust_Score'] < 0.3]), f"({len(df[df['Trust_Score'] < 0.3])/len(df)*100:.1f}%)")
print("   0.3-0.5: ", len(df[(df['Trust_Score'] >= 0.3) & (df['Trust_Score'] < 0.5)]), f"({len(df[(df['Trust_Score'] >= 0.3) & (df['Trust_Score'] < 0.5)])/len(df)*100:.1f}%)")
print("   0.5-0.7: ", len(df[(df['Trust_Score'] >= 0.5) & (df['Trust_Score'] < 0.7)]), f"({len(df[(df['Trust_Score'] >= 0.5) & (df['Trust_Score'] < 0.7)])/len(df)*100:.1f}%)")
print("   >= 0.7: ", len(df[df['Trust_Score'] >= 0.7]), f"({len(df[df['Trust_Score'] >= 0.7])/len(df)*100:.1f}%)")

