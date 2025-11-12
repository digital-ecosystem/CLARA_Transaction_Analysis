"""
Debug: Beispiel-Berechnung für Kunde 200001
"""
print("=" * 70)
print("BEISPIEL-BERECHNUNG: Kunde 200001")
print("=" * 70)

print("\n1. ANNAHMEN:")
print("   - Temporal Density: 21.0 Tx/Woche")
print("   - Entropy Complex: Ja (entropy_aggregate < 0.3)")
print("   - Trust Score: 0.71")
print("   - Layering Score: 0.0")

print("\n2. MODULE POINTS (laut Code):")
print("   Weight:")
print("     - Temporal Density 21.0 > 5.0 → SP = 400")
print("     - suspicion_net = 400 * 2.0 (multiplier) = 800")
print("     - weighted_points += 0.40 * 800 = 320")
print()
print("   Entropy:")
print("     - entropy_aggregate < 0.3 → SP = 150")
print("     - suspicion_net = 150 * 1.2 (multiplier) = 180")
print("     - weighted_points += 0.25 * 180 = 45")
print()
print("   Trust:")
print("     - Trust Score 0.71 → TP = 80 (0.6-0.8 Bereich)")
print("     - suspicion_net = (0 - 80) * 1.0 = -80")
print("     - weighted_points += 0.25 * (-80) = -20")
print()
print("   Statistics:")
print("     - Layering Score 0.0 → SP = 0")
print("     - suspicion_net = 0")
print("     - weighted_points += 0.10 * 0 = 0")

print("\n3. GESAMT WEIGHTED_POINTS:")
print("   weighted_points = 320 + 45 - 20 + 0 = 345")

print("\n4. ABSOLUTE SCORE:")
print("   amplification_factor = 1.0 (angenommen)")
print("   absolute_score = 345 * 1.0 * 0.7 = 241.5")

print("\n5. RELATIVE SCORE:")
print("   z_w = 0 (angenommen)")
print("   z_h = 0 (angenommen)")
print("   relative_score = (0.6 * 0 + 0.4 * 0) * 0.3 = 0")

print("\n6. TOTAL POINTS:")
print("   total_points = 241.5 + 0 = 241.5")

print("\n7. NONLINEAR SCALING:")
print("   241.5 ist im Bereich 150-300")
print("   scaled = 150 + (241.5 - 150) * 1.2 = 150 + 109.8 = 259.8")

print("\n8. ERGEBNIS:")
print("   suspicion_score = 259.8 SP")
print("   → Sollte YELLOW sein (150-300 SP)!")

print("\n9. TATSÄCHLICHER SCORE: 28.0 SP")
print("   → Nur 10.8% des erwarteten Werts!")
print("   → Problem: is_suspicious = False?")

