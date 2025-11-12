"""
Debug: Suspicion_Score Berechnung für Kunde 200001
"""
import pandas as pd
from analyzer import TransactionAnalyzer
from weight_detector import WeightDetector
from entropy_detector import EntropyDetector
from trust_score import TrustScoreCalculator
from statistical_methods import StatisticalAnalyzer

# Lade CSV
df = pd.read_csv('Analyzed_Trades_20251112_174445.csv', encoding='utf-8-sig')

# Filtere Kunde 200001
customer_df = df[df['Kundennummer'] == 200001].copy()

print("=" * 70)
print("DEBUG: Kunde 200001")
print("=" * 70)
print(f"\nAnzahl Transaktionen: {len(customer_df)}")
print(f"Suspicion_Score: {customer_df['Suspicion_Score'].iloc[0]}")
print(f"Risk_Level: {customer_df['Risk_Level'].iloc[0]}")
print(f"Flags: {customer_df['Flags'].iloc[0]}")
print(f"Temporal_Density_Weeks: {customer_df['Temporal_Density_Weeks'].iloc[0]}")
print(f"Entropy_Complex: {customer_df['Entropy_Complex'].iloc[0]}")
print(f"Layering_Score: {customer_df['Layering_Score'].iloc[0]}")

# Analysiere
analyzer = TransactionAnalyzer()
weight_detector = WeightDetector()
entropy_detector = EntropyDetector()
trust_calculator = TrustScoreCalculator()
statistical_analyzer = StatisticalAnalyzer()

# Konvertiere zu Transaktions-Format
transactions = []
for _, row in customer_df.iterrows():
    transactions.append({
        'customer_id': int(row['Kundennummer']),
        'amount': float(row['Auftragsvolumen']),
        'direction': row['In/Out'],
        'payment_method': row['Art'],
        'timestamp': pd.to_datetime(row['Datum'] + ' ' + str(row['Uhrzeit']), format='%d.%m.%Y %H:%M:%S')
    })

# Analysiere
weight_analysis = weight_detector.analyze(transactions, customer_id=200001)
entropy_analysis = entropy_detector.analyze(transactions, customer_id=200001)
trust_analysis = trust_calculator.calculate_trust_score(transactions, customer_id=200001)
statistical_analysis = statistical_analyzer.analyze(transactions, customer_id=200001)

print("\n" + "=" * 70)
print("ANALYSE-ERGEBNISSE")
print("=" * 70)
print(f"\nWeight Analysis:")
print(f"  is_suspicious: {weight_analysis.is_suspicious}")
print(f"  threshold_avoidance_ratio: {weight_analysis.threshold_avoidance_ratio}")
print(f"  cumulative_large_amount: {weight_analysis.cumulative_large_amount}")
print(f"  temporal_density_weeks: {weight_analysis.temporal_density_weeks}")
print(f"  z_score_30d: {weight_analysis.z_score_30d}")

print(f"\nEntropy Analysis:")
print(f"  entropy_aggregate: {entropy_analysis.entropy_aggregate}")
print(f"  is_complex: {entropy_analysis.is_complex}")
print(f"  z_score: {entropy_analysis.z_score}")

print(f"\nTrust Analysis:")
print(f"  current_score: {trust_analysis.current_score}")

print(f"\nStatistical Analysis:")
print(f"  layering_score: {statistical_analysis.layering_score}")

# Berechne Module Points
module_points = analyzer.calculate_module_points(
    weight_analysis,
    entropy_analysis,
    trust_analysis,
    statistical_analysis
)

print("\n" + "=" * 70)
print("MODULE POINTS")
print("=" * 70)
for name, points in module_points.items():
    print(f"\n{name}:")
    print(f"  Trust Points: {points.trust_points}")
    print(f"  Suspicion Points: {points.suspicion_points}")
    print(f"  Multiplier: {points.multiplier}")
    suspicion_net = (points.suspicion_points - points.trust_points) * points.multiplier
    print(f"  Suspicion Net: {suspicion_net}")

# Berechne Suspicion Score
suspicion_score = analyzer.calculate_suspicion_score(
    weight_analysis,
    entropy_analysis,
    trust_analysis,
    statistical_analysis
)

print("\n" + "=" * 70)
print("SUSPICION SCORE")
print("=" * 70)
print(f"Final Suspicion_Score: {suspicion_score}")

