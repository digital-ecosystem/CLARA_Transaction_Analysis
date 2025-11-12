"""
Debuggt das TP/SP-System für einen problematischen Kunden
"""

import pandas as pd
from pathlib import Path
from analyzer import TransactionAnalyzer
from models import Transaction
from datetime import datetime

# Lade die CSV
csv_file = Path("Trades_20251110_143922.csv")
if not csv_file.exists():
    print(f"CSV nicht gefunden: {csv_file}")
    exit(1)

df = pd.read_csv(csv_file, encoding='windows-1252')

print("="*70)
print("DEBUG: TP/SP-System Analyse")
print("="*70)

# Parse Transaktionen
transactions = []
for idx, row in df.iterrows():
    try:
        customer_id = str(row['Kundennummer'])
        transaction_id = str(row['Unique Transaktion ID'])
        customer_name = str(row['Vollständiger Name'])
        
        amount_str = str(row['Auftragsvolumen']).replace(',', '.')
        transaction_amount = float(amount_str)
        
        art = str(row['Art']).strip()
        if art == "Kredit":
            payment_method = "Kreditkarte"
        elif art == "Bar":
            payment_method = "Bar"
        elif art == "SEPA":
            payment_method = "SEPA"
        else:
            payment_method = art
        
        in_out = str(row['In/Out']).strip()
        transaction_type = "investment" if in_out == "In" else "auszahlung"
        
        timestamp = None
        if 'Timestamp' in df.columns and pd.notna(row['Timestamp']):
            try:
                date_str = str(row['Timestamp'])
                timestamp = pd.to_datetime(date_str, format='%d.%m.%Y')
            except:
                pass
        
        txn = Transaction(
            customer_id=customer_id,
            transaction_id=transaction_id,
            customer_name=customer_name,
            transaction_amount=transaction_amount,
            payment_method=payment_method,
            transaction_type=transaction_type,
            timestamp=timestamp
        )
        transactions.append(txn)
    except:
        continue

print(f"[OK] {len(transactions)} Transaktionen geladen\n")

# Erstelle Analyzer mit TP/SP-System
analyzer = TransactionAnalyzer(
    alpha=0.6,
    beta=0.4,
    historical_days=365,
    use_tp_sp_system=True
)

analyzer.add_transactions(transactions)

# Finde Kunde mit höchstem Score
print("Analysiere alle Kunden...")
profiles = analyzer.analyze_all_customers(recent_days=30)

# Sortiere nach Score
profiles.sort(key=lambda p: p.suspicion_score, reverse=True)

print(f"\n[OK] {len(profiles)} Kunden analysiert\n")

# Zeige Top 10
print("="*70)
print("TOP 10 KUNDEN (nach Suspicion Score)")
print("="*70)
for i, profile in enumerate(profiles[:10]):
    print(f"\n{i+1}. Kunde {profile.customer_id} - {profile.customer_name}")
    print(f"   Risk Level: {profile.risk_level.value}")
    print(f"   Suspicion Score: {profile.suspicion_score:.2f}")
    print(f"   Flags: {', '.join(profile.flags) if profile.flags else 'None'}")

# Detaillierte Analyse des Top-Kunden
print("\n" + "="*70)
print("DETAILLIERTE ANALYSE - TOP KUNDE")
print("="*70)

top_customer = profiles[0]
print(f"\nKunde: {top_customer.customer_id} - {top_customer.customer_name}")
print(f"Risk Level: {top_customer.risk_level.value}")
print(f"Suspicion Score: {top_customer.suspicion_score:.2f}")

# Weight Analysis
print(f"\n[WEIGHT ANALYSIS]")
wa = top_customer.weight_analysis
print(f"  is_suspicious: {wa.is_suspicious}")
print(f"  threshold_avoidance_ratio: {wa.threshold_avoidance_ratio:.2f}")
print(f"  cumulative_large_amount: {wa.cumulative_large_amount:.2f}")
print(f"  temporal_density_weeks: {wa.temporal_density_weeks:.2f}")
print(f"  z_score_30d: {wa.z_score_30d:.2f}")

# Entropy Analysis
print(f"\n[ENTROPY ANALYSIS]")
ea = top_customer.entropy_analysis
print(f"  is_complex: {ea.is_complex}")
print(f"  entropy_aggregate: {ea.entropy_aggregate:.2f}")
print(f"  z_score: {ea.z_score:.2f}")

# Trust Score
print(f"\n[TRUST SCORE]")
ta = top_customer.trust_score_analysis
print(f"  current_score: {ta.current_score:.2f}")

# Statistical
print(f"\n[STATISTICAL ANALYSIS]")
sa = top_customer.statistical_analysis
print(f"  layering_score: {sa.layering_score:.2f}")
print(f"  benford_score: {sa.benford_score:.2f}")
print(f"  velocity_score: {sa.velocity_score:.2f}")

# Berechne manuell Module Points
print(f"\n[MODULE POINTS - MANUELL BERECHNET]")
module_points = analyzer.calculate_module_points(wa, ea, ta, sa)

for name, points in module_points.items():
    net = points.suspicion_points - points.trust_points
    print(f"  {name.upper()}:")
    print(f"    TP: {points.trust_points:.0f}, SP: {points.suspicion_points:.0f}, µ: {points.multiplier:.1f}")
    print(f"    Net: {net:.0f}")

# Berechne Amplifikationsfaktor
amp_factor = analyzer.apply_amplification_logic(module_points)
print(f"\n[AMPLIFICATION FACTOR]: {amp_factor:.2f}")

# Zeige Verteilung
print("\n" + "="*70)
print("RISK LEVEL VERTEILUNG")
print("="*70)
risk_counts = {}
for level in ['GREEN', 'YELLOW', 'ORANGE', 'RED']:
    count = sum(1 for p in profiles if p.risk_level.value == level)
    risk_counts[level] = count
    percent = (count / len(profiles) * 100) if profiles else 0
    print(f"  {level:7s}: {count:3d} ({percent:5.1f}%)")

print(f"\n  Total: {len(profiles)} Kunden")
print(f"  Max Score: {profiles[0].suspicion_score:.2f}")
print("\n" + "="*70)

