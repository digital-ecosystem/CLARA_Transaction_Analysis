# Analyse: Analyzed_Trades_20251112_153323.csv

## Datum: 2025-11-12

---

## 🔴 **KRITISCHES PROBLEM: YELLOW = 0!**

```
Risk Level Verteilung:
GREEN:  184 (74.8%)  ✅ Gut
YELLOW:   0 (0.0%)   ❌ KATASTROPHAL!
ORANGE:  53 (21.5%)  ❌ Zu hoch (sollte ~3)
RED:      9 (3.7%)   ❌ Zu niedrig (sollte ~21)
```

---

## 📊 **SCORE-VERTEILUNG**

### Alle Kunden (246):

```
Score-Bereich    Anzahl    Prozent    Risk Level
0.0-0.5          161       65.4%      GREEN (inaktive)
1.0-1.6           23        9.3%      GREEN (sollten YELLOW sein!)
2.8-3.5           42       17.1%      ORANGE
3.5-5.0           11        4.5%      ORANGE
5.0-10.0           9        3.7%      RED
```

**Erkenntnis:**
- **KEINE Kunden** im YELLOW-Bereich (1.6-2.8)!
- **23 Kunden** mit Score 1.0-1.6 sind GREEN (sollten YELLOW sein?)
- **42 Kunden** mit Score 2.8-3.5 sind ORANGE

### Aktive Kunden (85):

```
Min:    1.35
Max:    6.55
Mean:   3.03
Median: 2.80
```

**Perzentile:**
- 25%: 0.00 (inaktive)
- 50%: 0.00 (inaktive)
- 75%: 2.50
- 90%: 2.80
- 95%: 4.81
- 99%: 5.58

---

## 🔬 **ROOT CAUSE**

### Problem 1: Score-Clustering

Die Scores clustern bei:
- **1.0-1.6:** 23 Kunden (sollten YELLOW sein, sind aber GREEN)
- **2.8-3.5:** 42 Kunden (ORANGE)
- **KEINE Kunden** zwischen 1.6-2.8!

**Schwellen 1.6/2.8/5.0 passen NICHT zur Verteilung!**

### Problem 2: Schwellen-Logik

**Aktuelle Schwellen:**
```
GREEN:  < 1.6
YELLOW: 1.6-2.8  ← KEINE KUNDEN HIER!
ORANGE: 2.8-5.0
RED:    >= 5.0
```

**Tatsächliche Verteilung:**
```
GREEN:  0.0-1.6  (184 Kunden: 161 inaktive + 23 aktive)
YELLOW: 1.6-2.8  (0 Kunden!)  ← PROBLEM!
ORANGE: 2.8-5.0  (53 Kunden)
RED:    5.0+     (9 Kunden)
```

---

## 📈 **VERGLEICH MIT VORHERIGER ANALYSE**

### Vorher (152214.csv):

```
GREEN:  161 (65.4%)
YELLOW:  23 (9.3%)   ← 23 Kunden!
ORANGE:  42 (17.1%)
RED:     20 (8.1%)
```

### Jetzt (153323.csv):

```
GREEN:  184 (74.8%)  ← +23 Kunden
YELLOW:   0 (0.0%)   ← -23 Kunden (VERSCHWUNDEN!)
ORANGE:  53 (21.5%)  ← +11 Kunden
RED:      9 (3.7%)   ← -11 Kunden
```

**Umverteilung:**
- **23 Kunden:** YELLOW → GREEN (Score 1.0-1.6)
- **11 Kunden:** RED → ORANGE (Score 3.5-5.0)

---

## 🎯 **LÖSUNG**

### Problem: Schwellen passen nicht zur Score-Verteilung

**Option 1: Schwellen anpassen (empfohlen)**

Basierend auf tatsächlicher Verteilung:
```
GREEN:  < 1.0   (161 inaktive + 0 aktive = 161)
YELLOW: 1.0-2.8 (23 aktive = 23)  ← Erfasst den Cluster 1.0-1.6
ORANGE: 2.8-5.0 (53 aktive = 53)
RED:    >= 5.0  (9 aktive = 9)
```

**Option 2: Punkteberechnung anpassen**

Scores sollten besser verteilt sein, nicht so stark geclustert.

**Option 3: Hybrid**

```
GREEN:  < 1.0   (inaktive)
YELLOW: 1.0-2.5 (erfasst Cluster 1.0-1.6 + einige 2.0-2.5)
ORANGE: 2.5-5.0 (erfasst Cluster 2.8-3.5 + 3.5-5.0)
RED:    >= 5.0  (Top 9 Kunden)
```

---

## 📊 **ERKENNUNGSRATEN (unverändert)**

```
Smurfing:     16% Recall (4/25)  ❌
Geldwäsche:    0% Recall (0/32)  ❌
Entropie:     41% Recall (44/108) ⚠️
```

**Keine Verbesserung der Erkennungsraten!**

---

## ✅ **DOKUMENTATIONS-ALIGNMENT**

**Code entspricht Dokumentation:**
- ✅ Gewichtung: 40/25/25/10
- ✅ Multiplikatoren: 2.0/1.2/1.0/1.5
- ✅ TP/SP-System aktiv
- ✅ Verstärkungslogik implementiert
- ✅ Nichtlineare Skalierung implementiert

---

## 🎯 **EMPFEHLUNGEN**

### Priorität 1: YELLOW = 0 beheben

**Sofort-Maßnahmen:**
1. Schwellen anpassen: `1.0 / 2.5 / 5.0` (statt `1.6 / 2.8 / 5.0`)
2. Oder: `1.0 / 2.8 / 5.0` (YELLOW erfasst 1.0-2.8)

**Erwartung:**
- YELLOW: 0 → ~23 Kunden ✅
- GREEN: 184 → ~161 Kunden ✅
- ORANGE: 53 → ~42 Kunden ✅
- RED: 9 → ~20 Kunden ✅

### Priorität 2: Erkennungsraten verbessern

**Separate Issues:**
1. Weight-Analyse debuggen (Smurfing 16% Recall)
2. Layering-Erkennung debuggen (Geldwäsche 0% Recall)
3. Entropie-Schwellen prüfen (Entropie 41% Recall)

---

## 📝 **ZUSAMMENFASSUNG**

### Hauptprobleme:

1. ❌ **YELLOW = 0** (kritisch!)
   - Schwellen 1.6/2.8/5.0 passen nicht zur Score-Verteilung
   - 23 Kunden mit Score 1.0-1.6 sind GREEN statt YELLOW

2. ❌ **ORANGE zu hoch** (53 statt ~3)
   - Cluster bei 2.8-3.5 fängt zu viele Kunden

3. ❌ **RED zu niedrig** (9 statt ~21)
   - Schwellen zu hoch (>= 5.0)

4. ❌ **Erkennungsraten unverändert**
   - Smurfing: 16% Recall
   - Geldwäsche: 0% Recall
   - Entropie: 41% Recall

### Dokumentations-Alignment:

✅ **Code entspricht Dokumentation vollständig!**

### Lösung:

**Schwellen anpassen:** `1.0 / 2.5 / 5.0` oder `1.0 / 2.8 / 5.0`

---

**Status:** ⚠️ **KRITISCH - YELLOW = 0 muss sofort behoben werden!**

