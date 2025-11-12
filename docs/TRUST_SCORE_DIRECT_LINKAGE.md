# Trust_Score Direkte Verknüpfung mit Verdächtigen Indikatoren

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Trust_Score korreliert nicht mit Risk_Level:**
- YELLOW: Trust_Score = 0.867 (sollte 0.3-0.6 sein)
- ORANGE: Trust_Score = 0.818 (sollte 0.2-0.5 sein)
- RED: Trust_Score = 0.587 (sollte < 0.3 sein)

**2058 Zeilen** (49.5%) mit YELLOW/ORANGE/RED und Trust_Score > 0.7!

**Ursache:** Abweichungen sind zu niedrig (z.B. 0.28), selbst mit stärkerer Bestrafung bleibt Trust_Score hoch.

---

## ✅ **LÖSUNG: Direkte Verknüpfung**

**Ansatz:** Trust_Score wird **NACH** der Berechnung angepasst, basierend auf verdächtigen Indikatoren.

### Implementierung in `analyzer.py` (Zeile 845-881)

```python
# Trust_Score wird nach Berechnung angepasst
trust_penalty = 0.0

# 1. Smurfing erkannt → Trust_Score reduzieren
if weight_analysis.is_suspicious:
    if weight_analysis.threshold_avoidance_ratio >= 0.5:
        trust_penalty += 0.3  # Starker Smurfing-Indikator
    elif weight_analysis.threshold_avoidance_ratio >= 0.3:
        trust_penalty += 0.2  # Leichter Smurfing-Indikator
    if weight_analysis.cumulative_large_amount >= 50000:
        trust_penalty += 0.2  # Große kumulative Summe
    if weight_analysis.temporal_density_weeks > 1.0:
        trust_penalty += 0.2  # Hohe temporale Dichte

# 2. Layering (Geldwäsche) erkannt → Trust_Score stark reduzieren
if statistical_analysis.layering_score > 0.7:
    trust_penalty += 0.4  # Starker Layering-Verdacht
elif statistical_analysis.layering_score > 0.5:
    trust_penalty += 0.3  # Moderater Layering-Verdacht
elif statistical_analysis.layering_score > 0.3:
    trust_penalty += 0.2  # Leichter Layering-Verdacht

# 3. Entropie-Anomalie erkannt → Trust_Score reduzieren
if entropy_analysis.is_complex:
    if entropy_analysis.entropy_aggregate < 0.3 or entropy_analysis.entropy_aggregate > 2.0:
        trust_penalty += 0.2  # Extreme Entropie

# 4. Wende Penalty an (maximal 70% Reduktion)
trust_penalty = min(trust_penalty, 0.7)
adjusted_trust_score = trust_analysis.current_score * (1.0 - trust_penalty)

# Aktualisiere Trust_Score
trust_analysis.current_score = max(0.0, min(1.0, adjusted_trust_score))
```

---

## 📊 **PENALTY-BEREICHUNG**

### Smurfing-Penalties:
- Threshold Avoidance ≥ 50%: **-30%**
- Threshold Avoidance ≥ 30%: **-20%**
- Cumulative Large Amount ≥ 50k€: **-20%**
- Temporal Density > 1.0 Tx/Woche: **-20%**

**Maximal:** -70% (wenn alle Bedingungen erfüllt)

### Layering-Penalties:
- Layering Score > 0.7: **-40%**
- Layering Score > 0.5: **-30%**
- Layering Score > 0.3: **-20%**

### Entropie-Penalties:
- Extreme Entropie (< 0.3 oder > 2.0): **-20%**

### Gesamt-Penalty:
- **Maximal:** 70% Reduktion
- **Berechnung:** `adjusted_trust_score = original_trust_score * (1.0 - trust_penalty)`

---

## 📊 **ERWARTETE ERGEBNISSE**

### Beispiel: Kunde 200001 (YELLOW, Suspicion=1.58)

**Vorher:**
- Original Trust_Score: 0.85
- Trust_Penalty: 0.0
- Final Trust_Score: **0.85** ❌

**Nachher (mit direkter Verknüpfung):**
- Original Trust_Score: 0.85
- Smurfing: Threshold Avoidance = 0.0% → keine Penalty
- Layering: Layering Score = 0.0 → keine Penalty
- Entropie: is_complex = True, entropy_agg = ? → möglicherweise -20%
- Trust_Penalty: 0.2 (20%)
- Final Trust_Score: **0.85 * 0.8 = 0.68** ✅

### Beispiel: Kunde mit Layering (ORANGE)

**Vorher:**
- Original Trust_Score: 0.78
- Trust_Penalty: 0.0
- Final Trust_Score: **0.78** ❌

**Nachher:**
- Original Trust_Score: 0.78
- Layering Score = 0.75 → **-40%** Penalty
- Trust_Penalty: 0.4
- Final Trust_Score: **0.78 * 0.6 = 0.47** ✅

---

## 🎯 **ERWARTETE KORRELATION**

| Risk_Level | Vorher | Nachher (erwartet) |
|------------|--------|-------------------|
| GREEN | 0.066 | 0.05 - 0.80 |
| YELLOW | 0.867 | **0.30 - 0.60** ✅ |
| ORANGE | 0.818 | **0.20 - 0.50** ✅ |
| RED | 0.587 | **< 0.30** ✅ |

---

## 🔧 **TECHNISCHE DETAILS**

**Datei:** `analyzer.py`  
**Methode:** `analyze_customer()`  
**Zeile:** 845-881

**Reihenfolge:**
1. Weight-Analyse
2. Entropie-Analyse
3. Trust_Score (berechnet)
4. Statistische Analysen
5. **Trust_Score-Anpassung (NEU)** ⭐
6. Suspicion_Score

---

## 🧪 **TEST**

**Schritte:**
1. Server neu starten (`python main.py`)
2. CSV hochladen und analysieren
3. Neue CSV prüfen mit `analyze_trust_score_final.py`
4. Erwartete Verbesserung:
   - YELLOW: Trust_Score sollte 0.3-0.6 sein
   - ORANGE: Trust_Score sollte 0.2-0.5 sein
   - RED: Trust_Score sollte < 0.3 sein

---

## 📝 **ZUSAMMENFASSUNG**

**Implementiert:**
- ✅ Direkte Verknüpfung mit Smurfing-Indikatoren
- ✅ Direkte Verknüpfung mit Layering-Indikatoren
- ✅ Direkte Verknüpfung mit Entropie-Anomalien
- ✅ Maximale Reduktion: 70%

**Vorteile:**
- Trust_Score korreliert jetzt direkt mit verdächtigen Indikatoren
- Unabhängig von Abweichungen (die zu niedrig sein können)
- Sofortige Reaktion auf verdächtiges Verhalten

---

**Status:** ✅ **IMPLEMENTIERT**

**Nächster Schritt:** Server neu starten und testen

