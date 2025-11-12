"""
Verifiziert: Werden Smurfer, Geldwäsche und Entropie richtig erkannt?
"""

import pandas as pd
from pathlib import Path
import sys

print("="*80)
print("ERKENNUNGS-RATE VERIFIZIERUNG")
print("="*80)

# 1. Lade Original-CSV (mit Flags)
original_csv = Path("Trades_20251110_143922.csv")
if not original_csv.exists():
    print(f"Fehler: {original_csv} nicht gefunden!")
    sys.exit(1)

df_original = pd.read_csv(original_csv, encoding='windows-1252')

# 2. Lade Analysierte CSV
analyzed_csv = Path("output/Analyzed_Trades_20251112_152214.csv")
if not analyzed_csv.exists():
    print(f"Fehler: {analyzed_csv} nicht gefunden!")
    sys.exit(1)

df_analyzed = pd.read_csv(analyzed_csv, encoding='utf-8-sig')

print(f"\n[1] Dateien geladen:")
print(f"    Original: {len(df_original)} Transaktionen")
print(f"    Analysiert: {len(df_analyzed)} Transaktionen")

# 3. Identifiziere problematische Kunden aus Original-CSV
print(f"\n[2] IDENTIFIZIERE PROBLEMATISCHE KUNDEN (Original-CSV)")
print("-" * 80)

# Suche nach Flags in Original-CSV
smurfers = set()
launderers = set()
entropy_customers = set()

for idx, row in df_original.iterrows():
    customer_id = str(row['Kundennummer'])
    flags = str(row.get('Flags', '')).upper()
    
    # Prüfe auf Smurfing-Flags
    if any(flag in flags for flag in ['SMURFING', 'SCHWELLEN', 'THRESHOLD']):
        smurfers.add(customer_id)
    
    # Prüfe auf Geldwäsche-Flags
    if any(flag in flags for flag in ['LAYERING', 'GELDWAESCHE', 'GELDWSCHE', 'GELDWÄSCHE']):
        launderers.add(customer_id)
    
    # Prüfe auf Entropie-Flags
    if any(flag in flags for flag in ['ENTROPIE', 'ENTROPY', 'KOMPLEX']):
        entropy_customers.add(customer_id)

print(f"    Smurfer (Original):        {len(smurfers)} Kunden")
print(f"    Geldwäsche (Original):     {len(launderers)} Kunden")
print(f"    Entropie (Original):       {len(entropy_customers)} Kunden")

# Zeige Beispiele
if smurfers:
    print(f"\n    Beispiel Smurfer: {list(smurfers)[:5]}")
if launderers:
    print(f"    Beispiel Geldwäsche: {list(launderers)[:5]}")
if entropy_customers:
    print(f"    Beispiel Entropie: {list(entropy_customers)[:5]}")

# 4. Prüfe Erkennung in Analysierter CSV
print(f"\n[3] ERKENNUNG IN ANALYSIERTER CSV")
print("-" * 80)

# Gruppiere nach Kunde
customer_analysis = df_analyzed.groupby('Kundennummer').agg({
    'Risk_Level': 'first',
    'Suspicion_Score': 'first',
    'Flags': lambda x: x.iloc[0] if pd.notna(x.iloc[0]) and x.iloc[0] != '' else '',
    'Threshold_Avoidance_Ratio_%': 'first',
    'Layering_Score': 'first',
    'Entropy_Complex': 'first',
    'Temporal_Density_Weeks': 'first',
}).reset_index()

# Identifiziere erkannte Kunden
detected_smurfers = set()
detected_launderers = set()
detected_entropy = set()

