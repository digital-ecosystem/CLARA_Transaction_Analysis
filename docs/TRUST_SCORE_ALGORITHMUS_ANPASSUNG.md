# Trust_Score Algorithmus Anpassung

## Datum: 2025-01-12
## Problem: Trust_Score korreliert nicht mit Risk_Level

---

## ❌ **GEFUNDENES PROBLEM**

### Widersprüchliche Korrelation

**Aktuelle Werte (vor Anpassung):**
- **GREEN:** Trust_Score = 0.047, Suspicion_Score = 0.00 ✅ OK
- **YELLOW:** Trust_Score = 0.823, Suspicion_Score = 1.57 ❌ **ZU HOCH!**
- **ORANGE:** Trust_Score = 0.739, Suspicion_Score = 3.45 ❌ **ZU HOCH!**
- **RED:** Trust_Score = 0.583, Suspicion_Score = 15.23 ❌ **ZU HOCH!**

**Problem:** Verdächtige Kunden (YELLOW/ORANGE/RED) haben zu hohe Trust_Scores!

**Erwartung:** Höheres Risk_Level → Niedrigerer Trust_Score

---

## ✅ **IMPLEMENTIERTE LÖSUNGEN**

### 1. **Gewichtung angepasst**

**Vorher:**
```python
t_new = (
    0.4 * predictability +              # 40%
    0.4 * (1.0 - self_deviation) +      # 40%
    0.2 * (1.0 - peer_deviation)         # 20%
)
```

**Nachher:**
```python
t_new = (
    0.25 * predictability +                      # 25% (reduziert)
    0.50 * (1.0 - self_deviation_penalty) +     # 50% (erhöht!)
    0.25 * (1.0 - peer_deviation_penalty)       # 25% (erhöht!)
)
```

**Begründung:**
- **Predictability** misst nur Vorhersagbarkeit, nicht Verdächtigkeit
- Ein Kunde kann sehr vorhersagbar sein (z.B. regelmäßiges Smurfing), aber trotzdem verdächtig
- **Self-Deviation** und **Peer-Deviation** erkennen verdächtiges Verhalten besser

---

### 2. **Nicht-lineare Bestrafung von Abweichungen**

**Vorher:**
```python
self_deviation_penalty = self_deviation
peer_deviation_penalty = peer_deviation
```

**Nachher:**
```python
self_deviation_penalty = self_deviation ** 1.5  # Quadratische Bestrafung
peer_deviation_penalty = peer_deviation ** 1.5
```

**Effekt:**
- Kleine Abweichungen: Linear bestraft
- Große Abweichungen: **Stärker bestraft** (z.B. 0.8 → 0.72, 0.9 → 0.85)
- Verdächtiges Verhalten wird stärker erkannt

**Beispiel:**
- `self_deviation = 0.5` → `penalty = 0.35` (30% Reduktion)
- `self_deviation = 0.8` → `penalty = 0.72` (10% Reduktion, aber absolut höher)

---

### 3. **Verschärfte Abweichungs-Normalisierung**

**Amount Deviation:**
- **Vorher:** `amount_deviation = min(amount_z / 3.0, 1.0)`
- **Nachher:** `amount_deviation = min(amount_z / 2.0, 1.0)`
- **Effekt:** Z-Score > 2.0 wird als sehr verdächtig betrachtet (statt > 3.0)

**Method Deviation:**
- **Vorher:** `method_deviation = min(kl_div / 2.0, 1.0)`
- **Nachher:** `method_deviation = min(kl_div / 1.5, 1.0)`
- **Effekt:** Kleinere KL-Divergenz wird bereits als verdächtig betrachtet

**Peer Deviation:**
- **Vorher:** `peer_deviation = min(peer_z / 3.0, 1.0)`
- **Nachher:** `peer_deviation = min(peer_z / 2.0, 1.0)`
- **Effekt:** Z-Score > 2.0 wird als sehr verdächtig betrachtet (statt > 3.0)

