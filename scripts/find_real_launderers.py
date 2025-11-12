"""
Finde echte Geldwäscher (mit Auszahlungen)
"""
import pandas as pd
import io

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Finde echte Geldwäscher (Bar-In + SEPA-Out)
real_launderers = []
for customer_id, group in df.groupby('Kundennummer'):
    bar_in = len(group[(group['Art'] == 'Bar') & (group['In/Out'] == 'In')])
    sepa_out = len(group[(group['Art'] == 'SEPA') & (group['In/Out'] == 'Out')])
    
    # WICHTIG: Prüfe ob wirklich Auszahlungen vorhanden sind
    total_out = len(group[group['In/Out'] == 'Out'])
    
    if bar_in >= 3 and sepa_out >= 3 and total_out > 0:
        real_launderers.append({
            'id': customer_id,
            'name': str(group[name_col].iloc[0]),
            'bar_in': bar_in,
            'sepa_out': sepa_out,
            'total_out': total_out,
            'total_txns': len(group)
        })

print("="*80)
print("ECHTE GELDWÄSCHER (Bar-In + SEPA-Out mit Auszahlungen)")
print("="*80)
print(f"Anzahl: {len(real_launderers)}")

if real_launderers:
    print("\nTop 20:")
    for i, l in enumerate(sorted(real_launderers, key=lambda x: x['bar_in'] + x['sepa_out'], reverse=True)[:20], 1):
        print(f"  {i:2d}. {l['name']:<30} ({l['id']}): Bar-In: {l['bar_in']:2d}, SEPA-Out: {l['sepa_out']:2d}, Total-Out: {l['total_out']:2d}, Total-Txns: {l['total_txns']:2d}")


