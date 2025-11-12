"""
Prüft ob alle Verhältnisse und Gewichtungen korrekt sind
"""
import re
from pathlib import Path

analyzer_file = Path('analyzer.py')
content = analyzer_file.read_text(encoding='utf-8')

print("="*80)
print("PRUEFUNG: ALLE VERHAELTNISSE & GEWICHTUNGEN")
print("="*80)

errors = []
warnings = []

# 1. Prüfe Modul-Gewichtungen (sollten 40/25/25/10 sein)
print("\n[1] MODUL-GEWICHTUNGEN")
print("-" * 80)

# Suche nach weighted_points Berechnung
weight_pattern = r'weighted_points\s*\+=\s*(0\.\d+)\s*\*\s*suspicion_net'
matches = re.findall(weight_pattern, content)

if matches:
    weights = [float(m) for m in matches]
    print(f"  Gefundene Gewichtungen: {weights}")
    
    # Erwartete Gewichtungen
    expected = {
        'weight': 0.40,
        'entropy': 0.25,
        'predictability': 0.25,
        'statistics': 0.10
    }
    
    # Prüfe ob Summe = 1.0
    total = sum(weights)
    if abs(total - 1.0) > 0.01:
        errors.append(f"Gewichtungen summieren sich nicht zu 1.0: {total}")
    else:
        print(f"  [OK] Summe der Gewichtungen: {total}")
    
    # Prüfe einzelne Gewichtungen
    if len(weights) >= 4:
        if abs(weights[0] - 0.40) > 0.01:
            errors.append(f"Weight-Gewichtung falsch: {weights[0]} (sollte 0.40)")
        else:
            print(f"  [OK] Weight: {weights[0]:.2f} (40%)")
        
        if abs(weights[1] - 0.25) > 0.01:
            errors.append(f"Entropy-Gewichtung falsch: {weights[1]} (sollte 0.25)")
        else:
            print(f"  [OK] Entropy: {weights[1]:.2f} (25%)")
        
        if abs(weights[2] - 0.25) > 0.01:
            errors.append(f"Predictability-Gewichtung falsch: {weights[2]} (sollte 0.25)")
        else:
            print(f"  [OK] Predictability: {weights[2]:.2f} (25%)")
        
        if abs(weights[3] - 0.10) > 0.01:
            errors.append(f"Statistics-Gewichtung falsch: {weights[3]} (sollte 0.10)")
        else:
            print(f"  [OK] Statistics: {weights[3]:.2f} (10%)")

# 2. Prüfe Multiplikatoren (µ)
print("\n[2] MULTIPLIKATOREN (µ)")
print("-" * 80)

multipliers = {
    'weight': 2.0,
    'entropy': 1.2,
    'predictability': 1.0,
    'statistics': 1.5
}

for module, expected_mu in multipliers.items():
    pattern = f"multiplier={expected_mu}"
    if pattern in content:
        print(f"  [OK] {module.capitalize()}: µ = {expected_mu}")
    else:
        # Suche nach multiplier für dieses Modul
        pattern = f"points\\['{module}'\\].*?multiplier=([0-9.]+)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            found_mu = float(match.group(1))
            if abs(found_mu - expected_mu) > 0.01:
                errors.append(f"{module.capitalize()}-Multiplikator falsch: {found_mu} (sollte {expected_mu})")
            else:
                print(f"  [OK] {module.capitalize()}: µ = {found_mu}")
        else:
            warnings.append(f"{module.capitalize()}-Multiplikator nicht gefunden")

# 3. Prüfe Risk Level Thresholds
print("\n[3] RISK LEVEL THRESHOLDS")
print("-" * 80)

thresholds = {
    'GREEN': 150,
    'YELLOW': 300,
    'ORANGE': 500,
    'RED': 500
}

for level, threshold in thresholds.items():
    if level == 'GREEN':
        pattern = r'suspicion_score\s*<\s*150'
    elif level == 'YELLOW':
        pattern = r'suspicion_score\s*<\s*300'
    elif level == 'ORANGE':
        pattern = r'suspicion_score\s*<\s*500'
    else:  # RED
        pattern = r'suspicion_score\s*>=\s*500|else:.*RED'
    
    if re.search(pattern, content):
        print(f"  [OK] {level}: Threshold {threshold} SP korrekt")
    else:
        errors.append(f"{level}-Threshold nicht gefunden oder falsch")

# 4. Prüfe 70/30 Aufteilung (Absolute/Relative)
print("\n[4] ABSOLUTE/RELATIVE AUFTEILUNG (70/30)")
print("-" * 80)

if '* 0.7' in content or '* 0.70' in content:
    print("  [OK] Absolute Score: 70% gefunden")
else:
    warnings.append("Absolute Score 70% nicht gefunden")

if '* 0.3' in content or '* 0.30' in content:
    print("  [OK] Relative Score: 30% gefunden")
else:
    warnings.append("Relative Score 30% nicht gefunden")

# 5. Prüfe Z-Score Skalierung
print("\n[5] Z-SCORE SKALIERUNG")
print("-" * 80)

# Sollte sein: max 5.0 Z-Score = 150 SP (30 SP pro Z-Score)
if '* 30.0' in content or '* 30' in content:
    print("  [OK] Z-Score Skalierung: 30 SP pro Z-Score gefunden")
else:
    warnings.append("Z-Score Skalierung (30 SP pro Z-Score) nicht gefunden")

# 6. Prüfe Nichtlineare Skalierung
print("\n[6] NICHTLINEARE SKALIERUNG")
print("-" * 80)

scaling_checks = [
    ('0-150 SP: Linear', r'abs_points\s*<=\s*150'),
    ('150-300 SP: Progressiv 1.2x', r'1\.2'),
    ('300-500 SP: Progressiv 1.5x', r'1\.5'),
    ('500+ SP: Dämpfung', r'0\.8|dampfung'),
]

for check_name, pattern in scaling_checks:
    if re.search(pattern, content, re.IGNORECASE):
        print(f"  [OK] {check_name}")
    else:
        warnings.append(f"{check_name} nicht gefunden")

# 7. Prüfe Verstärkungslogik
print("\n[7] VERSTAERKUNGSLOGIK")
print("-" * 80)

if '1.0 + 0.1 * (n_modules - 1)' in content or '0.1 * (n_modules - 1)' in content:
    print("  [OK] Verstärkungsfaktor: v = 1 + 0.1 × (n_Module - 1)")
else:
    warnings.append("Verstärkungsfaktor-Formel nicht gefunden")

if 'min(v, 1.3)' in content or 'max 30%' in content.lower():
    print("  [OK] Maximale Verstärkung: 30% (1.3x)")
else:
    warnings.append("Maximale Verstärkung (30%) nicht gefunden")

# Zusammenfassung
print("\n" + "="*80)
print("ZUSAMMENFASSUNG")
print("="*80)

if errors:
    print(f"\n❌ FEHLER ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")
else:
    print("\n[OK] KEINE FEHLER")

if warnings:
    print(f"\n[WARNUNG] WARNUNGEN ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")
else:
    print("\n[OK] KEINE WARNUNGEN")

if not errors and not warnings:
    print("\n[OK] ALLE VERHAELTNISSE SIND KORREKT!")
else:
    print("\n⚠️  Bitte die oben genannten Punkte überprüfen.")

