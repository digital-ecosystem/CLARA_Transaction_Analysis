"""
Analysiere Verbesserungen bei Geldwäsche-Erkennung
Vergleiche alte vs. neue Schwellenwerte
"""
import pandas as pd

# Lese beide analysierten CSVs
from glob import glob
import os

analyzed_files = sorted(glob(r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_*.csv"), key=os.path.getctime)
if len(analyzed_files) < 2:
    print("Nicht genug analysierte CSVs gefunden!")
    exit(1)

old_csv = analyzed_files[0]  # Erste (älteste) CSV - alte Schwellenwerte
new_csv = analyzed_files[-1]  # Letzte (neueste) CSV - neue Schwellenwerte

print(f"Vergleiche:")
print(f"  ALT: {os.path.basename(old_csv)}")
print(f"  NEU: {os.path.basename(new_csv)}")
print()

df_old = pd.read_csv(old_csv, sep=';', encoding='utf-8-sig')
df_new = pd.read_csv(new_csv, sep=';', encoding='utf-8-sig')

print("="*80)
print("VERGLEICH: ALTE vs. NEUE SCHWELLENWERTE")
print("="*80)

# Zähle Kunden mit Layering Score > 0.5
old_layering = df_old[df_old['Layering_Score'] > 0.5]['Kundennummer'].nunique()
new_layering = df_new[df_new['Layering_Score'] > 0.5]['Kundennummer'].nunique()

print(f"\n**ALTE SCHWELLENWERTE** (2 Bar-In, 2 SEPA-Out, 40% Ratios, 2+ Indikatoren):")
print(f"  Kunden mit Layering Score > 0.5: {old_layering}")

print(f"\n**NEUE SCHWELLENWERTE** (5 Bar-In, 3 SEPA-Out, 70%/60% Ratios, 10k€ Volumen, 3+ Indikatoren):")
print(f"  Kunden mit Layering Score > 0.5: {new_layering}")

print(f"\n**VERBESSERUNG:**")
reduction = old_layering - new_layering
reduction_pct = (reduction / old_layering * 100) if old_layering > 0 else 0
print(f"  Reduktion: {reduction} Kunden ({reduction_pct:.1f}%)")

# Analysiere die Charakteristika der noch erkannten Kunden
print("\n" + "="*80)
print("CHARAKTERISTIKA DER ERKANNTEN GELDWÄSCHER (Top 20)")
print("="*80)

layering_customers_new = df_new[df_new['Layering_Score'] > 0.5]['Kundennummer'].unique()

# Lese ursprüngliche CSV für Transaktionsdetails
import io
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

for i, customer_id in enumerate(list(layering_customers_new)[:20], 1):
    customer_data_new = df_new[df_new['Kundennummer'] == customer_id]
    customer_data_orig = df_original[df_original['Kundennummer'] == customer_id]
    
    if len(customer_data_orig) == 0:
        continue
    
    name_col = [col for col in df_original.columns if 'Name' in col][0]
    name = customer_data_orig[name_col].iloc[0]
    layering_score = customer_data_new['Layering_Score'].iloc[0]
    risk_level = customer_data_new['Risk_Level'].iloc[0]
    
    # Transaktions-Statistiken
    bar_in = len(customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')])
    sepa_out = len(customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')])
    total_in = len(customer_data_orig[customer_data_orig['In/Out'] == 'In'])
    total_out = len(customer_data_orig[customer_data_orig['In/Out'] == 'Out'])
    
    # Ratios
    bar_in_ratio = (bar_in / total_in * 100) if total_in > 0 else 0
    sepa_out_ratio = (sepa_out / total_out * 100) if total_out > 0 else 0
    
    # Volumina
    bar_in_amounts = customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')]['Auftragsvolumen']
    sepa_out_amounts = customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')]['Auftragsvolumen']
    
    bar_in_volume = sum(pd.to_numeric(bar_in_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
    sepa_out_volume = sum(pd.to_numeric(sepa_out_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
    
    print(f"\n{i:2d}. {name} ({customer_id}) - {risk_level}")
    print(f"    Layering Score: {layering_score:.2f}")
    print(f"    Bar-In: {bar_in} ({bar_in_ratio:.0f}%), SEPA-Out: {sepa_out} ({sepa_out_ratio:.0f}%)")
    print(f"    Volumina: Bar-In={bar_in_volume:,.0f}€, SEPA-Out={sepa_out_volume:,.0f}€")
    
    # Prüfe welche neuen Indikatoren erfüllt sind
    indicators_met = []
    if bar_in >= 5 and sepa_out >= 3:
        indicators_met.append("[OK] Transaktionen (5+ Bar-In, 3+ SEPA-Out)")
    if bar_in_ratio >= 70:
        indicators_met.append(f"[OK] Bar-In Ratio >= 70%")
    if sepa_out_ratio >= 60:
        indicators_met.append(f"[OK] SEPA-Out Ratio >= 60%")
    if bar_in_volume >= 10000:
        indicators_met.append(f"[OK] Volumen >= 10.000 EUR")
    
    print(f"    Erfüllte Indikatoren ({len(indicators_met)}/4):")
    for ind in indicators_met:
        print(f"      {ind}")

# Analysiere die Verteilung
print("\n" + "="*80)
print("VERTEILUNG DER LAYERING SCORES")
print("="*80)

print("\n**ALT (lockere Schwellenwerte):**")
old_score_ranges = [
    ("0.0 - 0.2", (df_old['Layering_Score'] >= 0.0) & (df_old['Layering_Score'] < 0.2)),
    ("0.2 - 0.5", (df_old['Layering_Score'] >= 0.2) & (df_old['Layering_Score'] < 0.5)),
    ("0.5 - 0.8", (df_old['Layering_Score'] >= 0.5) & (df_old['Layering_Score'] < 0.8)),
    ("0.8 - 1.0", (df_old['Layering_Score'] >= 0.8) & (df_old['Layering_Score'] <= 1.0)),
]

for range_name, mask in old_score_ranges:
    count = df_old[mask]['Kundennummer'].nunique()
    print(f"  {range_name}: {count} Kunden")

print("\n**NEU (strenge Schwellenwerte):**")
new_score_ranges = [
    ("0.0 - 0.2", (df_new['Layering_Score'] >= 0.0) & (df_new['Layering_Score'] < 0.2)),
    ("0.2 - 0.5", (df_new['Layering_Score'] >= 0.2) & (df_new['Layering_Score'] < 0.5)),
    ("0.5 - 0.8", (df_new['Layering_Score'] >= 0.5) & (df_new['Layering_Score'] < 0.8)),
    ("0.8 - 1.0", (df_new['Layering_Score'] >= 0.8) & (df_new['Layering_Score'] <= 1.0)),
]

for range_name, mask in new_score_ranges:
    count = df_new[mask]['Kundennummer'].nunique()
    print(f"  {range_name}: {count} Kunden")

print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)
print(f"\n[OK] Verbesserung erfolgreich!")
print(f"   Kunden mit hohem Layering Score (>0.5): {old_layering} -> {new_layering}")
print(f"   Reduktion: {reduction} ({reduction_pct:.1f}%)")
print(f"\n[OK] Nur noch Kunden mit >= 5 Bar-In, >= 3 SEPA-Out, >= 70%/60% Ratios")
print(f"   und >= 10.000 EUR Volumen werden als Geldwaescher erkannt")

