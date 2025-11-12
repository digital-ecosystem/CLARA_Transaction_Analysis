"""
Debug: Warum sind Suspicion_Scores so niedrig?
"""
import pandas as pd

csv_file = "Analyzed_Trades_20251112_172952.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 70)
print("DEBUG: SUSPICION_SCORE BERECHNUNG")
print("=" * 70)

# Beispiel: Kunde 200001 (hat Score 28.0, sollte aber höher sein)
customer_200001 = df[df['Kundennummer'] == 200001].iloc[0]

print("\n1. BEISPIEL KUNDE 200001:")
print(f"   Suspicion_Score: {customer_200001['Suspicion_Score']:.2f}")
print(f"   Risk_Level: {customer_200001['Risk_Level']}")
print(f"   Flags: {customer_200001['Flags']}")
print(f"   Temporal_Density_Weeks: {customer_200001['Temporal_Density_Weeks']:.2f}")
print(f"   Layering_Score: {customer_200001['Layering_Score']:.2f}")
print(f"   Entropy_Complex: {customer_200001['Entropy_Complex']}")

print("\n2. PROBLEM-ANALYSE:")
print("   Kunde 200001 hat:")
print("   - Temporal Density: 21.00 Tx/Woche (sehr hoch!)")
print("   - Entropy Complex: Ja")
print("   - Peer-Abweichung: Ja")
print("   Aber Suspicion_Score nur 28.0 (sollte > 150 sein für YELLOW)")

print("\n3. MÖGLICHE URSACHEN:")
print("   a) Weight-Analyse: is_suspicious = False?")
print("      → Temporal Density 21.0 sollte SP geben!")
print("   b) Gewichtung zu niedrig?")
print("      → 0.40 * SP * 2.0 * 0.7 = zu niedrig?")
print("   c) Relative Score zu niedrig?")
print("      → Z-Scores fehlen?")

print("\n4. ERWARTETE BERECHNUNG (Beispiel):")
print("   Weight: Temporal Density 21.0 > 5.0 → SP = 400")
print("   suspicion_net = 400 * 2.0 = 800")
print("   weighted_points = 0.40 * 800 = 320")
print("   absolute_score = 320 * 1.0 * 0.7 = 224")
print("   total_points ≈ 224")
print("   scaled_points (150-300 Bereich) = 150 + (224-150) * 1.2 = 238.8")
print("   → Sollte YELLOW sein (150-300 SP)!")

print("\n5. TATSÄCHLICHER SCORE: 28.0")
print("   → Das ist nur 11.7% des erwarteten Werts!")
print("   → Mögliche Ursache: is_suspicious = False?")

print("\n6. EMPFEHLUNG:")
print("   - Prüfe ob weight_analysis.is_suspicious korrekt gesetzt wird")
print("   - Prüfe ob Temporal Density richtig erkannt wird")
print("   - Prüfe ob die Gewichtung korrekt angewendet wird")

