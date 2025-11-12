# CLARA - Web UI Anleitung

## Überblick

Das CLARA Transaction Analysis System verfügt jetzt über eine moderne Web-Benutzeroberfläche für einfache CSV-Uploads und automatische Analysen.

## Features

✅ **Modernes UI** - Schönes, benutzerfreundliches Interface mit Drag & Drop  
✅ **CSV-Upload** - Einfaches Hochladen von Transaktionsdaten  
✅ **Automatische Analyse** - Sofortige Verarbeitung nach Upload  
✅ **Markierte CSV-Ausgabe** - Automatische Generierung einer analysierten CSV mit allen Markierungen  
✅ **Logging** - Alle Aktionen werden in `logs/` gespeichert  
✅ **Download-Funktion** - Direkter Download der analysierten CSV-Datei

## Schnellstart

### 1. Server starten

```bash
python main.py
```

Der Server läuft auf: **http://localhost:8000**

### 2. Web-UI öffnen

Öffne deinen Browser und gehe zu: **http://localhost:8000**

### 3. CSV hochladen

- Klicke auf die Upload-Fläche oder ziehe eine CSV-Datei per Drag & Drop
- Unterstütztes Format: Deutsches CSV mit Spalten:
  - `Kundennummer`
  - `Unique Transaktion ID`
  - `Vollständiger Name`
  - `Auftragsvolumen`
  - `In/Out`
  - `Art`
  - `Timestamp`
  - `Uhrzeit`

### 4. Analyse starten

- Klicke auf "Analyse starten"
- Der Fortschritt wird angezeigt
- Nach Abschluss siehst du die Ergebnisse:
  - Anzahl GREEN/YELLOW/ORANGE/RED Kunden
  - Gesamtzahl analysierter Kunden

### 5. CSV herunterladen

- Klicke auf "Analysierte CSV herunterladen"
- Die Datei enthält alle ursprünglichen Transaktionen plus:
  - `Risk_Level` - GREEN, YELLOW, ORANGE, RED
  - `Suspicion_Score` - Verdachtswert (0-10)
  - `Flags` - Alle erkannten Probleme
  - `Threshold_Avoidance_Ratio_%` - Schwellenvermeidung in %
  - `Cumulative_Large_Amount` - Kumulative große Beträge
  - `Temporal_Density_Weeks` - Zeitliche Dichte
  - `Layering_Score` - Geldwäsche-Score
  - `Entropy_Complex` - Entropie-Komplexität
  - `Trust_Score` - Vertrauenswert

## Verzeichnisstruktur

```
Black Box/
├── templates/
│   └── index.html          # Web-UI
├── logs/                   # Alle Log-Dateien
│   └── clara_YYYYMMDD.log
├── output/                 # Generierte CSV-Dateien
│   └── Analyzed_Trades_*.csv
└── main.py                 # FastAPI Server
```

## API-Endpunkte

### Web-UI
- `GET /` - Hauptseite mit Upload-Interface

### CSV-Analyse
- `POST /api/analyze/csv-upload` - Upload & Analyse
  - Input: CSV-Datei (multipart/form-data)
  - Output: JSON mit Zusammenfassung und Dateinamen

### Download
- `GET /api/download/{filename}` - Download der analysierten CSV

### Legacy-Endpunkte (weiterhin verfügbar)
- `POST /api/analyze/csv` - Ursprünglicher CSV-Upload
- `GET /api/statistics` - System-Statistiken
- `GET /api/flagged-customers` - Auffällige Kunden

## Logs

Alle Aktivitäten werden protokolliert in:
- **logs/clara_YYYYMMDD.log**

Logs enthalten:
- CSV-Upload-Informationen
- Anzahl geparster Transaktionen
- Anzahl analysierter Kunden
- Fehler und Warnungen
- Download-Aktivitäten

## Ausgabe-CSV

Die generierte CSV enthält:

### Original-Spalten
Alle Spalten aus der hochgeladenen CSV bleiben erhalten.

### Neue Analyse-Spalten
- **Risk_Level**: GREEN, YELLOW, ORANGE, RED
- **Suspicion_Score**: Verdachtswert (0-10+)
- **Flags**: Alle erkannten Probleme (z.B. "SMURFING | GELDWAESCHE")
- **Threshold_Avoidance_Ratio_%**: Schwellenvermeidung in %
- **Cumulative_Large_Amount**: Summe großer Transaktionen (>9500€)
- **Temporal_Density_Weeks**: Transaktionsdichte pro Woche
- **Layering_Score**: Geldwäsche-Verdachtswert (0-1)
- **Entropy_Complex**: "Ja" bei komplexem Transaktionsverhalten
- **Trust_Score**: Vertrauenswert (0-1, höher = vertrauenswürdiger)

## Beispiel-Workflow

1. **Upload**: `Trades_20251112.csv` (3000 Transaktionen)
2. **Analyse**: ~5-10 Sekunden
3. **Ausgabe**: `Analyzed_Trades_20251112_140231.csv`
4. **Log**: `logs/clara_20251112.log`

## Fehlerbehandlung

Das System behandelt automatisch:
- ✅ Verschiedene CSV-Encodings (UTF-8, Windows-1252, etc.)
- ✅ Fehlende oder ungültige Zeilen
- ✅ Datum/Uhrzeit-Format-Variationen
- ✅ Kommas in Beträgen (z.B. "1.234,56€")

## Sicherheit

- Nur CSV-Dateien werden akzeptiert
- Downloads sind auf das `output/`-Verzeichnis beschränkt
- Alle Eingaben werden validiert
- Fehler werden sicher behandelt und geloggt

## Performance

- **Upload**: < 1 Sekunde
- **Analyse**: ~0.5-2 Sekunden pro 1000 Transaktionen
- **CSV-Generierung**: < 1 Sekunde

## Unterstützung

Bei Problemen:
1. Prüfe die Logs in `logs/`
2. Stelle sicher, dass das CSV-Format korrekt ist
3. Prüfe die Konsolen-Ausgabe des Servers

