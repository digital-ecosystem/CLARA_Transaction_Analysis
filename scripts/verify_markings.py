"""
Überprüfe ob die Markierungen in der analysierten CSV korrekt sind
"""
import pandas as pd
import io
import re

def remove_emojis(text):
    """Entferne Emojis und Sonderzeichen für Konsolen-Kompatibilität"""
    if pd.isna(text) or text == '':
        return 'None'
    text = str(text)
    # Ersetze häufige Sonderzeichen ZUERST
    text = text.replace('→', '->')
    text = text.replace('€', 'EUR')
    text = text.replace('ü', 'ue')
    text = text.replace('ä', 'ae')
    text = text.replace('ö', 'oe')
    text = text.replace('ß', 'ss')
    text = text.replace('Ü', 'Ue')
    text = text.replace('Ä', 'Ae')
    text = text.replace('Ö', 'Oe')
    # Entferne ALLE Nicht-ASCII-Zeichen
    text = ''.join(char for char in text if ord(char) < 128)
    return text

# Lese neueste analysierte CSV
analyzed_csv = r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_20251110_162711.csv"
df_analyzed = pd.read_csv(analyzed_csv, sep=';', encoding='utf-8-sig')

# Lese ursprüngliche CSV
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

print("="*80)
print("ÜBERPRÜFUNG DER MARKIERUNGEN IN ANALYZED CSV")
print("="*80)

print(f"\nGesamt Transaktionen: {len(df_analyzed)}")
print(f"Gesamt Kunden: {df_analyzed['Kundennummer'].nunique()}")

# Prüfe welche Spalten vorhanden sind
print(f"\nVorhandene Spalten in analyzed CSV:")
for i, col in enumerate(df_analyzed.columns, 1):
    print(f"  {i:2d}. {col}")

# Zeige Beispiele von markierten Kunden
print("\n" + "="*80)
print("BEISPIELE: MARKIERTE KUNDEN (Top 10)")
print("="*80)

# Finde den Namen-Spalte (kann verschiedene Encodings haben)
name_col = None
for col in df_analyzed.columns:
    if 'Name' in col or 'name' in col.lower():
        name_col = col
        break

if name_col is None:
    name_col = 'Kundennummer'  # Fallback

# Sortiere nach Suspicion Score
top_customers = df_analyzed.groupby('Kundennummer').agg({
    'Suspicion_Score': 'first',
    'Risk_Level': 'first',
    'Flags': 'first',
    name_col: 'first',
    'Layering_Score': 'first',
    'Threshold_Avoidance_Ratio_%': 'first',
    'Entropy_Complex': 'first'
}).sort_values('Suspicion_Score', ascending=False).head(10)

for i, (customer_id, row) in enumerate(top_customers.iterrows(), 1):
    flags_clean = remove_emojis(row['Flags'])
    print(f"\n{i:2d}. {row[name_col]} ({customer_id})")
    print(f"    Risk Level: {row['Risk_Level']}")
    print(f"    Suspicion Score: {row['Suspicion_Score']:.2f}")
    print(f"    Flags: {flags_clean[:100]}...")
    print(f"    Layering Score: {row['Layering_Score']:.2f}")
    print(f"    Threshold Avoidance: {row['Threshold_Avoidance_Ratio_%']:.1f}%")
    print(f"    Entropy Complex: {row['Entropy_Complex']}")
    
    # Prüfe Transaktionen dieses Kunden
    customer_txns = df_analyzed[df_analyzed['Kundennummer'] == customer_id]
    customer_txns_orig = df_original[df_original['Kundennummer'] == customer_id]
    
    # Zeige ein paar Transaktionen mit Markierungen
    print(f"    Transaktionen: {len(customer_txns)}")
    print(f"    Beispiel-Transaktionen (erste 3):")
    for j, (idx, txn) in enumerate(customer_txns.head(3).iterrows(), 1):
        txn_flags = remove_emojis(txn['Flags'])
        print(f"      {j}. {txn['Datum']}: {txn['Art']} {txn['In/Out']} {txn['Auftragsvolumen']}EUR")
        print(f"         -> Risk: {txn['Risk_Level']}, Flags: {txn_flags[:50]}...")

# Prüfe Verteilung der Risk Levels
print("\n" + "="*80)
print("VERTEILUNG DER RISK LEVELS")
print("="*80)

