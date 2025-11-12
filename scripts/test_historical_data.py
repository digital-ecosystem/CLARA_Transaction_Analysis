"""
Test is_historical_data()
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()

df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Parse Transaktionen
all_transactions = []
name_col = [col for col in df.columns if 'Name' in col][0]

for idx, row in df.iterrows():
    try:
        customer_id = str(row['Kundennummer'])
        transaction_id = str(row['Unique Transaktion ID'])
        customer_name = str(row[name_col])
        
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

# Erstelle Analyzer
analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
analyzer.add_transactions(all_transactions)

print(f"Gesamt Transaktionen: {len(all_transactions)}")
print(f"Kunden im Analyzer: {len(analyzer.transaction_history)}")

# Prüfe is_historical_data
is_historical = analyzer.is_historical_data()
latest = analyzer.get_latest_timestamp()

print(f"\nLatest Timestamp: {latest}")
print(f"Is Historical Data: {is_historical}")

if latest:
    from datetime import datetime
    days_ago = (datetime.now() - latest).days
    print(f"Days ago: {days_ago}")

# Test Kunde 200008
customer_id = "200008"
print(f"\n" + "="*80)
print(f"Test Kunde {customer_id}:")
print("="*80)

if customer_id in analyzer.transaction_history:
    txns = analyzer.transaction_history[customer_id]
    print(f"Transaktionen im Analyzer: {len(txns)}")
    
    # Zeige Timestamps
    timestamps = [t.timestamp for t in txns if t.timestamp]
    if timestamps:
        print(f"Erste Transaktion: {min(timestamps)}")
        print(f"Letzte Transaktion: {max(timestamps)}")
    
    # Hole recent_txns
    recent_txns = analyzer.get_customer_transactions(
        customer_id,
        days=1825,
        use_data_end_as_reference=is_historical
    )
    
    print(f"\nRecent Transactions (1825 days, use_data_end_as_reference={is_historical}): {len(recent_txns)}")
    
    if len(recent_txns) == 0:
        print(f"PROBLEM: Keine recent_txns gefunden!")
        print(f"  -> Transaktionen werden nicht richtig gefiltert")
    else:
        # Analysiere
        try:
            profile = analyzer.analyze_customer(customer_id, recent_days=1825)
            
            print(f"\nAnalyse Ergebnis:")
            print(f"  Risk Level: {profile.risk_level}")
            print(f"  Suspicion Score: {profile.suspicion_score:.2f}")
            print(f"  Layering Score: {profile.statistical_analysis.layering_score:.4f}")
        except Exception as e:
            print(f"FEHLER bei Analyse: {e}")
            import traceback
            traceback.print_exc()


