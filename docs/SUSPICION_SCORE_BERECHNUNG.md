# Suspicion_Score Berechnung - Detaillierte Erklärung

## Übersicht

Der **Suspicion_Score** ist der finale Merkwürdigkeits-Index, der das Gesamtrisiko eines Kunden misst. Er wird aus **absoluten** und **relativen** Komponenten berechnet.

---

## Formel

```
Suspicion_Score = ABSOLUTE_SCORE (70%) + RELATIVE_SCORE (30%)
```

---

## 1. ABSOLUTE KOMPONENTEN (70% Gewicht)

Diese funktionieren **IMMER**, auch ohne historische Daten. Sie basieren auf **absoluten Schwellenwerten**.

### 1.1 Smurfing_Score (35% von 70% = 24.5% Gesamtgewicht)

**Basis:** `weight_analysis.is_suspicious` muss `True` sein.

**Punkteverteilung:**

| Indikator | Bedingung | Punkte |
|-----------|-----------|--------|
| **Threshold Avoidance** | `threshold_avoidance_ratio >= 0.5` | +2.0 |
| **Cumulative Large Amount** | `cumulative_large_amount >= 50,000€` | +1.5 |
| **Temporal Density** | `> 5.0 Tx/Woche` | +4.0 |
| | `2.0 - 5.0 Tx/Woche` | +3.0 |
| | `1.0 - 2.0 Tx/Woche` | +2.0 |
| | `0.5 - 1.0 Tx/Woche` | +1.0 |
| **Economic Plausibility** | `economic_plausibility_issue = True` | +1.5 |
| **Source of Funds** | `source_of_funds_exceeded = True` | +2.0 |

**Beispiel:**
- Threshold Avoidance: 60% → +2.0
- Temporal Density: 3.5 Tx/Woche → +3.0
- **Smurfing_Score = 5.0**

---

### 1.2 Entropy_Score (10% von 70% = 7% Gesamtgewicht)

**Punkteverteilung:**

| Indikator | Bedingung | Punkte |
|-----------|-----------|--------|
| **Extreme Konzentration** | `entropy_aggregate < 0.3` | +1.5 |
| **Extreme Streuung** | `entropy_aggregate > 2.0` | +1.5 |
| **Nur eine Zahlungsmethode** | `entropy_payment_method < 0.1` | +0.5 |

**Beispiel:**
- Entropy Aggregate: 0.2 → +1.5
- Payment Method Entropy: 0.05 → +0.5
- **Entropy_Score = 2.0**

---

### 1.3 Trust_Score (15% von 70% = 10.5% Gesamtgewicht)

**Punkteverteilung:**

| Trust_Score | Punkte |
|-------------|--------|
| `< 0.3` | +1.5 |
| `0.3 - 0.5` | +1.0 |
| `0.5 - 0.6` | +0.5 |
| `>= 0.6` | 0.0 |

**Beispiel:**
- Trust_Score = 0.45 → +1.0
- **Trust_Score_Punkte = 1.0**

---

### 1.4 Stats_Score (40% von 70% = 28% Gesamtgewicht)

**Berechnung:**
```python
stats_score = (
    0.10 * benford_score * 5 +        # 10% - Absolute Zahlenverteilung
    0.10 * velocity_score * 5 +       # 10% - Absolute Geschwindigkeit
    0.10 * time_anomaly_score * 5 +    # 10% - Absolute Zeitanomalien
    0.10 * clustering_score * 5 +     # 10% - Relative Clustering
    0.60 * layering_score * 5          # 60% - Geldwäsche-Muster (LAYERING)
)
```

**Alle Scores sind 0-1, werden mit 5 multipliziert (0-5 Skala).**

**Beispiel:**
- Benford Score: 0.3 → 0.10 * 0.3 * 5 = 0.15
- Velocity Score: 0.4 → 0.10 * 0.4 * 5 = 0.20
- Time Anomaly: 0.2 → 0.10 * 0.2 * 5 = 0.10
- Clustering: 0.3 → 0.10 * 0.3 * 5 = 0.15
- **Layering: 0.8 → 0.60 * 0.8 * 5 = 2.40** ⭐ (wichtigster Teil!)
- **Stats_Score = 3.0**

---

### 1.5 Absolute_Score Berechnung

```python
absolute_score = (
    0.35 * smurfing_score +   # 35% - Smurfing
    0.10 * entropy_score +     # 10% - Entropie
    0.15 * trust_score +       # 15% - Trust Score
    0.40 * stats_score         # 40% - Statistische Methoden (inkl. Layering)
) * 0.7  # 70% Gesamtgewicht
```

**Beispiel:**
- Smurfing_Score: 5.0
- Entropy_Score: 2.0
- Trust_Score: 1.0
- Stats_Score: 3.0

```python
absolute_score = (
    0.35 * 5.0 +   # 1.75
    0.10 * 2.0 +   # 0.20
    0.15 * 1.0 +   # 0.15
    0.40 * 3.0     # 1.20
) * 0.7
= 3.30 * 0.7
= 2.31
```

---

## 2. RELATIVE KOMPONENTEN (30% Gewicht)

