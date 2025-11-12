"""
Debug: Prüft Trust_Score Berechnung für verdächtige Kunden
"""
import pandas as pd
from analyzer import TransactionAnalyzer
from models import Transaction, PaymentMethod, TransactionType
from datetime import datetime

# Lese CSV
df = pd.read_csv("Analyzed_Trades_20251112_170438.csv", encoding='utf-8-sig')

# Test-Kunde: 200001 (YELLOW, Suspicion=1.58, Trust=0.85)
test_customer = "200001"

# Parse Transaktionen für Test-Kunde
customer_df = df[df['Kundennummer'].astype(str) == test_customer]
print(f"Test-Kunde: {test_customer}")
print(f"Risk_Level: {customer_df['Risk_Level'].iloc[0]}")
print(f"Suspicion_Score: {customer_df['Suspicion_Score'].iloc[0]}")
print(f"Trust_Score (CSV): {customer_df['Trust_Score'].iloc[0]}")
print(f"Anzahl Transaktionen: {len(customer_df)}")

# Parse zu Transaction-Objekten
transactions = []
for idx, row in customer_df.iterrows():
    try:
        amount_str = str(row['Auftragsvolumen']).replace(',', '.')
        amount = float(amount_str)
        
        art = str(row['Art']).strip()
        if art == "Kredit":
            payment_method = PaymentMethod.KREDITKARTE
        elif art == "Bar":
            payment_method = PaymentMethod.BAR
        elif art == "SEPA":
            payment_method = PaymentMethod.SEPA
        else:
            payment_method = PaymentMethod.SEPA
        
        in_out = str(row['In/Out']).strip()
        transaction_type = TransactionType.INVESTMENT if in_out == "In" else TransactionType.AUSZAHLUNG
        
        timestamp = None
        if pd.notna(row['Datum']):
            try:
                timestamp = pd.to_datetime(str(row['Datum']), format='%d.%m.%Y')
            except:
                pass
        
        txn = Transaction(
            customer_id=str(row['Kundennummer']),
            transaction_id=str(row['Unique Transaktion ID']),
            customer_name=str(row['Vollständiger Name']),
            transaction_amount=amount,
            payment_method=payment_method,
            transaction_type=transaction_type,
            timestamp=timestamp
        )
        transactions.append(txn)
    except Exception as e:
        print(f"Fehler bei Zeile {idx}: {e}")
        continue

print(f"\n{len(transactions)} Transaktionen geparst")

# Erstelle Analyzer
analyzer = TransactionAnalyzer()
analyzer.add_transactions(transactions)

# Analysiere Kunde (mit all_transactions für Peer-Abweichung)
profile = analyzer.analyze_customer(test_customer, recent_days=30, all_transactions=transactions)

print(f"\nAnalyse-Ergebnis:")
print(f"  Risk_Level: {profile.risk_level.value}")
print(f"  Suspicion_Score: {profile.suspicion_score:.2f}")

if profile.trust_score_analysis:
    ts = profile.trust_score_analysis
    print(f"\nTrust_Score Details:")
    print(f"  Current Score: {ts.current_score:.3f}")
    print(f"  Predictability: {ts.predictability:.3f}")
    print(f"  Self Deviation: {ts.self_deviation:.3f}")
    print(f"  Peer Deviation: {ts.peer_deviation:.3f}")
    
    # Manuelle Berechnung
    print(f"\nManuelle Berechnung:")
    self_dev_penalty = ts.self_deviation ** 1.5
    peer_dev_penalty = ts.peer_deviation ** 1.5
    
    t_new = (
        0.25 * ts.predictability +
        0.50 * (1.0 - self_dev_penalty) +
        0.25 * (1.0 - peer_dev_penalty)
    )
    
    print(f"  Self Deviation Penalty: {self_dev_penalty:.3f} (aus {ts.self_deviation:.3f})")
    print(f"  Peer Deviation Penalty: {peer_dev_penalty:.3f} (aus {ts.peer_deviation:.3f})")
    print(f"  T_new: {t_new:.3f}")
    print(f"  T_new Komponenten:")
    print(f"    Predictability (25%): {0.25 * ts.predictability:.3f}")
    print(f"    Self-Dev (50%): {0.50 * (1.0 - self_dev_penalty):.3f}")
    print(f"    Peer-Dev (25%): {0.25 * (1.0 - peer_dev_penalty):.3f}")
    
    print(f"\n  Final Trust_Score: {ts.current_score:.3f}")
    print(f"  CSV Trust_Score: {customer_df['Trust_Score'].iloc[0]:.3f}")
    
    if abs(ts.current_score - customer_df['Trust_Score'].iloc[0]) > 0.01:
        print(f"  [WARNUNG] Abweichung zwischen berechnetem und CSV-Wert!")