for idx, row in customer_analysis.iterrows():
    customer_id = str(row['Kundennummer'])
    flags = str(row['Flags']).upper()
    
    # Smurfing-Erkennung
    if (row['Threshold_Avoidance_Ratio_%'] > 0 or 
        'SMURFING' in flags or 'SCHWELLEN' in flags or 'THRESHOLD' in flags):
        detected_smurfers.add(customer_id)
    
    # Geldwäsche-Erkennung
    if (row['Layering_Score'] > 0.5 or 
        'LAYERING' in flags or 'GELDW' in flags):
        detected_launderers.add(customer_id)
    
    # Entropie-Erkennung
    if (row['Entropy_Complex'] == 'Ja' or 
        'ENTROPIE' in flags or 'ENTROPY' in flags):
        detected_entropy.add(customer_id)

print(f"    Erkannte Smurfer:          {len(detected_smurfers)} Kunden")
print(f"    Erkannte Geldwäsche:       {len(detected_launderers)} Kunden")
print(f"    Erkannte Entropie:         {len(detected_entropy)} Kunden")

# 5. Berechne Erkennungsraten
print(f"\n[4] ERKENNUNGS-RATEN")
print("=" * 80)

# Smurfing
if len(smurfers) > 0:
    true_positives_smurf = len(smurfers & detected_smurfers)
    false_negatives_smurf = len(smurfers - detected_smurfers)
    false_positives_smurf = len(detected_smurfers - smurfers)
    
    recall_smurf = (true_positives_smurf / len(smurfers) * 100) if len(smurfers) > 0 else 0
    precision_smurf = (true_positives_smurf / len(detected_smurfers) * 100) if len(detected_smurfers) > 0 else 0
    
    print(f"\nSMURFING:")
    print(f"  Original:           {len(smurfers)} Kunden")
    print(f"  Erkannt:            {len(detected_smurfers)} Kunden")
    print(f"  True Positives:     {true_positives_smurf} Kunden")
    print(f"  False Negatives:    {false_negatives_smurf} Kunden")
    print(f"  False Positives:    {false_positives_smurf} Kunden")
    print(f"  Recall:             {recall_smurf:.1f}%")
    print(f"  Precision:          {precision_smurf:.1f}%")
    
    if false_negatives_smurf > 0:
        print(f"\n  Nicht erkannte Smurfer:")
        for cid in list(smurfers - detected_smurfers)[:5]:
            print(f"    - Kunde {cid}")
else:
    print(f"\nSMURFING: Keine Smurfer in Original-CSV gefunden")

# Geldwäsche
if len(launderers) > 0:
    true_positives_launder = len(launderers & detected_launderers)
    false_negatives_launder = len(launderers - detected_launderers)
    false_positives_launder = len(detected_launderers - launderers)
    
    recall_launder = (true_positives_launder / len(launderers) * 100) if len(launderers) > 0 else 0
    precision_launder = (true_positives_launder / len(detected_launderers) * 100) if len(detected_launderers) > 0 else 0
    
    print(f"\nGELDWÄSCHE:")
    print(f"  Original:           {len(launderers)} Kunden")
    print(f"  Erkannt:            {len(detected_launderers)} Kunden")
    print(f"  True Positives:     {true_positives_launder} Kunden")
    print(f"  False Negatives:    {false_negatives_launder} Kunden")
    print(f"  False Positives:    {false_positives_launder} Kunden")
    print(f"  Recall:             {recall_launder:.1f}%")
    print(f"  Precision:          {precision_launder:.1f}%")
    
    if false_negatives_launder > 0:
        print(f"\n  Nicht erkannte Geldwäsche:")
        for cid in list(launderers - detected_launderers)[:5]:
            print(f"    - Kunde {cid}")
else:
    print(f"\nGELDWÄSCHE: Keine Geldwäsche in Original-CSV gefunden")

