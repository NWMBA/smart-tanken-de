(German below)

🚀 Smart-Tanken DE API
Fuel Intelligence & Logistics Benchmarking for the German Market
Smart-Tanken DE is a high-performance FastAPI wrapper for the Tankerkönig fuel database. It transforms raw pricing data into actionable insights for both consumers and logistics professionals. By combining local ZIP-to-Coordinate mapping with proprietary scoring logic, it provides more than just prices—it provides decisions.

✨ Key Features
Dual-Mode Search: Search by 5-digit German ZIP code (PLZ) or precise GPS coordinates (lat/lng).

Hassle Score™ Logic: Proprietary formula that weighs fuel savings against travel distance to provide a "GO" or "WAIT" verdict.

Intraday Trend Analysis: Heuristic modeling of the German "Daily Price Wave" to predict if prices are rising or falling.

Diesel Logistics Index: A dedicated B2B endpoint for carriers to calculate fuel surcharges and regional market averages.

Ultra-Lightweight: Uses a local JSON database for coordinate mapping to ensure sub-100ms response times.

🛠️ Tech Stack
Backend: Python 3.12+, FastAPI

Data Sourcing: Tankerkönig CC-BY-4.0

Environment: Uvicorn, Python-Dotenv

Deployment Ready: Optimized for Render, Railway, or Heroku.

🚀 Quick Start
1. Prerequisites
A Tankerkönig API Key (Get one free at tankerkoenig.de)

Python 3.12 or higher

2. Installation
PowerShell
# Clone the repository
git clone https://github.com/yourusername/germanfuelapi.git
cd germanfuelapi

# Set up virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Environment Setup
Create a .env file in the root directory:

Plaintext
TANKER_API_KEY=your_actual_api_key_here
4. Run the Server
PowerShell
python -m uvicorn main:app --reload
Visit http://127.0.0.1:8000/docs to explore the interactive API documentation.

📊 API Reference
GET /smart-fuel (Consumer Insights)
Returns the top 3 best fuel deals near a location.

Params: plz OR (lat & lng), fuel_type (e5, e10, diesel), radius.

Key Feature: Returns a hassle_score and verdict.

GET /diesel-index (B2B Logistics)
Returns regional market benchmarks for commercial use.

Params: plz OR (lat & lng), radius.

Key Feature: Returns a suggested_surcharge_pct based on standard German carrier "floaters."

🔒 Security & Best Practices
Rate Limiting: Designed to respect Tankerkönig’s 1-request-per-second guideline.

Error Handling: Graceful JSON responses for invalid PLZs, empty regions, or upstream provider downtime.

Data Privacy: No user location data is stored; coordinates are processed in-memory and discarded.

📄 License
This project is open-source under the MIT License. Data is provided by Tankerkönig under CC BY 4.0.


---

🚀 Smart-Tanken DE API
Kraftstoff-Intelligenz & Logistik-Benchmarking für den deutschen Markt
Smart-Tanken DE ist ein leistungsstarker FastAPI-Wrapper für die Tankerkönig-Datenbank. Die API verwandelt rohe Preisdaten in handfeste Entscheidungshilfen für Verbraucher und Logistik-Profis. Durch die Kombination von lokaler PLZ-Zuordnung und einer eigenen Analyse-Logik bietet sie mehr als nur Preislisten – sie liefert echte Empfehlungen.

✨ Hauptfunktionen
Dualer Suchmodus: Suche über die 5-stellige Postleitzahl (PLZ) oder präzise GPS-Koordinaten (lat/lng).

Hassle Score™ Logik: Ein eigener Algorithmus, der die Ersparnis gegen die Fahrtstrecke abwägt und ein klares Urteil ("GO" oder "WAIT") fällt.

Tages-Trend-Analyse: Heuristische Modellierung der deutschen "Preiswellen", um Vorhersagen über steigende oder fallende Preise zu treffen.

Diesel-Logistik-Index: Ein spezieller B2B-Endpunkt für Speditionen zur Berechnung von Diesel-Zuschlägen und regionalen Markt-Benchmarks.

Ultra-Schnell: Nutzt eine lokale JSON-Datenbank für das Koordinaten-Mapping, um Antwortzeiten von unter 100ms zu garantieren.

🛠️ Tech Stack
Backend: Python 3.12+, FastAPI

Datenquelle: Tankerkönig CC-BY-4.0

Umgebung: Uvicorn, Python-Dotenv

Cloud-Ready: Optimiert für die Bereitstellung auf Render, Railway oder Heroku.

🚀 Schnellstart
1. Voraussetzungen
Ein Tankerkönig API-Key (kostenlos unter tankerkoenig.de)

Python 3.12 oder höher

2. Installation
PowerShell
# Repository klonen
git clone https://github.com/deinbenutzername/germanfuelapi.git
cd germanfuelapi

# Virtuelle Umgebung einrichten
python -m venv venv
.\venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
3. Konfiguration
Erstelle eine .env-Datei im Hauptverzeichnis:

Plaintext
TANKER_API_KEY=dein_tatsaechlicher_api_key
4. Server starten
PowerShell
python -m uvicorn main:app --reload
Unter http://127.0.0.1:8000/docs findest du die interaktive API-Dokumentation.

📊 API-Referenz
GET /smart-fuel (Verbraucher-Einsichten)
Liefert die 3 besten Tank-Angebote in der Nähe.

Parameter: plz ODER (lat & lng), fuel_type (e5, e10, diesel), radius.

Highlight: Gibt den hassle_score und eine Handlungsempfehlung aus.

GET /diesel-index (B2B Logistik)
Liefert regionale Markt-Benchmarks für die gewerbliche Nutzung.

Parameter: plz ODER (lat & lng), radius.

Highlight: Berechnet einen suggested_surcharge_pct (vorgeschlagener Diesel-Zuschlag) basierend auf gängigen Logistik-Standards.

🔒 Sicherheit & Best Practices
Rate Limiting: Berücksichtigt die Tankerkönig-Richtlinie (max. 1 Abfrage pro Sekunde).

Fehlerbehandlung: Saubere JSON-Antworten bei ungültigen PLZs oder Ausfällen des Datenanbieters.

Datenschutz: Es werden keine Nutzerstandorte gespeichert; Koordinaten werden nur im Arbeitsspeicher verarbeitet.

📄 Lizenz
Dieses Projekt ist Open-Source unter der MIT-Lizenz. Die Daten werden von Tankerkönig unter CC BY 4.0 bereitgestellt.