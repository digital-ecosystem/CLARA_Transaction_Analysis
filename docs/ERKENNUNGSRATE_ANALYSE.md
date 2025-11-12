# Erkennungsrate-Analyse: Smurfer, Geldwäsche, Entropie

## Datum: 2025-11-12

---

## 🔍 **ERKENNUNGS-RATEN**

### Smurfing

```
Original (Muster):        25 Kunden
Erkannt:                  88 Kunden
True Positives:           4 Kunden
False Negatives:         21 Kunden
False Positives:         84 Kunden

Recall:                   16.0%  ❌ SEHR SCHLECHT!
Precision:                4.5%   ❌ SEHR SCHLECHT!
```

**Problem:**
- Nur **4 von 25 Smurfern** werden erkannt (16%)
- **84 False Positives** (zu viele Fehlalarme)
- **21 Smurfer werden NICHT erkannt**

**Nicht erkannte Smurfer:**
- 200226, 200012, 200027, 210012, 200204, ...

---

### Geldwäsche

```
Original (Muster):        32 Kunden
Erkannt:                  2 Kunden
True Positives:           0 Kunden
False Negatives:         32 Kunden
False Positives:         2 Kunden

Recall:                   0.0%   ❌ KATASTROPHAL!
Precision:                0.0%   ❌ KATASTROPHAL!
```

**Problem:**
- **KEIN EINZIGER** Geldwäsche-Kunde wird erkannt (0%)
- **32 Geldwäsche-Kunden** werden komplett übersehen
- **2 False Positives** (falsche Erkennung)

**Nicht erkannte Geldwäsche:**
- 210006, 200020, 200144, 200170, 200147, ...

---

### Entropie

```
Original (Muster):       108 Kunden
Erkannt:                  84 Kunden
True Positives:          44 Kunden
False Negatives:         64 Kunden
False Positives:         40 Kunden

Recall:                   40.7%  ⚠️  MITTEL
Precision:                52.4%  ⚠️  MITTEL
```

**Problem:**
- Nur **44 von 108 Entropie-Kunden** werden erkannt (41%)
- **64 Entropie-Kunden** werden übersehen
- **40 False Positives**

**Nicht erkannte Entropie:**
- 210006, 200202, 200020, 200078, 200144, ...

---

## 📊 **ZUSAMMENFASSUNG**

| Problem-Typ | Original | Erkannt | True Positives | Recall | Precision | Status |
|-------------|----------|---------|----------------|--------|-----------|--------|
| **Smurfing** | 25 | 88 | 4 | 16.0% | 4.5% | ❌ **KRITISCH** |
| **Geldwäsche** | 32 | 2 | 0 | 0.0% | 0.0% | ❌ **KATASTROPHAL** |
| **Entropie** | 108 | 84 | 44 | 40.7% | 52.4% | ⚠️ **MITTEL** |

**Gesamt:**
- **Smurfing:** 16% Recall → **84% werden NICHT erkannt!**
- **Geldwäsche:** 0% Recall → **100% werden NICHT erkannt!**
- **Entropie:** 41% Recall → **59% werden NICHT erkannt!**

---

## 🔬 **ROOT CAUSE ANALYSE**

### 1. Smurfing-Erkennung (16% Recall)

**Problem:**
- `Weight-Analyse` ist fast inaktiv (nur 1 Kunde mit `Threshold_Avoidance_Ratio > 0`)
- `is_suspicious` wird fast nie `True`
- `temporal_density_weeks` wird nicht korrekt berechnet

**Mögliche Ursachen:**
1. **Schwellen zu hoch:** `threshold_avoidance_ratio >= 0.5` ist zu streng
2. **Zeitfenster zu klein:** `recent_days=30` erfasst historische Daten nicht
3. **Berechnung fehlerhaft:** `weight_detector.py` Logik prüfen

**Empfehlung:**
- `weight_detector.py` debuggen
- Schwellen senken
- `temporal_density_weeks` Berechnung prüfen

---

### 2. Geldwäsche-Erkennung (0% Recall)

**Problem:**
- `Layering_Score` ist fast immer 0
- Nur 2 Kunden mit `Layering_Score > 0.5`
- **KEIN EINZIGER** echter Geldwäsche-Kunde wird erkannt