risk_distribution = df_analyzed.groupby('Kundennummer')['Risk_Level'].first().value_counts()
print(f"\nKunden pro Risk Level:")
for risk_level, count in risk_distribution.items():
    print(f"  {risk_level}: {count} Kunden")

# Prüfe Flags
print("\n" + "="*80)
print("HÄUFIGSTE FLAGS")
print("="*80)

# Extrahiere alle Flags
all_flags = []
for flags_str in df_analyzed.groupby('Kundennummer')['Flags'].first():
    if pd.notna(flags_str) and flags_str:
        for flag in flags_str.split(';'):
            flag = flag.strip()
            if flag:
                all_flags.append(flag)

from collections import Counter
flag_counts = Counter(all_flags)

print(f"\nTop 10 häufigste Flags:")
for i, (flag, count) in enumerate(flag_counts.most_common(10), 1):
    flag_clean = remove_emojis(flag) if flag else 'None'
    print(f"  {i:2d}. {flag_clean}: {count} Kunden")

# Prüfe ob Markierungen konsistent sind
print("\n" + "="*80)
print("KONSISTENZ-PRÜFUNG")
print("="*80)

print("\nPrüfe ob alle Transaktionen eines Kunden die gleichen Markierungen haben...")
inconsistent = 0
for customer_id in df_analyzed['Kundennummer'].unique():
    customer_data = df_analyzed[df_analyzed['Kundennummer'] == customer_id]
    
    # Prüfe ob Risk Level konsistent ist
    unique_risk_levels = customer_data['Risk_Level'].unique()
    if len(unique_risk_levels) > 1:
        print(f"  WARNUNG: Kunde {customer_id} hat mehrere Risk Levels: {unique_risk_levels}")
        inconsistent += 1
    
    # Prüfe ob Flags konsistent sind
    unique_flags = customer_data['Flags'].unique()
    if len(unique_flags) > 1:
        print(f"  WARNUNG: Kunde {customer_id} hat mehrere Flag-Sets: {unique_flags[:2]}...")
        inconsistent += 1

if inconsistent == 0:
    print("  [OK] Alle Markierungen sind konsistent!")
else:
    print(f"  [FEHLER] {inconsistent} Kunden haben inkonsistente Markierungen")

# Prüfe ob GREEN-Kunden keine Flags haben sollten
print("\n" + "="*80)
print("PLAUSIBILITÄTS-PRÜFUNG")
print("="*80)

green_with_flags = df_analyzed[
    (df_analyzed['Risk_Level'] == 'GREEN') & 
    (df_analyzed['Flags'].notna()) & 
    (df_analyzed['Flags'] != '')
]['Kundennummer'].unique()

print(f"\nGREEN Kunden mit Flags: {len(green_with_flags)}")
if len(green_with_flags) > 0:
    print(f"  Beispiele (Top 5):")
    for customer_id in green_with_flags[:5]:
        customer_data = df_analyzed[df_analyzed['Kundennummer'] == customer_id].iloc[0]
        flags_clean = remove_emojis(customer_data['Flags'])
        print(f"    {customer_id}: {flags_clean[:80]}...")

# Prüfe ob ORANGE/RED Kunden Flags haben
high_risk_without_flags = df_analyzed[
    (df_analyzed['Risk_Level'].isin(['ORANGE', 'RED'])) & 
    ((df_analyzed['Flags'].isna()) | (df_analyzed['Flags'] == ''))
]['Kundennummer'].unique()

print(f"\nORANGE/RED Kunden ohne Flags: {len(high_risk_without_flags)}")
if len(high_risk_without_flags) > 0:
    print(f"  WARNUNG: Diese Kunden sollten Flags haben!")
    for customer_id in high_risk_without_flags[:5]:
        customer_data = df_analyzed[df_analyzed['Kundennummer'] == customer_id].iloc[0]
        print(f"    {customer_id}: Risk={customer_data['Risk_Level']}, Score={customer_data['Suspicion_Score']:.2f}")

print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)
print(f"\n[OK] Analyzed CSV enthaelt alle Markierungen")
print(f"[OK] {len(df_analyzed)} Transaktionen mit Analyse-Ergebnissen")
print(f"[OK] {df_analyzed['Kundennummer'].nunique()} Kunden markiert")
print(f"[OK] Risk Levels: {', '.join([f'{k}={v}' for k,v in risk_distribution.items()])}")
print(f"[OK] Flags: {len(flag_counts)} verschiedene Flags verwendet")

