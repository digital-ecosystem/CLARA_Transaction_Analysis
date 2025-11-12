"""
Debug Trust_Score Berechnung für spezifische Kunden
"""
import pandas as pd
import io
from datetime import datetime
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer
from trust_score import TrustScoreCalculator

# Lese ursprüngliche CSV
original_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
with open(original_csv, 'rb') as f:
    contents = f.read()
df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

# Lese analysierte CSV
analyzed_csv = r"D:\My Progs\CLARA\Black Box\Analyzed_Trades_20251110_172632.csv"
df_analyzed = pd.read_csv(analyzed_csv, sep=';', encoding='utf-8-sig')

print("="*80)
print("TRUST_SCORE DEBUG")
print("="*80)

# Teste einige Kunden
test_customers = [
    ('200059', 'GREEN', 0.31, 0.610),  # Niedrigster Trust_Score
    ('200016', 'ORANGE', 2.53, 0.650),  # ORANGE mit niedrigem Trust
    ('200128', 'ORANGE', 2.55, 0.800),  # ORANGE mit hohem Trust
    ('210005', 'GREEN', 0.13, 0.910),   # Höchster Trust_Score
]

# Parse Transaktionen
name_col = [col for col in df_original.columns if 'Name' in col][0]

def parse_transactions(df, customer_id):
    transactions = []
    customer_data = df[df['Kundennummer'] == int(customer_id)]
    
    for idx, row in customer_data.iterrows():
        try:
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
                customer_id=str(customer_id),
                transaction_id=str(row['Unique Transaktion ID']),
                customer_name=str(row[name_col]),
                transaction_amount=transaction_amount,
                payment_method=payment_method,
                transaction_type=transaction_type,
                timestamp=timestamp
            )
            transactions.append(txn)
        except Exception as e:
            continue
    
    return transactions

# Analysiere jeden Test-Kunden
analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
all_transactions = []

for customer_id in df_original['Kundennummer'].unique():
    transactions = parse_transactions(df_original, customer_id)
    all_transactions.extend(transactions)

analyzer.add_transactions(all_transactions)

print("\n" + "="*80)
print("DETAILLIERTE ANALYSE")
print("="*80)

for customer_id, risk_level, suspicion, trust_csv in test_customers:
    print(f"\n{'='*80}")
    print(f"KUNDE {customer_id}")
    print(f"{'='*80}")
    print(f"Risk Level (CSV): {risk_level}")
    print(f"Suspicion Score (CSV): {suspicion}")
    print(f"Trust Score (CSV): {trust_csv}")
    
    # Analysiere direkt
    try:
        profile = analyzer.analyze_customer(str(customer_id))
        
        print(f"\nAnalyse-Ergebnis:")
        print(f"  Risk Level: {profile.risk_level.value}")
        print(f"  Suspicion Score: {profile.suspicion_score:.2f}")
        
        if profile.trust_score_analysis:
            ts = profile.trust_score_analysis
            print(f"\nTrust Score Details:")
            print(f"  Current Score: {ts.current_score:.3f}")
            print(f"  Predictability: {ts.predictability:.3f}")
            print(f"  Self Deviation: {ts.self_deviation:.3f}")
            print(f"  Peer Deviation: {ts.peer_deviation:.3f}")
            
            # Prüfe ob CSV-Wert übereinstimmt
            if abs(ts.current_score - trust_csv) > 0.01:
                print(f"\n  [WARNUNG] Trust Score Abweichung!")
                print(f"    CSV: {trust_csv:.3f}")
                print(f"    Berechnet: {ts.current_score:.3f}")
                print(f"    Differenz: {abs(ts.current_score - trust_csv):.3f}")
            else:
                print(f"\n  [OK] Trust Score stimmt überein")
        
        # Zeige Transaktionen
        customer_txns = [t for t in all_transactions if t.customer_id == str(customer_id)]
        print(f"\nTransaktionen: {len(customer_txns)}")
        
        if len(customer_txns) > 0:
            # Sortiere nach Datum
            customer_txns_sorted = sorted([t for t in customer_txns if t.timestamp], key=lambda t: t.timestamp)
            
            print(f"  Erste 5 Transaktionen:")
            for i, txn in enumerate(customer_txns_sorted[:5], 1):
                print(f"    {i}. {txn.timestamp.strftime('%Y-%m-%d') if txn.timestamp else 'N/A'}: {txn.payment_method.value} {txn.transaction_type.value} {txn.transaction_amount:.2f}EUR")
            
            print(f"  Letzte 5 Transaktionen:")
            for i, txn in enumerate(customer_txns_sorted[-5:], 1):
                print(f"    {i}. {txn.timestamp.strftime('%Y-%m-%d') if txn.timestamp else 'N/A'}: {txn.payment_method.value} {txn.transaction_type.value} {txn.transaction_amount:.2f}EUR")
            
            # Statistiken
            amounts = [t.transaction_amount for t in customer_txns]
            print(f"\n  Statistiken:")
            print(f"    Min Betrag: {min(amounts):.2f}EUR")
            print(f"    Max Betrag: {max(amounts):.2f}EUR")
            print(f"    Mean Betrag: {sum(amounts)/len(amounts):.2f}EUR")
            print(f"    Std Betrag: {pd.Series(amounts).std():.2f}EUR")
            
            # Zahlungsmethoden
            payment_methods = [t.payment_method.value for t in customer_txns]
            method_counts = pd.Series(payment_methods).value_counts()
            print(f"    Zahlungsmethoden: {dict(method_counts)}")
        
    except Exception as e:
        print(f"  [FEHLER] {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("PROBLEM-ANALYSE")
print("="*80)

print("\n1. Alle Trust_Scores sind sehr hoch (0.61 - 0.91)")
print("   -> Mögliche Ursachen:")
print("      - Vorhersagbarkeit wird zu hoch berechnet")
print("      - Selbst-Abweichung wird zu niedrig berechnet")
print("      - Peer-Abweichung wird nicht verwendet (peer_transactions = None)")

print("\n2. ORANGE Kunden haben höhere Trust_Scores als GREEN Kunden")
print("   -> Das ist widersprüchlich!")
print("   -> ORANGE sollte niedrigere Trust_Scores haben")

print("\n3. Kein Trust_Score < 0.5")
print("   -> Laut Code sollten Trust_Scores < 0.3 oder < 0.5 verdächtig sein")
print("   -> Aber alle Scores sind >= 0.61")

print("\n4. Trust_Score wird nicht richtig im Suspicion_Score verwendet")
print("   -> Da alle Trust_Scores >= 0.5 sind, wird kein zusätzlicher Verdacht hinzugefügt")
print("   -> Das bedeutet Trust_Score hat keinen Einfluss auf die Risikobewertung!")



