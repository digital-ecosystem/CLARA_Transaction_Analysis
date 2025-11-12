# Trust_Score Analyse - Gefundene Probleme

## Datum: 2025-11-10
## CSV: `Analyzed_Trades_20251110_172632.csv`

---

## ❌ **HAUPTPROBLEME**

### 1. **Alle Trust_Scores sind zu hoch**

**Statistiken:**
- Min: **0.610** (sollte bis 0.0 gehen können)
- Max: **0.910**
- Mean: **0.723** (sehr hoch!)
- Median: **0.720**

**Verteilung:**
- 0.0 - 0.2: **0 Kunden (0.0%)** ❌
- 0.2 - 0.3: **0 Kunden (0.0%)** ❌
- 0.3 - 0.5: **0 Kunden (0.0%)** ❌
- 0.5 - 0.7: **68 Kunden (27.6%)**
- 0.7 - 1.0: **178 Kunden (72.4%)**

**Problem:** Laut Code sollten Trust_Scores < 0.3 oder < 0.5 verdächtig sein, aber **kein einziger Kunde** hat einen Trust_Score < 0.5!

---

### 2. **Widersprüchliche Korrelation mit Risk_Level**

**ORANGE Kunden haben höhere Trust_Scores als GREEN Kunden:**
- GREEN: Trust_Score Durchschnitt = **0.725**
- YELLOW: Trust_Score Durchschnitt = **0.706**
- ORANGE: Trust_Score Durchschnitt = **0.743** ❌

**Das ist widersprüchlich!** ORANGE Kunden sollten niedrigere Trust_Scores haben, da sie verdächtiger sind.

**Beispiele:**
- Kunde 200128: Risk=**ORANGE**, Suspicion=2.55, Trust=**0.800** (sehr hoch!)
- Kunde 200016: Risk=**ORANGE**, Suspicion=2.53, Trust=**0.650** (moderat)

---

### 3. **Trust_Score hat keinen Einfluss auf Suspicion_Score**

**Code-Logik (analyzer.py Zeile 219-224):**
```python
trust_score = 0.0
if trust_analysis.current_score < 0.3:
    trust_score += 1.5  # Sehr niedriger Trust
elif trust_analysis.current_score < 0.5:
    trust_score += 0.5  # Niedriger Trust
```

**Problem:** Da **alle Trust_Scores >= 0.61** sind, wird **niemals** ein zusätzlicher Verdacht hinzugefügt!

**Ergebnis:** Der Trust_Score hat **keinen Einfluss** auf die Risikobewertung!

---

### 4. **Trust_Score Abweichungen zwischen CSV und direkter Berechnung**

**Beispiel Kunde 200059:**
- CSV Trust_Score: **0.610**
- Direkt berechnet: **0.431**
- Differenz: **0.179** ❌

**Mögliche Ursachen:**
- Glättung (beta = 0.7) führt zu unterschiedlichen Werten bei wiederholter Berechnung
- CSV wurde mit anderen Parametern erstellt
- Berechnung wurde zwischenzeitlich geändert

---

## 🔍 **URSPRUNGSPROBLEME**

### 1. **Peer-Abweichung zu niedrig**

**Code (analyzer.py Zeile 515):**
```python
peer_transactions=all_transactions  # Vereinfachung: alle als Peers
```

**Problem:** Alle Transaktionen werden als Peers verwendet, nicht nur ähnliche Kunden. Das führt zu:
- Sehr niedrigen Peer-Abweichungen (fast immer ≈ 0.0)
- Höheren Trust_Scores (weil Peer-Abweichung nur 20% Gewicht hat, aber niedrig ist)

**Beispiel Kunde 200059:**
- Peer Deviation: **0.000** (keine Abweichung, weil alle als Peers gelten)

---

### 2. **Vorhersagbarkeit zu hoch berechnet**

**Beispiel Kunde 200059:**
- Predictability: **0.462** (moderat)
- Self Deviation: **1.000** (maximal! - extrem anders als historisch)
- Peer Deviation: **0.000** (keine Abweichung)

**Berechnung:**
```
T_neu = 0.5 × 0.462 + 0.3 × (1 - 1.0) + 0.2 × (1 - 0.0)
      = 0.231 + 0.0 + 0.2
      = 0.431
```

**Problem:** Trotz maximaler Selbst-Abweichung (1.0) ist der Trust_Score noch 0.431, weil:
- Vorhersagbarkeit (0.462) ist nicht extrem niedrig
- Peer-Abweichung (0.0) ist zu niedrig

---

### 3. **Glättung (beta = 0.7) verhindert niedrige Scores**

**Code (trust_score.py Zeile 256-260):**
```python
if customer_id and customer_id in self.previous_scores:
    t_previous = self.previous_scores[customer_id]
    t_current = self.beta * t_previous + (1 - self.beta) * t_new
else:
    t_current = t_new
```

**Problem:** Mit beta = 0.7 bedeutet das:
- 70% des vorherigen Scores
- 30% des neuen Scores

**Ergebnis:** Selbst wenn ein Kunde plötzlich verdächtig wird (T_neu = 0.2), bleibt der Trust_Score hoch:
```
T(t) = 0.7 × 0.7 + 0.3 × 0.2
     = 0.49 + 0.06
     = 0.55 (immer noch > 0.5!)
```

---

## ✅ **LÖSUNGSVORSCHLÄGE**

### 1. **Peer-Abweichung korrigieren**
- Nicht alle Transaktionen als Peers verwenden
- Nur ähnliche Kunden (gleiches Segment, ähnliche Transaktionsgröße) als Peers verwenden
- Oder Peer-Abweichung ganz weglassen, wenn keine Peer-Daten verfügbar sind

### 2. **Schwellenwerte anpassen**
- Trust_Score < 0.5 sollte verdächtig sein (nicht nur < 0.3)
- Trust_Score < 0.6 sollte moderat verdächtig sein
- Aktuell: Alle Scores >= 0.61, daher keine Wirkung

### 3. **Glättung anpassen**
- Beta reduzieren (z.B. 0.5 statt 0.7) für schnellere Reaktion
- Oder beta dynamisch machen (höher bei stabilen Kunden, niedriger bei neuen/verdächtigen)

### 4. **Selbst-Abweichung stärker gewichten**
- Aktuell: 30% Gewicht
- Vorschlag: 40-50% Gewicht, da Selbst-Abweichung sehr wichtig ist

### 5. **Absolute Schwellenwerte nutzen**
- Code hat bereits `absolute_low_trust` Flag (Zeile 320-330)
- Aber es wird nicht im Suspicion_Score verwendet!
- Sollte verwendet werden für zusätzliche Flags oder Score-Boost

---

## 📊 **ZUSAMMENFASSUNG**

**Status:** ❌ **Trust_Score funktioniert nicht wie erwartet**

**Hauptprobleme:**
1. Alle Trust_Scores sind zu hoch (0.61 - 0.91)
2. Kein Trust_Score < 0.5, daher keine Wirkung auf Suspicion_Score
3. ORANGE Kunden haben höhere Trust_Scores als GREEN Kunden (widersprüchlich)
4. Peer-Abweichung ist zu niedrig (alle als Peers verwendet)
5. Glättung verhindert schnelle Reaktion auf verdächtiges Verhalten

**Empfehlung:**
- Trust_Score Berechnung überarbeiten
- Schwellenwerte anpassen
- Peer-Abweichung korrigieren
- Glättung anpassen oder abschaffen für verdächtige Fälle



