"""
Teste Entropie-Erkennung
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from entropy_detector import EntropyDetector

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Finde Entropie-Kunde aus CSV-Analyse
# Top Entropie-Kunde: Tobi Ornottobi (200003) - 15 Tx, 15 unique Beträge (100%)
test_customer_id = 200003
test_customer_data = df[df['Kundennummer'] == test_customer_id]

print("="*80)
print(f"TEST ENTROPIE-ERKENNUNG: {test_customer_data[name_col].iloc[0]} ({test_customer_id})")
print("="*80)

# Parse Transaktionen
transactions = []
for idx, row in test_customer_data.iterrows():
    customer_id_str = str(test_customer_id)
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

# Zeige Transaktionsdetails
amounts = [t.transaction_amount for t in transactions]
unique_amounts = len(set(amounts))
payment_methods = [t.payment_method.value for t in transactions]
unique_methods = len(set(payment_methods))

print(f"\nTransaktions-Details:")
print(f"  Gesamt: {len(transactions)}")
print(f"  Unique Beträge: {unique_amounts} ({unique_amounts/len(transactions)*100:.1f}%)")
print(f"  Unique Zahlungsmethoden: {unique_methods}")
print(f"  Beträge: {sorted(amounts)[:10]}...")

# Test Entropie direkt
entropy_detector = EntropyDetector()
entropy_analysis = entropy_detector.analyze(transactions, [])

print(f"\nEntropie-Analyse:")
print(f"  Entropy Amount: {entropy_analysis.entropy_amount:.4f}")
print(f"  Entropy Payment Method: {entropy_analysis.entropy_payment_method:.4f}")
print(f"  Entropy Transaction Type: {entropy_analysis.entropy_transaction_type:.4f}")
print(f"  Entropy Time: {entropy_analysis.entropy_time:.4f}")
print(f"  Entropy Aggregate: {entropy_analysis.entropy_aggregate:.4f}")
print(f"  Z-Score: {entropy_analysis.z_score:.4f}")
print(f"  Is Complex: {entropy_analysis.is_complex}")

if not entropy_analysis.is_complex:
    print(f"\nPROBLEM: Is Complex ist False, sollte aber True sein!")
    
    # Prüfe warum
    print(f"\nAbsolute Schwellenwerte:")
    if entropy_analysis.entropy_aggregate < 0.3:
        print(f"  Entropy Aggregate < 0.3: {entropy_analysis.entropy_aggregate:.4f} < 0.3 -> SOLLTE VERDÄCHTIG SEIN")
    elif entropy_analysis.entropy_aggregate > 2.0:
        print(f"  Entropy Aggregate > 2.0: {entropy_analysis.entropy_aggregate:.4f} > 2.0 -> SOLLTE VERDÄCHTIG SEIN")
    else:
        print(f"  Entropy Aggregate: {entropy_analysis.entropy_aggregate:.4f} (zwischen 0.3 und 2.0)")
    
    if entropy_analysis.entropy_payment_method < 0.1 and len(transactions) > 10:
        print(f"  Entropy Payment < 0.1: {entropy_analysis.entropy_payment_method:.4f} < 0.1 -> SOLLTE VERDÄCHTIG SEIN")
    else:
        print(f"  Entropy Payment: {entropy_analysis.entropy_payment_method:.4f}")
    
    if entropy_analysis.entropy_amount > 2.0 and len(transactions) >= 10:
        print(f"  Entropy Amount > 2.0: {entropy_analysis.entropy_amount:.4f} > 2.0 -> SOLLTE VERDÄCHTIG SEIN")
    else:
        print(f"  Entropy Amount: {entropy_analysis.entropy_amount:.4f}")
    
    print(f"\nRelative Schwellenwerte:")
    print(f"  |Z-Score| >= 2.5: {abs(entropy_analysis.z_score):.4f} >= 2.5 -> {abs(entropy_analysis.z_score) >= 2.5}")
else:
    print(f"\nOK: Is Complex ist True")

