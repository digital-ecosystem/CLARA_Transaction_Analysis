"""
Teste alle Problem-Typen direkt (ohne API)
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType, RiskLevel
from analyzer import TransactionAnalyzer

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

print("="*80)
print("TESTE ALLE PROBLEM-TYPEN (DIREKTE SIMULATION)")
print("="*80)

# 1. Parse ALLE Transaktionen
print("\n1. Parse ALLE Transaktionen...")
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

all_transactions = []
for idx, row in df.iterrows():
    try:
        customer_id = str(row['Kundennummer'])
        transaction_id = str(row['Unique Transaktion ID'])
        customer_name = str(row[name_col])
        
        art = str(row['Art']).strip()
        if art == "Bar":
            payment_method = PaymentMethod.BAR
        elif art == "SEPA":
            payment_method = PaymentMethod.SEPA
        else:
            payment_method = PaymentMethod.KREDITKARTE
        
        in_out = str(row['In/Out']).strip()
        if in_out == "In":
            transaction_type = TransactionType.INVESTMENT
        elif in_out == "Out":
            transaction_type = TransactionType.AUSZAHLUNG
        else:
            transaction_type = TransactionType.INVESTMENT
        
        amount_str = str(row['Auftragsvolumen']).replace(',', '.')
        transaction_amount = float(amount_str)
        
        timestamp = None
        if 'Timestamp' in df.columns and pd.notna(row['Timestamp']):
            try:
                date_str = str(row['Timestamp'])
                timestamp = pd.to_datetime(date_str, format='%d.%m.%Y')
            except:
                timestamp = None
        
        txn = Transaction(
            customer_id=customer_id,
            transaction_id=transaction_id,
            customer_name=customer_name,
            transaction_amount=transaction_amount,
            payment_method=payment_method,
            transaction_type=transaction_type,
            timestamp=timestamp
        )
        all_transactions.append(txn)
    except Exception as e:
        continue

print(f"   Gesamt Transaktionen geparst: {len(all_transactions)}")

# 2. Erstelle Analyzer
print("\n2. Erstelle Analyzer...")
custom_analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
custom_analyzer.add_transactions(all_transactions)

print(f"   Kunden im Analyzer: {len(custom_analyzer.transaction_history)}")

# 3. Analysiere alle Kunden
print("\n3. Analysiere alle Kunden...")
profiles = custom_analyzer.analyze_all_customers(recent_days=1825)

print(f"   Analysierte Profile: {len(profiles)}")

# 4. Zähle nach Risk Level
summary = {
    "green": sum(1 for p in profiles if p.risk_level == RiskLevel.GREEN),
    "yellow": sum(1 for p in profiles if p.risk_level == RiskLevel.YELLOW),
    "orange": sum(1 for p in profiles if p.risk_level == RiskLevel.ORANGE),
    "red": sum(1 for p in profiles if p.risk_level == RiskLevel.RED),
}

print(f"\n4. Summary:")
print(f"   GREEN: {summary['green']}")
print(f"   YELLOW: {summary['yellow']}")
print(f"   ORANGE: {summary['orange']}")
print(f"   RED: {summary['red']}")

# 5. Finde problematische Kunden aus CSV
print("\n5. Identifiziere problematische Kunden aus CSV...")

smurfers = []
launderers = []
entropy_customers = []

for customer_id, group in df.groupby('Kundennummer'):
    bar_in = len(group[(group['Art'] == 'Bar') & (group['In/Out'] == 'In')])
    sepa_out = len(group[(group['Art'] == 'SEPA') & (group['In/Out'] == 'Out')])
    total_out = len(group[group['In/Out'] == 'Out'])
    
    # Smurfing
    if bar_in >= 5:
        amounts = pd.to_numeric(group[(group['Art'] == 'Bar') & (group['In/Out'] == 'In')]['Auftragsvolumen'].str.replace(',', '.'), errors='coerce')
        threshold_avoid = amounts[(amounts >= 7000) & (amounts < 10000)]
        if len(threshold_avoid) >= 5:
            cumulative = amounts.sum()
            if cumulative >= 50000:
                smurfers.append(customer_id)
    
    # Geldwäsche
    if bar_in >= 3 and sepa_out >= 3 and total_out > 0:
        launderers.append(customer_id)
    
    # Entropie
    total_txns = len(group)
    if total_txns >= 10:
        amounts = pd.to_numeric(group['Auftragsvolumen'].str.replace(',', '.'), errors='coerce')
        unique_amounts = amounts.nunique()
        amount_ratio = unique_amounts / total_txns if total_txns > 0 else 0
        unique_methods = group['Art'].nunique()
        
        if amount_ratio >= 0.8 and unique_methods >= 2:
            entropy_customers.append(customer_id)

print(f"   Smurfing: {len(smurfers)}")
print(f"   Geldwäsche: {len(launderers)}")
print(f"   Entropie: {len(entropy_customers)}")

# 6. Prüfe Erkennungsrate
print("\n6. Prüfe Erkennungsrate...")

detected_smurfers = 0
detected_launderers = 0
detected_entropy = 0

for profile in profiles:
    customer_id = int(profile.customer_id)
    
    # Prüfe Smurfing
    if customer_id in smurfers:
        # Prüfe ob erkannt
        flags = [f.encode('ascii', 'ignore').decode('ascii') for f in profile.flags]
        has_smurfing = any('SMURFING' in f or 'THRESHOLD' in f for f in flags)
        if has_smurfing or profile.risk_level != RiskLevel.GREEN:
            detected_smurfers += 1
    
    # Prüfe Geldwäsche
    if customer_id in launderers:
        flags = [f.encode('ascii', 'ignore').decode('ascii') for f in profile.flags]
        has_layering = any('LAYERING' in f or 'GELDWAESCHE' in f or 'GELDWSCHE' in f for f in flags)
        if has_layering or profile.risk_level != RiskLevel.GREEN:
            detected_launderers += 1
    
    # Prüfe Entropie
    if customer_id in entropy_customers:
        if profile.entropy_analysis.is_complex or profile.risk_level != RiskLevel.GREEN:
            detected_entropy += 1

print(f"\nERKENNUNGSRATE:")
print(f"  Smurfing: {detected_smurfers} / {len(smurfers)} ({detected_smurfers/len(smurfers)*100:.1f}%)")
print(f"  Geldwäsche: {detected_launderers} / {len(launderers)} ({detected_launderers/len(launderers)*100:.1f}%)")
print(f"  Entropie: {detected_entropy} / {len(entropy_customers)} ({detected_entropy/len(entropy_customers)*100:.1f}%)")

