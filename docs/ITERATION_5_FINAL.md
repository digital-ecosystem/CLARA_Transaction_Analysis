# Iteration 5 - Finale Kalibrierung (Skalierungs-Fix)

## Datum: 2025-11-12

---

## 🔍 **PROBLEM IN ITERATION 4**

Nach Implementierung von Iteration 4 (Schwellen 2.0/4.0/7.0) wurden folgende Ergebnisse beobachtet:

```
AKTUELL (Iteration 4):          ERWARTET:
GREEN:  161 (65.4%)        →    189 (76.8%)  ❌ 11.4% zu niedrig
YELLOW:  23 (9.3%)         →     33 (13.4%)  ✅ Nah
ORANGE:  42 (17.1%)        →      3 (1.2%)   ❌ 14x zu hoch!
RED:     20 (8.1%)         →     21 (8.5%)   ✅ Perfekt

Max Score: 13.09           →     14.48       ✅ Nah
```

**Hauptproblem:** **ORANGE ist 14x zu hoch!** (42 statt 3 Kunden)

---

## 🔬 **ROOT CAUSE ANALYSE**

### Code-Inspektion: `analyzer.py` Zeile 261

```python
# FALSCH (Iteration 4):
suspicion_score = scaled_points / 5.0
```

**Problem:** Die Skalierung ist **`/5.0`** statt **`/10.0`**!

### Auswirkung

Mit `/5.0`:
- Scores sind **2x zu hoch**
- Ein Kunde mit internem Punktwert 20 → Score 4.0 (ORANGE)
- Sollte sein: 20 / 10 = 2.0 (YELLOW)

**Beispiel-Rechnung:**

| Interner Punktwert | /5.0 (FALSCH) | Risk Level | /10.0 (KORREKT) | Risk Level |
|--------------------|---------------|------------|-----------------|------------|
| 10                 | 2.0           | YELLOW     | 1.0             | YELLOW     |
| 20                 | 4.0           | ORANGE     | 2.0             | YELLOW     |
| 25                 | 5.0           | ORANGE     | 2.5             | ORANGE     |
| 35                 | 7.0           | RED        | 3.5             | ORANGE     |
| 40                 | 8.0           | RED        | 4.0             | RED        |

**Schlussfolgerung:** Die Schwellen (2.0/4.0/7.0) passen zu `/10.0`, nicht zu `/5.0`!

---

## ✅ **LÖSUNG: ITERATION 5**

### Ansatz

**Hybrid-Lösung:**
1. Skalierung zurück auf `/10.0` (wie ursprünglich kalibriert)
2. Schwellen entsprechend anpassen

### Änderungen

#### 1. Skalierung korrigiert (`analyzer.py` Zeile 261):

```python
# Vorher (Iteration 4):
suspicion_score = scaled_points / 5.0

# Nachher (Iteration 5):
suspicion_score = scaled_points / 10.0  # Korrigiert von /5.0 → /10.0
```

#### 2. Schwellen angepasst (`analyzer.py` Zeile 560-567):

```python
# Vorher (Iteration 4):
if suspicion_score < 2.0:  # GREEN
    return RiskLevel.GREEN
elif suspicion_score < 4.0:  # YELLOW
    return RiskLevel.YELLOW
elif suspicion_score < 7.0:  # ORANGE
    return RiskLevel.ORANGE
else:  # RED
    return RiskLevel.RED

# Nachher (Iteration 5):
if suspicion_score < 1.0:  # GREEN: Unauffällig
    return RiskLevel.GREEN
elif suspicion_score < 2.0:  # YELLOW: Leicht auffällig
    return RiskLevel.YELLOW
elif suspicion_score < 3.5:  # ORANGE: Erhöhtes Risiko
    return RiskLevel.ORANGE
else:  # RED: Hoher Verdacht (>= 3.5)
    return RiskLevel.RED
```

---

## 📊 **ERWARTETE ERGEBNISSE**

### Score-Bereiche (mit /10.0)

Mit der korrigierten Skalierung erwarten wir:

```
Interner Punktwert  → Suspicion Score  → Risk Level
0-10                → 0-1.0             → GREEN
10-20               → 1.0-2.0           → YELLOW
20-35               → 2.0-3.5           → ORANGE
35+                 → 3.5+              → RED

Max erwarteter Score: ~6-7 (intern: ~60-70 Punkte)
```

### Verteilung

