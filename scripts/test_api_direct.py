"""
Teste API direkt und vergleiche mit direkter Simulation
"""
import requests
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Test Kunde: Frank Furt (200008)
test_customer_id = 200008

print("="*80)
print("TEST: API vs. direkte Simulation")
print("="*80)

# 1. Teste API direkt
print("\n1. Teste API direkt...")
files = {'file': ('test.csv', open(csv_path, 'rb'), 'text/csv')}
data = {
    'start_date': '2021-01-01',
    'end_date': '2025-12-31',
    'recent_days': 1825,
    'historical_days': 1825
}

response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data, timeout=300)

if response.status_code == 200:
    results = response.json()
    
    customer_id_str = str(test_customer_id)
    flagged_dict = {c['customer_id']: c for c in results['flagged_customers']}
    
    print(f"   API Summary:")
    print(f"     GREEN: {results['summary']['green']}")
    print(f"     YELLOW: {results['summary']['yellow']}")
    print(f"     ORANGE: {results['summary']['orange']}")
    print(f"     RED: {results['summary']['red']}")
    print(f"     Flagged: {len(results['flagged_customers'])}")
    
    if customer_id_str in flagged_dict:
        api_profile = flagged_dict[customer_id_str]
        print(f"\n   API Ergebnis für Kunde {customer_id_str}:")
        print(f"     Risk Level: {api_profile['risk_level']}")
        print(f"     Suspicion Score: {api_profile['suspicion_score']:.2f}")
        print(f"     Layering Score: {api_profile['statistical_analysis']['layering_score']:.4f}")
    else:
        print(f"\n   API Ergebnis für Kunde {customer_id_str}:")
        print(f"     Kunde ist GREEN (nicht in flagged_customers)")
    
    # 2. Simuliere direkte Analyse
    print("\n2. Simuliere direkte Analyse...")
    with open(csv_path, 'rb') as f:
        contents = f.read()
    df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))
    
    name_col = [col for col in df.columns if 'Name' in col][0]
    
    all_transactions = []
    for idx, row in df.iterrows():
        try:
            customer_id = str(row['Kundennummer'])
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
    
    custom_analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
    custom_analyzer.add_transactions(all_transactions)
    
    profiles = custom_analyzer.analyze_all_customers(recent_days=1825)
    
    print(f"   Direkte Simulation Summary:")
    from models import RiskLevel
    summary = {
        "green": sum(1 for p in profiles if p.risk_level == RiskLevel.GREEN),
        "yellow": sum(1 for p in profiles if p.risk_level == RiskLevel.YELLOW),
        "orange": sum(1 for p in profiles if p.risk_level == RiskLevel.ORANGE),
        "red": sum(1 for p in profiles if p.risk_level == RiskLevel.RED),
    }
    print(f"     GREEN: {summary['green']}")
    print(f"     YELLOW: {summary['yellow']}")
    print(f"     ORANGE: {summary['orange']}")
    print(f"     RED: {summary['red']}")
    
    for profile in profiles:
        if profile.customer_id == customer_id_str:
            print(f"\n   Direkte Simulation Ergebnis für Kunde {customer_id_str}:")
            print(f"     Risk Level: {profile.risk_level}")
            print(f"     Suspicion Score: {profile.suspicion_score:.2f}")
            print(f"     Layering Score: {profile.statistical_analysis.layering_score:.4f}")
            break
    
    # 3. Vergleiche
    print("\n3. Vergleich:")
    if customer_id_str in flagged_dict:
        api_profile = flagged_dict[customer_id_str]
        direct_profile = next((p for p in profiles if p.customer_id == customer_id_str), None)
        
        if direct_profile:
            if api_profile['risk_level'] != direct_profile.risk_level.value:
                print(f"   PROBLEM: Risk Level unterschiedlich!")
                print(f"     API: {api_profile['risk_level']}")
                print(f"     Direkt: {direct_profile.risk_level.value}")
            
            if abs(api_profile['suspicion_score'] - direct_profile.suspicion_score) > 0.01:
                print(f"   PROBLEM: Suspicion Score unterschiedlich!")
                print(f"     API: {api_profile['suspicion_score']:.2f}")
                print(f"     Direkt: {direct_profile.suspicion_score:.2f}")
            
            if abs(api_profile['statistical_analysis']['layering_score'] - direct_profile.statistical_analysis.layering_score) > 0.01:
                print(f"   PROBLEM: Layering Score unterschiedlich!")
                print(f"     API: {api_profile['statistical_analysis']['layering_score']:.4f}")
                print(f"     Direkt: {direct_profile.statistical_analysis.layering_score:.4f}")
            else:
                print(f"   OK: Layering Score gleich")
    else:
        direct_profile = next((p for p in profiles if p.customer_id == customer_id_str), None)
        if direct_profile and direct_profile.risk_level != RiskLevel.GREEN:
            print(f"   PROBLEM: Kunde ist GREEN in API, aber {direct_profile.risk_level.value} in direkter Simulation!")
            print(f"     Direkt: {direct_profile.risk_level.value}, Suspicion Score: {direct_profile.suspicion_score:.2f}, Layering Score: {direct_profile.statistical_analysis.layering_score:.4f}")

else:
    print(f"FEHLER: {response.status_code}")

