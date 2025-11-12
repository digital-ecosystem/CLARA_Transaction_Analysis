"""
Test vollständigen Analyzer mit echten Transaktionen
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer

csv_path = r"D:\My Progs\CLARA\2\Kunden CSV Generator\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()

df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Bekannter Geldwaescher: Ryan Kommen (200200)
customer_id = 200200
customer_data = df[df['Kundennummer'] == customer_id]

print(f"Kunde {customer_id}: {customer_data['Vollständiger Name'].iloc[0]}")
print("="*80)

# Parse Transaktionen
transactions = []
for idx, row in customer_data.iterrows():
    customer_id_str = str(customer_id)
    transaction_id = str(row['Unique Transaktion ID'])
    customer_name = str(row['Vollständiger Name'])
    
    # Payment Method
    art = str(row['Art']).strip()
    if art == "Bar":
        payment_method = PaymentMethod.BAR
    elif art == "SEPA":
        payment_method = PaymentMethod.SEPA
    else:
        payment_method = PaymentMethod.KREDITKARTE
    
    # Transaction Type
    in_out = str(row['In/Out']).strip()
    if in_out == "In":
        transaction_type = TransactionType.INVESTMENT
    elif in_out == "Out":
        transaction_type = TransactionType.AUSZAHLUNG
    else:
        transaction_type = TransactionType.INVESTMENT
    
    # Amount
    amount_str = str(row['Auftragsvolumen']).replace(',', '.')
    transaction_amount = float(amount_str)
    
    # Timestamp
    timestamp = None
    if 'Timestamp' in df.columns and pd.notna(row['Timestamp']):
        try:
            date_str = str(row['Timestamp'])
            timestamp = pd.to_datetime(date_str, format='%d.%m.%Y')
        except:
            timestamp = None
    
    txn = Transaction(
        customer_id=customer_id_str,
        transaction_id=transaction_id,
        customer_name=customer_name,
        transaction_amount=transaction_amount,
        payment_method=payment_method,
        transaction_type=transaction_type,
        timestamp=timestamp
    )
    transactions.append(txn)

print(f"\nTransaktionen: {len(transactions)}")

# Erstelle Analyzer
analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
analyzer.add_transactions(transactions)

# Analysiere Kunde
profile = analyzer.analyze_customer(str(customer_id), recent_days=1825)

print(f"\nRisk Level: {profile.risk_level}")
print(f"Suspicion Score: {profile.suspicion_score:.2f}")
print(f"Layering Score: {profile.statistical_analysis.layering_score:.4f}")
print(f"Entropy Aggregate: {profile.entropy_analysis.entropy_aggregate:.4f}")

print(f"\nFlags:")
for flag in profile.flags:
    flag_clean = flag.encode('ascii', 'ignore').decode('ascii')
    print(f"  - {flag_clean}")

# Prüfe ob Layering Flag gesetzt ist
has_layering = any('LAYERING' in f or 'GELDWAESCHE' in f for f in [f.encode('ascii', 'ignore').decode('ascii') for f in profile.flags])
print(f"\nHat Layering Flag: {has_layering}")

if profile.statistical_analysis.layering_score > 0.3 and not has_layering:
    print("PROBLEM: Layering Score > 0.3 aber kein Flag!")


