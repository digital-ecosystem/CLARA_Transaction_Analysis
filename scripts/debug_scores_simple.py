"""
Einfaches Debug-Script für Scores in der generierten CSV
"""

import pandas as pd
from pathlib import Path

# Lade die analysierte CSV
output_dir = Path("output")
csv_files = list(output_dir.glob("Analyzed_Trades_*.csv"))
latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)

print(f"Analysiere: {latest_csv.name}\n")

df = pd.read_csv(latest_csv, encoding='utf-8-sig')

# Gruppiere nach Kunde
customer_data = df.groupby('Kundennummer').agg({
    'Risk_Level': 'first',
    'Suspicion_Score': 'first',
    'Flags': 'first',
    'Threshold_Avoidance_Ratio_%': 'first',
    'Layering_Score': 'first',
    'Entropy_Complex': 'first',
    'Trust_Score': 'first'
}).reset_index()

# Sort by Score
customer_data = customer_data.sort_values('Suspicion_Score', ascending=False)

print("="*90)
print("TOP 20 KUNDEN (nach Suspicion Score)")
print("="*90)
print(f"{'#':<3} {'ID':<8} {'Risk':<7} {'Score':<6} {'TAR%':<6} {'Layer':<6} {'Trust':<6} {'Flags'}")
print("-"*90)

for idx, (i, row) in enumerate(customer_data.head(20).iterrows()):
    flags_str = str(row['Flags']) if pd.notna(row['Flags']) and row['Flags'] else "None"
    # Remove problematic characters
    flags_short = flags_str[:40].encode('ascii', 'ignore').decode('ascii')
    print(f"{idx+1:<3} {row['Kundennummer']:<8} {row['Risk_Level']:<7} {row['Suspicion_Score']:<6.2f} "
          f"{row['Threshold_Avoidance_Ratio_%']:<6.1f} {row['Layering_Score']:<6.2f} "
          f"{row['Trust_Score']:<6.2f} {flags_short}")

print("\n" + "="*90)
print("STATISTICS")
print("="*90)
print(f"Total Kunden: {len(customer_data)}")
print(f"Max Score: {customer_data['Suspicion_Score'].max():.2f}")
print(f"Mean Score: {customer_data['Suspicion_Score'].mean():.2f}")
print(f"Median Score: {customer_data['Suspicion_Score'].median():.2f}")

print(f"\nKunden mit Score > 5.0: {len(customer_data[customer_data['Suspicion_Score'] > 5.0])}")
print(f"Kunden mit Score > 2.0: {len(customer_data[customer_data['Suspicion_Score'] > 2.0])}")
print(f"Kunden mit Score > 1.0: {len(customer_data[customer_data['Suspicion_Score'] > 1.0])}")

# Zeige einige Details für high-score Kunden
high_scorers = customer_data[customer_data['Suspicion_Score'] > 1.0].head(5)

if len(high_scorers) > 0:
    print("\n" + "="*90)
    print("DETAILLIERTE WERTE (Score > 1.0)")
    print("="*90)
    
    for idx, row in high_scorers.iterrows():
        print(f"\nKunde {row['Kundennummer']}:")
        print(f"  Risk Level: {row['Risk_Level']}")
        print(f"  Suspicion Score: {row['Suspicion_Score']:.4f}")
        print(f"  Threshold Avoidance: {row['Threshold_Avoidance_Ratio_%']:.1f}%")
        print(f"  Layering Score: {row['Layering_Score']:.4f}")
        print(f"  Trust Score: {row['Trust_Score']:.4f}")
        print(f"  Entropy Complex: {row['Entropy_Complex']}")
        print(f"  Flags: {row['Flags']}")

print("\n" + "="*90)

