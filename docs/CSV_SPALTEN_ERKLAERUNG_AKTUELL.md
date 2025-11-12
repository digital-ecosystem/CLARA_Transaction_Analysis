# CSV-Spalten Erklärung - Analysierte Trades (Aktuell)

## 📋 Übersicht

Diese Dokumentation erklärt **jede Spalte** in der analysierten CSV-Datei (`Analyzed_Trades_*.csv`), was die Werte bedeuten und wie sie berechnet werden.

**Stand:** 2025-01-12 (nach Trust_Score Entfernung)

---

## 1. **Datum** (Date)

**Bedeutung:**  
Das Datum der Transaktion im Format `DD.MM.YYYY` (z.B. `14.02.2021`).

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert aus der Eingabe-CSV.

**Beispiel:**  
`14.02.2021`

---

## 2. **Uhrzeit** (Time)

**Bedeutung:**  
Die Uhrzeit der Transaktion als numerischer Wert (Tagesbruchteil).

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert. In Excel wird dieser Wert als Zeit formatiert (`HH:MM:SS`).

**Format:**
- `0.0` = 00:00:00 (Mitternacht)
- `0.5` = 12:00:00 (Mittag)
- `0.630266` = ca. 15:07 Uhr

**Beispiel:**  
`0.630266` (entspricht ca. 15:07 Uhr)

---

## 3. **Timestamp**

**Bedeutung:**  
Vollständiger Zeitstempel der Transaktion (Datum + Uhrzeit kombiniert).

**Quelle:**  
Berechnet aus `Datum` + `Uhrzeit`.

**Berechnung:**  
```python
timestamp = Excel_Datum + Uhrzeit
# Excel_Datum = Anzahl Tage seit 01.01.1900
# Uhrzeit = Tagesbruchteil (0.0 = 00:00:00, 0.5 = 12:00:00)
```

**Beispiel:**  
`44250.630266` (entspricht 14.02.2021 15:07 Uhr)

**Excel-Format:**  
Zahlenformat mit vielen Dezimalstellen

---

## 4. **Kundennummer** (Customer Number)

**Bedeutung:**  
Eindeutige Identifikationsnummer des Kunden.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`200001`

---

## 5. **Unique Transaktion ID**

**Bedeutung:**  
Eindeutige Identifikationsnummer der Transaktion.

**Quelle:**  
Direkt aus der Original-CSV übernommen oder generiert.

**Berechnung:**  
Format: `{Kundennummer}-{Timestamp}`

**Beispiel:**  
`200001-0,630266203703704`

---

## 6. **Vollständiger Name** (Full Name)

**Bedeutung:**  
Vollständiger Name des Kunden.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`Bo Lerwagen`

---

## 7. **Auftragsvolumen** (Order Volume)

**Bedeutung:**  
Der Betrag der Transaktion in EUR.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Excel-Format:**  
Buchhaltungszahlenformat (`#,##0.00`) mit Tausender-Trennzeichen

**Beispiel:**  
`14000` (14.000,00 EUR)

---

## 8. **In/Out**

**Bedeutung:**  
Richtung der Transaktion.

**Werte:**
- `In`: Einzahlung/Investment (Geld kommt rein)
- `Out`: Auszahlung/Withdrawal (Geld geht raus)

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`In`

---

## 9. **Art** (Payment Method)

**Bedeutung:**  
Zahlungsmethode der Transaktion.

**Werte:**
- `Bar`: Bargeld
- `SEPA`: SEPA-Überweisung
- `Kredit`: Kreditkarte
- `Krypto`: Kryptowährung
- etc.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`SEPA`

---

## 10. **Risk_Level** ⭐

**Bedeutung:**  
Das **Risiko-Level** des Kunden, basierend auf dem Suspicion_Score.

**Werte:**
- `GREEN`: Unauffällig (Suspicion_Score < 150 SP)
- `YELLOW`: Leichte Auffälligkeit (150 ≤ Suspicion_Score < 300 SP)
- `ORANGE`: Erhöhtes Risiko (300 ≤ Suspicion_Score < 500 SP)
- `RED`: Hoher Verdacht (Suspicion_Score ≥ 500 SP)

