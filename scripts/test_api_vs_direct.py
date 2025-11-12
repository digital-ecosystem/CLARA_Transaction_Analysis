"""
Vergleiche API-Analyse vs. direkte Analyse
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
print("VERGLEICH: API-Analyse vs. direkte Analyse")
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
    
    # 2. Parse ALLE Transaktionen wie in main.py
    print("\n2. Parse ALLE Transaktionen wie in main.py...")
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
    
    print(f"   Gesamt Transaktionen geparst: {len(all_transactions)}")
    
    # 3. Erstelle Analyzer wie in main.py
    print("\n3. Erstelle Analyzer wie in main.py...")
    custom_analyzer = TransactionAnalyzer(
        alpha=0.6,
        beta=0.4,
        historical_days=1825
    )
    custom_analyzer.add_transactions(all_transactions)
    
    print(f"   Kunden im Analyzer: {len(custom_analyzer.transaction_history)}")
    
    # 4. Test Kunde direkt
    customer_id_str = str(test_customer_id)
    print(f"\n4. Test Kunde {customer_id_str} direkt...")
    
    if customer_id_str in custom_analyzer.transaction_history:
        txns = custom_analyzer.transaction_history[customer_id_str]
        print(f"   Transaktionen im Analyzer: {len(txns)}")
        
        # Prüfe recent_txns
        recent_txns = custom_analyzer.get_customer_transactions(
            customer_id_str,
            days=1825,
            use_data_end_as_reference=True
        )
        print(f"   Recent Transactions (1825 days): {len(recent_txns)}")
        
        if len(recent_txns) == 0:
            print(f"   PROBLEM: Keine recent_txns gefunden!")
            
            # Prüfe Timestamps
            timestamps = [t.timestamp for t in txns if t.timestamp]
            if timestamps:
                print(f"   Timestamps im Analyzer:")
                print(f"     Erste: {min(timestamps)}")
                print(f"     Letzte: {max(timestamps)}")
                
                latest = custom_analyzer.get_latest_timestamp()
                if latest:
                    print(f"   Latest Timestamp (Analyzer): {latest}")
                    cutoff = latest - pd.Timedelta(days=1825)
                    print(f"   Cutoff (1825 days before latest): {cutoff}")
                    
                    before_cutoff = [t for t in txns if t.timestamp and t.timestamp < cutoff]
                    after_cutoff = [t for t in txns if t.timestamp and t.timestamp >= cutoff]
                    print(f"   Transaktionen vor Cutoff: {len(before_cutoff)}")
                    print(f"   Transaktionen nach Cutoff: {len(after_cutoff)}")
        else:
            # Analysiere
            try:
                profile = custom_analyzer.analyze_customer(customer_id_str, recent_days=1825)
                print(f"\n   Direkte Analyse Ergebnis:")
                print(f"     Risk Level: {profile.risk_level}")
                print(f"     Suspicion Score: {profile.suspicion_score:.2f}")
                print(f"     Layering Score: {profile.statistical_analysis.layering_score:.4f}")
                
                # Prüfe API-Ergebnis
                flagged_dict = {c['customer_id']: c for c in results['flagged_customers']}
                if customer_id_str in flagged_dict:
                    api_profile = flagged_dict[customer_id_str]
                    print(f"\n   API-Analyse Ergebnis:")
                    print(f"     Risk Level: {api_profile['risk_level']}")
                    print(f"     Suspicion Score: {api_profile['suspicion_score']:.2f}")
                    print(f"     Layering Score: {api_profile['statistical_analysis']['layering_score']:.4f}")
                    
                    if profile.statistical_analysis.layering_score != api_profile['statistical_analysis']['layering_score']:
                        print(f"\n   PROBLEM: Layering Score unterschiedlich!")
                        print(f"     Direkt: {profile.statistical_analysis.layering_score:.4f}")
                        print(f"     API: {api_profile['statistical_analysis']['layering_score']:.4f}")
                else:
                    print(f"\n   API-Analyse Ergebnis:")
                    print(f"     Kunde ist GREEN (nicht in flagged_customers)")
                    print(f"     -> PROBLEM: Kunde sollte YELLOW sein!")
            except Exception as e:
                print(f"   FEHLER: {e}")
                import traceback
                traceback.print_exc()
    else:
        print(f"   PROBLEM: Kunde nicht im Analyzer!")

else:
    print(f"FEHLER: {response.status_code}")


