# CSV-Spalten Erklärung - Analysierte Trades

## 📋 Übersicht

Diese Dokumentation erklärt jede Spalte in der analysierten CSV-Datei (`Analyzed_Trades_*.csv`), was die Werte bedeuten und wie sie berechnet werden.

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

---

## 4. **Kundennummer** (Customer Number)

**Bedeutung:**  
Eindeutige Identifikationsnummer des Kunden.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`CUST001`

---

## 5. **Unique Transaktion ID**

**Bedeutung:**  
Eindeutige Identifikationsnummer der Transaktion.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`TXN001`

---

## 6. **Vollständiger Name** (Full Name)

**Bedeutung:**  
Vollständiger Name des Kunden.

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`Max Mustermann`

---

## 7. **Auftragsvolumen** (Order Volume)

**Bedeutung:**  
Der Betrag der Transaktion in Euro (EUR).

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert. In Excel wird dieser Wert als Buchhaltungsformat formatiert (`#,##0.00`).

**Beispiel:**  
`14000.00` (entspricht 14.000,00€ in Excel)

---

## 8. **In/Out**

**Bedeutung:**  
Transaktionsrichtung:
- **In:** Einzahlung/Investment (Geld kommt zum Kunden)
- **Out:** Auszahlung (Geld verlässt den Kunden)

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`In` oder `Out`

---

## 9. **Art** (Type)

**Bedeutung:**  
Zahlungsmethode der Transaktion:
- **Bar:** Bargeld
- **SEPA:** SEPA-Überweisung
- **Kreditkarte:** Kreditkartenzahlung

**Quelle:**  
Direkt aus der Original-CSV übernommen.

**Berechnung:**  
Keine Berechnung, Original-Wert.

**Beispiel:**  
`Bar`, `SEPA`, `Kreditkarte`

---

## 10. **Risk_Level** ⭐

**Bedeutung:**  
Das Risiko-Level des Kunden, basierend auf dem `Suspicion_Score`:
- **GREEN:** Normales Verhalten, keine Auffälligkeiten (`Suspicion_Score < 1.0`)
- **YELLOW:** Leichte Auffälligkeiten, Monitoring empfohlen (`1.0 ≤ Suspicion_Score < 2.5`)
- **ORANGE:** Deutliche Verdachtsmomente, Überprüfung erforderlich (`2.5 ≤ Suspicion_Score < 5.0`)
- **RED:** Starker Verdacht, sofortige Aktion nötig (`Suspicion_Score ≥ 5.0`)

**Quelle:**  
Berechnet durch `TransactionAnalyzer.determine_risk_level()`.

**Berechnung:**  
```python
def determine_risk_level(suspicion_score: float) -> RiskLevel:
    if suspicion_score < 1.0:
        return RiskLevel.GREEN
    elif suspicion_score < 2.5:
        return RiskLevel.YELLOW
    elif suspicion_score < 5.0:
        return RiskLevel.ORANGE
    else:
        return RiskLevel.RED
```

**Beispiel:**  
`YELLOW`, `ORANGE`, `RED`

---

## 11. **Suspicion_Score** ⭐⭐⭐

**Bedeutung:**  
Der finale Merkwürdigkeits-Index, der das Gesamtrisiko eines Kunden misst. **Höhere Werte = höheres Risiko.**

**WICHTIG:** In Excel wird dieser Wert mit **-100** multipliziert (negativ), d.h. `1.35` wird zu `-135.00`.

**Quelle:**  
Berechnet durch `TransactionAnalyzer._calculate_suspicion_score_tp_sp()`.

**Berechnung:**  
```python
Suspicion_Score = ABSOLUTE_SCORE (70%) + RELATIVE_SCORE (30%)

# ABSOLUTE_SCORE (70%):
absolute_score = (
    0.40 * weight_points +      # 40% - Smurfing (Weight-Analyse)
    0.25 * entropy_points +     # 25% - Entropie
    0.25 * trust_points +       # 25% - Trust Score
    0.10 * statistics_points    # 10% - Statistische Methoden
) * amplification_factor * 0.7

# RELATIVE_SCORE (30%):
relative_score = (
    0.6 * z_weight +            # Weight Z-Score (Änderung im Smurfing)
    0.4 * z_entropy             # Entropie Z-Score (Änderung in Komplexität)
) * 0.3

# Final:
Suspicion_Score = absolute_score + relative_score
Suspicion_Score = scaled_points / 10.0  # Skalierung
```

**Bereich:**  
Typischerweise `0.0` bis `7.0` (theoretisch unbegrenzt nach oben).

**Beispiel:**  
`1.35` (wird in Excel zu `-135.00`)

