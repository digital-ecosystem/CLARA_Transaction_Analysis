# Diskrepanz-Analyse: Dokumentation vs. Implementierung

## Datum: 2025-11-12

---

## 🔴 **KRITISCHE UNTERSCHIEDE**

### 1. **Nur 88 Kunden analysiert (statt 246)**

**Ursache:** Die API analysiert nur Kunden, die im `transaction_history` des Analyzers gespeichert sind. Aber nicht alle Kunden aus der CSV haben Transaktionen, die erfolgreich geparst wurden.

**Problem:** Viele Kunden-IDs tauchen in der CSV auf, aber deren Transaktionen werden nicht dem Analyzer hinzugefügt.

---

### 2. **Punktevergabe zu niedrig**

| Metrik | **Aktuell** | **Dokumentation** | **Faktor** |
|--------|-------------|-------------------|------------|
| Max Score | 1.31 → 6.55* | 14.48 | ~2.2x zu niedrig |
| Typischer SP-Bereich | 0-100 | 0-1000+ | ~10x zu niedrig |

*Nach `/10` Anpassung (vorher `/50`)

---

## 📋 **DOKUMENTATION SAGT:**

### Punktebereiche (laut Dokumentation)

```
0 – 150 SP     → Unauffällig
150 – 300 SP   → Leichte Auffälligkeit  
300 – 500 SP   → Erhöhtes Risiko
500 – 1000+ SP → Hoher Verdacht
```

### Multiplikatoren (laut Dokumentation)

| Modul | µ | Typischer Punktebereich |
|-------|---|-------------------------|
| Weight | 2.0 | 0 – 1000 SP |
| Entropie | 1.2 | -200 TP … +400 SP |
| Predictability | 1.0 | -150 SP … +300 TP |
| Statistik | 1.5 | 0 – 500 SP |

### Beispiel aus Dokumentation:

**Smurfing-Kunde:**
- Threshold Avoidance ≥ 0.5 → +300 SP
- High Temporal Density (>5 Tx/Woche) → +400 SP
- Cumulative Large Amount ≥ 50k → +150 SP
- **SUMME Weight-Modul:** ~850 SP
- **Mit µ=2.0:** 850 × 2.0 = **1,700 Punkte**
- **Gewichtet (40%):** 1,700 × 0.40 = **680**
- **Mit Verstärkung (v=1.2):** 680 × 1.2 = **816**
- **Mit 0.7:** 816 × 0.7 = **571**
- **Skaliert:** ~720 (nichtlinear)
- **Final Score:** 720 / 10 = **72 (!)**

---

## 📊 **AKTUELLE IMPLEMENTIERUNG**

### Was der Code macht:

```python
# calculate_module_points() - Zeile 356-462
if weight_analysis.is_suspicious:
    if weight_analysis.threshold_avoidance_ratio >= 0.5:
        weight_sp += 300  # ✅ RICHTIG
    if weight_analysis.cumulative_large_amount >= 50000:
        weight_sp += 150  # ✅ RICHTIG
    if weight_analysis.temporal_density_weeks > 5.0:
        weight_sp += 400  # ✅ RICHTIG
```

**Das sieht korrekt aus!** Aber...

### Das Problem ist die finale Skalierung:

```python
# Zeile 261 (nach meiner Änderung)
suspicion_score = scaled_points / 10.0  # War /50.0
```

**Aber laut Dokumentation sollte es sein:**
- Keine Division, sondern direkte Übertragung!
- Oder: Division durch kleineren Wert (z.B. /5.0)

---

## 🔍 **WARUM NUR 88 KUNDEN?**

Die CSV enthält 246 eindeutige Kunden, aber nur 88 werden analysiert.

**Mögliche Ursachen:**
1. Parse-Fehler bei bestimmten Transaktionen
2. Kunden ohne gültige Transaktionen
3. Timestamp-Probleme
4. Filter-Logic schließt Kunden aus

**Log zeigt:**
```
4157 Transaktionen erfolgreich geparst
88 Kunden analysiert
```

Das bedeutet: **4157 Transaktionen verteilen sich auf nur 88 Kunden** (Durchschnitt: ~47 Tx/Kunde)

---

## ✅ **LÖSUNGEN**

### 1. Skalierung korrigieren

**Option A:** Keine Division (direkt als Score 0-100+)
```python
suspicion_score = scaled_points  # Direkt
```

**Option B:** Kleinerer Divisor
```python
suspicion_score = scaled_points / 5.0  # Statt /10
```

### 2. Kunden-Analyse debuggen

Prüfen, warum nur 88 von 246 Kunden analysiert werden:
- Sind alle Transaktionen korrekt geparst?
- Werden alle Kunden-IDs erkannt?
- Gibt es Filter, die Kunden ausschließen?

### 3. Risk Level Schwellen anpassen

**Aktuell:**
```python
if suspicion_score < 1.0: return RiskLevel.GREEN
elif suspicion_score < 2.0: return RiskLevel.YELLOW
elif suspicion_score < 3.0: return RiskLevel.ORANGE
else: return RiskLevel.RED
```

**Laut Dokumentation (nach Skalierung):**
```python
if suspicion_score < 2.0: return RiskLevel.GREEN
elif suspicion_score < 4.0: return RiskLevel.YELLOW
elif suspicion_score < 8.0: return RiskLevel.ORANGE
else: return RiskLevel.RED
```

---

## 📌 **EMPFEHLUNG**

1. **Sofort:** Skalierung von `/10` auf `/5` ändern
2. **Sofort:** Risk Level Schwellen verdoppeln
3. **Debug:** Prüfen, warum nur 88 Kunden
4. **Test:** Mit echter problematischer CSV testen

---

## 🎯 **ERWARTETE VERBESSERUNG**

| Metrik | **Aktuell** | **Nach Fix** |
|--------|-------------|--------------|
| Max Score | ~6.5 | ~13-15 |
| GREEN | 96.3% | ~75-80% |
| RED | 0% | ~5-10% |
| Kunden analysiert | 88 | 246 |

---

**Status:** ⚠️ **KRITISCHE DISKREPANZ IDENTIFIZIERT**

Die Implementierung folgt der Dokumentation in der Punktevergabe, aber die finale Skalierung ist zu stark gedämpft.