**Quelle:**  
Berechnet durch `TransactionAnalyzer.determine_risk_level()`.

**Berechnung:**  
```python
if suspicion_score < 150:
    return RiskLevel.GREEN
elif suspicion_score < 300:
    return RiskLevel.YELLOW
elif suspicion_score < 500:
    return RiskLevel.ORANGE
else:
    return RiskLevel.RED
```

**Excel-Format:**  
Farbcodierung:
- GREEN: Hellgrün (`#C6EFCE`)
- YELLOW: Gelb (`#FFEB9C`)
- ORANGE: Orange (`#FFA500`)
- RED: Rot (`#FF6B6B`)

**Beispiel:**  
`ORANGE`

---

## 11. **Suspicion_Score** ⭐⭐

**Bedeutung:**  
Der **Suspicion Score** (Verdachts-Score) misst das Gesamtrisiko eines Kunden. Höhere Werte = höheres Risiko.

**Quelle:**  
Berechnet durch `TransactionAnalyzer.calculate_suspicion_score()`.

**Berechnung:**  
Der Suspicion_Score wird aus mehreren Komponenten berechnet:

1. **Module Points (TP/SP System):**
   - Weight-Analyse (40% Gewicht): Smurfing-Erkennung
   - Entropy-Analyse (30% Gewicht): Verhaltenskomplexität
   - Statistics-Analyse (30% Gewicht): Layering, Benford, Velocity, etc.

2. **Gewichtete Summe:**
   ```python
   weighted_points = (
       0.40 * weight_suspicion_net +
       0.30 * entropy_suspicion_net +
       0.30 * statistics_suspicion_net
   )
   ```

3. **Verstärkungslogik:**
   - Wenn mehrere Module gleichzeitig auffällig sind, wird der Score verstärkt

4. **Absolute (70%) + Relative (30%):**
   ```python
   absolute_score = weighted_points * amplification_factor * 0.7
   relative_score = (alpha * z_w + beta * z_h) * 30.0 * 0.3
   total_points = absolute_score + relative_score
   ```

5. **Nichtlineare Skalierung:**
   - 0-150 SP: Linear
   - 150-300 SP: Progressiv (1.2x)
   - 300-500 SP: Progressiv (1.5x)
   - 500+ SP: Dämpfung

**Bereich:**  
`0.0` bis `1000+` (Suspicion Points)

**Schwellenwerte:**
- `< 150 SP`: GREEN (Unauffällig)
- `150 - 300 SP`: YELLOW (Leichte Auffälligkeit)
- `300 - 500 SP`: ORANGE (Erhöhtes Risiko)
- `≥ 500 SP`: RED (Hoher Verdacht)

**Excel-Format:**  
Zahlenformat (`0.00`) und **negativ** (z.B. `-322.76`)

**Beispiel:**  
`332.76` (CSV) → `-332.76` (Excel)

**WICHTIG:**  
Der Suspicion_Score wird **direkt** verwendet (keine Multiplikation oder Division mehr).

---

## 12. **Flags** ⭐

**Bedeutung:**  
Spezifische Warnungen und Indikatoren, die für diesen Kunden erkannt wurden.

**Quelle:**  
Generiert durch `TransactionAnalyzer.generate_flags()`.

**Berechnung:**  
Flags werden basierend auf verschiedenen Analysen generiert:

**Weight-Analyse Flags:**
- `⏱️ HOHE TEMPORALE DICHTE: X.XX Transaktionen/Woche` (wenn > 1.0)
- `💰 SCHWELLEN-VERMEIDUNG: X.X% der Bar-Investments nah unter 10.000€` (wenn ratio >= 0.3)
- `📊 KUMULATIVE SUMME: X.XXX€ nah unter Grenze` (wenn >= 30.000€)
- `⚠️ SOF ÜBERSCHRITTEN: Source of Funds überschritten` (wenn source_of_funds_exceeded)
- `💸 ECONOMIC PLAUSIBILITY: Unrealistisch vs. Einkommen` (wenn economic_plausibility_issue)

