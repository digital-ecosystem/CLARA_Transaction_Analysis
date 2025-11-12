# Excel-Export Feature - Dokumentation

## Datum: 2025-11-12

---

## ✅ **IMPLEMENTIERT**

### Feature: Excel-Download mit Formatierung

Das System erstellt jetzt automatisch eine **formatierte Excel-Datei** (.xlsx) neben der CSV-Datei.

---

## 🎨 **FORMATIERUNG**

### Header-Zeile:
- **Hintergrund:** Blau (#4472C4)
- **Schrift:** Weiß, Fett, Größe 11
- **Ausrichtung:** Zentriert, Textumbruch
- **Rahmen:** Dünne Linien um alle Zellen

### Risk Level Spalte:
- **GREEN:** Grüner Hintergrund (#C6EFCE), Fett
- **YELLOW:** Gelber Hintergrund (#FFEB9C), Fett
- **ORANGE:** Roter Hintergrund (#FFC7CE), Fett
- **RED:** Dunkelroter Hintergrund (#FF0000), Fett

### Zahlen-Formatierung:
- **Suspicion_Score:** 2 Dezimalstellen (0.00)
- **Prozentwerte:** 1 Dezimalstelle (0.0)
- **Beträge** (Auftragsvolumen, Cumulative_Large_Amount): Tausender-Trennzeichen (#,##0.00)

### Spaltenbreiten:
- Automatisch angepasst für optimale Lesbarkeit
- Flags-Spalte: 50 Zeichen (breit für längere Texte)
- Andere Spalten: 12-25 Zeichen je nach Inhalt

### Weitere Features:
- **Header-Zeile eingefroren:** Zeile 1 bleibt beim Scrollen sichtbar
- **Rahmen:** Alle Zellen haben dünne Rahmen
- **Ausrichtung:** Linksbündig für Text, zentriert für Header

---

## 🔧 **IMPLEMENTIERUNG**

### 1. Backend (`main.py`)

**Neue Funktion: `create_excel_file()`**
- Erstellt formatierte Excel-Datei mit openpyxl
- Verwendet Workbook, Styles, Formatierung
- Speichert in `output/` Verzeichnis

**Erweiterte API:**
- `/api/download/{filename}` unterstützt jetzt `.xlsx` Dateien
- Automatische Media-Type-Erkennung

**CSV-Upload Endpoint:**
- Erstellt automatisch Excel-Datei nach CSV-Erstellung
- Gibt `excel_filename` in Response zurück

### 2. Frontend (`templates/index.html`)

**Neue UI-Elemente:**
- Excel-Download-Button neben CSV-Button
- Beide Buttons nebeneinander (48% Breite)
- Excel-Button: Grüne Farbe (#28a745)

**JavaScript:**
- Zeigt Excel-Button nur wenn `excel_filename` vorhanden
- Download-Link wird automatisch gesetzt

---

## 📋 **VERWENDUNG**

### Für Benutzer:

1. **CSV hochladen** via UI
2. **Analyse starten**
3. **Nach Analyse:**
   - **CSV-Button:** Lädt CSV-Datei herunter
   - **Excel-Button:** Lädt formatierte Excel-Datei herunter

### Excel-Datei Features:

- ✅ **Schön formatiert** - Professionelles Aussehen
- ✅ **Farbcodierung** - Risk Levels sofort erkennbar
- ✅ **Eingefrorene Header** - Bequemes Scrollen
- ✅ **Formatierte Zahlen** - Lesbare Beträge und Prozente
- ✅ **Optimale Spaltenbreiten** - Alles passt perfekt

---

## 🔍 **TECHNISCHE DETAILS**

### Abhängigkeiten:

- **openpyxl:** Python-Bibliothek für Excel-Dateien
- Automatische Erkennung: Falls nicht verfügbar, wird Excel-Export übersprungen

### Dateinamen:

- CSV: `Analyzed_Trades_YYYYMMDD_HHMMSS.csv`
- Excel: `Analyzed_Trades_YYYYMMDD_HHMMSS.xlsx`
- Beide haben denselben Zeitstempel

### Fehlerbehandlung:

- Falls openpyxl nicht verfügbar: Excel-Export wird übersprungen, CSV funktioniert weiterhin
- Falls Excel-Erstellung fehlschlägt: Warning im Log, CSV wird trotzdem erstellt

---

## 📝 **CODE-STRUKTUR**

### `create_excel_file()` Funktion:

```python
def create_excel_file(df: pd.DataFrame, output_dir: Path, timestamp: str) -> str:
    # 1. Erstelle Workbook
    # 2. Definiere Farben und Styles
    # 3. Schreibe Header (formatiert)
    # 4. Schreibe Daten (mit Formatierung)
    # 5. Passe Spaltenbreiten an
    # 6. Friere Header-Zeile ein
    # 7. Speichere Datei
    return excel_filename
```

### Formatierungs-Logik:

- **Risk Level:** Farbcodierung basierend auf Wert
- **Zahlen:** Formatierung basierend auf Spaltenname
- **Header:** Immer blau mit weißer Schrift
- **Rahmen:** Alle Zellen haben Rahmen

---

## ✅ **STATUS**

**Implementiert:** ✅
**Getestet:** ⏳ (Bereit zum Test)
**Dokumentiert:** ✅

---

**Nächste Schritte:**
1. Server neu starten
2. CSV hochladen
3. Excel-Button testen
4. Formatierung prüfen

