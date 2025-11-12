
"""
Debug: Warum fehlen 10 Kunden in der Python-Analyse?
"""
import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV direkt
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

csv_customers = set(df['Kundennummer'].unique())
print(f"CSV Kunden: {len(csv_customers)}")

# Lade CSV in API
files = {'file': ('test.csv', open(csv_path, 'rb'), 'text/csv')}
data = {
    'start_date': '2021-01-01',
    'end_date': '2025-12-31',
    'recent_days': 1825,
    'historical_days': 1825
}

print("\nLade CSV in API...")
response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data, timeout=300)

if response.status_code == 200:
    results = response.json()
    
    # Alle analysierten Kunden
    analyzed_customers = set()
    for customer in results['flagged_customers']:
        analyzed_customers.add(int(customer['customer_id']))
    
    # Prüfe auch GREEN Kunden (in summary)
    print(f"\nAPI Ergebnisse:")
    print(f"  Flagged (YELLOW/ORANGE/RED): {len(analyzed_customers)}")
    print(f"  GREEN: {results['summary']['green']}")
    print(f"  Gesamt analysiert: {len(analyzed_customers) + results['summary']['green']}")
    
    # Fehlende Kunden
    missing = csv_customers - analyzed_customers
    
    # Prüfe ob GREEN Kunden fehlen
    total_analyzed = len(analyzed_customers) + results['summary']['green']
    if total_analyzed < len(csv_customers):
        print(f"\nFEHLENDE KUNDEN: {len(csv_customers) - total_analyzed}")
        
        # Prüfe fehlende Kunden in CSV
        print("\nFehlende Kunden (Top 10):")
        for i, cust_id in enumerate(sorted(missing)[:10], 1):
            cust_data = df[df['Kundennummer'] == cust_id]
            name_col = [col for col in df.columns if 'Name' in col][0]
            name = cust_data[name_col].iloc[0] if len(cust_data) > 0 else "UNKNOWN"
            txns = len(cust_data)
            print(f"  {i}. {name} ({cust_id}): {txns} Transaktionen")
            
            # Prüfe warum fehlt
            if txns == 0:
                print(f"     -> KEINE Transaktionen!")
            else:
                # Prüfe Timestamps
                if 'Timestamp' in df.columns:
                    timestamps = pd.to_datetime(cust_data['Timestamp'], format='%d.%m.%Y', errors='coerce')
                    valid_timestamps = timestamps.dropna()
                    if len(valid_timestamps) == 0:
                        print(f"     -> KEINE gültigen Timestamps!")
                    else:
                        print(f"     -> Timestamps: {valid_timestamps.min()} bis {valid_timestamps.max()}")
else:
    print(f"FEHLER: {response.status_code}")


