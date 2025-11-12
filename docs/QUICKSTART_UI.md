# CLARA Web-UI - Schnellstart

## Schritt-für-Schritt Anleitung

### 1. Server starten

Öffne ein Terminal/PowerShell-Fenster und führe aus:

```bash
cd "D:\My Progs\CLARA\Black Box"
python main.py
```

Du solltest sehen:

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     CLARA - Transaction Analysis System                      ║
║     Anti-Smurfing & Anomaly Detection                        ║
║                                                               ║
║     API läuft auf: http://localhost:8000                     ║
║     Dokumentation: http://localhost:8000/docs                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Lasse dieses Fenster offen!** Der Server läuft weiter, solange das Fenster offen ist.

### 2. Web-UI öffnen

Öffne deinen Browser (Chrome, Firefox, Edge) und gehe zu:

```
http://localhost:8000
```

Du siehst jetzt die **CLARA Web-Benutzeroberfläche**.

### 3. CSV hochladen

Es gibt zwei Möglichkeiten:

#### Option A: Drag & Drop
- Ziehe eine CSV-Datei direkt in den Upload-Bereich

#### Option B: Klicken & Auswählen
- Klicke auf den Upload-Bereich
- Wähle eine CSV-Datei aus (z.B. `Trades_20251110_143922.csv`)

### 4. Analyse starten

- Klicke auf den Button **"Analyse starten"**
- Ein Fortschrittsbalken zeigt den Status
- Nach wenigen Sekunden erscheinen die Ergebnisse:
  - 🟢 **GREEN**: Keine Auffälligkeiten
  - 🟡 **YELLOW**: Leichte Auffälligkeiten
  - 🟠 **ORANGE**: Mittlere Auffälligkeiten
  - 🔴 **RED**: Schwere Auffälligkeiten

### 5. CSV herunterladen

- Klicke auf **"Analysierte CSV herunterladen"**
- Die Datei wird automatisch heruntergeladen
- Öffne sie mit Excel oder einem Text-Editor

## Die analysierte CSV enthält

### Original-Spalten
Alle Spalten aus der hochgeladenen CSV bleiben erhalten.

### Neue Spalten

| Spalte | Beschreibung | Beispiel |
|--------|--------------|----------|
| `Risk_Level` | Risiko-Stufe | GREEN, YELLOW, ORANGE, RED |
| `Suspicion_Score` | Verdachtswert | 0.0 bis 10+ |
| `Flags` | Erkannte Probleme | "SMURFING \| GELDWAESCHE" |
| `Threshold_Avoidance_Ratio_%` | Schwellenvermeidung | 85.5 % |
| `Cumulative_Large_Amount` | Große Beträge (>9500€) | 25000.00 |
| `Temporal_Density_Weeks` | Transaktionen/Woche | 4.2 |
| `Layering_Score` | Geldwäsche-Score | 0.75 |
| `Entropy_Complex` | Komplexes Verhalten | Ja / Nein |
| `Trust_Score` | Vertrauenswert | 0.35 |

## CSV-Format

Das System erwartet ein **deutsches CSV-Format** mit folgenden Spalten:

```
Datum,Uhrzeit,Timestamp,Kundennummer,Unique Transaktion ID,Vollständiger Name,Auftragsvolumen,In/Out,Art
```

### Beispiel-Zeile:
```csv
03.11.2021,0.663,03.11.2021,1001,TXN_001,Max Mustermann,"9.876,54",In,Bar
```

### Spalten-Erklärung:
- **Datum**: DD.MM.YYYY (optional, wenn Timestamp vorhanden)
- **Uhrzeit**: Dezimalwert (0.663 = ~15:54 Uhr)
- **Timestamp**: DD.MM.YYYY
- **Kundennummer**: Eindeutige Kunden-ID
- **Unique Transaktion ID**: Eindeutige Transaktions-ID
- **Vollständiger Name**: Name des Kunden
- **Auftragsvolumen**: Betrag (mit Komma: "1.234,56")
- **In/Out**: "In" oder "Out"
- **Art**: "Bar", "SEPA" oder "Kredit"

## Logs prüfen

Alle Aktivitäten werden in `logs/` gespeichert:

```
logs/
└── clara_20251112.log
```

Beispiel-Log:
```
2025-11-12 14:02:31 - CLARA - INFO - CSV-Upload gestartet: Trades_20251110_143922.csv
2025-11-12 14:02:31 - CLARA - INFO - CSV erfolgreich mit windows-1252 gelesen
2025-11-12 14:02:32 - CLARA - INFO - 3000 Transaktionen erfolgreich geparst
2025-11-12 14:02:35 - CLARA - INFO - 150 Kunden analysiert
2025-11-12 14:02:35 - CLARA - INFO - Analysierte CSV gespeichert: Analyzed_Trades_20251112_140231.csv
2025-11-12 14:02:40 - CLARA - INFO - CSV-Download: Analyzed_Trades_20251112_140231.csv
```

## Ausgabe-Dateien

Alle generierten CSV-Dateien werden in `output/` gespeichert:

```
output/
├── Analyzed_Trades_20251112_140231.csv
├── Analyzed_Trades_20251112_141520.csv
└── ...
```

## Testen (Optional)

Führe den Test-Script aus (in einem **zweiten Terminal**, während der Server läuft):

```bash
python test_ui_api.py
```

Dieser prüft:
- ✅ Server-Erreichbarkeit
- ✅ Web-UI
- ✅ CSV-Upload & Analyse
- ✅ CSV-Download
- ✅ Log-Dateien

## Problemlösung

### Server startet nicht

**Problem:** Port 8000 bereits belegt

**Lösung:**
```bash
# Finde welcher Prozess Port 8000 nutzt (Windows PowerShell)
netstat -ano | findstr :8000

# Beende den Prozess (ersetze PID mit der gefundenen ID)
taskkill /PID <PID> /F
```

### CSV wird nicht akzeptiert

**Problem:** Falsches Format

**Lösung:**
- Stelle sicher, dass die CSV-Datei die deutschen Spaltennamen hat
- Prüfe, dass die Datei nicht leer ist
- Versuche, die CSV mit einem Text-Editor zu öffnen und prüfe das Format

### Analyse dauert sehr lange

**Problem:** Sehr große CSV-Datei (>10.000 Transaktionen)

**Lösung:**
- Das ist normal! Die Analyse kann bei sehr großen Dateien 30-60 Sekunden dauern
- Der Fortschrittsbalken zeigt den Status
- Schließe nicht den Browser während der Analyse

### Download funktioniert nicht

**Problem:** Datei wurde nicht gefunden

**Lösung:**
- Prüfe, ob die Datei in `output/` existiert
- Prüfe die Logs in `logs/` für Fehler
- Starte die Analyse erneut

## Support

Bei Problemen:
1. Prüfe die Logs: `logs/clara_YYYYMMDD.log`
2. Prüfe die Konsolen-Ausgabe des Servers
3. Führe `test_ui_api.py` aus, um die API zu testen

## Nächste Schritte

- Öffne die API-Dokumentation: http://localhost:8000/docs
- Lese die vollständige Dokumentation: `README_UI.md`
- Teste mit echten Daten!

