"""
Pruefe CSV-Daten genauer
"""
import pandas as pd
import io

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Test Kunde 200200
customer_id = 200200
customer_data = df[df['Kundennummer'] == customer_id]

print(f"Kunde: {customer_data[name_col].iloc[0]} ({customer_id})")
print(f"Gesamt Transaktionen: {len(customer_data)}")
print("\n" + "="*80)
print("DETAILLIERTE TRANSACTIONS-ANALYSE")
print("="*80)

# Zeige alle Transaktionen
print("\nAlle Transaktionen:")
for idx, row in customer_data.iterrows():
    art = str(row['Art']).strip()
    in_out = str(row['In/Out']).strip()
    amount = str(row['Auftragsvolumen']).strip()
    timestamp = str(row['Timestamp']) if 'Timestamp' in df.columns else "N/A"
    print(f"  {timestamp}: {in_out} | {art} | {amount}€")

# Statistiken
bar_in = customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'In')]
bar_out = customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'Out')]
sepa_in = customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'In')]
sepa_out = customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'Out')]
kredit_in = customer_data[(customer_data['Art'] == 'Kredit') & (customer_data['In/Out'] == 'In')]
kredit_out = customer_data[(customer_data['Art'] == 'Kredit') & (customer_data['In/Out'] == 'Out')]

print("\n" + "="*80)
print("STATISTIKEN")
print("="*80)
print(f"Bar-In:     {len(bar_in)}")
print(f"Bar-Out:    {len(bar_out)}")
print(f"SEPA-In:    {len(sepa_in)}")
print(f"SEPA-Out:   {len(sepa_out)}")
print(f"Kredit-In:  {len(kredit_in)}")
print(f"Kredit-Out: {len(kredit_out)}")

print("\n" + "="*80)
print("PROBLEM-ANALYSE")
print("="*80)

# Pruefe warum als Geldwaescher erkannt wurde
if len(bar_in) >= 3 and len(sepa_out) >= 3:
    print("✓ Erfüllt Kriterien für Geldwäsche (Bar-In >= 3, SEPA-Out >= 3)")
else:
    print("X Erfüllt NICHT Kriterien für Geldwäsche")
    if len(bar_in) < 3:
        print(f"  - Bar-In: {len(bar_in)} < 3")
    if len(sepa_out) < 3:
        print(f"  - SEPA-Out: {len(sepa_out)} < 3")
    
    # Pruefe ob andere Auszahlungen vorhanden
    total_out = len(bar_out) + len(sepa_out) + len(kredit_out)
    print(f"\n  Gesamt Auszahlungen: {total_out}")
    if total_out > 0:
        print(f"    Bar-Out: {len(bar_out)}")
        print(f"    SEPA-Out: {len(sepa_out)}")
        print(f"    Kredit-Out: {len(kredit_out)}")
        
        # Pruefe ob Layering mit anderen Methoden möglich
        electronic_out = len(sepa_out) + len(kredit_out)
        if len(bar_in) >= 3 and electronic_out >= 3:
            print(f"\n  → MÖGLICHES LAYERING: Bar-In ({len(bar_in)}) + Electronic-Out ({electronic_out})")
        else:
            print(f"\n  → KEIN LAYERING: Bar-In ({len(bar_in)}) + Electronic-Out ({electronic_out})")