# Entropie
if len(entropy_customers) > 0:
    true_positives_entropy = len(entropy_customers & detected_entropy)
    false_negatives_entropy = len(entropy_customers - detected_entropy)
    false_positives_entropy = len(detected_entropy - entropy_customers)
    
    recall_entropy = (true_positives_entropy / len(entropy_customers) * 100) if len(entropy_customers) > 0 else 0
    precision_entropy = (true_positives_entropy / len(detected_entropy) * 100) if len(detected_entropy) > 0 else 0
    
    print(f"\nENTROPIE:")
    print(f"  Original:           {len(entropy_customers)} Kunden")
    print(f"  Erkannt:            {len(detected_entropy)} Kunden")
    print(f"  True Positives:     {true_positives_entropy} Kunden")
    print(f"  False Negatives:    {false_negatives_entropy} Kunden")
    print(f"  False Positives:    {false_positives_entropy} Kunden")
    print(f"  Recall:             {recall_entropy:.1f}%")
    print(f"  Precision:          {precision_entropy:.1f}%")
    
    if false_negatives_entropy > 0:
        print(f"\n  Nicht erkannte Entropie:")
        for cid in list(entropy_customers - detected_entropy)[:5]:
            print(f"    - Kunde {cid}")
else:
    print(f"\nENTROPIE: Keine Entropie in Original-CSV gefunden")

# 6. Risk Level Analyse
print(f"\n[5] RISK LEVEL VERTEILUNG")
print("=" * 80)

risk_by_type = {
    'Smurfer': {},
    'Geldwäsche': {},
    'Entropie': {}
}

for customer_id in smurfers:
    risk = customer_analysis[customer_analysis['Kundennummer'] == customer_id]['Risk_Level'].values
    if len(risk) > 0:
        level = risk[0]
        risk_by_type['Smurfer'][level] = risk_by_type['Smurfer'].get(level, 0) + 1

for customer_id in launderers:
    risk = customer_analysis[customer_analysis['Kundennummer'] == customer_id]['Risk_Level'].values
    if len(risk) > 0:
        level = risk[0]
        risk_by_type['Geldwäsche'][level] = risk_by_type['Geldwäsche'].get(level, 0) + 1

for customer_id in entropy_customers:
    risk = customer_analysis[customer_analysis['Kundennummer'] == customer_id]['Risk_Level'].values
    if len(risk) > 0:
        level = risk[0]
        risk_by_type['Entropie'][level] = risk_by_type['Entropie'].get(level, 0) + 1

for problem_type, risk_dist in risk_by_type.items():
    if risk_dist:
        print(f"\n{problem_type}:")
        total = sum(risk_dist.values())
        for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
            count = risk_dist.get(level, 0)
            percent = (count / total * 100) if total > 0 else 0
            print(f"  {level:<8}: {count:>3} ({percent:>5.1f}%)")

# 7. Zusammenfassung
print(f"\n[6] ZUSAMMENFASSUNG")
print("=" * 80)

print(f"\n[ERKENNUNGS-QUALITÄT]")
if len(smurfers) > 0:
    if recall_smurf >= 80:
        print(f"  ✅ Smurfing: Gute Erkennung ({recall_smurf:.1f}% Recall)")
    elif recall_smurf >= 50:
        print(f"  ⚠️  Smurfing: Mittlere Erkennung ({recall_smurf:.1f}% Recall)")
    else:
        print(f"  ❌ Smurfing: Schlechte Erkennung ({recall_smurf:.1f}% Recall)")

if len(launderers) > 0:
    if recall_launder >= 80:
        print(f"  ✅ Geldwäsche: Gute Erkennung ({recall_launder:.1f}% Recall)")
    elif recall_launder >= 50:
        print(f"  ⚠️  Geldwäsche: Mittlere Erkennung ({recall_launder:.1f}% Recall)")
    else:
        print(f"  ❌ Geldwäsche: Schlechte Erkennung ({recall_launder:.1f}% Recall)")

if len(entropy_customers) > 0:
    if recall_entropy >= 80:
        print(f"  ✅ Entropie: Gute Erkennung ({recall_entropy:.1f}% Recall)")
    elif recall_entropy >= 50:
        print(f"  ⚠️  Entropie: Mittlere Erkennung ({recall_entropy:.1f}% Recall)")
    else:
        print(f"  ❌ Entropie: Schlechte Erkennung ({recall_entropy:.1f}% Recall)")

print("\n" + "=" * 80)

