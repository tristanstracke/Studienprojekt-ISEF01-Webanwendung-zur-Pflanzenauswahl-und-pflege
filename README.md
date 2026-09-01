# Care for Plants

Webanwendung zur Unterstuetzung privater Nutzender bei Auswahl und Pflege von
Pflanzen. Studienprojekt im Kurs ISEF01 (Projekt Software Engineering) an der
IU Internationalen Hochschule.

Umgesetzt sind zwei Anwendungsfaelle:

- **UC1** Standorte anlegen, Pflanzen-Wunschliste fuehren, Eignung einer Pflanze
  fuer einen Standort pruefen
- **UC2** Pflegeaufgaben je Pflanze mit Intervall, Kalenderansicht, Abhaken

## Technischer Ueberblick

| | |
|---|---|
| Sprache | Python 3.12 |
| Framework | Django 5.2, serverseitig gerendert |
| Datenbank | SQLite auf persistentem Volume |
| Auslieferung | Gunicorn, WhiteNoise |
| Hosting | Railway |
| Test | pytest, Ruff, GitHub Actions |

## Lokale Einrichtung

Voraussetzung ist Python 3.12 oder neuer.

```bash
git clone <repository-adresse>
cd care-for-plants

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt

cp .env.example .env               # Werte bei Bedarf anpassen
export DEBUG=True SECRET_KEY=lokaler-platzhalter

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Die Anwendung laeuft anschliessend unter http://127.0.0.1:8000/, die
Administrationsoberflaeche unter http://127.0.0.1:8000/admin/.

## Pruefungen

```bash
pytest                             # Tests
pytest --cov=plants                # Tests mit Abdeckungsmessung
ruff check .                       # statische Pruefung
ruff format .                      # Formatierung
python manage.py check --deploy    # Konfigurationspruefung fuer die Produktion
```

Dieselben Schritte laufen bei jedem Push in GitHub Actions. Schlaegt einer fehl,
laesst sich der Pull Request nicht zusammenfuehren.

## Umgebungsvariablen

| Variable | Bedeutung | lokal | Produktion |
|---|---|---|---|
| `SECRET_KEY` | Signaturschluessel von Django | Platzhalter | zufaellig erzeugt |
| `DEBUG` | Fehlersuchmodus | `True` | `False` |
| `DATA_DIR` | Verzeichnis der Datenbankdatei | nicht gesetzt | `/data` (Volume) |
| `RAILWAY_PUBLIC_DOMAIN` | oeffentliche Adresse | nicht gesetzt | von Railway gesetzt |

`DATA_DIR` ist die wichtigste Variable im Betrieb: Ohne sie liegt die
Datenbankdatei im Container und ist nach jeder Veroeffentlichung leer.

## Aufbau

```
config/     Projekteinstellungen, Adressen auf oberster Ebene
plants/     Fachliche Anwendung
  models.py    Datenmodell
  eignung.py   Regeln der Eignungspruefung, ohne Datenbankbezug
  admin.py     Administrationsoberflaeche
tests/      Tests der Fachlogik, ohne Datenbank lauffaehig
templates/  Gemeinsame Vorlagen
```

## Dokumentation

Datenmodell, Entscheidungslog und die Erlaeuterungen zu einzelnen Codestellen
liegen im uebergeordneten Projektordner und wandern mit dem naechsten Schritt
nach `docs/`.