**Detaillierte Erklärung:**  
Siehe `SUSPICION_SCORE_BERECHNUNG.md`

---

## 12. **Flags** ⭐

**Bedeutung:**  
Spezifische Warnungen und Indikatoren, die für diesen Kunden erkannt wurden. Mehrere Flags werden durch ` | ` getrennt.

**Quelle:**  
Generiert durch `TransactionAnalyzer.generate_flags()`.

**Berechnung:**  
Flags werden basierend auf den Analyseergebnissen generiert:

**Smurfing-Flags:**
- `🚨 SMURFING-VERDACHT: Bar-Investments nah unter 10.000€ Grenze`
- `💰 GROSSE KUMULATIVE SUMME: X€ nah unter Grenze`
- `⚠️ SMURFING-VERDACHT: Viele kleine Transaktionen`
- `📊 Z-SCORE ERHÖHT: Plötzliche Änderung im Verhalten`

**Geldwäsche-Flags:**
- `💸 GELDWÄSCHE-VERDACHT: Cash-to-Bank Layering erkannt`
- `🔄 LAYERING: Bar-Investments → SEPA-Auszahlungen`
- `⏱️ ZEITLICHE NÄHE: Auszahlungen kurz nach Bar-Investments`

**Entropie-Flags:**
- `🔀 ENTROPIE-KANALISATION: Extreme Konzentration`
- `🌀 ENTROPIE-VERSCHLEIERUNG: Extreme Streuung`
- `📱 EINZIGE ZAHLUNGSMETHODE: Nur eine Zahlungsmethode verwendet`

**Trust Score Flags:**
- `⚠️ NIEDRIGER TRUST SCORE: Unvorhersagbares Verhalten`
- `📉 SELBST-ABWEICHUNG: Abweichung vom eigenen Muster`
- `👥 PEER-ABWEICHUNG: Abweichung von Peer-Gruppe`

**Beispiel:**  
`🚨 SMURFING-VERDACHT: Bar-Investments nah unter 10.000€ Grenze | 💰 GROSSE KUMULATIVE SUMME: 75.000€ nah unter Grenze`

---

## 13. **Threshold_Avoidance_Ratio_%** ⭐

**Bedeutung:**  
Der Anteil der Bar-Investments, die **nah unter der Bar-Grenze** (7.000€ - 9.999€) liegen. Dies ist ein starker Indikator für **Smurfing** (Vermeidung der Meldepflicht bei 10.000€).

**Quelle:**  
Berechnet durch `WeightDetector.detect_threshold_avoidance()`.

**Berechnung:**  
```python
# Finde Bar-Investments nah unter Grenze
bar_investments = [t for t in transactions 
                   if t.payment_method == "Bar" 
                   and t.transaction_type == "investment"]

threshold_avoidance_txns = [t for t in bar_investments
                            if 7000.0 <= t.transaction_amount < 10000.0]

threshold_avoidance_ratio = len(threshold_avoidance_txns) / len(bar_investments)
# Wird mit 100 multipliziert für Prozent (%)
```

**Bereich:**  
`0.0%` bis `100.0%`

**Schwellenwerte:**
- `≥ 30%`: Leicht verdächtig
- `≥ 50%`: Verdächtig (starker Smurfing-Indikator)
- `≥ 70%`: Sehr verdächtig

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
threshold_avoidance_txns = [t for t in bar_investments
                            if 7000.0 <= t.transaction_amount < 10000.0]

cumulative_large_amount = sum(t.transaction_amount 
                              for t in threshold_avoidance_txns)
```

**Bereich:**  
`0.00` bis unbegrenzt (in EUR)

**Schwellenwerte:**
- `≥ 30.000€`: Leicht verdächtig
- `≥ 50.000€`: Verdächtig (starker Smurfing-Indikator)
- `≥ 100.000€`: Sehr verdächtig

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
# Berechne tatsächliche Zeitspanne
timestamps = [t.timestamp for t in transactions if t.timestamp]
min_time = min(timestamps)
max_time = max(timestamps)
actual_days = (max_time - min_time).days + 1
actual_weeks = actual_days / 7.0

# Transaktionen pro Woche
temporal_density_weeks = len(transactions) / actual_weeks
```

**Bereich:**  
`0.0` bis unbegrenzt (Transaktionen/Woche)

**Schwellenwerte:**
- `< 0.25`: Normal (weniger als 1 Transaktion/Monat)
- `0.25 - 0.5`: Leicht verdächtig (1-2 Transaktionen/Monat)
- `0.5 - 1.0`: Verdächtig (2-4 Transaktionen/Monat)
- `> 1.0`: Sehr verdächtig (mehr als 4 Transaktionen/Monat)