**Entropy-Analyse Flags:**
- `📍 ENTROPIE-KANALISATION: Extreme Konzentration auf wenige Muster` (wenn entropy_aggregate < 0.3)
- `🌊 ENTROPIE-CHAOS: Extreme Streuung` (wenn entropy_aggregate > 2.0)
- `👥 PEER-ABWEICHUNG: Untypisch für Kundengruppe` (wenn peer_deviation hoch)

**Statistics-Analyse Flags:**
- `🔴 LAYERING-VERDACHT: Bar → SEPA Muster erkannt` (wenn layering_score > 0.5)
- `📈 BENFORD-ABWEICHUNG: Unnatürliche Zahlenverteilung` (wenn benford_score > 0.6)
- `⚡ HOHE GESCHWINDIGKEIT: X Transaktionen/Tag` (wenn velocity_score > 0.7)
- `🌙 ZEITANOMALIE: Ungewöhnliche Transaktionszeiten` (wenn time_anomaly_score > 0.6)

**Format:**  
Mehrere Flags werden mit ` | ` (Pipe mit Leerzeichen) getrennt.

**Beispiel:**  
`⏱️ HOHE TEMPORALE DICHTE: 21.00 Transaktionen/Woche | 📍 ENTROPIE-KANALISATION: Extreme Konzentration auf wenige Muster | 👥 PEER-ABWEICHUNG: Untypisch für Kundengruppe`

---

## 13. **Threshold_Avoidance_Ratio_%** ⭐

**Bedeutung:**  
Der **Anteil** (in Prozent) der Bar-Investments, die nah unter der Bar-Grenze (7.000€ - 9.999€) liegen. Ein hoher Wert deutet auf **Smurfing** hin.

**Quelle:**  
Berechnet durch `WeightDetector.detect_threshold_avoidance()`.

**Berechnung:**  
```python
# 1. Finde alle Bar-Investments
bar_investments = [t for t in transactions
                   if t.payment_method == "Bar" 
                   and t.transaction_type == "investment"]

# 2. Finde die, die nah unter der Grenze liegen
threshold_avoidance_txns = [t for t in bar_investments
                            if 7000.0 <= t.transaction_amount < 10000.0]

# 3. Berechne Ratio
threshold_avoidance_ratio = len(threshold_avoidance_txns) / len(bar_investments)
if len(bar_investments) == 0:
    threshold_avoidance_ratio = 0.0

# 4. Konvertiere zu Prozent
threshold_avoidance_ratio_percent = threshold_avoidance_ratio * 100
```

**Bereich:**  
`0.0%` bis `100.0%`

**Schwellenwerte:**
- `< 30%`: Normal
- `≥ 30%`: Leicht verdächtig
- `≥ 50%`: Verdächtig (starker Smurfing-Indikator)
- `≥ 70%`: Sehr verdächtig

**Excel-Format:**  
Prozentformat (`0.0`)

**Beispiel:**  
`65.5%` (65.5% der Bar-Investments liegen nah unter 10.000€)

---

## 14. **Cumulative_Large_Amount** ⭐

**Bedeutung:**  
Die **kumulative Summe** aller Transaktionen, die nah unter der Bar-Grenze (7.000€ - 9.999€) liegen. Ein hoher Wert deutet auf **Smurfing** hin.

**Quelle:**  
Berechnet durch `WeightDetector.detect_threshold_avoidance()`.

**Berechnung:**  
```python
# 1. Finde alle Bar-Investments nah unter der Grenze
threshold_avoidance_txns = [t for t in bar_investments
                            if 7000.0 <= t.transaction_amount < 10000.0]

# 2. Summiere die Beträge
cumulative_large_amount = sum(t.transaction_amount 
                              for t in threshold_avoidance_txns)
```

**Bereich:**  
`0.00` bis unbegrenzt (in EUR)

**Schwellenwerte:**
- `< 30.000€`: Normal
- `≥ 30.000€`: Leicht verdächtig
- `≥ 50.000€`: Verdächtig (starker Smurfing-Indikator)
- `≥ 100.000€`: Sehr verdächtig

**Excel-Format:**  
Buchhaltungszahlenformat (`#,##0.00`)

