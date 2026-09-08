# Care for Plants

Webanwendung zur Unterstützung privater Nutzender bei Auswahl und Pflege von
Pflanzen. Studienprojekt im Kurs ISEF01 (Projekt Software Engineering) an der
IU Internationalen Hochschule.

Umgesetzt sind zwei Anwendungsfälle:

- **UC1** Standorte anlegen, Pflanzen-Wunschliste führen, Eignung einer Pflanze
  für einen Standort prüfen
- **UC2** Pflegeaufgaben je Pflanze mit Intervall, Kalenderansicht, Abhaken

## Technischer Überblick

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

cp .env.example .env               # ohne DEBUG=1 bricht der Start ab

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Die Anwendung läuft anschließend unter http://127.0.0.1:8000/, die
Administrationsoberfläche unter http://127.0.0.1:8000/admin/.

## Prüfungen

```bash
pytest                             # Tests (laufen mit abgeschaltetem Fehlersuchmodus)
pytest --cov=plants                # Tests mit Abdeckungsmessung
ruff check .                       # statische Pruefung
ruff format .                      # Formatierung
python manage.py check --deploy    # Konfigurationspruefung fuer die Produktion
```

Dieselben Schritte laufen bei jedem Push in GitHub Actions. Schlägt einer fehl,
lässt sich der Pull Request nicht zusammenführen.

## Umgebungsvariablen

| Variable | Bedeutung | lokal | Produktion |
|---|---|---|---|
| `DEBUG` | Fehlersuchmodus | `1` setzen | nicht setzen |
| `SECRET_KEY` | Signaturschlüssel von Django | wird bei `DEBUG=1` je Start zufällig erzeugt | **muss gesetzt sein** |
| `DATA_DIR` | Verzeichnis der Datenbankdatei | nicht gesetzt | `/data` (Volume) |
| `RAILWAY_PUBLIC_DOMAIN` | öffentliche Adresse | nicht gesetzt | von Railway gesetzt |

Beide Schalter sind bewusst sicher voreingestellt: Ist `DEBUG` nicht gesetzt,
gilt der Produktionsbetrieb, und ohne `SECRET_KEY` startet die Anwendung dann
gar nicht erst. Eine vergessene Variable führt so zu einem sichtbaren Fehler
statt zu einer laufenden, aber offenen Anwendung. Lokal genügt `DEBUG=1`; der
Schlüssel wird dann bei jedem Start neu erzeugt und kann nicht versehentlich
in eine Produktionsumgebung geraten.

Das Zurücksetzen vergessener Kennwörter verschickt eine E-Mail. Ein
Postausgangsserver ist für den Prototyp nicht vorgesehen, deshalb schreibt die
Anwendung die Nachricht in das Protokoll; bei Railway steht sie unter *Logs*.
Der Administrator kann den enthaltenen Link von dort weitergeben.

`DATA_DIR` ist die wichtigste Variable im Betrieb: Ohne sie liegt die
Datenbankdatei im Container und ist nach jeder Veröffentlichung leer.

## Aufbau

```
config/     Projekteinstellungen, Adressen auf oberster Ebene
plants/     Fachliche Anwendung
  models.py    Datenmodell
  eignung.py   Regeln der Eignungsprüfung, ohne Datenbankbezug
  admin.py     Administrationsoberfläche
tests/      Tests der Fachlogik, ohne Datenbank lauffähig
templates/  Gemeinsame Vorlagen
```

## Dokumentation

Datenmodell, Entscheidungslog und die Erläuterungen zu einzelnen Codestellen
liegen im übergeordneten Projektordner und wandern mit dem nächsten Schritt
nach `docs/`.