**Beispiel:**  
`0.93` (0.93 Transaktionen/Woche = ca. 4 Transaktionen/Monat)

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

# 4. Berechne Volumen-Match (wie viel wurde ausgezahlt vs. eingezahlt)
volume_match_score = min(1.0, withdrawal_volume / investment_volume)

# 5. Berechne zeitliche Nähe (wie viele Auszahlungen haben Bar-Investments in den letzten 90 Tagen)
time_proximity_score = ...

# 6. Kombiniere zu Layering Score
base_score = (
    0.35 * bar_investment_ratio +
    0.35 * electronic_withdrawal_ratio +
    0.15 * volume_match_score +
    0.15 * time_proximity_score
)

# 7. Absolute Indikatoren (boost)
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
- `≥ 0.9`: Starker Layering-Verdacht

**Beispiel:**  
`0.75` (75% Layering-Score = verdächtig)

**Absolute Indikatoren:**
- Mindestens 3 Bar-Investments UND 2 SEPA-Auszahlungen
- Bar-Investment Ratio ≥ 50%
- Electronic Withdrawal Ratio ≥ 40%
- Mindestvolumen ≥ 5.000€
- Zeitliche Nähe: ≥ 30% der Auszahlungen haben Bar-Investments in den letzten 90 Tagen

---

## 17. **Entropy_Complex** ⭐

**Bedeutung:**  
Gibt an, ob das Transaktionsverhalten **ungewöhnlich komplex** oder **ungewöhnlich einfach** ist (Entropie-Anomalie).

**Quelle:**  
Berechnet durch `EntropyDetector.analyze()`.

**Berechnung:**  
```python
# Berechne Shannon-Entropie für verschiedene Dimensionen
entropy_amount = calculate_shannon_entropy(betrags_verteilung)
entropy_payment = calculate_shannon_entropy(zahlungsmethoden_verteilung)
entropy_type = calculate_shannon_entropy(transaktionstyp_verteilung)
entropy_time = calculate_shannon_entropy(zeit_verteilung)

# Aggregierte Entropie
entropy_aggregate = (
    0.25 * entropy_amount +
    0.30 * entropy_payment +
    0.20 * entropy_type +
    0.25 * entropy_time
)

# Absolute Schwellenwerte
is_complex = False
if entropy_aggregate < 0.3:  # Extreme Konzentration
    is_complex = True
elif entropy_aggregate > 2.0:  # Extreme Streuung
    is_complex = True

if entropy_payment < 0.1 and len(transactions) > 10:
    is_complex = True  # Nur eine Zahlungsmethode

# Hohe Betrags-Diversität
if len(transactions) >= 10:
    unique_ratio = unique_amounts / len(transactions)
    if unique_ratio >= 0.8:  # >= 80% unique Beträge
        is_complex = True
    if entropy_amount >= 1.0:
        is_complex = True
```

**Werte:**
- **Ja:** Ungewöhnliche Komplexität erkannt (verdächtig)
- **Nein:** Normale Komplexität

**Beispiel:**  
`Ja` oder `Nein`

**Entropie-Bedeutung:**
- **Niedrige Entropie (< 0.3):** Extreme Konzentration (alles gleich, z.B. immer 8.000€ Bar)
- **Hohe Entropie (> 2.0):** Extreme Streuung (alles unterschiedlich, Verschleierung)

---

## 18. **Trust_Score** ⭐

**Bedeutung:**  
Ein dynamischer Score, der die **Vorhersagbarkeit und Vertrauenswürdigkeit** des Kundenverhaltens misst. **Höhere Werte = vertrauenswürdiger.**

**Quelle:**  
Berechnet durch `TrustScoreCalculator.calculate_trust_score()`.

**Berechnung:**  
```python
# 1. Predictability (Vorhersagbarkeit)
predictability = (
    0.4 * cv_score +           # Variationskoeffizient der Beträge
    0.3 * interval_score +     # Regelmäßigkeit der Intervalle
    0.3 * trend_score           # Trend-Stabilität
)

# 2. Self-Deviation (Abweichung vom eigenen Muster)
self_deviation = (
    0.6 * amount_deviation +    # Abweichung der Beträge
    0.4 * method_deviation      # Abweichung der Zahlungsmethoden (KL-Divergenz)
)

# 3. Peer-Deviation (Abweichung von Peer-Gruppe)
peer_deviation = z_score_gegen_peer_gruppe

# 4. Neuer Trust Score
t_new = (
    0.4 * predictability +
    0.4 * (1.0 - self_deviation) +  # Niedrige Abweichung = gut
    0.2 * (1.0 - peer_deviation)
)

# 5. Exponential Smoothing (dynamisch)
if customer_id in previous_scores:
    t_previous = previous_scores[customer_id]
    
    # Dynamischer Beta-Faktor
    if t_new < 0.4:
        beta_dynamic = 0.4  # Reagiert schneller bei niedrigem Score
    elif t_new < 0.6:
        beta_dynamic = 0.6
    else:
        beta_dynamic = 0.7  # Standard-Beta
    
    t_current = beta_dynamic * t_previous + (1 - beta_dynamic) * t_new
else:
    t_current = t_new
```

