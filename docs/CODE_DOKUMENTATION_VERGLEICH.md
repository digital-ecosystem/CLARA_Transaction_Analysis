# Code vs. Dokumentation Vergleich

## Datum: 2025-01-12

---

## ❌ **KRITISCHES PROBLEM: Predictability-Analyse fehlt komplett!**

### Dokumentation sagt:
- **Vier Analyseebenen:**
  1. Weight-Analyse (Anti-Smurfing) - 40% Gewichtung
  2. Entropie-Analyse (Verhaltenskomplexität) - 25% Gewichtung
  3. **Predictability-Analyse (Verhaltensstabilität) - 25% Gewichtung** ⚠️
  4. Statistische Methoden - 10% Gewichtung

### Code zeigt:
- **Nur drei Analyseebenen:**
  1. Weight-Analyse - 40% Gewichtung ✅
  2. Entropie-Analyse - 30% Gewichtung ⚠️ (sollte 25% sein)
  3. **Predictability-Analyse - FEHLT KOMPLETT!** ❌
  4. Statistische Methoden - 30% Gewichtung ⚠️ (sollte 10% sein)

**Aktuelle Gewichtung im Code:**
```python
# analyzer.py, Zeile 234-239
if name == 'weight':
    weighted_points += 0.40 * suspicion_net  # ✅ KORREKT
elif name == 'entropy':
    weighted_points += 0.30 * suspicion_net  # ❌ SOLLTE 0.25 SEIN
elif name == 'statistics':
    weighted_points += 0.30 * suspicion_net  # ❌ SOLLTE 0.10 SEIN
# Predictability fehlt komplett! ❌
```

**Sollte sein (laut Dokumentation):**
```python
if name == 'weight':
    weighted_points += 0.40 * suspicion_net  # 40%
elif name == 'entropy':
    weighted_points += 0.25 * suspicion_net  # 25%
elif name == 'predictability':
    weighted_points += 0.25 * suspicion_net  # 25% - FEHLT!
elif name == 'statistics':
    weighted_points += 0.10 * suspicion_net  # 10%
```

---

## 📊 **Detaillierter Vergleich**

### 1. Gewichtung der Module

| Modul | Dokumentation | Code | Status |
|-------|---------------|------|--------|
| Weight | 40% | 40% | ✅ KORREKT |
| Entropie | 25% | 30% | ❌ FALSCH (sollte 25% sein) |
| **Predictability** | **25%** | **0% (FEHLT!)** | ❌ **KRITISCH** |
| Statistik | 10% | 30% | ❌ FALSCH (sollte 10% sein) |

**Problem:** Die fehlende Predictability-Gewichtung (25%) wurde auf Entropie (+5%) und Statistik (+20%) verteilt.

---

### 2. Multiplikatoren (µ)

| Modul | Dokumentation | Code | Status |
|-------|---------------|------|--------|
| Weight | µ = 2.0 | µ = 2.0 | ✅ KORREKT |
| Entropie | µ = 1.2 | µ = 1.2 | ✅ KORREKT |
| **Predictability** | **µ = 1.0** | **FEHLT!** | ❌ **KRITISCH** |
| Statistik | µ = 1.5 | µ = 1.5 | ✅ KORREKT |

**Code (analyzer.py, Zeile 402-452):**
```python
points['weight'] = ModulePoints(
    trust_points=weight_tp,
    suspicion_points=weight_sp,
    multiplier=2.0  # ✅ KORREKT
)

points['entropy'] = ModulePoints(
    trust_points=entropy_tp,
    suspicion_points=entropy_sp,
    multiplier=1.2  # ✅ KORREKT
)

# Predictability fehlt komplett! ❌

points['statistics'] = ModulePoints(
    trust_points=stats_tp,
    suspicion_points=stats_sp,
    multiplier=1.5  # ✅ KORREKT
)
```

---

### 3. Aggregationsformel

**Dokumentation:**
```
Gesamtpunkte = (W × 0.40) + (E × 0.25) + (P × 0.25) + (S × 0.10)
```

**Code (analyzer.py, Zeile 224-239):**
```python
# FEHLT: Predictability (P × 0.25)
weighted_points = 0.0
for name, points in module_points.items():
    if name == 'trust':
        continue  # Trust_Score entfernt (OK)
    
    suspicion_net = (points.suspicion_points - points.trust_points) * points.multiplier
    
    if name == 'weight':
        weighted_points += 0.40 * suspicion_net  # ✅
    elif name == 'entropy':
        weighted_points += 0.30 * suspicion_net  # ❌ SOLLTE 0.25 SEIN
    elif name == 'statistics':
        weighted_points += 0.30 * suspicion_net  # ❌ SOLLTE 0.10 SEIN
    # FEHLT: Predictability! ❌
```

---

### 4. Verstärkungsfaktor

**Dokumentation:**
```
v = 1 + 0.1 × (n_Module - 1)
Maximal 30% Verstärkung
```

**Code (analyzer.py, Zeile 476-480):**
```python
if n_modules > 1:
    v = 1.0 + 0.1 * (n_modules - 1)
    # Maximal 30% Verstärkung
    v = min(v, 1.3)
else:
    v = 1.0
```

