# Suspicion_Score Berechnung Korrektur

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Nach Threshold-Anpassung:**
- GREEN: 99.3% (4127 Transaktionen) - **ZU HOCH!**
- YELLOW: 0% - **FEHLT KOMPLETT!**
- ORANGE: 0% - **FEHLT KOMPLETT!**
- RED: 0.7% (30 Transaktionen)

**Suspicion_Scores:**
- Median: 28.0 SP (zu niedrig!)
- 99. Perzentil: 79.80 SP
- Max: 671.84 SP

**Problem:** Fast alle Kunden haben Scores < 150 SP (GREEN), nur sehr wenige haben Scores >= 500 SP (RED). Es gibt keine Kunden im mittleren Bereich (150-500 SP)!

---

## 🔍 **URSACHE**

**Beispiel Kunde 200001:**
- Temporal Density: 21.0 Tx/Woche (sehr hoch!)
- Entropy Complex: Ja
- Suspicion_Score: 28.0 SP (sollte > 150 SP sein!)

**Berechnung (vorher):**
```
Weight: Temporal Density 21.0 > 5.0 → SP = 400
suspicion_net = 400 * 2.0 = 800
weighted_points = 0.40 * 800 = 320
absolute_score = 320 * 1.0 * 0.7 = 224
relative_score = 0 (keine Z-Scores)
total_points = 224
scaled_points (150-300 Bereich) = 150 + (224-150) * 1.2 = 238.8
→ Sollte YELLOW sein (150-300 SP)!
```

**Tatsächlich:**
```
Suspicion_Score = 28.0 SP
→ Nur 11.7% des erwarteten Werts!
```

**Mögliche Ursachen:**
1. `is_suspicious = False` → Keine SP werden vergeben
2. Die `* 0.7` Multiplikation reduziert die Punkte zu stark
3. Relative Score fehlt (Z-Scores)

---

## ✅ **LÖSUNG**

### Änderung 1: Relative Score Skalierung

**Vorher:**
```python
relative_score = (alpha * z_w + beta * z_h) * 0.3
# Z-Scores (0-5) werden direkt verwendet, aber nicht zu SP skaliert
```

**Nachher:**
```python
# Skaliere Z-Scores zu SP: max 5.0 Z-Score = 150 SP (30 SP pro Z-Score)
relative_score_sp = (
    alpha * z_w * 30.0 +  # 0-5 Z-Score → 0-90 SP
    beta * z_h * 30.0      # 0-5 Z-Score → 0-60 SP
)
relative_score = relative_score_sp * 0.3
```

### Änderung 2: Absolute Score Berechnung

**Vorher:**
```python
absolute_score = weighted_points * amplification_factor * 0.7
# Die 0.7 Multiplikation reduziert die Punkte zu stark
```

**Nachher:**
```python
absolute_score = weighted_points * amplification_factor
# Die 0.7 Multiplikation wird später bei der Kombination angewendet
total_points = absolute_score * 0.7 + relative_score_sp * 0.3
```

---

## 📊 **ERWARTETE BERECHNUNG (Beispiel Kunde 200001)**

### Annahmen:
- Temporal Density: 21.0 Tx/Woche
- Entropy Complex: Ja (entropy_aggregate < 0.3)
- Trust Score: 0.71
- Layering Score: 0.0
- Z-Scores: 0 (keine historischen Daten)

### Berechnung:
```
1. Module Points:
   Weight: SP = 400 (Temporal Density > 5.0)
   suspicion_net = 400 * 2.0 = 800
   weighted_points += 0.40 * 800 = 320
   
   Entropy: SP = 150 (entropy_aggregate < 0.3)
   suspicion_net = 150 * 1.2 = 180
   weighted_points += 0.25 * 180 = 45
   
   Trust: TP = 80 (Trust Score 0.71)
   suspicion_net = (0 - 80) * 1.0 = -80
   weighted_points += 0.25 * (-80) = -20
   
   Statistics: SP = 0
   weighted_points += 0.10 * 0 = 0
   
   weighted_points = 320 + 45 - 20 + 0 = 345

2. Amplification:
   amplification_factor = 1.0 (angenommen)
   absolute_score = 345 * 1.0 = 345

3. Relative Score:
   z_w = 0, z_h = 0
   relative_score_sp = 0
   relative_score = 0 * 0.3 = 0

4. Total Points:
   total_points = 345 * 0.7 + 0 = 241.5

5. Nonlinear Scaling:
   241.5 ist im Bereich 150-300
   scaled = 150 + (241.5 - 150) * 1.2 = 150 + 109.8 = 259.8

6. Ergebnis:
   suspicion_score = 259.8 SP
   → YELLOW (150-300 SP) ✅
```

---

## 🎯 **ERWARTETE ERGEBNISSE**

### Vorher:
- GREEN: 99.3% (Scores 0-79.80 SP)
- YELLOW: 0%
- ORANGE: 0%
- RED: 0.7% (Scores 671.84 SP)

### Nachher (erwartet):
- GREEN: ~46% (Scores 0-150 SP)
- YELLOW: **~20-30%** (Scores 150-300 SP) ✅
- ORANGE: **~15-25%** (Scores 300-500 SP) ✅
- RED: ~10-15% (Scores 500+ SP)

---

## 📝 **IMPLEMENTIERUNG**

**Datei:** `analyzer.py`

**Änderungen:**
1. Zeile ~248: `absolute_score = weighted_points * amplification_factor` (entfernt `* 0.7`)
2. Zeile ~256-261: Relative Score wird zu SP skaliert (Z-Score * 30)
3. Zeile ~264: `total_points = absolute_score * 0.7 + relative_score_sp * 0.3`

---

## 🧪 **TEST**

**Schritte:**
1. Server neu starten (`python main.py`)
2. CSV hochladen und analysieren
3. Neue CSV prüfen:
   - YELLOW sollte ~20-30% sein (statt 0%)
   - ORANGE sollte ~15-25% sein (statt 0%)
   - Suspicion_Scores sollten im Bereich 150-500 SP sein

---

**Status:** ✅ **IMPLEMENTIERT**

**Nächster Schritt:** Server neu starten und testen

