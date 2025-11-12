"""
Simuliere API-Analyse direkt
"""
import pandas as pd
import io
from models import Transaction, PaymentMethod, TransactionType
from analyzer import TransactionAnalyzer

csv_path = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"

# Test Kunde: Frank Furt (200008)
test_customer_id = 200008

print("="*80)
print("SIMULIERE API-ANALYSE")
print("="*80)

# 1. Parse ALLE Transaktionen wie in main.py
print("\n1. Parse ALLE Transaktionen wie in main.py...")
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

# 2. Erstelle Analyzer wie in main.py
print("\n2. Erstelle Analyzer wie in main.py...")
custom_analyzer = TransactionAnalyzer(
    alpha=0.6,
    beta=0.4,
    historical_days=1825
)
custom_analyzer.add_transactions(all_transactions)

print(f"   Kunden im Analyzer: {len(custom_analyzer.transaction_history)}")

# 3. Analysiere alle Kunden wie in main.py
print("\n3. Analysiere alle Kunden wie in main.py...")
recent_days = 1825
profiles = custom_analyzer.analyze_all_customers(recent_days=recent_days)

print(f"   Analysierte Profile: {len(profiles)}")

# 4. Test Kunde
customer_id_str = str(test_customer_id)
print(f"\n4. Test Kunde {customer_id_str}...")

found = False
for profile in profiles:
    if profile.customer_id == customer_id_str:
        found = True
        print(f"   Gefunden in Profilen")
        print(f"   Risk Level: {profile.risk_level}")
        print(f"   Suspicion Score: {profile.suspicion_score:.2f}")
        print(f"   Layering Score: {profile.statistical_analysis.layering_score:.4f}")
        
        # Prüfe ob in flagged
        if profile.risk_level.value != "GREEN":
            print(f"   -> In flagged_customers (YELLOW/ORANGE/RED)")
        else:
            print(f"   -> NICHT in flagged_customers (GREEN)")
        break

if not found:
    print(f"   NICHT in Profilen gefunden!")

# 5. Zähle nach Risk Level
print("\n5. Zähle nach Risk Level...")
from models import RiskLevel

summary = {
    "green": sum(1 for p in profiles if p.risk_level == RiskLevel.GREEN),
    "yellow": sum(1 for p in profiles if p.risk_level == RiskLevel.YELLOW),
    "orange": sum(1 for p in profiles if p.risk_level == RiskLevel.ORANGE),
    "red": sum(1 for p in profiles if p.risk_level == RiskLevel.RED),
}

print(f"   GREEN: {summary['green']}")
print(f"   YELLOW: {summary['yellow']}")
print(f"   ORANGE: {summary['orange']}")
print(f"   RED: {summary['red']}")

# 6. Prüfe ob Kunde in flagged
flagged = [p for p in profiles if p.risk_level != RiskLevel.GREEN]
print(f"\n6. Flagged Customers: {len(flagged)}")

if customer_id_str in [p.customer_id for p in flagged]:
    print(f"   Kunde {customer_id_str} ist in flagged_customers")
else:
    print(f"   Kunde {customer_id_str} ist NICHT in flagged_customers")
    print(f"   -> PROBLEM: Kunde sollte in flagged_customers sein!")


