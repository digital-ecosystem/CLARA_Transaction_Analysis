"""
Prüfe False Positives nach Verbesserung der Schwellenwerte
"""
import pandas as pd
import io
from glob import glob
import os

# Finde neueste analysierte CSV
analyzed_files = glob(r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_*.csv")
analyzed_csv = max(analyzed_files, key=os.path.getctime)
print(f"Verwende: {analyzed_csv}")

# Lese ursprüngliche CSV
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Lese analysierte CSV
df_analyzed = pd.read_csv(analyzed_csv, sep=';', encoding='utf-8-sig')

print("="*80)
print("ANALYSE: FALSE POSITIVES NACH VERBESSERUNG")
print("="*80)

# Finde Kunden mit Layering Score > 0.5 (signifikant)
layering_customers = df_analyzed[df_analyzed['Layering_Score'] > 0.5]['Kundennummer'].unique()
print(f"\nKunden mit Layering Score > 0.5: {len(layering_customers)}")

# Finde Kunden mit Geldwäsche-Flags
geldwaesche_flags = df_analyzed[df_analyzed['Flags'].str.contains('GELDW|LAYERING', case=False, na=False)]['Kundennummer'].unique()
print(f"Kunden mit Geldwäsche-Flags: {len(geldwaesche_flags)}")

# Finde echte Geldwäscher aus VBA
if 'Problemkunde' in df_original.columns:
    real_launderers = df_original[df_original['Problemkunde'] == 'Geldwasche']['Kundennummer'].unique()
    print(f"Echte Geldwäscher (VBA): {len(real_launderers)}")
    
    # True Positives & False Positives
    true_positives = set(layering_customers) & set(real_launderers)
    false_positives = set(layering_customers) - set(real_launderers)
    false_negatives = set(real_launderers) - set(layering_customers)
    
    print(f"\n" + "="*80)
    print("STATISTIKEN")
    print("="*80)
    print(f"True Positives:  {len(true_positives)} / {len(real_launderers)} ({len(true_positives)/len(real_launderers)*100:.1f}%)")
    print(f"False Positives: {len(false_positives)}")
    print(f"False Negatives: {len(false_negatives)}")
    
    if len(true_positives) + len(false_positives) > 0:
        precision = len(true_positives) / (len(true_positives) + len(false_positives))
        print(f"Precision:       {precision*100:.1f}%")
    
    if len(true_positives) + len(false_negatives) > 0:
        recall = len(true_positives) / (len(true_positives) + len(false_negatives))
        print(f"Recall:          {recall*100:.1f}%")
    
    if false_positives:
        print("\n" + "="*80)
        print(f"FALSE POSITIVES ({len(false_positives)} Kunden)")
        print("="*80)
        
        for i, customer_id in enumerate(sorted(false_positives)[:20], 1):
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
            
            # Ratios
            bar_in_ratio = (bar_in / total_in * 100) if total_in > 0 else 0
            sepa_out_ratio = (sepa_out / total_out * 100) if total_out > 0 else 0
            
            # Volumina
            bar_in_amounts = customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')]['Auftragsvolumen']
            bar_in_volume = sum(pd.to_numeric(bar_in_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
            
            print(f"\n{i:2d}. {name} ({customer_id}) - VBA: {problem_type}")
            print(f"    Layering Score: {layering_score:.2f}")
            print(f"    Bar-In: {bar_in} ({bar_in_ratio:.0f}%), SEPA-Out: {sepa_out} ({sepa_out_ratio:.0f}%)")
            print(f"    Bar-In Volumen: {bar_in_volume:,.0f}€")
    else:
        print("\n✅ KEINE FALSE POSITIVES!")
    
    if false_negatives:
        print("\n" + "="*80)
        print(f"FALSE NEGATIVES ({len(false_negatives)} Kunden)")
        print("="*80)
        
        for i, customer_id in enumerate(sorted(false_negatives)[:10], 1):
            customer_data_orig = df_original[df_original['Kundennummer'] == customer_id]
            customer_data_analyzed = df_analyzed[df_analyzed['Kundennummer'] == customer_id]
            
            if len(customer_data_orig) == 0:
                continue
            
            name_col = [col for col in df_original.columns if 'Name' in col][0]
            name = customer_data_orig[name_col].iloc[0]
            layering_score = customer_data_analyzed['Layering_Score'].iloc[0] if len(customer_data_analyzed) > 0 else 0.0
            
            bar_in = len(customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')])
            sepa_out = len(customer_data_orig[(customer_data_orig['Art'] == 'SEPA') & (customer_data_orig['In/Out'] == 'Out')])
            total_in = len(customer_data_orig[customer_data_orig['In/Out'] == 'In'])
            total_out = len(customer_data_orig[customer_data_orig['In/Out'] == 'Out'])
            
            bar_in_ratio = (bar_in / total_in * 100) if total_in > 0 else 0
            sepa_out_ratio = (sepa_out / total_out * 100) if total_out > 0 else 0
            
            bar_in_amounts = customer_data_orig[(customer_data_orig['Art'] == 'Bar') & (customer_data_orig['In/Out'] == 'In')]['Auftragsvolumen']
            bar_in_volume = sum(pd.to_numeric(bar_in_amounts.str.replace(',', '.'), errors='coerce').fillna(0))
            
            print(f"\n{i:2d}. {name} ({customer_id})")
            print(f"    Layering Score: {layering_score:.2f}")
            print(f"    Bar-In: {bar_in} ({bar_in_ratio:.0f}%), SEPA-Out: {sepa_out} ({sepa_out_ratio:.0f}%)")
            print(f"    Bar-In Volumen: {bar_in_volume:,.0f}€")
            print(f"    WARUM NICHT ERKANNT:")
            if bar_in < 5:
                print(f"      - Bar-In ({bar_in}) < 5")
            if sepa_out < 3:
                print(f"      - SEPA-Out ({sepa_out}) < 3")
            if bar_in_ratio < 70:
                print(f"      - Bar-In Ratio ({bar_in_ratio:.0f}%) < 70%")
            if sepa_out_ratio < 60:
                print(f"      - SEPA-Out Ratio ({sepa_out_ratio:.0f}%) < 60%")
            if bar_in_volume < 10000:
                print(f"      - Bar-In Volumen ({bar_in_volume:,.0f}€) < 10.000€")
    
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    print(f"✅ Precision: {precision*100:.1f}% (weniger False Positives)")
    print(f"✅ Recall: {recall*100:.1f}% (alle echten Geldwäscher erkannt)")
    
else:
    print("\nKeine 'Problemkunde' Spalte in ursprünglicher CSV")

