# Geldwäsche-Erkennung: Merkmale und Kriterien

## Aktuelle Geldwäsche-Merkmale (Layering Detection)

Das System erkennt Geldwäsche basierend auf dem klassischen **Cash-to-Bank Layering** Muster:

### 1. Absolute Schwellenwerte (2+ erforderlich):

#### Indikator 1: Anzahl Transaktionen
- **Mindestens 2 Bar-Einzahlungen (Bar-In)**
- **Mindestens 2 SEPA-Auszahlungen (SEPA-Out)**
- ❗ **PROBLEM**: Sehr niedrig - viele normale Kunden erfüllen dies

#### Indikator 2: Bar-Investment Ratio
- **>= 40% der Investments in Bar**
- ❗ **PROBLEM**: Viele Kunden investieren hauptsächlich in Bar

#### Indikator 3: Electronic Withdrawal Ratio
- **>= 40% der Auszahlungen elektronisch (SEPA/Kreditkarte)**
- ❗ **PROBLEM**: Normale Auszahlungen sind oft elektronisch

#### Indikator 4: Zeitliche Nähe (Time Proximity)
- **>= 30% der Auszahlungen haben Bar-Investments in den letzten 90 Tagen**
- ❗ **PROBLEM**: Zu weit gefasst - normale Kunden können dies erfüllen

---

## Probleme der aktuellen Erkennung

### False Positives durch:

1. **Zu niedrige Schwellenwerte**
   - 2 Bar-In + 2 SEPA-Out ist SEHR niedrig
   - Normale Sparer mit wenigen Transaktionen erfüllen dies leicht

2. **Kein Volumen-Check**
   - Kleine Beträge (z.B. 500€ Bar-In, 300€ SEPA-Out) werden gleich behandelt
   - Echte Geldwäsche involviert GROSSE Beträge

3. **Zeitfenster zu groß**
   - 90 Tage ist sehr lang
   - Normale Kunden zahlen ein und heben später ab

4. **Keine Frequenz-Prüfung**
   - Ein paar Transaktionen über Monate = normal
   - Viele Transaktionen in kurzer Zeit = verdächtig

---

## Empfohlene Verbesserungen

### 1. Höhere Mindest-Transaktionszahlen

```python
# AKTUELL (zu niedrig):
if len(bar_investments) >= 2 and len(electronic_withdrawals) >= 2:

# EMPFOHLEN:
if len(bar_investments) >= 5 and len(electronic_withdrawals) >= 3:
```

### 2. Minimales Volumen

```python
# NEU: Mindestvolumen prüfen
min_total_volume = 10000  # Mindestens 10.000€ Gesamtvolumen

bar_in_volume = sum(t.transaction_amount for t in bar_investments)
electronic_out_volume = sum(t.transaction_amount for t in electronic_withdrawals)

if bar_in_volume >= min_total_volume and electronic_out_volume >= min_total_volume * 0.5:
    # Verdächtig
```

### 3. Kürzeres Zeitfenster

```python
# AKTUELL:
if (withdrawal.timestamp - t.timestamp).days <= 90:

# EMPFOHLEN für echte Geldwäsche:
if (withdrawal.timestamp - t.timestamp).days <= 30:
# Rapid layering = Geld wird schnell "gewaschen"
```

### 4. Frequenz-Prüfung

```python
# NEU: Prüfe Transaktionsdichte
if len(bar_investments) >= 5:
    # Berechne Zeitspanne
    timestamps = [t.timestamp for t in bar_investments if t.timestamp]
    if timestamps:
        time_span_days = (max(timestamps) - min(timestamps)).days
        if time_span_days < 30:  # 5+ Transaktionen in 30 Tagen
            # SEHR verdächtig - rapid layering
```

### 5. Höhere Ratios

```python
# AKTUELL:
if bar_investment_ratio >= 0.4:  # 40%

# EMPFOHLEN:
if bar_investment_ratio >= 0.7:  # 70%
# Echte Geldwäsche = fast ALLES in Bar
```

---

## Echte Geldwäsche-Charakteristika (VBA-generiert)

Aus der VBA-Code-Analyse:

```vba
' Geldwäsche-Kunden haben:
- 8-13 Bar-In Transaktionen (mindestens 8)
- 5-8 SEPA-Out Transaktionen (mindestens 5)
- Transaktionen in ersten 90 Tagen komprimiert
- Cash-Ins in ersten 30-60 Tagen
- SEPA-Outs 20-60 Tage nach Cash-Ins
- 85-98% der Cash-Ins werden wieder ausgezahlt
- Kein normales Spar-Muster
```

---

## Zusammenfassung: Vorgeschlagene neue Schwellenwerte

```python
# NEUE SCHWELLENWERTE für Geldwäsche-Erkennung:

absolute_layering_indicators = 0

# 1. Mindestens 5 Bar-In UND 3 SEPA-Out (statt 2 und 2)
if len(bar_investments) >= 5 and len(electronic_withdrawals) >= 3:
    absolute_layering_indicators += 1

# 2. Bar-Investment Ratio >= 70% (statt 40%)
if bar_investment_ratio >= 0.7:
    absolute_layering_indicators += 1

# 3. Electronic Withdrawal Ratio >= 60% (statt 40%)
if electronic_withdrawal_ratio >= 0.6:
    absolute_layering_indicators += 1

# 4. Time Proximity: >= 50% in 30 Tagen (statt 30% in 90 Tagen)
# Kürzeres Zeitfenster, höherer Prozentsatz

# 5. NEU: Minimales Volumen >= 10.000€
if bar_in_volume >= 10000:
    absolute_layering_indicators += 1

# Wenn 3+ Indikatoren erfüllt (statt 2+)
if absolute_layering_indicators >= 3:
    # Layering erkannt
```

---

## Empfehlung

Die aktuellen Schwellenwerte sind **zu niedrig** und führen zu vielen **False Positives**.

**Nächster Schritt:**
1. Erhöhe Mindest-Transaktionszahlen auf 5 Bar-In + 3 SEPA-Out
2. Erhöhe Ratios auf 70% Bar-In, 60% SEPA-Out
3. Füge Mindestvolumen-Check hinzu (>= 10.000€)
4. Verkürze Zeitfenster auf 30 Tage
5. Erhöhe erforderliche Indikatoren auf 3 (statt 2)

Dies sollte False Positives drastisch reduzieren und nur echte Geldwäscher erkennen.

