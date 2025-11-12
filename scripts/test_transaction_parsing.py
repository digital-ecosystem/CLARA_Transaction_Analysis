"""
Test ob Transaktionen richtig geparst werden
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from statistical_methods import StatisticalAnalyzer

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

# Parse wie in main.py
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
    
    # Erstelle Transaction (wie in main.py)
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

print(f"\nTransaktionen geparst: {len(transactions)}")
print(f"  Investments: {len([t for t in transactions if t.transaction_type == TransactionType.INVESTMENT])}")
print(f"  Auszahlungen: {len([t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG])}")
print(f"  Bar: {len([t for t in transactions if t.payment_method == PaymentMethod.BAR])}")
print(f"  SEPA: {len([t for t in transactions if t.payment_method == PaymentMethod.SEPA])}")

# Test Layering Score
analyzer = StatisticalAnalyzer()
layering_score = analyzer.cash_to_bank_layering_detection(transactions)

print(f"\nLayering Score: {layering_score:.4f}")
print(f"  (Sollte > 0.3 sein für Flag)")

# Zeige Details
investments = [t for t in transactions if t.transaction_type == TransactionType.INVESTMENT]
auszahlungen = [t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG]

bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]

print(f"\nDetails:")
print(f"  Investments: {len(investments)}")
print(f"    Bar: {len(bar_investments)} ({len(bar_investments)/len(investments)*100:.0f}%)")
print(f"  Auszahlungen: {len(auszahlungen)}")
print(f"    SEPA/Kreditkarte: {len(electronic_withdrawals)} ({len(electronic_withdrawals)/len(auszahlungen)*100:.0f}%)")

if layering_score < 0.3:
    print(f"\nPROBLEM: Layering Score zu niedrig!")
    print(f"  Bar Investment Ratio: {len(bar_investments)/len(investments) if investments else 0:.2f}")
    print(f"  Electronic Withdrawal Ratio: {len(electronic_withdrawals)/len(auszahlungen) if auszahlungen else 0:.2f}")