**Beispiel:**  
`75.000,00` (75.000€ kumulative Summe nah unter Grenze)

---

## 15. **Temporal_Density_Weeks** ⭐

**Bedeutung:**  
Die **temporale Dichte** der Transaktionen, gemessen als **Transaktionen pro Woche**. Ein hoher Wert deutet auf verdächtige Aktivität hin.

**Quelle:**  
Berechnet durch `WeightDetector.calculate_temporal_density_weeks()`.

**Berechnung:**  
```python
# 1. Berechne tatsächliche Zeitspanne
txns_with_time = [t for t in transactions if t.timestamp]
timestamps = [t.timestamp for t in txns_with_time]
min_time = min(timestamps)
max_time = max(timestamps)

actual_days = (max_time - min_time).days + 1
actual_days = max(actual_days, 1)  # Mindestens 1 Tag

# 2. Konvertiere zu Wochen
actual_weeks = actual_days / 7.0

# 3. Transaktionen pro Woche
temporal_density_weeks = len(txns_with_time) / actual_weeks
```

**Bereich:**  
`0.0` bis unbegrenzt (Transaktionen/Woche)

**Schwellenwerte:**
- `< 0.25`: Normal (weniger als 1 Transaktion/Monat)
- `0.25 - 0.5`: Leicht verdächtig (1-2 Transaktionen/Monat)
- `0.5 - 1.0`: Verdächtig (2-4 Transaktionen/Monat)
- `1.0 - 2.0`: Sehr verdächtig (4-8 Transaktionen/Monat)
- `2.0 - 5.0`: Extrem verdächtig (8-20 Transaktionen/Monat)
- `> 5.0`: Sehr extrem verdächtig (mehr als 20 Transaktionen/Monat)

**Excel-Format:**  
Zahlenformat (`0.00`)

**Beispiel:**  
`21.0` (21 Transaktionen/Woche = sehr hohe Dichte!)

---

## 16. **Layering_Score** ⭐⭐

**Bedeutung:**  
Der Score für **Cash-to-Bank Layering** (Geldwäsche-Muster). Misst das Muster: **Bar-Einzahlungen → SEPA/Kreditkarte-Auszahlungen**.

**Quelle:**  
Berechnet durch `StatisticalAnalyzer.cash_to_bank_layering_detection()`.

**Berechnung:**  
```python
# 1. Trenne Investments und Auszahlungen
investments = [t for t in transactions if t.transaction_type == "investment"]
auszahlungen = [t for t in transactions if t.transaction_type == "auszahlung"]

# 2. Finde Bar-Investments und elektronische Auszahlungen
bar_investments = [t for t in investments if t.payment_method == "Bar"]
electronic_withdrawals = [t for t in auszahlungen 
                          if t.payment_method in ["SEPA", "Kreditkarte"]]

# 3. Berechne Verhältnisse
bar_investment_ratio = len(bar_investments) / len(investments)
electronic_withdrawal_ratio = len(electronic_withdrawals) / len(auszahlungen)

# 4. Berechne Volumen-Match
investment_volume = sum(t.transaction_amount for t in bar_investments)
withdrawal_volume = sum(t.transaction_amount for t in electronic_withdrawals)
volume_ratio = withdrawal_volume / investment_volume if investment_volume > 0 else 0.0
volume_match_score = 1.0 - abs(1.0 - volume_ratio) if 0.5 < volume_ratio < 1.5 else 0.0

# 5. Berechne zeitliche Nähe (Auszahlungen innerhalb von 30 Tagen nach Bar-Einzahlungen)
time_proximity_score = ...

# 6. Kombiniere zu Base Score
base_score = (
    0.35 * bar_investment_ratio +
    0.35 * electronic_withdrawal_ratio +
    0.15 * volume_match_score +
    0.15 * time_proximity_score
)

# 7. Absolute Indikatoren (boost)
absolute_layering_indicators = 0
if bar_investment_ratio >= 0.3: absolute_layering_indicators += 1
if electronic_withdrawal_ratio >= 0.3: absolute_layering_indicators += 1
if volume_match_score >= 0.5: absolute_layering_indicators += 1
if time_proximity_score >= 0.5: absolute_layering_indicators += 1

# 8. Final Score
if absolute_layering_indicators >= 2:
    layering_score = min(1.0, base_score + boost)
else:
    layering_score = base_score * 0.3  # Reduktion bei zu wenigen Indikatoren
```

