"""
Simuliere CSV-Analyse direkt
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

# Parse ALLE Transaktionen wie in main.py
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

print(f"Gesamt Transaktionen geparst: {len(all_transactions)}")

# Erstelle Analyzer
analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
analyzer.add_transactions(all_transactions)

print(f"Kunden im Analyzer: {len(analyzer.transaction_history)}")

# Test Kunde 200008
customer_id = "200008"
print(f"\n" + "="*80)
print(f"Test Kunde {customer_id}:")
print("="*80)

if customer_id in analyzer.transaction_history:
    txns = analyzer.transaction_history[customer_id]
    print(f"Transaktionen im Analyzer: {len(txns)}")
    
    # Analysiere
    try:
        profile = analyzer.analyze_customer(customer_id, recent_days=1825)
        
        print(f"\nAnalyse Ergebnis:")
        print(f"  Risk Level: {profile.risk_level}")
        print(f"  Suspicion Score: {profile.suspicion_score:.2f}")
        print(f"  Layering Score: {profile.statistical_analysis.layering_score:.4f}")
        
        if profile.statistical_analysis.layering_score == 0.0:
            print(f"\nPROBLEM: Layering Score ist 0.0!")
            
            # Prüfe Transaktionen
            investments = [t for t in txns if t.transaction_type == TransactionType.INVESTMENT]
            auszahlungen = [t for t in txns if t.transaction_type == TransactionType.AUSZAHLUNG]
            
            bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
            electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]
            
            print(f"  Investments: {len(investments)}")
            print(f"    Bar: {len(bar_investments)}")
            print(f"  Auszahlungen: {len(auszahlungen)}")
            print(f"    SEPA/Kreditkarte: {len(electronic_withdrawals)}")
            
            # Test Layering direkt
            from statistical_methods import StatisticalAnalyzer
            stat_analyzer = StatisticalAnalyzer()
            layering_score = stat_analyzer.cash_to_bank_layering_detection(txns)
            print(f"\n  Direkter Layering Score: {layering_score:.4f}")
        else:
            print(f"  -> OK!")
    except Exception as e:
        print(f"FEHLER bei Analyse: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Kunde {customer_id} NICHT im Analyzer!")


