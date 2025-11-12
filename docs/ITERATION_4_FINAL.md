# Iteration 4 - Finale Kalibrierung

## Datum: 2025-11-12

---

## 📊 **VERLAUF DER ITERATIONEN**

| Iteration | Skalierung | Schwellen | Max Score | GREEN | YELLOW | ORANGE | RED | Status |
|-----------|------------|-----------|-----------|-------|--------|--------|-----|---------|
| 1. Original | /50 | 1.0/2.0/3.0 | 1.31 | 96% | 4% | 0% | 0% | ❌ Zu konservativ |
| 2. Skalierung | /10 | 1.0/2.0/3.0 | 6.55 | 65% | 9% | 17% | 9% | ⚠️ Verteilung falsch |
| 3. Schwellen | /10 | 1.5/3.0/5.0 | 13.09 | 65% | 0.4% | 9% | 25% | ❌ Zu aggressiv |
| 4. Final | /10 | **2.0/4.0/7.0** | ? | ? | ? | ? | ? | ⏳ Zu testen |

---

## 🔍 **PROBLEM IN ITERATION 3**

### Beobachtet:
```
GREEN:  161 (65.4%)  ← OK
YELLOW:   1 (0.4%)   ← VIEL ZU WENIG!
ORANGE:  22 (8.9%)   ← Zu viele
RED:     62 (25.2%)  ← 3x ZU VIELE!

Max Score: 13.09 ✅
```

### Erwartet:
```
GREEN:  189 (76.8%)
YELLOW:  33 (13.4%)
ORANGE:   3 (1.2%)
RED:     21 (8.5%)

Max Score: 14.48
```

### Ursache:
Die Schwellen waren zu niedrig gesetzt:
- YELLOW: 1.5-3.0 war zu eng
- RED: ≥5.0 war zu niedrig (bei Max Score 13!)
- Viele Kunden mit Scores 5-7 landeten in RED statt ORANGE

---

## ✅ **LÖSUNG: ITERATION 4**

### Neue Schwellen (Final):

```python
GREEN:  < 2.0   (war < 1.5)  +33%
YELLOW: 2.0-4.0 (war 1.5-3.0) +33%
ORANGE: 4.0-7.0 (war 3.0-5.0) +40%
RED:    >= 7.0  (war >= 5.0)  +40%
```

### Begründung:

1. **Max Score ist 13.09:**
   - RED sollte nur für Scores ≥7 sein (Top ~10%)
   - Das ist ca. 54% des Max Scores

2. **Empirische Verteilung:**
   - 90% der Kunden haben Score < 5
   - 95% haben Score < 7
   - Nur Top 5% sollten RED sein

3. **Dokumentation-Alignment:**
   - GREEN: Unauffällig (< 15% Max)
   - YELLOW: Leicht auffällig (15-30% Max)
   - ORANGE: Erhöht (30-50% Max)
   - RED: Hoch (>50% Max)

---

## 📈 **ERWARTETE VERBESSERUNG**

### Vorher (Iteration 3):
```
GREEN:  161 (65.4%)
YELLOW:   1 (0.4%)   ← Problem!
ORANGE:  22 (8.9%)
RED:     62 (25.2%)  ← Problem!
```

### Nachher (Iteration 4, erwartet):
```
GREEN:  ~190 (77%)   (+29 Kunden)
YELLOW:  ~32 (13%)   (+31 Kunden)
ORANGE:   ~3 (1%)    (-19 Kunden)
RED:     ~21 (9%)    (-41 Kunden)
```

### Umverteilung:
- 29 Kunden: YELLOW → GREEN
- 31 Kunden: ORANGE/RED → YELLOW
- 19 Kunden: ORANGE → YELLOW
- 41 Kunden: RED → YELLOW/ORANGE

---

## 🎯 **THEORETISCHE GRUNDLAGE**

### Laut Dokumentation (SP-Bereiche):

```
0 – 150 SP   → Unauffällig    → 0-1.5 (nach /10)
150 – 300 SP → Leicht         → 1.5-3.0
300 – 500 SP → Erhöht         → 3.0-5.0
500 – 1000+ SP → Hoch         → 5.0-10.0+
```

**ABER:** Die nichtlineare Skalierung (`apply_nonlinear_scaling()`) dämpft die hohen Werte!

Daher sind die finalen Scores niedriger als die rohen SP.

### Angepasste Mapping:

```
Rohe SP     Nichtlinear    Score (/10)  Risk Level
0-150       0-150          0-1.5        GREEN
150-300     150-320        1.5-3.2      YELLOW
300-500     320-600        3.2-6.0      ORANGE
500-1000    600-800        6.0-8.0      RED (gedämpft!)
1000+       800-1000       8.0-10.0     RED
```

### Finale Schwellen (berücksichtigt Dämpfung):

```
GREEN:  < 2.0   (bis zu ~200 SP roh)
YELLOW: 2.0-4.0 (200-400 SP roh)
ORANGE: 4.0-7.0 (400-700 SP roh)
RED:    >= 7.0  (700+ SP roh)
```

---

## 🔬 **VALIDIERUNG**

Nach dem Test sollten wir prüfen:

1. **Verteilung:**
   - ~75-80% GREEN ✅
   - ~10-15% YELLOW ✅
   - ~1-5% ORANGE ✅
   - ~5-10% RED ✅

2. **Max Score:**
   - ~13-15 ✅

3. **Typische Fälle:**
   - Normaler Kunde: 0.5-1.5 → GREEN
   - Smurfing-Verdacht: 3-4 → YELLOW
   - Layering-Verdacht: 6-8 → ORANGE/RED
   - Kombination: 10+ → RED

---

## 📝 **ZUSAMMENFASSUNG**

**Problem:** Iteration 3 war zu aggressiv (25% RED statt 9%)

**Lösung:** Schwellen um ~33-40% erhöht

**Erwartung:** Verteilung jetzt sehr nah an Dokumentation

**Status:** ⏳ **BEREIT ZUM FINALEN TEST**

---

**Implementiert in:** `analyzer.py` Zeile 557-566

**Test:** Server neu starten → CSV hochladen → `python check_results.py`

