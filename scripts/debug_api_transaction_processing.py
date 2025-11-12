"""
Debug: Warum werden Transaktionen in API-Analyse nicht richtig verarbeitet?
"""
import requests
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer
from statistical_methods import StatisticalAnalyzer

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Test Kunde: Frank Furt (200008) - Bar-In: 8, SEPA-Out: 5
test_customer_id = 200008

print("="*80)
print("DEBUG: API-Transaktionsverarbeitung")
print("="*80)

# 1. Lade CSV in API
files = {'file': ('test.csv', open(csv_path, 'rb'), 'text/csv')}
data = {
    'start_date': '2021-01-01',
    'end_date': '2025-12-31',
    'recent_days': 1825,
    'historical_days': 1825
}

print("\n1. Lade CSV in API...")
response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data, timeout=300)

if response.status_code == 200:
    results = response.json()
    
    # 2. Prüfe ob Kunde in Ergebnissen
    customer_id_str = str(test_customer_id)
    flagged_dict = {c['customer_id']: c for c in results['flagged_customers']}
    
    print(f"\n2. Prüfe Kunde {customer_id_str} in API-Ergebnissen...")
    
    if customer_id_str in flagged_dict:
        profile = flagged_dict[customer_id_str]
        print(f"   Gefunden in flagged_customers")
        print(f"   Risk Level: {profile['risk_level']}")
        print(f"   Suspicion Score: {profile['suspicion_score']:.2f}")
        print(f"   Layering Score: {profile['statistical_analysis']['layering_score']:.4f}")
    else:
        print(f"   NICHT in flagged_customers (wahrscheinlich GREEN)")
        print(f"   Summary: GREEN={results['summary']['green']}, YELLOW={results['summary']['yellow']}, ORANGE={results['summary']['orange']}")
    
    # 3. Parse Transaktionen direkt aus CSV
    print(f"\n3. Parse Transaktionen direkt aus CSV...")
    with open(csv_path, 'rb') as f:
        contents = f.read()
    df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))
    
    name_col = [col for col in df.columns if 'Name' in col][0]
    test_customer_data = df[df['Kundennummer'] == test_customer_id]
    
    print(f"   Transaktionen in CSV: {len(test_customer_data)}")
    
    # Parse wie in main.py
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
    
    print(f"   Transaktionen geparst: {len(transactions)}")
    
    # 4. Test mit Analyzer direkt
    print(f"\n4. Test mit Analyzer direkt...")
    analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
    analyzer.add_transactions(transactions)
    
    try:
        profile = analyzer.analyze_customer(customer_id_str, recent_days=1825)
        print(f"   Risk Level: {profile.risk_level}")
        print(f"   Suspicion Score: {profile.suspicion_score:.2f}")
        print(f"   Layering Score: {profile.statistical_analysis.layering_score:.4f}")
        
        if profile.statistical_analysis.layering_score == 0.0:
            print(f"\n   PROBLEM: Layering Score ist 0.0 bei direkter Analyse!")
        else:
            print(f"\n   OK: Layering Score ist {profile.statistical_analysis.layering_score:.4f} bei direkter Analyse")
            
            # Prüfe warum in API-Analyse 0.0
            if customer_id_str in flagged_dict:
                api_layering = flagged_dict[customer_id_str]['statistical_analysis']['layering_score']
                if api_layering == 0.0:
                    print(f"   PROBLEM: In API-Analyse ist Layering Score 0.0!")
                    print(f"   -> Transaktionen werden in API-Analyse nicht richtig verarbeitet")
    except Exception as e:
        print(f"   FEHLER: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Test Layering direkt
    print(f"\n5. Test Layering direkt...")
    stat_analyzer = StatisticalAnalyzer()
    layering_score = stat_analyzer.cash_to_bank_layering_detection(transactions)
    print(f"   Direkter Layering Score: {layering_score:.4f}")
    
    # Zeige Details
    investments = [t for t in transactions if t.transaction_type == TransactionType.INVESTMENT]
    auszahlungen = [t for t in transactions if t.transaction_type == TransactionType.AUSZAHLUNG]
    bar_investments = [t for t in investments if t.payment_method == PaymentMethod.BAR]
    electronic_withdrawals = [t for t in auszahlungen if t.payment_method in [PaymentMethod.SEPA, PaymentMethod.KREDITKARTE]]
    
    print(f"\n   Details:")
    print(f"     Investments: {len(investments)}")
    print(f"       Bar: {len(bar_investments)}")
    print(f"     Auszahlungen: {len(auszahlungen)}")
    print(f"       SEPA/Kreditkarte: {len(electronic_withdrawals)}")
    
else:
    print(f"FEHLER: {response.status_code}")


