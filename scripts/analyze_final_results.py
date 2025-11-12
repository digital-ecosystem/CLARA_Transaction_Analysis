"""
Finale Analyse der neuen CSV nach allen Änderungen
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_172239.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("FINALE ANALYSE - Analyzed_Trades_20251112_172239.csv")
print("=" * 70)

print("\n1. RISK LEVEL VERTEILUNG:")
risk_dist = df['Risk_Level'].value_counts()
print(risk_dist)
print(f"\n   Gesamt: {len(df)} Transaktionen")
print(f"   Eindeutige Kunden: {df['Kundennummer'].nunique()}")

print("\n2. TRUST_SCORE KORRELATION:")
print("   Erwartung: Hoeheres Risk_Level -> Niedrigerer Trust_Score")
print("\n   Tatsaechlich:")
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        avg_suspicion = level_df['Suspicion_Score'].mean()
        min_trust = level_df['Trust_Score'].min()
        max_trust = level_df['Trust_Score'].max()
        print(f"      {level:6s}: Trust={avg_trust:.3f} (min={min_trust:.3f}, max={max_trust:.3f}), Suspicion={avg_suspicion:.2f}")

print("\n3. EINZIGE ZAHLUNGSMETHODE FLAG:")
einzige = df[df['Flags'].str.contains('EINZIGE ZAHLUNGSMETHODE', na=False)]
print(f"   Anzahl mit Flag: {len(einzige)} ({len(einzige)/len(df)*100:.1f}%)")
if len(einzige) == 0:
    print("   [OK] Flag wurde erfolgreich entfernt!")
else:
    print("   [WARNUNG] Flag ist noch vorhanden!")

print("\n4. SUSPICION_SCORE STATISTIKEN:")
print(df['Suspicion_Score'].describe())

print("\n5. TRUST_SCORE STATISTIKEN:")
print(df['Trust_Score'].describe())

print("\n6. VERGLEICH MIT VORHERIGEN WERTEN:")
print("   Vorher (171517.csv):")
print("      YELLOW: Trust=0.620")
print("      ORANGE: Trust=0.690")
print("      RED: Trust=0.474")
print("\n   Jetzt:")
for level in ['YELLOW', 'ORANGE', 'RED']:
    level_df = df[df['Risk_Level'] == level]
    if len(level_df) > 0:
        avg_trust = level_df['Trust_Score'].mean()
        old_trust = {'YELLOW': 0.620, 'ORANGE': 0.690, 'RED': 0.474}[level]
        change = avg_trust - old_trust
        status = "VERBESSERT" if change < -0.05 else "VERSCHLECHERT" if change > 0.05 else "STABIL"
        print(f"      {level:6s}: Trust={avg_trust:.3f} ({change:+.3f}) [{status}]")

print("\n7. FLAGS HAEUFIGKEIT (Top 10):")
all_flags = []
for flags_str in df['Flags'].dropna():
    if flags_str:
        # Entferne Emojis für bessere Lesbarkeit
        flags = flags_str.split(' | ')
        for flag in flags:
            # Entferne Emojis
            clean_flag = ''.join(char for char in flag if ord(char) < 128)
            all_flags.append(clean_flag)

flag_counts = pd.Series(all_flags).value_counts().head(10)
for flag, count in flag_counts.items():
    print(f"   {count:4d}x: {flag[:60]}")

print("\n8. WIDERSPRUECHLICHE FAELLE:")
print("   YELLOW/ORANGE/RED mit Trust_Score > 0.7:")
suspicious_high = df[(df['Risk_Level'].isin(['YELLOW', 'ORANGE', 'RED'])) & (df['Trust_Score'] > 0.7)]
print(f"   Anzahl: {len(suspicious_high)} ({len(suspicious_high)/len(df)*100:.1f}%)")
if len(suspicious_high) > 0:
    print(f"   Trust Durchschnitt: {suspicious_high['Trust_Score'].mean():.2f}")
    print(f"   Suspicion Durchschnitt: {suspicious_high['Suspicion_Score'].mean():.2f}")
    if len(suspicious_high) / len(df) > 0.1:
        print("   [WARNUNG] Immer noch viele widerspruechliche Faelle!")
    else:
        print("   [OK] Nur wenige widerspruechliche Faelle")