**Bereich:**  
`0.0` bis `1.0` (höher = verdächtiger)

**Schwellenwerte:**
- `< 0.3`: Kein Layering-Verdacht
- `0.3 - 0.5`: Leicht verdächtig
- `0.5 - 0.7`: Verdächtig
- `0.7 - 0.9`: Sehr verdächtig
- `≥ 0.9`: Extrem verdächtig (starkes Geldwäsche-Muster)

**Excel-Format:**  
Zahlenformat (`0.00`)

**Beispiel:**  
`0.85` (85% Layering-Score = sehr verdächtig!)

---

## 17. **Entropy_Complex** ⭐

**Bedeutung:**  
Gibt an, ob das Transaktionsverhalten **komplex** (ungewöhnlich) ist, basierend auf der Entropie-Analyse.

**Quelle:**  
Berechnet durch `EntropyDetector.analyze()`.

**Berechnung:**  
```python
# 1. Berechne Entropie für verschiedene Dimensionen
entropy_amount = shannon_entropy(amounts)  # Betragsentropie
entropy_payment_method = shannon_entropy(payment_methods)  # Kanalentropie
entropy_transaction_type = shannon_entropy(transaction_types)  # Typenentropie
entropy_time = shannon_entropy(time_patterns)  # Zeitentropie

# 2. Aggregiere Entropie
entropy_aggregate = (
    0.30 * entropy_amount +
    0.30 * entropy_payment_method +
    0.20 * entropy_transaction_type +
    0.20 * entropy_time
)

# 3. Prüfe ob komplex
is_complex = (entropy_aggregate < 0.3) or (entropy_aggregate > 2.0)
# - < 0.3: Extreme Konzentration (zu wenig Variation)
# - > 2.0: Extreme Streuung (zu viel Variation)
```

**Werte:**
- `Ja`: Entropie ist komplex (entropy_aggregate < 0.3 oder > 2.0)
- `Nein`: Entropie ist normal (0.3 ≤ entropy_aggregate ≤ 2.0)

**Beispiel:**  
`Ja` (Extreme Konzentration oder Streuung erkannt)

---

## 📊 **Zusammenfassung der Analyse-Spalten**

| Spalte | Bedeutung | Bereich | Verdächtig wenn |
|--------|-----------|---------|----------------|
| **Risk_Level** | Risiko-Kategorie | GREEN/YELLOW/ORANGE/RED | ORANGE oder RED |
| **Suspicion_Score** | Gesamt-Verdachts-Score | 0-1000+ SP | ≥ 300 SP |
| **Threshold_Avoidance_Ratio_%** | Anteil nah unter Grenze | 0-100% | ≥ 50% |
| **Cumulative_Large_Amount** | Kumulative Summe | 0-∞ EUR | ≥ 50.000€ |
| **Temporal_Density_Weeks** | Transaktionen/Woche | 0-∞ | > 1.0 |
| **Layering_Score** | Geldwäsche-Muster | 0.0-1.0 | ≥ 0.5 |
| **Entropy_Complex** | Komplexes Verhalten | Ja/Nein | Ja |

---

## 🔍 **Interpretation**

**Normale Kunden:**
- Risk_Level: GREEN
- Suspicion_Score: < 150 SP
- Threshold_Avoidance_Ratio: < 30%
- Temporal_Density_Weeks: < 0.5
- Layering_Score: < 0.3
- Entropy_Complex: Nein

**Verdächtige Kunden:**
- Risk_Level: YELLOW/ORANGE/RED
- Suspicion_Score: ≥ 150 SP
- Threshold_Avoidance_Ratio: ≥ 50%
- Temporal_Density_Weeks: > 1.0
- Layering_Score: ≥ 0.5
- Entropy_Complex: Ja

---

**Stand:** 2025-01-12  
**Version:** 2.0 (nach Trust_Score Entfernung)

