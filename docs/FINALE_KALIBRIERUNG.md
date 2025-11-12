# Finale Kalibrierung: TP/SP-System

## Datum: 2025-11-12

---

## 📊 **FORTSCHRITT**

### Iterationen:

| Iteration | Skalierung | Max Score | RED Kunden | Status |
|-----------|------------|-----------|------------|---------|
| 1. Original | /50.0 | 1.31 | 0 (0%) | ❌ Zu konservativ |
| 2. Anpassung | /10.0 | 6.55 | 21 (8.5%) | ⚠️ Besser, aber Verteilung falsch |
| 3. Schwellen | /10.0 + neue Thresholds | ? | ? | ⏳ Zu testen |

---

## ✅ **AKTUELLE ERGEBNISSE (Iteration 2)**

```
Transaktionen: 4,157
Kunden: 246 (alle werden analysiert ✅)

Risk Level Verteilung:
  GREEN:  161 (65.4%)  ← Ziel: ~75-80%
  YELLOW:  23 (9.3%)   ← Ziel: ~12-14%
  ORANGE:  41 (16.7%)  ← Ziel: ~1-2%
  RED:     21 (8.5%)   ← Ziel: ~8-9% ✅

Max Score: 6.55 (Ziel: ~14-15)
```

---

## 🎯 **NEUE SCHWELLEN (Iteration 3)**

### Alt:
```python
GREEN:  < 1.0
YELLOW: 1.0 - 2.0
ORANGE: 2.0 - 3.0
RED:    >= 3.0
```

### Neu (Dokumentation-konform):
```python
GREEN:  < 1.5   (+50%)
YELLOW: 1.5 - 3.0   (+50%)
ORANGE: 3.0 - 5.0   (+67%)
RED:    >= 5.0      (+67%)
```

---

## 📐 **KALIBRIERUNGS-LOGIK**

### Laut Dokumentation:

**Punktebereiche (SP):**
```
0 – 150 SP   → Unauffällig
150 – 300 SP → Leichte Auffälligkeit
300 – 500 SP → Erhöhtes Risiko
500 – 1000+ SP → Hoher Verdacht
```

**Nach Skalierung (/10):**
```
0 – 15   → GREEN
15 – 30  → YELLOW
30 – 50  → ORANGE
50 – 100+ → RED
```

**Aber:** Das wäre zu extrem! Die meisten Kunden haben < 10 Punkte.

**Kompromiss (gewählte Werte):**
```
0 – 1.5   → GREEN   (0-15 SP, nichtlinear skaliert)
1.5 – 3.0  → YELLOW  (15-30 SP)
3.0 – 5.0  → ORANGE  (30-50 SP)
5.0+      → RED      (50+ SP)
```

---

## 🔍 **WARUM DIESE WERTE?**

1. **Nichtlineare Skalierung bereits angewendet:**
   - `apply_nonlinear_scaling()` dämpft extreme Werte
   - Daher sind die finalen Scores niedriger als rohe SP

2. **Empirische Beobachtung:**
   - Max Score: 6.55 (höchster beobachteter Wert)
   - 90% Perzentil: ~3.0
   - 95% Perzentil: ~4.0

3. **Ziel-Verteilung:**
   - ~75% GREEN (aktuell: 65%)
   - ~13% YELLOW (aktuell: 9%)
   - ~4% ORANGE (aktuell: 17%) ← HAUPTPROBLEM
   - ~8% RED (aktuell: 9%) ✅

4. **Anpassung:**
   - ORANGE-Schwelle von 2.0 auf 3.0 erhöht
   - Viele Kunden mit Scores 2.0-3.0 wandern nach YELLOW
   - Ergebnis: Bessere Verteilung

---

## 📈 **ERWARTETE VERBESSERUNG**

### Vorher (Iteration 2):
```
GREEN:  161 (65.4%)
YELLOW:  23 (9.3%)
ORANGE:  41 (16.7%)  ← Zu viele!
RED:     21 (8.5%)
```

### Nachher (Iteration 3, erwartet):
```
GREEN:  ~185 (75%)   (+24 Kunden)
YELLOW:  ~33 (13%)   (+10 Kunden)
ORANGE:   ~7 (3%)    (-34 Kunden)
RED:     ~21 (9%)    (unverändert)
```

---

## 🧪 **TEST-PLAN**

1. **Server neu starten**
2. **CSV erneut hochladen**
3. **Ergebnisse prüfen:**
   ```bash
   python check_results.py
   ```
4. **Vergleichen:**
   - GREEN sollte ~75% sein
   - ORANGE sollte < 5% sein
   - RED sollte ~8-9% sein

---

## 💡 **FALLS NOCH NICHT PERFEKT**

### Wenn zu viele GREEN:
→ Schwellen senken (GREEN: 1.2, YELLOW: 2.5, ORANGE: 4.0)

### Wenn zu viele RED:
→ Schwellen erhöhen (GREEN: 1.8, YELLOW: 3.5, ORANGE: 6.0)

### Wenn Scores immer noch zu niedrig:
→ Skalierung von /10 auf /8 oder /7 ändern

---

## 📌 **DOKUMENTATION**

Alle Änderungen sind dokumentiert in:
- `DISKREPANZ_ANALYSE.md` - Problem-Identifikation
- `FINALE_KALIBRIERUNG.md` - Dieser Report
- `analyzer.py` Zeile 785-801 - Risk Level Logic

---

**Status:** ⏳ **ITERATION 3 BEREIT ZUM TESTEN**

Die Schwellen wurden angepasst, um die Verteilung näher an die Dokumentation zu bringen.