**Bereich:**  
`0.0` bis `1.0` (höher = vertrauenswürdiger)

**Schwellenwerte:**
- `< 0.3`: Sehr niedrig (unvorhersagbar, verdächtig)
- `0.3 - 0.5`: Niedrig (leicht verdächtig)
- `0.5 - 0.6`: Mittel (neutral)
- `0.6 - 0.8`: Hoch (vertrauenswürdig)
- `≥ 0.8`: Sehr hoch (sehr vertrauenswürdig)

**Beispiel:**  
`0.45` (niedriger Trust Score = verdächtig)

**Komponenten:**
- **Predictability:** Misst, wie vorhersagbar das Verhalten ist (stabile Beträge, regelmäßige Intervalle, keine Trends)
- **Self-Deviation:** Misst, wie sehr das aktuelle Verhalten vom eigenen historischen Muster abweicht
- **Peer-Deviation:** Misst, wie sehr das Verhalten von der Peer-Gruppe abweicht

---

## 📊 Zusammenfassung der wichtigsten Spalten

| Spalte | Bedeutung | Wichtig für |
|--------|-----------|-------------|
| **Risk_Level** | Risiko-Kategorie | ⭐⭐⭐ Hauptindikator |
| **Suspicion_Score** | Gesamtrisiko-Score | ⭐⭐⭐ Hauptindikator |
| **Flags** | Spezifische Warnungen | ⭐⭐ Detaillierte Indikatoren |
| **Threshold_Avoidance_Ratio_%** | Smurfing-Indikator | ⭐⭐ Smurfing-Erkennung |
| **Cumulative_Large_Amount** | Smurfing-Indikator | ⭐⭐ Smurfing-Erkennung |
| **Layering_Score** | Geldwäsche-Indikator | ⭐⭐ Geldwäsche-Erkennung |
| **Entropy_Complex** | Komplexitäts-Indikator | ⭐ Entropie-Erkennung |
| **Trust_Score** | Vertrauenswürdigkeit | ⭐ Zusätzliche Information |

---

## 🔍 Wie die Spalten zusammenwirken

### Beispiel: Smurfing-Erkennung

Ein Kunde mit:
- `Threshold_Avoidance_Ratio_% = 65.5%` (viele Transaktionen nah unter 10.000€)
- `Cumulative_Large_Amount = 75.000€` (große kumulative Summe)
- `Temporal_Density_Weeks = 0.93` (hohe Dichte)

→ Wird als **Smurfing-Verdacht** erkannt:
- `Risk_Level = YELLOW` oder `ORANGE`
- `Suspicion_Score = 1.5 - 3.0`
- `Flags = "🚨 SMURFING-VERDACHT: Bar-Investments nah unter 10.000€ Grenze"`

### Beispiel: Geldwäsche-Erkennung

Ein Kunde mit:
- `Layering_Score = 0.75` (starkes Layering-Muster)
- Viele Bar-Investments und SEPA-Auszahlungen

→ Wird als **Geldwäsche-Verdacht** erkannt:
- `Risk_Level = ORANGE` oder `RED`
- `Suspicion_Score = 3.0 - 6.0`
- `Flags = "💸 GELDWÄSCHE-VERDACHT: Cash-to-Bank Layering erkannt"`

### Beispiel: Entropie-Erkennung

Ein Kunde mit:
- `Entropy_Complex = Ja` (ungewöhnliche Komplexität)
- Viele unterschiedliche Beträge, Zahlungsmethoden, Zeiten

→ Wird als **Entropie-Verdacht** erkannt:
- `Risk_Level = YELLOW` oder `ORANGE`
- `Suspicion_Score = 1.0 - 3.0`
- `Flags = "🌀 ENTROPIE-VERSCHLEIERUNG: Extreme Streuung"`

---

## 📚 Weitere Dokumentation

- **Suspicion_Score Berechnung:** `SUSPICION_SCORE_BERECHNUNG.md`
- **Trust Score Korrekturen:** `TRUST_SCORE_KORREKTUREN.md`
- **System-Dokumentation:** `CLARA_System_Dokumentation_v2.md`

---

**Erstellt:** 2025-01-12  
**Version:** 1.0

