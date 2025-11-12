"""
Debug: Warum werden problematische Kunden nicht erkannt?
"""
import requests
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer
from statistical_methods import StatisticalAnalyzer

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV direkt
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Finde bekannte problematische Kunden aus CSV-Analyse
print("="*80)
print("PROBLEM 1: GELDWÄSCHE-KUNDEN NICHT ERKANNT")
print("="*80)

# Bekannte Geldwäscher aus CSV
known_launderers = []
for customer_id, group in df.groupby('Kundennummer'):
    bar_in = len(group[(group['Art'] == 'Bar') & (group['In/Out'] == 'In')])
    sepa_out = len(group[(group['Art'] == 'SEPA') & (group['In/Out'] == 'Out')])
    if bar_in >= 3 and sepa_out >= 3:
        known_launderers.append({
            'id': customer_id,
            'name': str(group[name_col].iloc[0]),
            'bar_in': bar_in,
            'sepa_out': sepa_out
        })

print(f"\nBekannte Geldwäscher aus CSV: {len(known_launderers)}")

# Teste einen nicht erkannten Geldwäscher direkt
test_customer_id = 200200  # Ryan Kommen (Bar-In=6, SEPA-Out=4)
test_customer_data = df[df['Kundennummer'] == test_customer_id]

if len(test_customer_data) > 0:
    print(f"\nTest Kunde: {test_customer_data[name_col].iloc[0]} ({test_customer_id})")
    print(f"Transaktionen in CSV: {len(test_customer_data)}")
    
    # Parse Transaktionen
    transactions = []
    for idx, row in test_customer_data.iterrows():
        customer_id_str = str(test_customer_id)
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
            customer_id=customer_id_str,
            transaction_id=transaction_id,
            customer_name=customer_name,
            transaction_amount=transaction_amount,
            payment_method=payment_method,
            transaction_type=transaction_type,
            timestamp=timestamp
        )
        transactions.append(txn)
    
    print(f"Transaktionen geparst: {len(transactions)}")
    
    # Test Layering direkt
    stat_analyzer = StatisticalAnalyzer()
    layering_score = stat_analyzer.cash_to_bank_layering_detection(transactions)
    
    print(f"\nDirekter Layering Score: {layering_score:.4f}")
    
    # Zeige Details
    investments = [t for t in transactions if t.transaction_type == TransactionType.INVESTMENT]
    auszahlungen = [t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG]
    bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
    electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]
    
    print(f"  Investments: {len(investments)}")
    print(f"    Bar: {len(bar_investments)}")
    print(f"  Auszahlungen: {len(auszahlungen)}")
    print(f"    SEPA/Kreditkarte: {len(electronic_withdrawals)}")
    
    # Test mit Analyzer
    analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
    analyzer.add_transactions(transactions)
    
    try:
        profile = analyzer.analyze_customer(str(test_customer_id), recent_days=1825)
        print(f"\nAnalyzer Ergebnis:")
        print(f"  Risk Level: {profile.risk_level}")
        print(f"  Suspicion Score: {profile.suspicion_score:.2f}")
        print(f"  Layering Score: {profile.statistical_analysis.layering_score:.4f}")
        
        if profile.statistical_analysis.layering_score == 0.0:
            print(f"\n  PROBLEM: Layering Score ist 0.0, obwohl direkt 1.0!")
            
            # Prüfe Transaktionen im Analyzer
            if str(test_customer_id) in analyzer.transaction_history:
                txns_in_analyzer = analyzer.transaction_history[str(test_customer_id)]
                print(f"  Transaktionen im Analyzer: {len(txns_in_analyzer)}")
                
                # Prüfe recent_txns
                recent_txns = analyzer.get_customer_transactions(
                    str(test_customer_id),
                    days=1825,
                    use_data_end_as_reference=True
                )
                print(f"  Recent Transactions (1825 days): {len(recent_txns)}")
                
                if len(recent_txns) == 0:
                    print(f"  PROBLEM: Keine recent_txns gefunden!")
                    
                    # Prüfe Timestamps
                    timestamps = [t.timestamp for t in txns_in_analyzer if t.timestamp]
                    if timestamps:
                        print(f"  Timestamps im Analyzer:")
                        print(f"    Erste: {min(timestamps)}")
                        print(f"    Letzte: {max(timestamps)}")
                        
                        from datetime import datetime
                        latest = analyzer.get_latest_timestamp()
                        if latest:
                            print(f"  Latest Timestamp (Analyzer): {latest}")
                            cutoff = latest - pd.Timedelta(days=1825)
                            print(f"  Cutoff (1825 days before latest): {cutoff}")
                            
                            before_cutoff = [t for t in txns_in_analyzer if t.timestamp and t.timestamp < cutoff]
                            after_cutoff = [t for t in txns_in_analyzer if t.timestamp and t.timestamp >= cutoff]
                            print(f"  Transaktionen vor Cutoff: {len(before_cutoff)}")
                            print(f"  Transaktionen nach Cutoff: {len(after_cutoff)}")
    except Exception as e:
        print(f"FEHLER bei Analyse: {e}")
        import traceback
        traceback.print_exc()


