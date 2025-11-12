# CLARA - Transaction Analysis System

Ein intelligentes System zur Erkennung von Geldwäsche-Mustern (Anti-Smurfing) und anomalem Transaktionsverhalten.

## Features

### 1. **Anti-Smurfing Detection (Weight-basiert)**
- Erkennt "Structuring": viele kleine Transaktionen statt weniger großer
- Kombiniert Transaktionshöhe und Häufigkeit intelligent
- Rollierende Zeitfenster (7, 30, 90 Tage)
- Personalisierte Baselines und Z-Score-Normalisierung

### 2. **Komplexitätsmessung (Shannon-Entropie)**
- Mehrdimensionale Entropie-Analyse:
  - Betragsprofil (Binning)
  - Zahlungsmethoden-Verteilung
  - Transaktionsarten-Verteilung
  - Zeitmuster
- Erkennt ungewöhnliche Streuung und Verschleierungsversuche

### 3. **Dynamischer Trust Score**
- Vorhersagbarkeit des Kundenverhaltens
- Vergleich mit historischem Profil
- Adaptive Response mit Recovery-Mechanismus

### 4. **Zusätzliche Statistische Methoden**
- Benford's Law (Erst-Ziffer-Analyse)
- Velocity Checks (Transaktionsgeschwindigkeit)
- Zeitreihen-Anomalie-Detektion
- Clustering von Verhaltensmustern

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

### API starten

```bash
python main.py
```

Die API läuft auf `http://localhost:8000`

### API-Dokumentation

Öffnen Sie `http://localhost:8000/docs` für die interaktive Swagger-Dokumentation.

### Endpunkte

#### 1. Einzelne Transaktion analysieren
```http
POST /api/analyze/transaction
```

#### 2. CSV-Datei analysieren
```http
POST /api/analyze/csv
```

#### 3. Kunden-Risikoprofil abrufen
```http
GET /api/customer/{customer_id}/risk-profile
```

#### 4. Alle auffälligen Kunden abrufen
```http
GET /api/flagged-customers
```

## CSV-Format

```csv
customer_id,transaction_id,customer_name,transaction_amount,payment_method,transaction_type,timestamp
CUST001,TXN001,Max Mustermann,1500.00,Bar,investment,2024-01-15 10:30:00
```

Felder:
- `customer_id`: Eindeutige Kunden-ID
- `transaction_id`: Eindeutige Transaktions-ID
- `customer_name`: Kundenname
- `transaction_amount`: Betrag in EUR
- `payment_method`: Bar, SEPA, Kreditkarte
- `transaction_type`: investment, auszahlung
- `timestamp`: Zeitstempel (optional)

## Risiko-Levels

- **GREEN** (0-1.5): Kein Verdacht
- **YELLOW** (1.5-2.5): Leichte Auffälligkeiten
- **ORANGE** (2.5-3.5): Erhöhtes Risiko, Nachweise empfohlen
- **RED** (>3.5): Hoher Verdacht, Nachweise erforderlich

## Architektur

```
├── main.py                  # FastAPI Application
├── models.py                # Pydantic Data Models
├── analyzer.py              # Hauptanalyse-Engine
├── weight_detector.py       # Anti-Smurfing Weight-Berechnung
├── entropy_detector.py      # Shannon-Entropie
├── trust_score.py           # Trust Score Berechnung
├── statistical_methods.py   # Zusätzliche Methoden
└── requirements.txt         # Dependencies
```

## Beispiel

```python
import requests

# CSV hochladen
with open('transactions.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze/csv',
        files={'file': f}
    )

results = response.json()
for customer in results['flagged_customers']:
    print(f"{customer['customer_id']}: {customer['risk_level']} - {customer['suspicion_score']:.2f}")
```

## Technische Details

### Weight-Berechnung (Anti-Smurfing)

```
Weight_W = Σ (Ã_tag × F̃_tag)
```

- Ã_tag = log(1 + Summe der Beträge pro Tag)
- F̃_tag = log(1 + Anzahl Transaktionen pro Tag)
- Z-Score Normalisierung gegen Baseline

### Shannon-Entropie

```
H = -Σ p_i log(p_i)
```

Berechnet über:
- Betragsbins
- Zahlungsmethoden
- Transaktionstypen
- Zeitverteilung

### Trust Score

```
T(t) = β × T(t-1) + (1-β) × T_neu
```

Mit Vorhersagbarkeits- und Abweichungskomponenten.

## Lizenz

Proprietär - CLARA System