**Mögliche Ursachen:**
1. **Zeitfenster zu klein:** `recent_days=30` erfasst keine historischen Daten
2. **Schwellen zu hoch:** `layering_score > 0.5` ist zu streng
3. **Temporal Proximity:** SEPA-Outs liegen zu weit von Cash-Ins entfernt

**Empfehlung:**
- `statistical_methods.py` → `cash_to_bank_layering_detection()` prüfen
- Zeitfenster für Layering-Erkennung erhöhen
- Schwellen senken

---

### 3. Entropie-Erkennung (41% Recall)

**Problem:**
- **64 von 108 Entropie-Kunden** werden übersehen
- `Entropy_Complex` ist nur bei 84 Kunden `Ja`
- **40 False Positives**

**Mögliche Ursachen:**
1. **Schwellen zu hoch:** `entropy_aggregate` Schwellen zu streng
2. **Berechnung:** `entropy_detector.py` Logik prüfen
3. **Zeitfenster:** `recent_days=30` erfasst nicht alle Transaktionen

**Empfehlung:**
- `entropy_detector.py` Schwellen prüfen
- `entropy_aggregate` Berechnung verifizieren

---

## ✅ **DOKUMENTATIONS-ALIGNMENT**

### Gewichtung

**Dokumentation:**
- Weight-Analyse: 40% (Multiplikator µ = 2.0)
- Entropie-Analyse: 25% (Multiplikator µ = 1.2)
- Predictability: 25% (Multiplikator µ = 1.0)
- Statistische Methoden: 10% (Multiplikator µ = 1.5)

**Code-Implementierung (`analyzer.py`):**
- ✅ `calculate_module_points()`: Multiplikatoren korrekt (2.0/1.2/1.0/1.5)
- ✅ `_calculate_suspicion_score_tp_sp()`: Gewichtung korrekt (0.40/0.25/0.25/0.10)
- ✅ Verstärkungslogik: `apply_amplification_logic()` implementiert
- ✅ Nichtlineare Skalierung: `apply_nonlinear_scaling()` implementiert
- ✅ Finale Skalierung: `/10.0` korrekt

**Fazit:** ✅ **Code entspricht Dokumentation!**

---

## 🎯 **EMPFEHLUNGEN**

### Priorität 1: Geldwäsche-Erkennung (0% Recall!)

**Sofort-Maßnahmen:**
1. `statistical_methods.py` → `cash_to_bank_layering_detection()` debuggen
2. Zeitfenster für Layering erhöhen (nicht nur `recent_days=30`)
3. Schwellen senken (`layering_score > 0.3` statt `> 0.5`)

### Priorität 2: Smurfing-Erkennung (16% Recall)

**Sofort-Maßnahmen:**
1. `weight_detector.py` debuggen
2. `is_suspicious` Schwellen senken
3. `temporal_density_weeks` Berechnung prüfen
4. `threshold_avoidance_ratio` Schwellen senken

### Priorität 3: Entropie-Erkennung (41% Recall)

**Sofort-Maßnahmen:**
1. `entropy_detector.py` Schwellen prüfen
2. `entropy_aggregate` Berechnung verifizieren
3. Zeitfenster anpassen

---

## 📝 **ZUSAMMENFASSUNG**

### Erkennungsraten:
- ❌ **Smurfing:** 16% Recall (KRITISCH)
- ❌ **Geldwäsche:** 0% Recall (KATASTROPHAL)
- ⚠️ **Entropie:** 41% Recall (MITTEL)

### Dokumentations-Alignment:
- ✅ **Gewichtung:** Korrekt implementiert
- ✅ **Multiplikatoren:** Korrekt implementiert
- ✅ **TP/SP-System:** Aktiv und korrekt
- ✅ **Verstärkungslogik:** Implementiert
- ✅ **Nichtlineare Skalierung:** Implementiert

### Hauptproblem:
- **Code entspricht Dokumentation**, aber **Erkennungsraten sind katastrophal**
- **Weight-Analyse** und **Layering-Erkennung** funktionieren nicht richtig
- **Schwellen zu hoch** oder **Berechnungen fehlerhaft**

---

**Nächste Schritte:**
1. `weight_detector.py` debuggen
2. `statistical_methods.py` → Layering-Erkennung debuggen
3. `entropy_detector.py` Schwellen prüfen
4. Zeitfenster für historische Daten anpassen