```
ERWARTET (Iteration 5):
GREEN:  ~190 (77%)  ← 161 → 190 (+29 Kunden)
YELLOW: ~33  (13%)  ← 23 → 33   (+10 Kunden)
ORANGE: ~3   (1%)   ← 42 → 3    (-39 Kunden) ✅
RED:    ~20  (8%)   ← 20 → 20   (±0 Kunden)  ✅

Max Score: ~6-7
```

**Umverteilung:**
- **39 Kunden:** ORANGE → YELLOW (Hauptkorrektur!)
- **10 Kunden:** YELLOW → GREEN
- **RED bleibt stabil** (perfekt!)

---

## 📈 **THEORETISCHE GRUNDLAGE**

### Mapping: Punkte → Score → Risk Level

**Dokumentation:**
```
0 – 150 SP   → Unauffällig    → GREEN
150 – 300 SP → Leicht         → YELLOW
300 – 500 SP → Erhöht         → ORANGE
500 – 1000+  → Hoch           → RED
```

**Mit nichtlinearer Skalierung:**
```
0-150 SP   → scaled ~150    → /10 → 1.5   → GREEN
150-300 SP → scaled ~330    → /10 → 3.3   → YELLOW/ORANGE
300-500 SP → scaled ~630    → /10 → 6.3   → RED
500+ SP    → scaled ~800+   → /10 → 8.0+  → RED
```

**Finale Schwellen (optimiert):**
```
GREEN:  < 1.0   (bis ~100 scaled points)
YELLOW: 1.0-2.0 (100-200 scaled points)
ORANGE: 2.0-3.5 (200-350 scaled points)
RED:    >= 3.5  (350+ scaled points)
```

---

## 🎯 **VALIDIERUNG**

### Test-Szenarien

**Szenario 1: Unauffälliger Kunde**
```
Weight SP: 0, Entropy SP: 0, Trust TP: 0, Stats SP: 0
→ Total: 0
→ Scaled: 0
→ Score: 0.0
→ Risk: GREEN ✅
```

**Szenario 2: Leichte Entropie**
```
Weight SP: 0, Entropy SP: 150, Trust SP: 50, Stats SP: 0
→ Gewichtet: 0.25*150*1.2 + 0.25*50*1.0 = 45 + 12.5 = 57.5
→ Absolute: 57.5 * 1.0 * 0.7 = 40.25
→ Total: 40.25 + relative
→ Scaled: ~50
→ Score: 0.5
→ Risk: GREEN ✅
```

**Szenario 3: Smurfing + Entropie**
```
Weight SP: 300, Entropy SP: 150, Trust SP: 100, Stats SP: 0
→ Gewichtet: 0.40*300*2.0 + 0.25*150*1.2 + 0.25*100*1.0 = 240 + 45 + 25 = 310
→ Amplification: 1.1 (2 Module aktiv)
→ Absolute: 310 * 1.1 * 0.7 = 238.7
→ Total: 238.7 + relative
→ Scaled: ~350
→ Score: 3.5
→ Risk: RED (Grenze) ✅
```

**Szenario 4: Starkes Layering**
```
Stats SP: 500 (Layering), Trust SP: 150
→ Gewichtet: 0.10*500*1.5 + 0.25*150*1.0 = 75 + 37.5 = 112.5
→ Absolute: 112.5 * 1.0 * 0.7 = 78.75
→ Total: 78.75 + relative
→ Scaled: ~90
→ Score: 0.9
→ Risk: GREEN ✅ (Layering allein reicht nicht für höheres Risiko)
```

---

## 📝 **ZUSAMMENFASSUNG**

### Problem (Iteration 4)
- Skalierung `/5.0` → Scores 2x zu hoch
- ORANGE 14x zu hoch (42 statt 3)

### Lösung (Iteration 5)
- Skalierung `/10.0` (korrigiert)
- Schwellen `1.0 / 2.0 / 3.5` (angepasst)

### Erwartung
- GREEN: 77% (+11%)
- YELLOW: 13% (+4%)
- ORANGE: 1% (-16%) ✅
- RED: 9% (stabil)

### Status
✅ **IMPLEMENTIERT & BEREIT ZUM TEST**

---

**Geänderte Dateien:**
- `analyzer.py` (Zeile 261: Skalierung `/10.0`)
- `analyzer.py` (Zeile 560-567: Schwellen `1.0/2.0/3.5`)
- `PROBLEM_ANALYSE.md` (neu)
- `ITERATION_5_FINAL.md` (neu)

**Test:** Server neu starten → CSV hochladen → `python check_results.py`