**Status:** ✅ **KORREKT**

---

### 5. Absolute (70%) + Relative (30%) Aufteilung

**Dokumentation:**
- Absolute Komponenten: 70%
- Relative Komponenten: 30%

**Code (analyzer.py, Zeile 248, 264):**
```python
absolute_score = weighted_points * amplification_factor * 0.7  # ✅ 70%
# ...
total_points = absolute_score + relative_score_sp * 0.3  # ✅ 30%
```

**Status:** ✅ **KORREKT**

---

### 6. Risikozonen (Suspicion Points)

**Dokumentation:**
| Suspicion Points | Risikostufe |
|-----------------|-------------|
| 0 – 150 | Unauffällig (GREEN) |
| 150 – 300 | Leichte Auffälligkeit (YELLOW) |
| 300 – 500 | Erhöhtes Risiko (ORANGE) |
| 500 – 1000+ | Hoher Verdacht (RED) |

**Code (analyzer.py, Zeile 551-558):**
```python
if suspicion_score < 150:  # GREEN
    return RiskLevel.GREEN
elif suspicion_score < 300:  # YELLOW
    return RiskLevel.YELLOW
elif suspicion_score < 500:  # ORANGE
    return RiskLevel.ORANGE
else:  # RED (>= 500)
    return RiskLevel.RED
```

**Status:** ✅ **KORREKT**

---

### 7. Nichtlineare Skalierung

**Dokumentation:**
- 0-150 SP: Linear
- 150-300 SP: Progressiv (1.2x)
- 300-500 SP: Progressiv (1.5x)
- 500+ SP: Dämpfung (logarithmisch)

**Code (analyzer.py, Zeile 514-528):**
```python
if abs_points <= 150:
    scaled = abs_points  # Linear
elif abs_points <= 300:
    scaled = 150 + (abs_points - 150) * 1.2  # Progressiv 1.2x
elif abs_points <= 500:
    scaled = 150 + 150 * 1.2 + (abs_points - 300) * 1.5  # Progressiv 1.5x
else:
    excess = abs_points - 500
    scaled = 150 + 150 * 1.2 + 200 * 1.5 + excess * 0.8  # Dämpfung
```

**Status:** ✅ **KORREKT**

---

### 8. Predictability-Analyse - Was fehlt?

**Dokumentation beschreibt:**

**Analysebereiche:**
1. **Zeitliche Stabilität** - Konstanz der zeitlichen Abstände zwischen Transaktionen
2. **Betrags-Konsistenz** - Gleichbleibende Betragsmuster über Zeit
3. **Kanal-Kontinuität** - Wiederkehrende Nutzung etablierter Kanäle
4. **Ziel-Stabilität** - Konstanz der Empfänger und Gegenparteien

**Bewertungslogik:**
- Kurzfristig (30 Tage): spontane oder abrupte Änderungen
- Mittelfristig (90 Tage): saisonale oder zyklische Schwankungen
- Langfristig (180 Tage): strukturelle Stabilität

**Punkteverteilung:**
- **Trust Points (TP):**
  - Hohe Predictability (T ≥ 0.8) → +150 TP
  - Langfristig konstante Frequenz innerhalb SoF-Rahmens → +80 TP
- **Suspicion Points (SP):**
  - Instabiles Verhalten → -150 SP

**Multiplikator:** µ = 1.0

**Gewichtung:** 25% (zusammen mit Entropie)

---

## 🔍 **Zusammenfassung der Probleme**

### ❌ **KRITISCH:**
1. **Predictability-Analyse fehlt komplett** - 25% Gewichtung fehlt
2. **Entropie-Gewichtung falsch** - 30% statt 25%
3. **Statistik-Gewichtung falsch** - 30% statt 10%

### ✅ **KORREKT:**
1. Weight-Gewichtung (40%)
2. Multiplikatoren (Weight 2.0, Entropie 1.2, Statistik 1.5)
3. Verstärkungsfaktor (v = 1 + 0.1 × (n-1))
4. Absolute (70%) + Relative (30%) Aufteilung
5. Risikozonen (150/300/500)
6. Nichtlineare Skalierung

---

## 🎯 **Empfohlene Maßnahmen**

1. **Predictability-Analyse implementieren:**
   - Neues Modul `predictability_detector.py` erstellen
   - Analysebereiche: Zeitliche Stabilität, Betrags-Konsistenz, Kanal-Kontinuität, Ziel-Stabilität
   - TP/SP System: +150 TP bei hoher Predictability, -150 SP bei Instabilität
   - Multiplikator: µ = 1.0
   - Gewichtung: 25%

2. **Gewichtungen korrigieren:**
   - Entropie: 30% → 25%
   - Predictability: 0% → 25% (neu)
   - Statistik: 30% → 10%

3. **Aggregationsformel korrigieren:**
   ```python
   weighted_points = (
       0.40 * weight_suspicion_net +
       0.25 * entropy_suspicion_net +
       0.25 * predictability_suspicion_net +  # NEU
       0.10 * statistics_suspicion_net
   )
   ```

---

**Stand:** 2025-01-12  
**Status:** Code entspricht NICHT vollständig der Dokumentation - Predictability-Analyse fehlt!

