"""
Test Layering-Erkennung direkt über API
"""
import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\2\Kunden CSV Generator\Trades_20251110_143922.csv"

# Upload CSV
files = {'file': ('test.csv', open(csv_path, 'rb'), 'text/csv')}
data = {
    'start_date': '2021-01-01',
    'end_date': '2025-12-31',
    'recent_days': 1825,
    'historical_days': 1825
}

print("Uploading CSV...")
response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data, timeout=300)

if response.status_code == 200:
    results = response.json()
    
    # Bekannte Geldwaescher
    known_launderers = [200200, 200201, 200220, 200226, 200227]
    
    print("\n" + "="*80)
    print("LAYERING SCORES FUR BEKANNTE GELDWAESCHER:")
    print("="*80)
    
    # Prüfe flagged customers
    flagged_dict = {c['customer_id']: c for c in results['flagged_customers']}
    
    for customer_id in known_launderers:
        customer_id_str = str(customer_id)
        
        # Prüfe ob in flagged customers
        if customer_id_str in flagged_dict:
            profile = flagged_dict[customer_id_str]
            layering_score = profile['statistical_analysis']['layering_score']
            risk_level = profile['risk_level']
            suspicion_score = profile['suspicion_score']
            
            flags = profile.get('flags', [])
            flags_clean = [f.encode('ascii', 'ignore').decode('ascii') for f in flags]
            has_layering_flag = any('LAYERING' in f or 'GELDWAESCHE' in f or 'GELDWSCHE' in f for f in flags_clean)
            
            print(f"  Flags: {flags_clean}")
            
            print(f"\nKunde {customer_id}:")
            print(f"  Risk Level: {risk_level}")
            print(f"  Suspicion Score: {suspicion_score:.2f}")
            print(f"  Layering Score: {layering_score:.4f}")
            print(f"  Hat Layering Flag: {has_layering_flag}")
            
            if layering_score > 0.3 and not has_layering_flag:
                print(f"  -> PROBLEM: Score > 0.3 aber kein Flag!")
        else:
            # Prüfe ob in summary (GREEN)
            print(f"\nKunde {customer_id}:")
            print(f"  -> NICHT in flagged_customers (wahrscheinlich GREEN)")
            
            # Zeige Transaktionen aus CSV
            with open(csv_path, 'rb') as f:
                contents = f.read()
            df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))
            customer_data = df[df['Kundennummer'] == customer_id]
            
            bar_in = len(customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'In')])
            sepa_out = len(customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'Out')])
            
            print(f"  Bar-In: {bar_in}, SEPA-Out: {sepa_out}")
            
            if bar_in >= 3 and sepa_out >= 3:
                print(f"  -> SOLLTE ERKANNT WERDEN!")
else:
    print(f"FEHLER: {response.status_code}")
    print(response.text)

