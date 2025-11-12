"""
Prüfe Geldwäsche-Flags in der analysierten CSV
"""
import pandas as pd
import io

# Lese analysierte CSV
csv_path = r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_20251110_160843.csv"

print("="*80)
print("PRÜFE GELDWÄSCHE-ERKENNUNGEN")
print("="*80)

# Lese CSV
df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')

print(f"\nGesamt Transaktionen: {len(df)}")
print(f"Gesamt Kunden: {df['Kundennummer'].nunique()}")

# Finde Kunden mit Geldwäsche-Flags
geldwaesche_customers = df[df['Flags'].str.contains('GELDW|LAYERING', case=False, na=False)]['Kundennummer'].unique()

print(f"\nKunden mit Geldwäsche-Flags: {len(geldwaesche_customers)}")

# Analysiere diese Kunden
print("\n" + "="*80)
print("KUNDEN MIT GELDWÄSCHE-FLAGS (Top 20)")
print("="*80)

for i, customer_id in enumerate(list(geldwaesche_customers)[:20], 1):
    customer_data = df[df['Kundennummer'] == customer_id]
    
    name = customer_data['Vollständiger Name'].iloc[0]
    risk_level = customer_data['Risk_Level'].iloc[0]
    flags = customer_data['Flags'].iloc[0]
    layering_score = customer_data['Layering_Score'].iloc[0]
    
    # Transaktions-Statistiken
    bar_in = len(customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'In')])
    sepa_out = len(customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'Out')])
    total_in = len(customer_data[customer_data['In/Out'] == 'In'])
    total_out = len(customer_data[customer_data['In/Out'] == 'Out'])
    
    print(f"\n{i:2d}. {name} ({customer_id})")
    print(f"    Risk Level: {risk_level}")
    print(f"    Layering Score: {layering_score:.2f}")
    print(f"    Flags: {flags}")
    print(f"    Transaktionen: {len(customer_data)} (In: {total_in}, Out: {total_out})")
    print(f"    Bar-In: {bar_in}, SEPA-Out: {sepa_out}")
    
    # Prüfe ob echter Geldwäscher (aus VBA)
    problem_type = customer_data['Problemkunde'].iloc[0] if 'Problemkunde' in customer_data.columns else "N/A"
    if problem_type != "N/A":
        print(f"    VBA Problem Type: {problem_type}")

# Prüfe auch ursprüngliche CSV
print("\n" + "="*80)
print("VERGLEICH MIT URSPRÜNGLICHER CSV")
print("="*80)

# Lese ursprüngliche CSV
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Finde echte Geldwäscher (mit Problemkunde = Geldwaesche)
if 'Problemkunde' in df_original.columns:
    real_launderers = df_original[df_original['Problemkunde'] == 'Geldwasche']['Kundennummer'].unique()
    print(f"\nEchte Geldwäscher (aus VBA): {len(real_launderers)}")
    
    # Prüfe wie viele erkannt wurden
    detected = set(geldwaesche_customers) & set(real_launderers)
    false_positives = set(geldwaesche_customers) - set(real_launderers)
    
    print(f"Erkannt: {len(detected)} / {len(real_launderers)} ({len(detected)/len(real_launderers)*100:.1f}%)")
    print(f"False Positives: {len(false_positives)}")
    
    if false_positives:
        print(f"\nFalse Positives (Top 10):")
        for i, customer_id in enumerate(list(false_positives)[:10], 1):
            customer_data = df[df['Kundennummer'] == customer_id]
            name = customer_data['Vollständiger Name'].iloc[0]
            layering_score = customer_data['Layering_Score'].iloc[0]
            
            bar_in = len(customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'In')])
            sepa_out = len(customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'Out')])
            
            # Prüfe VBA Problem Type
            original_customer = df_original[df_original['Kundennummer'] == customer_id]
            if len(original_customer) > 0:
                problem_type = original_customer['Problemkunde'].iloc[0] if pd.notna(original_customer['Problemkunde'].iloc[0]) else "Normal"
            else:
                problem_type = "Unknown"
            
            print(f"  {i:2d}. {name} ({customer_id}): Bar-In={bar_in}, SEPA-Out={sepa_out}, Layering Score={layering_score:.2f}, VBA Type={problem_type}")
else:
    print("\nKeine 'Problemkunde' Spalte in ursprünglicher CSV gefunden")

