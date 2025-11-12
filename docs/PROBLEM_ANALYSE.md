# Problem-Analyse: Dokumentation vs. Implementierung

## Datum: 2025-11-12

---

## 🔍 **FESTGESTELLTE DISKREPANZEN**

### 1. **Verteilung stimmt nicht**

```
AKTUELL (Analyzed_Trades_20251112_151038.csv):
GREEN:  161 (65.4%)  ❌  Soll: 189 (76.8%)
YELLOW:  23 (9.3%)   ✅  Soll: 33 (13.4%) (nah)
ORANGE:  42 (17.1%)  ❌  Soll: 3 (1.2%)  ← MASSIVES PROBLEM!
RED:     20 (8.1%)   ✅  Soll: 21 (8.5%)

Max Score: 13.09     ✅  Soll: 14.48 (nah)
```

**Hauptproblem:** **ORANGE ist 14x zu hoch!** (42 statt 3)

---

### 2. **Weight-Analyse funktioniert NICHT**

```
Module-Aktivität:
  Weight-Analyse aktiv:      1 Kunde (0.4%)  ❌
  Layering-Analyse aktiv:    3 Kunden (1.2%)
  Entropie-Analyse positiv:  84 Kunden (34.1%)  ← Dominiert!
  Trust Score < 0.5:         159 Kunden (64.6%)
```

**Problem:**
- **Nur 1 Kunde** hat `Threshold_Avoidance_Ratio > 0`
- **Keine SMURFING Flags**!
- **Entropie dominiert** (83 von 88 Flags)

**Laut Dokumentation:**
- **Weight sollte 40% Gewicht haben** (Anti-Smurfing)
- **Entropie nur 25%**

---

### 3. **ROOT CAUSE: Skalierung falsch**

**Code in `analyzer.py` Zeile 261:**

```python
suspicion_score = scaled_points / 5.0
```

**Sollte sein (laut Kalibrierung):**

```python
suspicion_score = scaled_points / 10.0
```

**Auswirkung:**
- Scores sind **2x zu hoch**!
- **ORANGE-Schwelle (4.0-7.0)** fängt zu viele Kunden
- **GREEN-Schwelle (< 2.0)** ist zu streng

---

## 📊 **DETAILLIERTE ANALYSE**

### Score-Verteilung (Perzentile)

```
25%:   0.00  ← 75% inaktive Kunden (Score 0)
50%:   0.00  ← Median ist 0
75%:   4.99  ← Top 25% haben Scores 5-13
90%:   5.60
95%:   9.63
99%:  11.17
Max:  13.09
```

**Interpretation:**
- **161 Kunden mit Score 0** (inaktive, DEFAULT-Profile)
- **85 Kunden mit Score > 0** (analysiert)
- Von diesen 85:
  - **~20-25** sollten GREEN sein (Score < 2.0)
  - **~33** sollten YELLOW sein (Score 2.0-4.0)
  - **~3** sollten ORANGE sein (Score 4.0-7.0)
  - **~21** sollten RED sein (Score >= 7.0)

**Aktuell (mit /5.0):**
- Scores sind **doppelt so hoch**
- Score 2.5 → wird zu 5.0 → ORANGE statt YELLOW!
- Score 3.5 → wird zu 7.0 → RED statt ORANGE!

---

## 🔧 **LÖSUNGEN**

### LÖSUNG 1: Skalierung korrigieren ✅ **EMPFOHLEN**

**Änderung in `analyzer.py` Zeile 261:**

```python
# Von:
suspicion_score = scaled_points / 5.0

# Zu:
suspicion_score = scaled_points / 10.0
```

**Erwartete Wirkung:**
- Scores halbiert
- ORANGE: 42 → ~3-5 Kunden ✅
- GREEN: 161 → ~185-190 Kunden ✅
- Max Score: 13.09 → ~6.5 (zu niedrig!)

**Problem:** Max Score wird dann zu niedrig!

---

### LÖSUNG 2: Punkteberechnung erhöhen

**Alternative:** Punkte in `calculate_module_points` erhöhen

**Beispiel:**
```python
# Temporal Density
if weight_analysis.temporal_density_weeks > 5.0:
    weight_sp += 800  # statt 400
elif weight_analysis.temporal_density_weeks > 2.0:
    weight_sp += 600  # statt 300
```

**Problem:** Umfangreiche Änderungen nötig

---

### LÖSUNG 3: Hybrid-Ansatz ✅ **BESTE LÖSUNG**

1. **Skalierung auf `/10.0` zurück** (wie kalibriert)
2. **Schwellen anpassen** (Iteration 5)

**Neue Schwellen:**

```python
GREEN:  < 1.0   (statt < 2.0)
YELLOW: 1.0-2.0 (statt 2.0-4.0)
ORANGE: 2.0-3.5 (statt 4.0-7.0)
RED:    >= 3.5  (statt >= 7.0)
```

**Begründung:**
- Mit `/10.0`: Max Score ~6.5
- ORANGE (2.0-3.5) → ~3-5 Kunden ✅
- RED (>= 3.5) → ~20-25 Kunden ✅
- GREEN (< 1.0) → ~185-190 Kunden ✅

---

## 🎯 **EMPFEHLUNG**

**LÖSUNG 3 implementieren:**

1. **Skalierung korrigieren:**
   ```python
   # analyzer.py Zeile 261
   suspicion_score = scaled_points / 10.0
   ```

2. **Schwellen anpassen:**
   ```python
   # analyzer.py Zeile 560-567
   if suspicion_score < 1.0:
       return RiskLevel.GREEN
   elif suspicion_score < 2.0:
       return RiskLevel.YELLOW
   elif suspicion_score < 3.5:
       return RiskLevel.ORANGE
   else:
       return RiskLevel.RED
   ```

**Erwartete Verteilung:**
- GREEN: ~185-190 (75-77%)  ✅
- YELLOW: ~30-35 (12-14%)   ✅
- ORANGE: ~3-5 (1-2%)       ✅
- RED: ~20-25 (8-10%)       ✅
- Max Score: ~6-7           ✅

---

## 📋 **WEIGHT-ANALYSE PROBLEM**

**Separates Problem:** Weight-Analyse funktioniert nicht richtig

**Symptome:**
- Nur 1 Kunde mit `Threshold_Avoidance_Ratio > 0`
- Keine SMURFING Flags
- Sollte ~40% Gewicht haben, aber ist fast inaktiv

**Mögliche Ursachen:**
1. Schwelle für `is_suspicious` zu hoch
2. `temporal_density_weeks` wird nicht berechnet
3. `threshold_avoidance_ratio` Berechnung fehlerhaft
4. Nur 30-Tage-Fenster (viele Kunden inaktiv)

**Empfehlung:**
- Separate Untersuchung der `weight_detector.py`
- Prüfen: Warum `is_suspicious` fast nie `True` ist
- ggf. Schwellen senken oder Logik anpassen

---

## 📝 **ZUSAMMENFASSUNG**

**Hauptproblem:** Skalierung `/5.0` statt `/10.0` → Scores 2x zu hoch

**Folgen:**
- ORANGE 14x zu hoch (42 statt 3)
- GREEN 11% zu niedrig
- Schwellen passen nicht zur Skalierung

**Lösung:**
1. Skalierung: `/10.0`
2. Schwellen: `1.0 / 2.0 / 3.5`
3. Erwartung: Dokumentations-konforme Verteilung

**Nächste Schritte:**
1. Hybrid-Lösung implementieren
2. Weight-Analyse debuggen (separates Issue)
3. Testen und verifizieren

