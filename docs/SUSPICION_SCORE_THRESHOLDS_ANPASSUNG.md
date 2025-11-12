# Suspicion_Score Thresholds Anpassung

## Datum: 2025-01-12

---

## ❌ **PROBLEM**

**Zu viele ORANGE, zu wenig YELLOW:**
- ORANGE: 46.4% (1929 Transaktionen)
- YELLOW: 0.6% (27 Transaktionen) ⚠️

**Aktuelle Suspicion_Scores:**
- YELLOW: 1.35 (nur ein Wert!)
- ORANGE: 2.80-4.81
- RED: 5.58-67.18

**Laut Dokumentation sollten die Thresholds sein:**
- GREEN: 0-150 SP (Unauffällig)
- YELLOW: 150-300 SP (Leichte Auffälligkeit)
- ORANGE: 300-500 SP (Erhöhtes Risiko)
- RED: 500-1000+ SP (Hoher Verdacht)

---

## 🔍 **URSACHE**

**Problem 1: Skalierung zu klein**
- Aktuell: `suspicion_score = scaled_points / 10.0`
- Das reduziert die Scores um Faktor 10
- Beispiel: 280 SP → 28.0 Score (falsch!)

**Problem 2: Thresholds zu niedrig**
- Aktuell: GREEN < 1.0, YELLOW < 2.5, ORANGE < 5.0
- Laut Dokumentation: GREEN < 150, YELLOW < 300, ORANGE < 500

---

## ✅ **LÖSUNG**

### 1. Skalierung entfernt

**Vorher:**
```python
suspicion_score = scaled_points / 10.0
```

**Nachher:**
```python
# Laut Dokumentation: Suspicion Points werden direkt verwendet (0-1000+)
suspicion_score = scaled_points
```

### 2. Risk Level Thresholds angepasst

**Vorher:**
```python
if suspicion_score < 1.0: return RiskLevel.GREEN
elif suspicion_score < 2.5: return RiskLevel.YELLOW
elif suspicion_score < 5.0: return RiskLevel.ORANGE
else: return RiskLevel.RED
```

**Nachher:**
```python
if suspicion_score < 150: return RiskLevel.GREEN      # 0-150 SP
elif suspicion_score < 300: return RiskLevel.YELLOW   # 150-300 SP
elif suspicion_score < 500: return RiskLevel.ORANGE  # 300-500 SP
else: return RiskLevel.RED                            # >= 500 SP
```

---

## 📊 **ERWARTETE ERGEBNISSE**

### Vorher (mit falscher Skalierung):
- GREEN: 46.0% (Scores 0.00)
- YELLOW: 0.6% (Scores 1.35)
- ORANGE: 46.4% (Scores 2.80-4.81)
- RED: 6.9% (Scores 5.58-67.18)

### Nachher (mit korrekter Skalierung):
- GREEN: ~46% (Scores 0-150 SP)
- YELLOW: **~20-30%** (Scores 150-300 SP) ✅
- ORANGE: **~15-25%** (Scores 300-500 SP) ✅
- RED: ~10-15% (Scores 500+ SP)

---

## 🎯 **BEGRÜNDUNG**

**Laut Dokumentation:**
> "Die aggregierten Suspicion-Points werden auf eine standardisierte Risikoskala übertragen, die vier Zonen umfasst:
> - 0 – 150: Unauffällig
> - 150 – 300: Leichte Auffälligkeit
> - 300 – 500: Erhöhtes Risiko
> - 500 – 1000+: Hoher Verdacht"

**Die Suspicion Points werden direkt verwendet, ohne weitere Skalierung!**

---

## 📝 **IMPLEMENTIERUNG**

**Datei:** `analyzer.py`

**Änderungen:**
1. Zeile ~261: `suspicion_score = scaled_points` (statt `/10.0`)
2. Zeile ~565-572: Thresholds angepasst (150/300/500 statt 1.0/2.5/5.0)

---

## 🧪 **TEST**

**Schritte:**
1. Server neu starten (`python main.py`)
2. CSV hochladen und analysieren
3. Neue CSV prüfen:
   - YELLOW sollte ~20-30% sein (statt 0.6%)
   - ORANGE sollte ~15-25% sein (statt 46.4%)
   - Suspicion_Scores sollten im Bereich 0-1000+ sein

---

**Status:** ✅ **IMPLEMENTIERT**

**Nächster Schritt:** Server neu starten und testen

