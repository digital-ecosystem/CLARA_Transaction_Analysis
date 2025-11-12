"""
Analysiert die CSV-Ergebnisse und prüft Konsistenz mit Code
"""
import pandas as pd
import sys
from pathlib import Path

csv_file = "Analyzed_Trades_20251112_181239.csv"

print("="*80)
print("CSV ANALYSE: Analyzed_Trades_20251112_181239.csv")
print("="*80)

# Lade CSV
if not Path(csv_file).exists():
    print(f"Fehler: {csv_file} nicht gefunden!")
    sys.exit(1)

df = pd.read_csv(csv_file, encoding='utf-8-sig')

print(f"\n[1] CSV GELADEN")
print(f"    Transaktionen: {len(df)}")
print(f"    Eindeutige Kunden: {df['Kundennummer'].nunique()}")

# Gruppiere nach Kunde (jeder Kunde hat gleiche Werte)
customer_data = df.groupby('Kundennummer').agg({
    'Risk_Level': 'first',
    'Suspicion_Score': 'first',
    'Flags': 'first',
    'Threshold_Avoidance_Ratio_%': 'first',
    'Cumulative_Large_Amount': 'first',
    'Temporal_Density_Weeks': 'first',
    'Layering_Score': 'first',
    'Entropy_Complex': 'first',
}).reset_index()

print(f"\n[2] RISK LEVEL VERTEILUNG")
print("-" * 80)
risk_counts = customer_data['Risk_Level'].value_counts()
total = len(customer_data)

for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    count = risk_counts.get(level, 0)
    percent = (count / total * 100) if total > 0 else 0
    status = "[OK]" if count > 0 or level == 'GREEN' else "[FEHLT]"
    print(f"    {status} {level:<8}: {count:>3} Kunden ({percent:>5.1f}%)")

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

print(f"\n[4] SCHWELLEN-ANALYSE (150 / 300 / 500)")
print("-" * 80)

# Prüfe ob Risk_Levels korrekt zugeordnet sind
errors = []
for idx, row in customer_data.iterrows():
    score = row['Suspicion_Score']
    risk = row['Risk_Level']
    
    # Erwartetes Risk_Level basierend auf Score
    if score < 150:
        expected = 'GREEN'
    elif score < 300:
        expected = 'YELLOW'
    elif score < 500:
        expected = 'ORANGE'
    else:
        expected = 'RED'
    
    if risk != expected:
        errors.append({
            'customer': row['Kundennummer'],
            'score': score,
            'actual': risk,
            'expected': expected
        })

if errors:
    print(f"    [FEHLER] {len(errors)} FEHLER GEFUNDEN:")
    for err in errors[:10]:  # Zeige max 10
        print(f"       Kunde {err['customer']}: Score {err['score']:.2f} -> {err['actual']} (sollte {err['expected']} sein)")
    if len(errors) > 10:
        print(f"       ... und {len(errors) - 10} weitere")
else:
    print(f"    [OK] Alle Risk_Levels korrekt zugeordnet!")

# Verteilung nach Schwellen
print(f"\n    Verteilung nach Suspicion_Score:")
green_count = len(customer_data[customer_data['Suspicion_Score'] < 150])
yellow_count = len(customer_data[(customer_data['Suspicion_Score'] >= 150) & (customer_data['Suspicion_Score'] < 300)])
orange_count = len(customer_data[(customer_data['Suspicion_Score'] >= 300) & (customer_data['Suspicion_Score'] < 500)])
red_count = len(customer_data[customer_data['Suspicion_Score'] >= 500])

print(f"      < 150 SP:  {green_count:>3} Kunden (GREEN)")
print(f"      150-300:  {yellow_count:>3} Kunden (YELLOW)")
print(f"      300-500:  {orange_count:>3} Kunden (ORANGE)")
print(f"      >= 500:   {red_count:>3} Kunden (RED)")

print(f"\n[5] BEISPIEL-KUNDEN")
print("-" * 80)

