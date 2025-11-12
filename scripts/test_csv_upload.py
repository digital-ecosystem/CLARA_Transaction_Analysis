"""
Test CSV Upload direkt
"""
import requests

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\2\Kunden CSV Generator\Trades_20251110_143922.csv"

# Upload CSV
files = {'file': ('test.csv', open(csv_path, 'rb'), 'text/csv')}
data = {
    'start_date': '2021-01-01',
    'end_date': '2025-12-31',
    'recent_days': 1825,  # 5 Jahre (um alle Transaktionen zu erfassen)
    'historical_days': 1825
}

print("Uploading CSV...")
response = requests.post(f"{BASE_URL}/api/analyze/csv", files=files, data=data, timeout=300)

if response.status_code == 200:
    results = response.json()
    print(f"\nStatus: {results['status']}")
    print(f"Message: {results['message']}")
    print(f"Analyzed Customers: {results['analyzed_customers']}")
    print(f"Flagged Customers: {len(results['flagged_customers'])}")
    print(f"\nSummary:")
    print(f"  GREEN:  {results['summary']['green']}")
    print(f"  YELLOW: {results['summary']['yellow']}")
    print(f"  ORANGE: {results['summary']['orange']}")
    print(f"  RED:    {results['summary']['red']}")
    
    # Zeige flagged customers
    if results['flagged_customers']:
        print(f"\nFlagged Customers:")
        for c in results['flagged_customers'][:10]:
            print(f"  - {c['customer_id']}: {c['risk_level']} (Score: {c['suspicion_score']:.2f})")
    else:
        print("\nKeine flagged customers!")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)

