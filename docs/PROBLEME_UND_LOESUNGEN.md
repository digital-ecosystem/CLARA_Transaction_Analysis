# Probleme und Lösungen

## Problem 1: Geldwäscher werden nicht erkannt

### Problem:
- **CSV-Analyse findet:** 73 echte Geldwäscher (Bar-In + SEPA-Out)
- **Python-Analyse erkennt:** Nur 2-13 Geldwäscher (16% Erkennungsrate)
- **Layering Score:** Viele Geldwäscher haben Layering Score 0.0 in API-Analyse, aber 1.0 bei direkter Analyse

### Ursache:
1. **Schwellenwerte zu streng:** Die absoluten Schwellenwerte in `cash_to_bank_layering_detection` sind zu streng:
   - Mindestens 3 Bar-In UND 3 SEPA-Out (zu streng)
   - Bar-Investment Ratio >= 50% (zu streng)
   - Electronic-Withdrawal Ratio >= 50% (zu streng)
   - Time Proximity Score >= 50% (zu streng)
   - 3+ absolute Indikatoren erforderlich (zu streng)

2. **Transaktionsverarbeitung:** Die Transaktionen werden in der API-Analyse möglicherweise nicht richtig verarbeitet

### Lösung:
1. **Schwellenwerte reduziert:**
   - Mindestens 2 Bar-In UND 2 SEPA-Out (statt 3)
   - Bar-Investment Ratio >= 40% (statt 50%)
   - Electronic-Withdrawal Ratio >= 40% (statt 50%)
   - Time Proximity Score >= 30% (statt 50%)
   - 2+ absolute Indikatoren erforderlich (statt 3)

2. **Code angepasst:** `statistical_methods.py` - `cash_to_bank_layering_detection`

## Problem 2: Entropie-Kunden werden nicht erkannt

### Problem:
- **CSV-Analyse findet:** 153 Entropie-Kunden
- **Python-Analyse erkennt:** 0 Entropie-Kunden (0% Erkennungsrate)

### Ursache:
- Entropie-Erkennung funktioniert nicht richtig oder die Schwellenwerte sind zu streng

### Lösung:
- TODO: Entropie-Erkennung überprüfen und anpassen

## Problem 3: Smurfing-Erkennung funktioniert gut

### Status:
- **CSV-Analyse findet:** 91 Smurfing-Kunden
- **Python-Analyse erkennt:** 63 Smurfing-Kunden (105% - mehr als erwartet)
- **Erkennungsrate:** Sehr gut!

### Lösung:
- Keine Änderungen erforderlich

## Nächste Schritte:

1. ✅ **Schwellenwerte für Layering angepasst** - Implementiert
2. ⏳ **Testen ob Layering-Erkennung jetzt besser funktioniert**
3. ⏳ **Entropie-Erkennung überprüfen und anpassen**
4. ⏳ **Transaktionsverarbeitung in API-Analyse überprüfen**