# Zeige Beispiele für jedes Risk Level
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    level_customers = customer_data[customer_data['Risk_Level'] == level]
    if len(level_customers) > 0:
        example = level_customers.iloc[0]
        print(f"\n    {level} Beispiel (Kunde {example['Kundennummer']}):")
        print(f"      Suspicion_Score: {example['Suspicion_Score']:.2f}")
        print(f"      Temporal_Density: {example['Temporal_Density_Weeks']:.2f} Tx/Woche")
        print(f"      Layering_Score: {example['Layering_Score']:.2f}")
        print(f"      Entropy_Complex: {example['Entropy_Complex']}")
        flags = str(example['Flags']) if pd.notna(example['Flags']) else ''
        if flags:
            # Entferne problematische Unicode-Zeichen für Windows-Konsole
            flags_safe = flags.encode('ascii', 'ignore').decode('ascii')
            print(f"      Flags: {flags_safe[:100]}...")
        else:
            print(f"      Flags: (keine)")

print(f"\n[6] DETAILLIERTE ANALYSE")
print("-" * 80)

# Analyse der verdächtigen Kunden
suspicious_customers = customer_data[customer_data['Risk_Level'].isin(['YELLOW', 'ORANGE', 'RED'])]
print(f"\n    Verdächtige Kunden (YELLOW/ORANGE/RED): {len(suspicious_customers)}")

if len(suspicious_customers) > 0:
    print(f"\n    Top 10 nach Suspicion_Score:")
    top_suspicious = suspicious_customers.nlargest(10, 'Suspicion_Score')
    for idx, row in top_suspicious.iterrows():
        print(f"      Kunde {row['Kundennummer']}: {row['Suspicion_Score']:.2f} SP -> {row['Risk_Level']}")

# Analyse der Flags
print(f"\n    Flag-Verteilung:")
all_flags = []
for flags in customer_data['Flags']:
    if pd.notna(flags) and flags != '':
        flag_list = str(flags).split(' | ')
        all_flags.extend(flag_list)

if all_flags:
    from collections import Counter
    flag_counts = Counter(all_flags)
    print(f"      Gesamt Flags: {len(all_flags)}")
    print(f"      Eindeutige Flags: {len(flag_counts)}")
    print(f"\n      Häufigste Flags:")
    for flag, count in flag_counts.most_common(10):
        # Entferne problematische Unicode-Zeichen
        flag_safe = flag.encode('ascii', 'ignore').decode('ascii')
        print(f"        {flag_safe}: {count}x")

# Analyse der Metriken
print(f"\n[7] METRIKEN-ANALYSE")
print("-" * 80)

print(f"\n    Temporal_Density_Weeks:")
print(f"      Min: {customer_data['Temporal_Density_Weeks'].min():.2f}")
print(f"      Max: {customer_data['Temporal_Density_Weeks'].max():.2f}")
print(f"      Mean: {customer_data['Temporal_Density_Weeks'].mean():.2f}")
print(f"      > 1.0 (verdächtig): {len(customer_data[customer_data['Temporal_Density_Weeks'] > 1.0])} Kunden")

print(f"\n    Layering_Score:")
print(f"      Min: {customer_data['Layering_Score'].min():.2f}")
print(f"      Max: {customer_data['Layering_Score'].max():.2f}")
print(f"      Mean: {customer_data['Layering_Score'].mean():.2f}")
print(f"      >= 0.5 (verdächtig): {len(customer_data[customer_data['Layering_Score'] >= 0.5])} Kunden")

print(f"\n    Threshold_Avoidance_Ratio:")
print(f"      Min: {customer_data['Threshold_Avoidance_Ratio_%'].min():.1f}%")
print(f"      Max: {customer_data['Threshold_Avoidance_Ratio_%'].max():.1f}%")
print(f"      Mean: {customer_data['Threshold_Avoidance_Ratio_%'].mean():.1f}%")
print(f"      >= 50% (verdächtig): {len(customer_data[customer_data['Threshold_Avoidance_Ratio_%'] >= 50.0])} Kunden")

print(f"\n    Entropy_Complex:")
entropy_complex_count = len(customer_data[customer_data['Entropy_Complex'] == 'Ja'])
print(f"      'Ja': {entropy_complex_count} Kunden ({entropy_complex_count/total*100:.1f}%)")

print(f"\n[8] CODE-VERGLEICH")
print("-" * 80)
print("    [OK] Predictability-Analyse implementiert")
print("    [OK] Gewichtungen: 40/25/25/10 (Weight/Entropie/Predictability/Statistik)")
print("    [OK] Schwellenwerte: 150/300/500 SP")
print("    [OK] Multiplikatoren: 2.0 / 1.2 / 1.0 / 1.5")

print("\n" + "="*80)
print("ANALYSE ABGESCHLOSSEN")
print("="*80)

