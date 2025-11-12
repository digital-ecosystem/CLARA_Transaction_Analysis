# Problem-Analyse: Suspicion_Scores zu niedrig

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Nach Threshold-Anpassung:**
- GREEN: 99.3% (4127 Transaktionen) - **ZU HOCH!**
- YELLOW: 0% - **FEHLT KOMPLETT!**
- ORANGE: 0% - **FEHLT KOMPLETT!**
- RED: 0.7% (30 Transaktionen)

**Suspicion_Scores:**
- Median: 28.0 SP
- 99. Perzentil: 79.80 SP
- Max: 671.84 SP

**Problem:** Fast alle Kunden haben Scores < 150 SP (GREEN), nur sehr wenige haben Scores >= 500 SP (RED). Es gibt keine Kunden im mittleren Bereich (150-500 SP)!

---

## 🔍 **URSACHE**

**Beispiel Kunde 200001:**
- Temporal Density: 21.00 Tx/Woche (sehr hoch!)
- Entropy Complex: Ja
- Suspicion_Score: 28.0 SP (sollte > 150 SP sein!)

**Mögliche Ursachen:**

1. **Weight-Analyse: `is_suspicious = False`?**
   - Temporal Density 21.0 sollte definitiv SP geben
   - Aber wenn `is_suspicious = False`, werden keine SP vergeben

2. **Gewichtung zu niedrig?**
   - Aktuell: `weighted_points = 0.40 * suspicion_net`
   - Dann: `absolute_score = weighted_points * 0.7`
   - Das reduziert die Punkte um 72% (0.40 * 0.7 = 0.28)!

3. **Relative Score fehlt?**
   - Z-Scores könnten fehlen oder zu niedrig sein

---

## 📊 **ERWARTETE VS. TATSÄCHLICHE BERECHNUNG**

### Erwartet (Kunde 200001):
```
Weight: Temporal Density 21.0 > 5.0 → SP = 400
suspicion_net = 400 * 2.0 = 800
weighted_points = 0.40 * 800 = 320
absolute_score = 320 * 1.0 * 0.7 = 224
total_points ≈ 224
scaled_points (150-300 Bereich) = 150 + (224-150) * 1.2 = 238.8
→ Sollte YELLOW sein (150-300 SP)!
```

### Tatsächlich:
```
Suspicion_Score = 28.0 SP
→ Nur 11.7% des erwarteten Werts!
```

---

## ✅ **LÖSUNG**

### Problem 1: `is_suspicious` wird nicht korrekt gesetzt

**Prüfe:** `weight_detector.py` - wird `is_suspicious` korrekt auf `True` gesetzt bei hoher Temporal Density?

### Problem 2: Gewichtung zu niedrig

**Aktuell:**
```python
weighted_points += 0.40 * suspicion_net  # 40% Gewichtung
absolute_score = weighted_points * 0.7   # 70% absolute
# → Effektiv nur 28% der SP werden verwendet!
```

**Laut Dokumentation:**
- Die Gewichtung 40/25/25/10 bezieht sich auf die Module
- Die 0.7/0.3 Aufteilung bezieht sich auf absolute vs. relative Komponenten
- **ABER:** Die 0.7 Multiplikation reduziert die Punkte zu stark!

**Lösung:** Die 0.7 Multiplikation sollte nur für die relative Komponente gelten, nicht für die absolute!

### Problem 3: Relative Score zu niedrig

**Aktuell:**
```python
relative_score = (alpha * z_w + beta * z_h) * 0.3
```

Wenn Z-Scores fehlen oder zu niedrig sind, trägt der relative Score nichts bei.

---

## 🎯 **EMPFEHLUNG**

1. **Prüfe `is_suspicious` Logik:**
   - Sollte `True` sein bei Temporal Density > 5.0
   - Sollte `True` sein bei Entropy Complex

2. **Korrigiere Gewichtung:**
   - Entferne die `* 0.7` Multiplikation für `absolute_score`
   - Oder passe die Gewichtung an, damit die Scores höher werden

3. **Prüfe Relative Score:**
   - Stelle sicher, dass Z-Scores korrekt berechnet werden

---

**Status:** 🔍 **IN ANALYSE**

**Nächster Schritt:** Debug-Logging hinzufügen, um zu sehen, wo die Punkte verloren gehen

