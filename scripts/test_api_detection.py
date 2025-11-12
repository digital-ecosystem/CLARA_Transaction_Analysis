"""
Teste API-Erkennung für echte Geldwäscher
"""
import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"
csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Lese CSV
with open(csv_path, 'rb') as f:
    contents = f.read()
df = pd.read_csv(io.StringIO(contents.decode('windows-1252')))

name_col = [col for col in df.columns if 'Name' in col][0]

# Finde echte Geldwäscher
real_launderers = []
for customer_id, group in df.groupby('Kundennummer'):
    bar_in = len(group[(group['Art'] == 'Bar') & (group['In/Out'] == 'In')])
    sepa_out = len(group[(group['Art'] == 'SEPA') & (group['In/Out'] == 'Out')])
    total_out = len(group[group['In/Out'] == 'Out'])
    
    if bar_in >= 3 and sepa_out >= 3 and total_out > 0:
        real_launderers.append({
            'id': customer_id,
            'name': str(group[name_col].iloc[0]),
            'bar_in': bar_in,
            'sepa_out': sepa_out
        })

print("="*80)
print("TEST API-ERKENNUNG FÜR ECHTE GELDWÄSCHER")
print("="*80)
print(f"Gesamt echte Geldwäscher: {len(real_launderers)}")

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
    
    flagged_dict = {c['customer_id']: c for c in results['flagged_customers']}
    
    detected = []
    not_detected = []
    
    for launderer in real_launderers[:30]:  # Teste Top 30
        customer_id_str = str(launderer['id'])
        
        if customer_id_str in flagged_dict:
            profile = flagged_dict[customer_id_str]
            flags = profile.get('flags', [])
            flags_clean = [f.encode('ascii', 'ignore').decode('ascii') for f in flags]
            has_layering = any('LAYERING' in f or 'GELDWAESCHE' in f or 'GELDWSCHE' in f for f in flags_clean)
            
            if has_layering:
                detected.append({
                    'id': launderer['id'],
                    'name': launderer['name'],
                    'bar_in': launderer['bar_in'],
                    'sepa_out': launderer['sepa_out'],
                    'risk': profile['risk_level'],
                    'score': profile['suspicion_score'],
                    'layering_score': profile['statistical_analysis']['layering_score']
                })
            else:
                not_detected.append({
                    'id': launderer['id'],
                    'name': launderer['name'],
                    'bar_in': launderer['bar_in'],
                    'sepa_out': launderer['sepa_out'],
                    'risk': profile['risk_level'],
                    'score': profile['suspicion_score'],
                    'layering_score': profile['statistical_analysis']['layering_score']
                })
        else:
            not_detected.append({
                'id': launderer['id'],
                'name': launderer['name'],
                'bar_in': launderer['bar_in'],
                'sepa_out': launderer['sepa_out'],
                'risk': 'GREEN',
                'score': 0.0,
                'layering_score': 0.0
            })
    
    print(f"\nERKANNT: {len(detected)}")
    print(f"NICHT ERKANNT: {len(not_detected)}")
    
    print("\n" + "="*80)
    print("ERKANNTE GELDWÄSCHER (Top 10):")
    print("="*80)
    for d in detected[:10]:
        print(f"  {d['name']:<30} ({d['id']}): {d['risk']} | Score: {d['score']:.2f} | Layering: {d['layering_score']:.3f} | Bar-In: {d['bar_in']}, SEPA-Out: {d['sepa_out']}")
    
    print("\n" + "="*80)
    print("NICHT ERKANNTE GELDWÄSCHER (Top 10):")
    print("="*80)
    for d in not_detected[:10]:
        print(f"  {d['name']:<30} ({d['id']}): {d['risk']} | Score: {d['score']:.2f} | Layering: {d['layering_score']:.3f} | Bar-In: {d['bar_in']}, SEPA-Out: {d['sepa_out']}")
        
        # Warum nicht erkannt?
        if d['layering_score'] == 0.0:
            print(f"    -> PROBLEM: Layering Score ist 0.0")
        elif d['layering_score'] > 0.3 and d['risk'] == 'GREEN':
            print(f"    -> PROBLEM: Layering Score {d['layering_score']:.3f} > 0.3 aber GREEN (Score zu niedrig: {d['score']:.2f})")
        elif d['layering_score'] < 0.3:
            print(f"    -> PROBLEM: Layering Score {d['layering_score']:.3f} < 0.3 (zu niedrig)")
    
    # Statistiken
    print("\n" + "="*80)
    print("STATISTIKEN:")
    print("="*80)
    print(f"Erkannt: {len(detected)} / {len(real_launderers[:30])} ({len(detected)/len(real_launderers[:30])*100:.1f}%)")
    
    if detected:
        avg_bar_in_detected = sum(d['bar_in'] for d in detected) / len(detected)
        avg_sepa_out_detected = sum(d['sepa_out'] for d in detected) / len(detected)
        print(f"\nErkannt - Durchschnitt:")
        print(f"  Bar-In: {avg_bar_in_detected:.1f}")
        print(f"  SEPA-Out: {avg_sepa_out_detected:.1f}")
    
    if not_detected:
        avg_bar_in_not = sum(d['bar_in'] for d in not_detected) / len(not_detected)
        avg_sepa_out_not = sum(d['sepa_out'] for d in not_detected) / len(not_detected)
        print(f"\nNicht erkannt - Durchschnitt:")
        print(f"  Bar-In: {avg_bar_in_not:.1f}")
        print(f"  SEPA-Out: {avg_sepa_out_not:.1f}")
else:
    print(f"FEHLER: {response.status_code}")


