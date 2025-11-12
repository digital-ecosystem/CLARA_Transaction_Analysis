"""
Prüfe False Positives bei Geldwäsche-Erkennung
"""
import pandas as pd
import io

# Lese ursprüngliche CSV
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Lese analysierte CSV
analyzed_csv = r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_20251110_160843.csv"
df_analyzed = pd.read_csv(analyzed_csv, sep=';', encoding='utf-8-sig')

print("="*80)
print("ANALYSE: FALSE POSITIVES BEI GELDWÄSCHE-ERKENNUNG")
print("="*80)

# Finde Kunden mit Layering Score > 0
layering_customers = df_analyzed[df_analyzed['Layering_Score'] > 0]['Kundennummer'].unique()
print(f"\nKunden mit Layering Score > 0: {len(layering_customers)}")

# Finde echte Geldwäscher aus VBA
if 'Problemkunde' in df_original.columns:
    real_launderers = df_original[df_original['Problemkunde'] == 'Geldwasche']['Kundennummer'].unique()
    print(f"Echte Geldwäscher (VBA): {len(real_launderers)}")
    
    # False Positives
    false_positives = set(layering_customers) - set(real_launderers)
    print(f"False Positives: {len(false_positives)}")
    
    print("\n" + "="*80)
    print("FALSE POSITIVES (Top 20)")
    print("="*80)
    
    for i, customer_id in enumerate(list(false_positives)[:20], 1):
        customer_data_orig = df_original[df_original['Kundennummer'] == customer_id]
        customer_data_analyzed = df_analyzed[df_analyzed['Kundennummer'] == customer_id]
        
        if len(customer_data_orig) == 0 or len(customer_data_analyzed) == 0:
            continue
        
        name_col = [col for col in df_original.columns if 'Name' in col][0]
        name = customer_data_orig[name_col].iloc[0]
        layering_score = customer_data_analyzed['Layering_Score'].iloc[0]
        
        # VBA Problem Type
        problem_type = customer_data_orig['Problemkunde'].iloc[0] if pd.notna(customer_data_orig['Problemkunde'].iloc[0]) else "Normal"
        
        # Transaktions-Statistiken
        bar_in = len(customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')])
        sepa_out = len(customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')])
        total_in = len(customer_data_orig[customer_data_orig['In/Out'] == 'In'])
        total_out = len(customer_data_orig[customer_data_orig['In/Out'] == 'Out'])
        
        # Berechne Ratios
        bar_in_ratio = (bar_in / total_in * 100) if total_in > 0 else 0
        sepa_out_ratio = (sepa_out / total_out * 100) if total_out > 0 else 0
        
        # Berechne Volumina
        bar_in_amounts = customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')]['Auftragsvolumen']
        sepa_out_amounts = customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')]['Auftragsvolumen']
        
        bar_in_volume = sum(pd.to_numeric(bar_in_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
        sepa_out_volume = sum(pd.to_numeric(sepa_out_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
        
        print(f"\n{i:2d}. {name} ({customer_id}) - VBA Type: {problem_type}")
        print(f"    Layering Score: {layering_score:.2f}")
        print(f"    Transaktionen: {len(customer_data_orig)} (In: {total_in}, Out: {total_out})")
        print(f"    Bar-In: {bar_in} ({bar_in_ratio:.0f}%), SEPA-Out: {sepa_out} ({sepa_out_ratio:.0f}%)")
        print(f"    Volumina: Bar-In={bar_in_volume:,.0f}€, SEPA-Out={sepa_out_volume:,.0f}€")
        
        # Prüfe welche Indikatoren erfüllt sind
        indicators = []
        if bar_in >= 2 and sepa_out >= 2:
            indicators.append(f"✓ Transaktionen (Bar-In={bar_in}, SEPA-Out={sepa_out})")
        if bar_in_ratio >= 40:
            indicators.append(f"✓ Bar-In Ratio ({bar_in_ratio:.0f}% >= 40%)")
        if sepa_out_ratio >= 40:
            indicators.append(f"✓ SEPA-Out Ratio ({sepa_out_ratio:.0f}% >= 40%)")
        
        print(f"    Erfüllte Indikatoren: {len(indicators)}")
        for ind in indicators:
            print(f"      {ind}")
    
    # Zeige auch echte Geldwäscher zum Vergleich
    print("\n" + "="*80)
    print("ECHTE GELDWÄSCHER ZUM VERGLEICH (Top 5)")
    print("="*80)
    
    for i, customer_id in enumerate(list(real_launderers)[:5], 1):
        customer_data_orig = df_original[df_original['Kundennummer'] == customer_id]
        customer_data_analyzed = df_analyzed[df_analyzed['Kundennummer'] == customer_id]
        
        if len(customer_data_orig) == 0 or len(customer_data_analyzed) == 0:
            continue
        
        name = customer_data_orig[name_col].iloc[0]
        layering_score = customer_data_analyzed['Layering_Score'].iloc[0]
        
        bar_in = len(customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')])
        sepa_out = len(customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')])
        total_in = len(customer_data_orig[customer_data_orig['In/Out'] == 'In'])
        total_out = len(customer_data_orig[customer_data_orig['In/Out'] == 'Out'])
        
        bar_in_ratio = (bar_in / total_in * 100) if total_in > 0 else 0
        sepa_out_ratio = (sepa_out / total_out * 100) if total_out > 0 else 0
        
        bar_in_amounts = customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')]['Auftragsvolumen']
        sepa_out_amounts = customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')]['Auftragsvolumen']
        
        bar_in_volume = sum(pd.to_numeric(bar_in_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
        sepa_out_volume = sum(pd.to_numeric(sepa_out_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
        
        print(f"\n{i}. {name} ({customer_id})")
        print(f"   Layering Score: {layering_score:.2f}")
        print(f"   Transaktionen: {len(customer_data_orig)} (In: {total_in}, Out: {total_out})")
        print(f"   Bar-In: {bar_in} ({bar_in_ratio:.0f}%), SEPA-Out: {sepa_out} ({sepa_out_ratio:.0f}%)")
        print(f"   Volumina: Bar-In={bar_in_volume:,.0f}€, SEPA-Out={sepa_out_volume:,.0f}€")
else:
    print("\nKeine 'Problemkunde' Spalte in ursprünglicher CSV")

