"""
Debug warum Layering Score 0.0 ist
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from statistical_methods import StatisticalAnalyzer

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Test nicht erkannten Geldwäscher: Frank Furt (200008) - Bar-In: 8, SEPA-Out: 5
test_customer_id = 200008
test_customer_data = df[df['Kundennummer'] == test_customer_id]

print("="*80)
print(f"DEBUG: {test_customer_data[name_col].iloc[0]} ({test_customer_id})")
print("="*80)

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

print(f"\nLayering Score: {layering_score:.4f}")

# Zeige Details
investments = [t for t in transactions if t.transaction_type == TransactionType.INVESTMENT]
auszahlungen = [t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG]
bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]

print(f"\nDetails:")
print(f"  Investments: {len(investments)}")
print(f"    Bar: {len(bar_investments)}")
print(f"  Auszahlungen: {len(auszahlungen)}")
print(f"    SEPA/Kreditkarte: {len(electronic_withdrawals)}")

if layering_score == 0.0:
    print(f"\nPROBLEM: Layering Score ist 0.0!")
    
    # Prüfe warum
    if not investments:
        print(f"  -> KEINE Investments!")
    if not auszahlungen:
        print(f"  -> KEINE Auszahlungen!")
    if not bar_investments:
        print(f"  -> KEINE Bar-Investments!")
    if not electronic_withdrawals:
        print(f"  -> KEINE Electronic-Withdrawals!")
    
    # Prüfe Ratios
    if investments and auszahlungen:
        bar_investment_ratio = len(bar_investments) / len(investments)
        electronic_withdrawal_ratio = len(electronic_withdrawals) / len(auszahlungen)
        
        print(f"\n  Ratios:")
        print(f"    Bar-Investment Ratio: {bar_investment_ratio:.2f}")
        print(f"    Electronic-Withdrawal Ratio: {electronic_withdrawal_ratio:.2f}")
        
        # Prüfe absolute Indikatoren
        print(f"\n  Absolute Indikatoren:")
        if len(bar_investments) >= 2 and len(electronic_withdrawals) >= 2:
            print(f"    ✓ Mindestens 2 Bar-In UND 2 SEPA-Out")
        else:
            print(f"    ✗ Mindestens 2 Bar-In UND 2 SEPA-Out: Bar-In={len(bar_investments)}, SEPA-Out={len(electronic_withdrawals)}")
        
        if bar_investment_ratio >= 0.4:
            print(f"    ✓ Bar-Investment Ratio >= 0.4")
        else:
            print(f"    ✗ Bar-Investment Ratio >= 0.4: {bar_investment_ratio:.2f}")
        
        if electronic_withdrawal_ratio >= 0.4:
            print(f"    ✓ Electronic-Withdrawal Ratio >= 0.4")
        else:
            print(f"    ✗ Electronic-Withdrawal Ratio >= 0.4: {electronic_withdrawal_ratio:.2f}")
        
        # Prüfe time_proximity_score
        if bar_investments and electronic_withdrawals:
            time_proximity_score = 0.0
            for withdrawal in electronic_withdrawals:
                if withdrawal.timestamp:
                    recent_bar_investments = [
                        t for t in bar_investments
                        if t.timestamp and 
                        (withdrawal.timestamp - t.timestamp).days <= 90 and
                        (withdrawal.timestamp - t.timestamp).days >= 0
                    ]
                    if recent_bar_investments:
                        time_proximity_score += 1.0
            
            if len(electronic_withdrawals) > 0:
                time_proximity_score /= len(electronic_withdrawals)
            
            print(f"\n  Time Proximity Score: {time_proximity_score:.2f}")
            if time_proximity_score >= 0.3:
                print(f"    ✓ Time Proximity Score >= 0.3")
            else:
                print(f"    ✗ Time Proximity Score >= 0.3: {time_proximity_score:.2f}")
                
                # Zeige warum
                print(f"\n    Details:")
                for withdrawal in electronic_withdrawals[:3]:
                    if withdrawal.timestamp:
                        recent_bar = [
                            t for t in bar_investments
                            if t.timestamp and 
                            (withdrawal.timestamp - t.timestamp).days <= 90 and
                            (withdrawal.timestamp - t.timestamp).days >= 0
                        ]
                        print(f"      SEPA-Out {withdrawal.timestamp.strftime('%Y-%m-%d')}: {len(recent_bar)} Bar-In in letzten 90 Tagen")
                        
                        if len(recent_bar) == 0:
                            # Zeige wann Bar-Ins waren
                            bar_dates = [t.timestamp.strftime('%Y-%m-%d') for t in bar_investments if t.timestamp]
                            print(f"        Bar-Ins waren: {', '.join(bar_dates[:5])}")
                            if bar_dates:
                                days_diff = [(withdrawal.timestamp - pd.to_datetime(t)).days for t in bar_dates if t]
                                if days_diff:
                                    print(f"        Tage-Differenz: {min(days_diff)} bis {max(days_diff)} Tage")


