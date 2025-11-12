# Trust_Score Entfernung aus Suspicion_Score Berechnung

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Benutzer-Feedback:**
- "Früher hat alles gut funktioniert außer Trust_Score"
- "Dann hast du probiert die Trust_Score Berechnung anzupassen und jetzt funktioniert der Rest schlecht"
- "Kannst du vielleicht den Trust_Score komplett entfernen, weil der Suspicion_Score zeigt uns schon ob wir den Kunden vertrauen sollen"

**Aktuelle Situation:**
- GREEN: 99.3% (zu hoch!)
- YELLOW: 0% (fehlt komplett!)
- ORANGE: 0% (fehlt komplett!)
- RED: 0.7%

**Suspicion_Scores:**
- Median: 28.0 SP (zu niedrig!)
- 99. Perzentil: 79.80 SP
- Max: 671.84 SP

---

## 🔍 **URSACHE**

**Was ist passiert?**

1. **Früher:** Suspicion_Score Berechnung funktionierte gut (ohne Trust_Score)
2. **Dann:** Trust_Score wurde hinzugefügt und angepasst, um mit Risk_Level zu korrelieren
3. **Jetzt:** Suspicion_Score Berechnung funktioniert nicht mehr gut

**Mögliche Ursachen:**
- Trust_Score reduziert Suspicion_Score zu stark (durch Trust Points)
- Trust_Score Gewichtung (25%) reduziert die Gesamtpunkte
- Trust_Score-basierte Dämpfung in Verstärkungslogik reduziert Scores

---

## ✅ **LÖSUNG: Trust_Score komplett entfernen**

### Änderung 1: Trust_Score aus Module Points entfernt

**Vorher:**
```python
points['trust'] = ModulePoints(
    trust_points=trust_tp,
    suspicion_points=trust_sp,
    multiplier=1.0
)
```

**Nachher:**
```python
# Trust_Score ENTFERNT - nicht mehr verwendet
# Suspicion_Score zeigt bereits, ob dem Kunden vertraut werden soll
# Keine Trust Points mehr berechnen
```

### Änderung 2: Gewichtung angepasst (40/30/30 statt 40/25/25/10)

**Vorher:**
```python
if name == 'weight':
    weighted_points += 0.40 * suspicion_net  # 40%
elif name == 'entropy':
    weighted_points += 0.25 * suspicion_net  # 25%
elif name == 'trust':
    weighted_points += 0.25 * suspicion_net  # 25%
elif name == 'statistics':
    weighted_points += 0.10 * suspicion_net  # 10%
```

**Nachher:**
```python
if name == 'trust':
    continue  # Überspringe Trust_Score

if name == 'weight':
    weighted_points += 0.40 * suspicion_net  # 40%
elif name == 'entropy':
    weighted_points += 0.30 * suspicion_net  # 30% (statt 25%)
elif name == 'statistics':
    weighted_points += 0.30 * suspicion_net  # 30% (statt 10%)
```

### Änderung 3: Trust_Score aus Legacy-Berechnung entfernt

**Vorher:**
```python
absolute_score = (
    0.40 * smurfing_score +
    0.25 * entropy_score +
    0.25 * trust_score +      # Trust_Score
    0.10 * stats_score
) * 0.7
```

**Nachher:**
```python
absolute_score = (
    0.40 * smurfing_score +
    0.30 * entropy_score +     # Erhöht (statt 25%)
    0.30 * stats_score         # Erhöht (statt 10%)
) * 0.7
```

### Änderung 4: Verstärkungslogik angepasst

**Vorher:**
```python
# Predictability + Entropie (niedrig) = Dämpfung
if 'trust' in module_points and 'entropy' in module_points:
    if (module_points['trust'].trust_points > 100 and 
        module_points['entropy'].suspicion_points < 50):
        v *= 0.8  # Dämpfung bei dokumentierter Regelmäßigkeit
```

**Nachher:**
```python
# Trust_Score wurde entfernt - keine Dämpfung mehr basierend auf Trust
```

---

## 📊 **ERWARTETE ERGEBNISSE**

### Vorher:
- GREEN: 99.3% (Scores 0-79.80 SP)
- YELLOW: 0%
- ORANGE: 0%
- RED: 0.7% (Scores 671.84 SP)

### Nachher (erwartet):
- **GREEN: ~46%** (Scores 0-150 SP) ✅
- **YELLOW: ~20-30%** (Scores 150-300 SP) ✅
- **ORANGE: ~15-25%** (Scores 300-500 SP) ✅
- **RED: ~10-15%** (Scores 500+ SP) ✅

**Begründung:**
- Ohne Trust_Score Reduktion sollten Suspicion_Scores höher sein
- Gewichtung 40/30/30 (statt 40/25/25/10) erhöht Statistics-Gewicht (Layering!)
- Keine Trust-basierte Dämpfung mehr

---

## 📝 **IMPLEMENTIERUNG**

**Datei:** `analyzer.py`

**Änderungen:**
1. Zeile ~429-431: Trust_Score Berechnung entfernt
2. Zeile ~227-228: Trust_Score aus weighted_points entfernt
3. Zeile ~234-239: Gewichtung angepasst (40/30/30)
4. Zeile ~325-326: Trust_Score aus Legacy-Berechnung entfernt
5. Zeile ~338-342: Gewichtung angepasst (40/30/30)
6. Zeile ~494: Trust-basierte Dämpfung entfernt

---

## 🎯 **WICHTIGE PUNKTE**

1. **Trust_Score wird weiterhin berechnet** (für CSV-Ausgabe), aber **nicht mehr in Suspicion_Score verwendet**
2. **Suspicion_Score zeigt bereits Vertrauen:** Niedriger Score = Vertrauen, Hoher Score = Verdacht
3. **Gewichtung angepasst:** Statistics (Layering) hat jetzt 30% statt 10% - wichtig für Geldwäsche-Erkennung!

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

