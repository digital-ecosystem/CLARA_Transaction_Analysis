"""
Teste echten Geldwäscher der nicht erkannt wurde
"""
import requests
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer
from statistical_methods import StatisticalAnalyzer

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Test echten Geldwäscher: Anne Kaffek (200068) - Bar-In: 19, SEPA-Out: 11
test_customer_id = 200068
test_customer_data = df[df['Kundennummer'] == test_customer_id]

print("="*80)
print(f"TEST: {test_customer_data[name_col].iloc[0]} ({test_customer_id})")
print("="*80)
print(f"Transaktionen in CSV: {len(test_customer_data)}")

# Statistiken aus CSV
bar_in = test_customer_data[(test_customer_data['Art'] == 'Bar') & (test_customer_data['In/Out'] == 'In')]
sepa_out = test_customer_data[(test_customer_data['Art'] == 'SEPA') & (test_customer_data['In/Out'] == 'Out')]

print(f"\nCSV Statistiken:")
print(f"  Bar-In: {len(bar_in)}")
print(f"  SEPA-Out: {len(sepa_out)}")

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

print(f"\nTransaktionen geparst: {len(transactions)}")

# Test Layering direkt
stat_analyzer = StatisticalAnalyzer()
layering_score = stat_analyzer.cash_to_bank_layering_detection(transactions)

print(f"\nDirekter Layering Score: {layering_score:.4f}")

# Zeige Details
investments = [t for t in transactions if t.transaction_type == TransactionType.INVESTMENT]
auszahlungen = [t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG]
bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]

print(f"\nTransaktions-Details:")
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
    
    flags = profile.flags
    flags_clean = [f.encode('ascii', 'ignore').decode('ascii') for f in flags]
    has_layering = any('LAYERING' in f or 'GELDWAESCHE' in f or 'GELDWSCHE' in f for f in flags_clean)
    print(f"  Hat Layering Flag: {has_layering}")
    
    if profile.statistical_analysis.layering_score == 0.0:
        print(f"\n  PROBLEM: Layering Score ist 0.0!")
        
        # Prüfe warum Layering Score 0.0 ist
        print(f"\n  Layering-Detection Details:")
        
        # Prüfe cash_to_sepa_ratio
        if len(bar_investments) > 0 and len(electronic_withdrawals) > 0:
            total_bar_in = sum(t.transaction_amount for t in bar_investments)
            total_electronic_out = sum(t.transaction_amount for t in electronic_withdrawals)
            total_investments = sum(t.transaction_amount for t in investments)
            total_withdrawals = sum(t.transaction_amount for t in auszahlungen)
            
            cash_to_sepa_ratio = total_bar_in / total_investments if total_investments > 0 else 0
            volume_matching = total_withdrawals / total_investments if total_investments > 0 else 0
            
            print(f"    Total Bar-In: {total_bar_in:,.0f}€")
            print(f"    Total Electronic-Out: {total_electronic_out:,.0f}€")
            print(f"    Total Investments: {total_investments:,.0f}€")
            print(f"    Total Withdrawals: {total_withdrawals:,.0f}€")
            print(f"    Cash-to-SEPA Ratio: {cash_to_sepa_ratio:.2f}")
            print(f"    Volume Matching: {volume_matching:.2f}")
            
            # Prüfe zeitliche Nähe
            if bar_investments and electronic_withdrawals:
                bar_dates = [t.timestamp for t in bar_investments if t.timestamp]
                out_dates = [t.timestamp for t in electronic_withdrawals if t.timestamp]
                
                if bar_dates and out_dates:
                    avg_bar_date = pd.Timestamp(sum(bar_dates, pd.Timestamp(0)) / len(bar_dates))
                    avg_out_date = pd.Timestamp(sum(out_dates, pd.Timestamp(0)) / len(out_dates))
                    days_diff = (avg_out_date - avg_bar_date).days
                    
                    print(f"    Avg Bar-In Date: {avg_bar_date.strftime('%Y-%m-%d')}")
                    print(f"    Avg Out Date: {avg_out_date.strftime('%Y-%m-%d')}")
                    print(f"    Days Difference: {days_diff}")
                    
                    # Prüfe time_proximity_score
                    recent_outs = [t for t in electronic_withdrawals if t.timestamp and any(
                        (t.timestamp - bar_t.timestamp).days <= 90 and (t.timestamp - bar_t.timestamp).days >= 0
                        for bar_t in bar_investments if bar_t.timestamp
                    )]
                    time_proximity_score = len(recent_outs) / len(electronic_withdrawals) if electronic_withdrawals else 0
                    print(f"    Time Proximity Score: {time_proximity_score:.2f}")
                    
                    if time_proximity_score < 0.5:
                        print(f"    PROBLEM: Time Proximity Score {time_proximity_score:.2f} < 0.5 (zu niedrig)")
except Exception as e:
    print(f"FEHLER bei Analyse: {e}")
    import traceback
    traceback.print_exc()


