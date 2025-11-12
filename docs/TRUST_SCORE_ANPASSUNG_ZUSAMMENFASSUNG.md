# Trust_Score Anpassung - Zusammenfassung

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Trust_Score korreliert nicht mit Risk_Level:**
- YELLOW: Trust_Score = 0.823 (sollte 0.3-0.6 sein)
- ORANGE: Trust_Score = 0.739 (sollte 0.2-0.5 sein)
- RED: Trust_Score = 0.583 (sollte < 0.3 sein)

**1923 Zeilen** mit YELLOW/ORANGE/RED und Trust_Score > 0.7!

---

## ✅ **IMPLEMENTIERTE LÖSUNGEN**

### 1. **Gewichtung angepasst**
- Predictability: 40% → 25%
- Self-Deviation: 40% → 50% (wenn Peer-Dev > 0) oder 80% (wenn Peer-Dev = 0)
- Peer-Deviation: 20% → 25% (nur wenn > 0)

### 2. **Nicht-lineare Bestrafung verschärft**
- Vorher: `^1.5`
- Nachher: `^2.0` (stärkere Bestrafung)

### 3. **Peer Deviation = 0.0 Problem behoben**
- **Vorher:** Peer-Dev = 0.0 → `(1.0 - 0.0) = 1.0` → Trust_Score erhöht sich stark ❌
- **Nachher:** Peer-Dev = 0.0 → neutral behandelt, Self-Deviation wird stärker gewichtet ✅

### 4. **Verschärfte Normalisierung**
- Amount Deviation: `/3.0` → `/2.0`
- Method Deviation: `/2.0` → `/1.5`
- Peer Deviation: `/3.0` → `/2.0`

### 5. **Verbesserte dynamische Glättung**
- Basierend auf `max(Abweichungen)` statt nur `T_neu`
- Sehr verdächtig: `beta = 0.2` (schnelle Reaktion)
- Verdächtig: `beta = 0.3` (schnelle Reaktion)

### 6. **Cache-Reset**
- `previous_scores` wird bei jeder neuen Analyse-Session zurückgesetzt

---

## 🔍 **DEBUG-ERGEBNISSE**

**Test-Kunde 200001 (YELLOW, Suspicion=1.58):**
- Predictability: 0.568
- Self Deviation: 0.280
- Peer Deviation: 0.000

**Problem:** Selbst mit `^2.0` Bestrafung:
- Self-Dev Penalty: `0.280^2 = 0.078`
- `(1.0 - 0.078) = 0.922` → immer noch sehr hoch!
- Trust_Score: 0.851 (fast unverändert)

**Ursache:** Abweichungen sind zu niedrig (0.28), selbst mit stärkerer Bestrafung bleibt der Score hoch.

---

## 💡 **WEITERE MÖGLICHKEITEN**

### Option 1: Normalisierung noch weiter verschärfen
- Amount Deviation: `/2.0` → `/1.5`
- Method Deviation: `/1.5` → `/1.0`
- Peer Deviation: `/2.0` → `/1.5`

### Option 2: Verdächtige Indikatoren direkt einbeziehen
- Wenn `weight_analysis.is_suspicious = True` → Trust_Score reduzieren
- Wenn `layering_score > 0.5` → Trust_Score reduzieren
- Wenn `entropy_analysis.is_complex = True` → Trust_Score reduzieren

### Option 3: Suspicion_Score direkt verknüpfen
```python
# Trust_Score basierend auf Suspicion_Score
if suspicion_score > 0:
    trust_penalty = min(suspicion_score / 10.0, 0.5)
    t_new = t_new * (1.0 - trust_penalty)
```

---

## 📊 **ERWARTETE ERGEBNISSE**

**Nach Anpassungen:**
- YELLOW: Trust_Score sollte niedriger sein (0.4-0.7 statt 0.8+)
- ORANGE: Trust_Score sollte niedriger sein (0.3-0.6 statt 0.7+)
- RED: Trust_Score sollte niedriger sein (< 0.4 statt 0.5+)

**Aber:** Wenn Abweichungen sehr niedrig sind (z.B. 0.28), bleibt der Trust_Score hoch, auch mit stärkerer Bestrafung.

---

## 🧪 **NÄCHSTE SCHRITTE**

1. ✅ Server neu starten
2. ✅ CSV neu analysieren
3. ⏳ Prüfen ob Trust_Scores niedriger sind
4. ⏳ Falls nicht: Option 2 oder 3 implementieren (direkte Verknüpfung mit verdächtigen Indikatoren)

---

**Status:** ✅ **IMPLEMENTIERT** (aber möglicherweise nicht ausreichend)

**Empfehlung:** Falls Trust_Scores immer noch zu hoch sind, Option 2 oder 3 implementieren.

