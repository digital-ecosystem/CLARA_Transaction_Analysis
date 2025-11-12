"""
Test Kunde direkt über API
"""
import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

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
    
    # Test Kunde 200008 (Frank Furt)
    customer_id = "200008"
    
    print(f"\nAnalysiere Kunde {customer_id}...")
    print("="*80)
    
    # Hole Kundendetails
    try:
        detail_response = requests.get(
            f"{BASE_URL}/api/customer/{customer_id}/risk-profile",
            params={'recent_days': 1825},
            timeout=30
        )
        
        if detail_response.status_code == 200:
            profile = detail_response.json()
            
            print(f"Risk Level: {profile['risk_level']}")
            print(f"Suspicion Score: {profile['suspicion_score']:.2f}")
            print(f"Layering Score: {profile['statistical_analysis']['layering_score']:.4f}")
            
            print(f"\nFlags:")
            for flag in profile.get('flags', []):
                flag_clean = flag.encode('ascii', 'ignore').decode('ascii')
                print(f"  - {flag_clean}")
            
            # Zeige Transaktionen aus CSV
            with open(csv_path, 'rb') as f:
                contents = f.read()
            df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))
            
            customer_data = df[df['Kundennummer'] == int(customer_id)]
            
            print(f"\nCSV Transaktionen:")
            print(f"  Gesamt: {len(customer_data)}")
            
            bar_in = customer_data[(customer_data['Art'] == 'Bar') & (customer_data['In/Out'] == 'In')]
            sepa_out = customer_data[(customer_data['Art'] == 'SEPA') & (customer_data['In/Out'] == 'Out')]
            
            print(f"  Bar-In: {len(bar_in)}")
            print(f"  SEPA-Out: {len(sepa_out)}")
            
            if len(bar_in) > 0 and len(sepa_out) > 0:
                # Zeige zeitliche Nähe
                customer_data['Datum_parsed'] = pd.to_datetime(customer_data['Timestamp'], format='%d.%m.%Y')
                bar_in_dates = pd.to_datetime(bar_in['Timestamp'], format='%d.%m.%Y')
                sepa_out_dates = pd.to_datetime(sepa_out['Timestamp'], format='%d.%m.%Y')
                
                print(f"\n  Zeitliche Analyse:")
                print(f"    Bar-In Durchschnitt: {bar_in_dates.mean().strftime('%Y-%m-%d')}")
                print(f"    SEPA-Out Durchschnitt: {sepa_out_dates.mean().strftime('%Y-%m-%d')}")
                
                avg_bar_date = bar_in_dates.mean()
                for idx, row in sepa_out.iterrows():
                    sepa_date = pd.to_datetime(row['Timestamp'], format='%d.%m.%Y')
                    days_diff = (sepa_date - avg_bar_date).days
                    print(f"    SEPA-Out {sepa_date.strftime('%Y-%m-%d')}: {days_diff} Tage nach avg Bar-In")
        else:
            print(f"FEHLER: {detail_response.status_code}")
            print(detail_response.text)
    except Exception as e:
        print(f"FEHLER: {e}")
else:
    print(f"FEHLER: {response.status_code}")


