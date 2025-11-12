"""
Umfassende Analyse der neuen CSV-Ergebnisse
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_171517.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("UMFASSENDE ANALYSE DER ERGEBNISSE")
print("=" * 70)

print("\n1. RISK LEVEL VERTEILUNG:")
risk_dist = df['Risk_Level'].value_counts()
print(risk_dist)
print(f"\n   Gesamt: {len(df)} Transaktionen")
print(f"   Eindeutige Kunden: {df['Kundennummer'].nunique()}")

print("\n2. TRUST_SCORE VERBESSERUNG:")
print("   Vorher (Analyzed_Trades_20251112_171055.csv):")
print("      YELLOW: 0.867")
print("      ORANGE: 0.818")
print("      RED: 0.587")
print("\n   Jetzt:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        avg_suspicion = level_df['Suspicion_Score'].mean()
        print(f"      {level:6s}: Trust={avg_trust:.3f}, Suspicion={avg_suspicion:.2f}")

print("\n3. TRUST_SCORE KORRELATION:")
print("   Erwartung: Hoeheres Risk_Level -> Niedrigerer Trust_Score")
correlation = df.groupby('Risk_Level')[['Trust_Score', 'Suspicion_Score']].mean()
print(correlation)

print("\n4. EINZIGE ZAHLUNGSMETHODE FLAG:")
einzige = df[df['Flags'].str.contains('EINZIGE ZAHLUNGSMETHODE', na=False)]
print(f"   Anzahl mit Flag: {len(einzige)} ({len(einzige)/len(df)*100:.1f}%)")
print(f"   Risk Level Verteilung:")
print(einzige['Risk_Level'].value_counts())
print("\n   Problem: Viele normale Kunden verwenden nur eine Zahlungsmethode!")
print("   Dies ist NICHT verdaechtig an sich.")

print("\n5. SUSPICION_SCORE STATISTIKEN:")
print(df['Suspicion_Score'].describe())

print("\n6. FLAGS HAEUFIGKEIT:")
all_flags = []
for flags_str in df['Flags'].dropna():
    if flags_str:
        flags = flags_str.split(' | ')
        all_flags.extend(flags)

flag_counts = pd.Series(all_flags).value_counts().head(10)
print(flag_counts)