---

### 4. **Verbesserte dynamische Glättung**

**Vorher:**
```python
if t_new < 0.4:
    beta_dynamic = 0.4
elif t_new < 0.6:
    beta_dynamic = 0.6
else:
    beta_dynamic = self.beta  # 0.7
```

**Nachher:**
```python
max_deviation = max(self_deviation, peer_deviation)

if max_deviation > 0.7 or t_new < 0.3:
    beta_dynamic = 0.2  # Sehr wenig Glättung (schnelle Reaktion)
elif max_deviation > 0.5 or t_new < 0.4:
    beta_dynamic = 0.3  # Wenig Glättung
elif max_deviation > 0.3 or t_new < 0.6:
    beta_dynamic = 0.5  # Moderate Glättung
else:
    beta_dynamic = self.beta  # Normale Glättung (0.7)
```

**Vorteile:**
- **Basierend auf Abweichungen** (nicht nur T_neu)
- **Schnellere Reaktion** auf verdächtiges Verhalten
- **Weniger Glättung** bei hohen Abweichungen = verdächtiges Verhalten wird schneller erkannt

---

## 📊 **ERWARTETE ERGEBNISSE**

### Vorher (aktuell):
| Risk_Level | Trust_Score | Suspicion_Score |
|------------|-------------|-----------------|
| GREEN | 0.047 | 0.00 |
| YELLOW | **0.823** ❌ | 1.57 |
| ORANGE | **0.739** ❌ | 3.45 |
| RED | **0.583** ❌ | 15.23 |

### Nachher (erwartet):
| Risk_Level | Trust_Score | Suspicion_Score |
|------------|-------------|-----------------|
| GREEN | 0.05 - 0.80 | 0.00 |
| YELLOW | **0.30 - 0.60** ✅ | 1.0 - 2.5 |
| ORANGE | **0.20 - 0.50** ✅ | 2.5 - 5.0 |
| RED | **< 0.30** ✅ | >= 5.0 |

**Korrelation:** Höheres Risk_Level → Niedrigerer Trust_Score ✅

---

## 🔧 **TECHNISCHE DETAILS**

### Datei: `trust_score.py`

**Geänderte Methoden:**
1. `calculate_self_deviation()` - Zeile 154-183
   - Amount Deviation: `/3.0` → `/2.0`
   - Method Deviation: `/2.0` → `/1.5`

2. `calculate_peer_deviation()` - Zeile 214-222
   - Peer Deviation: `/3.0` → `/2.0`

3. `calculate_trust_score()` - Zeile 246-293
   - Gewichtung: `0.4/0.4/0.2` → `0.25/0.50/0.25`
   - Nicht-lineare Bestrafung: `^1.5`
   - Dynamische Glättung basierend auf `max_deviation`

---

## 🧪 **TEST**

**Schritte:**
1. Server neu starten (`python main.py`)
2. CSV hochladen und analysieren
3. Neue CSV-Datei prüfen
4. `analyze_trust_score.py` ausführen, um Korrelation zu überprüfen

**Erwartete Verbesserung:**
- YELLOW/ORANGE/RED Kunden sollten niedrigere Trust_Scores haben
- Bessere Korrelation zwischen Trust_Score und Risk_Level
- Weniger widersprüchliche Fälle (YELLOW mit Trust_Score > 0.7)

---

## 📝 **ZUSAMMENFASSUNG**

**Hauptänderungen:**
1. ✅ Abweichungen stärker gewichtet (50% statt 40%)
2. ✅ Nicht-lineare Bestrafung (^1.5)
3. ✅ Verschärfte Normalisierung (/2.0 statt /3.0)
4. ✅ Verbesserte dynamische Glättung (basierend auf Abweichungen)

**Ziel:** Trust_Score sollte umgekehrt zu Suspicion_Score korrelieren

---

**Status:** ✅ **IMPLEMENTIERT**

**Nächster Schritt:** Server neu starten und testen