Diese erkennen **ÄNDERUNGEN** im Verhalten (nur mit historischen Daten).

### 2.1 Z-Scores

**Weight Z-Score:**
```python
z_w = max(0, min(weight_analysis.z_score_30d, 5))
# Nur wenn z_score_30d > 0, sonst 0
```

**Entropy Z-Score:**
```python
z_h = max(0, min(abs(entropy_analysis.z_score), 5))
# Nur wenn z_score != 0, sonst 0
```

### 2.2 Relative_Score Berechnung

```python
relative_score = (
    alpha * z_w +         # Weight Z-Score (Änderung im Smurfing)
    beta * z_h            # Entropie Z-Score (Änderung in Komplexität)
) * 0.3  # 30% Gesamtgewicht
```

**Standardwerte:**
- `alpha = 0.6` (Gewicht für Weight Z-Score)
- `beta = 0.4` (Gewicht für Entropie Z-Score)

**Beispiel:**
- z_w = 2.5
- z_h = 1.8

```python
relative_score = (
    0.6 * 2.5 +   # 1.50
    0.4 * 1.8     # 0.72
) * 0.3
= 2.22 * 0.3
= 0.67
```

---

## 3. FINALER SUSPICION_SCORE

```python
Suspicion_Score = absolute_score + relative_score
```

**Beispiel:**
- Absolute_Score: 2.31
- Relative_Score: 0.67
- **Suspicion_Score = 2.98**

---

## 4. RISIKO-LEVEL ZUORDNUNG

Basierend auf dem Suspicion_Score wird das **Risk_Level** bestimmt:

| Suspicion_Score | Risk_Level | Bedeutung |
|----------------|------------|-----------|
| `< 1.0` | **GREEN** | Normales Verhalten, keine Auffälligkeiten |
| `1.0 - 2.0` | **YELLOW** | Leichte Auffälligkeiten, Monitoring empfohlen |
| `2.0 - 3.0` | **ORANGE** | Deutliche Verdachtsmomente, Überprüfung erforderlich |
| `>= 3.0` | **RED** | Starker Verdacht, sofortige Aktion nötig |

**Beispiel:**
- Suspicion_Score = 2.98 → **ORANGE** ⚠️

---

## 5. GEWICHTUNG ZUSAMMENFASSUNG

### Absolute Komponenten (70%):
- **Smurfing:** 24.5% (35% von 70%)
- **Entropie:** 7.0% (10% von 70%)
- **Trust_Score:** 10.5% (15% von 70%)
- **Stats_Score (inkl. Layering):** 28.0% (40% von 70%)
  - Layering allein: **16.8%** (60% von 40% von 70%) ⭐

### Relative Komponenten (30%):
- **Weight Z-Score:** 18% (60% von 30%)
- **Entropy Z-Score:** 12% (40% von 30%)

---

## 6. WICHTIGSTE FAKTOREN

1. **Layering (Geldwäsche):** 16.8% Gesamtgewicht ⭐⭐⭐
2. **Smurfing:** 24.5% Gesamtgewicht ⭐⭐⭐
3. **Stats_Score (gesamt):** 28.0% Gesamtgewicht ⭐⭐
4. **Trust_Score:** 10.5% Gesamtgewicht ⭐
5. **Entropie:** 7.0% Gesamtgewicht

---

## 7. BEISPIEL-BERECHNUNG (Komplett)

### Kunde: Verdächtiger Geldwäscher

**Absolute Komponenten:**
- Smurfing_Score: 0.0 (kein Smurfing)
- Entropy_Score: 0.0 (normale Entropie)
- Trust_Score: 0.5 (Trust_Score = 0.55 → +0.5)
- Stats_Score: 3.0 (Layering_Score = 0.8 → 2.4, andere = 0.6)

```python
absolute_score = (
    0.35 * 0.0 +   # 0.00
    0.10 * 0.0 +   # 0.00
    0.15 * 0.5 +   # 0.08
    0.40 * 3.0     # 1.20
) * 0.7
= 1.28 * 0.7
= 0.90
```

**Relative Komponenten:**
- z_w = 0.0 (keine Änderung)
- z_h = 0.0 (keine Änderung)

```python
relative_score = (
    0.6 * 0.0 +   # 0.00
    0.4 * 0.0     # 0.00
) * 0.3
= 0.0
```

**Finaler Suspicion_Score:**
```
Suspicion_Score = 0.90 + 0.0 = 0.90
Risk_Level = GREEN
```

**Problem:** Layering wird nicht stark genug gewichtet! ⚠️

---

## 8. ANPASSUNGEN FÜR BESSERE ERKENNUNG

**Aktuelle Gewichtung:**
- Layering: 16.8% (zu niedrig für Geldwäsche-Erkennung)

**Empfehlung:**
- Layering sollte mindestens 20-25% Gesamtgewicht haben
- Oder: Layering_Score direkt in absolute_score einbeziehen (zusätzlich zu stats_score)

---

## 9. CODE-REFERENZ

**Datei:** `analyzer.py`

**Funktion:** `calculate_suspicion_score()` (Zeile 152-266)

**Risk Level:** `determine_risk_level()` (Zeile 268-292)

