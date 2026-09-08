# Betriebsdokumentation – Care for Plants

Stand: 07.09.2026 · Verantwortlich: Tristan Stracke (Rolle Entwickler) ·
Projekt ISEF01, IU Internationale Hochschule

---

## 1 Zweck und Geltungsbereich

Dieses Dokument beschreibt, wie die Webanwendung *Care for Plants* betrieben
wird: welche Umgebung sie benötigt, wie sie von null in Betrieb genommen
wird, was bei einer Veröffentlichung geschieht, wie der Datenbestand
gesichert und wiederhergestellt wird und wie auf die zu erwartenden
Störungen zu reagieren ist.

Es richtet sich an zwei Gruppen: an das Projektteam, das die Anwendung
während der Laufzeit betreibt, und an den Tutor, der sie prüft, ohne etwas
zu installieren. Nicht Gegenstand sind die fachlichen Abläufe der Anwendung
(siehe Benutzerhandbuch) und der innere Aufbau der Software (siehe
technische Dokumentation).

Der Geltungsbereich umfasst die Umgebung, die während der Projektlaufzeit
betrieben wird. Ein Betrieb über die Projektlaufzeit hinaus, ein
Mehrbenutzerbetrieb mit echten personenbezogenen Daten und ein
Bereitschaftsdienst sind ausdrücklich nicht vorgesehen; an den Stellen, an
denen daraus eine bewusste Abweichung von üblicher Betriebspraxis folgt,
ist das vermerkt.

---

## 2 Systemüberblick und Laufzeitumgebung

**Öffentliche Adresse:** https://studienprojekt-isef01.up.railway.app

Die Anwendung ist ein Django-Monolith, der serverseitig HTML erzeugt. Es
gibt keinen getrennten Frontend-Dienst, keine API für Dritte und keine
Hintergrundprozesse. Daraus folgt der Betriebsaufbau: **ein** Dienst, **eine**
Datenbankdatei, **ein** Veröffentlichungsweg.

| Baustein | Umsetzung | Begründung |
|---|---|---|
| Anwendungsserver | Gunicorn, gebunden an `0.0.0.0:$PORT` | Von Railway vorgegebener Port, derzeit 8080 |
| Webrahmenwerk | Django 5.2.17 (Python 3.12) | Rahmenwerk laut MS 3 |
| Datenbank | SQLite, Datei auf einem Volume | Zwei Anwendungsfälle, wenige Nutzer; ein Datenbankdienst wäre für diesen Zuschnitt Aufwand ohne Nutzen |
| Statische Dateien | WhiteNoise, komprimiert | Erspart einen zweiten Webserver |
| Plattform | Railway | Kostenlos bzw. günstig, ohne Installation erreichbar, Volume verfügbar |
| Quellcode | GitHub, Zweig `main` | Nur `main` wird veröffentlicht |

Der Startbefehl steht im `Procfile` und führt drei Schritte in fester
Reihenfolge aus:

```
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi --bind 0.0.0.0:$PORT
```

Die Migrationen laufen damit bei jedem Start. Das ist bewusst so gewählt:
Ein vergessener manueller Migrationsschritt wäre die wahrscheinlichste
Ursache für einen Ausfall nach einer Veröffentlichung. Der Preis dieser
Entscheidung ist, dass eine fehlerhafte Migration den Start verhindert; bei
einem Team von drei Personen und einer Laufzeit von vier Wochen ist das
Risiko geringer als das des vergessenen Schrittes.

---

## 3 Konfiguration

Alles, was sich zwischen lokaler Entwicklung und Produktion unterscheidet,
kommt aus Umgebungsvariablen. Es gibt genau eine Einstellungsdatei
(`config/settings.py`); getrennte Dateien je Umgebung laufen erfahrungsgemäß
auseinander.

| Variable | Wirkung | Produktion | Lokal |
|---|---|---|---|
| `SECRET_KEY` | Signaturschlüssel von Django | **muss gesetzt sein**, langer Zufallswert | wird bei `DEBUG=1` je Start neu erzeugt |
| `DEBUG` | Fehlersuchmodus | nicht gesetzt bzw. `False` | `DEBUG=1` |
| `DATA_DIR` | Verzeichnis der Datenbankdatei | `/data` (Volume) | leer, dann Projektverzeichnis |
| `RAILWAY_PUBLIC_DOMAIN` | öffentliche Adresse | von Railway automatisch gesetzt | entfällt |

Derzeit gesetzt sind auf Railway `SECRET_KEY`, `DEBUG=False` und
`DATA_DIR=/data`. `DEBUG=False` ist technisch entbehrlich, da die Anwendung
ohne die Variable ohnehin im Produktionsmodus startet; der Eintrag bleibt,
weil er die Absicht sichtbar macht.

**Fail-Safe-Verhalten.** Beide sicherheitsrelevanten Schalter sind so
voreingestellt, dass ein Fehler zum Startabbruch führt und nicht zu einer
laufenden, aber offenen Anwendung: `DEBUG` ist ohne Variable *aus*, und
fehlt bei ausgeschaltetem `DEBUG` der `SECRET_KEY`, bricht der Start mit
`ImproperlyConfigured` ab. Eine Anwendung, die mit eingeschaltetem
Fehlersuchmodus im Netz steht, gibt Einstellungen und Datenbankinhalte
preis; ein abgebrochener Start ist der deutlich harmlosere Fehler.

**Lokale Entwicklung.** Eine Datei `.env` im Projektverzeichnis wird beim
Start eingelesen; bereits gesetzte Umgebungsvariablen behalten Vorrang.
Vorlage ist `.env.example`:

```
cp .env.example .env
```

**Sicherheitseinstellungen bei ausgeschaltetem `DEBUG`:** Weiterleitung auf
HTTPS, Cookies nur über HTTPS, `X-Frame-Options: DENY`, HSTS mit einer
Stunde. Die kurze HSTS-Dauer ist eine bewusste Abweichung: Ein üblicher Wert
von einem Jahr würde den Browser der Prüfenden auch dann auf HTTPS
festlegen, wenn die Anwendung später unter einer anderen Adresse läuft.

---

## 4 Inbetriebnahme von null

Der Fall tritt ein, wenn die Umgebung neu aufgesetzt wird oder der
Datenbestand verloren ist. Alle Schritte sind wiederholbar.

1. **Dienst anlegen** und mit dem GitHub-Repository verbinden, Zweig `main`.
2. **Volume einhängen**, Mount Path `/data`, Größe 500 MB.
3. **Variablen setzen:** `SECRET_KEY` (langer Zufallswert), `DATA_DIR=/data`.
   Einen Schlüssel erzeugt:
   `python -c "import secrets; print(secrets.token_urlsafe(64))"`
4. **Veröffentlichen** (Push auf `main` oder `railway up`). Migrationen und
   das Einsammeln der statischen Dateien laufen beim Start automatisch.
5. **Stammdaten laden** – der Pflanzenkatalog:
   `railway run python manage.py loaddata pflanzenarten`
6. **Zugänge und Testdaten anlegen:**
   `railway run python manage.py testdaten`

Schritt 6 legt den Administrator und die vier Testzugänge an (Abschnitt 7).
Das Kommando ist mehrfach ausführbar, ohne Daten zu verdoppeln.

---

## 5 Regelbetrieb und Veröffentlichung

Veröffentlicht wird ausschließlich über die Pipeline in
`.github/workflows/ci.yml`. Ein Push auf `main` löst zwei Aufträge aus:

1. **Prüfung** – Ruff (Regelverstöße und Formatierung), `manage.py check`
   und `check --deploy`, danach die Testreihe mit Abdeckungsbericht.
2. **Veröffentlichung** – `railway up`, aber nur bei `needs: pruefung`,
   also erst nach vollständig bestandener Prüfung, und nur für `main`.

Damit ist die Prüfung ein **Qualitätstor**: Ein fehlgeschlagener Test
verhindert die Auslieferung. Manuelles Veröffentlichen am Tor vorbei bliebe technisch
möglich (`railway up` von einem Arbeitsplatz mit gültigem Token), ist aber
nicht vorgesehen und im Störungsfall zu vermerken. Dies ist die einzige
verbliebene Lücke im Auslieferungsweg; sie ließe sich nur schließen, indem
das Railway-Token ausschließlich der Pipeline zur Verfügung steht.

Änderungen erreichen `main` ausschließlich über Pull Requests mit Review
durch ein zweites Teammitglied. Diese Regel ist seit dem 07.09.2026 nicht
mehr nur abgesprochen, sondern technisch durchgesetzt: Ein Ruleset auf dem
Standardzweig verlangt einen Pull Request mit einer Freigabe, verlangt das
Bestehen des Statuschecks `Statische Pruefung und Tests` und verbietet
erzwungene Pushes. Ein direkter Commit auf `main` wird vom Server
abgewiesen – auch für den Eigentümer des Repositorys.

Damit fällt die Lücke weg, die zwischen einer Absprache und ihrer
Einhaltung liegt: Das Qualitätstor aus MS 3 lässt sich nicht mehr unter
Zeitdruck umgehen, und die Einhaltung ist in den Repository-Einstellungen
belegbar, statt nur behauptet zu werden.

**Was bei einer Veröffentlichung mit den Daten geschieht:** Der Container
wird ersetzt, das Volume bleibt bestehen. Da die Datenbankdatei unter
`/data` liegt, überlebt der Datenbestand jede Veröffentlichung. Läge sie im
Container, wäre sie jedes Mal leer – dies ist der wichtigste Einzelpunkt
dieses Dokuments.

---

## 6 Datenhaltung, Sicherung, Wiederanlauf

**Ablage.** Eine Datei, `/data/db.sqlite3`, auf einem dauerhaften Volume.
Hochgeladene Dateien gibt es nicht; die Anwendung speichert ausschließlich
Text und Zahlen.

**Sicherung.** Eine Kopie der Datenbankdatei genügt:

```
railway run python -c "import shutil,datetime; shutil.copy('/data/db.sqlite3', '/data/sicherung-' + datetime.date.today().isoformat() + '.sqlite3')"
```

**Bewusste Abweichung.** Ein automatischer Sicherungslauf ist nicht
eingerichtet. Dafür gibt es zwei Gründe. Erstens bietet Railway
Volume-Sicherungen und Point-in-Time-Recovery ausschließlich im Pro-Tarif
an; das Projekt wird auf dem darunterliegenden Tarif betrieben, weil die
höhere Stufe für vier Wochen Laufzeit nicht zu rechtfertigen wäre.
Zweitens besteht der Datenbestand ausschließlich aus Testdaten, die sich
mit `manage.py testdaten` in einem Befehl wiederherstellen lassen – der
Wiederanlauf dauert kürzer als das Einspielen einer Sicherung.

Diese Abwägung ist an den Zuschnitt des Projekts gebunden. Sobald echte
Nutzerdaten entstünden, wäre sie nicht haltbar: Dann wären entweder der
Pro-Tarif oder ein Wechsel auf einen Datenbankdienst mit eigener Sicherung
erforderlich.

**Wiederanlauf nach Datenverlust.** Stammdaten laden, Testdaten anlegen –
die Schritte 5 und 6 aus Abschnitt 4. Dauer wenige Minuten.

---

## 7 Zugänge

| Zugang | Kennwort | Zweck |
|---|---|---|
| `admin` | `Pflanze-Admin-2026` | Administrationsoberfläche unter `/admin/` |
| `tutor` | `Pflanze-Test-2026` | Prüfzugang mit Standorten, Pflanzen und Pflegeaufgaben |
| `tutor-neu` | `Pflanze-Test-2026` | Prüfzugang ohne Daten, für den Einstieg von null |
| `kai` | `Pflanze-Test-2026` | Testzugang mit Standorten, Pflanzen und Pflegeaufgaben |
| `kai-neu` | `Pflanze-Test-2026` | Testzugang ohne Daten, für den Einstieg von null |
| `kilian` | `Pflanze-Test-2026` | wie `kai` |
| `kilian-neu` | `Pflanze-Test-2026` | wie `kai-neu` |

Die Zugänge des Tutors sind bewusst von denen des Teams getrennt: So bleibt
seine Prüfung von Änderungen des Teams unberührt, und umgekehrt kann er
nichts verändern, was für die Nachvollziehbarkeit noch gebraucht wird.

Die bestückten Zugänge enthalten drei Standorte, drei Pflanzen im Bestand,
zwei auf der Wunschliste sowie Pflegeaufgaben, die auf alle vier Gruppen des
Kalenders verteilt sind – überfällig, heute, diese Woche, danach. Die
Fälligkeiten werden bei jeder Ausführung des Kommandos neu auf den
Ausführungstag bezogen, damit auch Wochen später noch etwas zu prüfen ist.

**Bewusste Abweichung.** Die Kennwörter stehen im Klartext im Quelltext
(`plants/management/commands/testdaten.py`) und in dieser Dokumentation. Für
einen Produktivbetrieb wäre das unzulässig. Hier handelt es sich um eine
Demonstrationsumgebung ohne echte personenbezogene Daten, und die
Prüfungsordnung verlangt, dass der Tutor die Anwendung ohne Rückfrage
bedienen kann. Die Zugänge sind nach Abschluss der Bewertung zu löschen.

**Kennwort vergessen.** Die Anwendung verschickt keine E-Mails; die
Nachricht zum Zurücksetzen wird in das Protokoll geschrieben. Der
Administrator kann den Link dort ablesen (Reiter *Deployments* → *Logs*)
oder das Kennwort direkt setzen:

```
railway run python manage.py changepassword <benutzername>
```

---

## 8 Störungen und Behebung

| Beobachtung | Ursache | Behebung |
|---|---|---|
| Start bricht ab, `ImproperlyConfigured: SECRET_KEY ist nicht gesetzt` | Variable fehlt oder wurde gelöscht | `SECRET_KEY` setzen und erneut veröffentlichen |
| Anwendung antwortet mit `DisallowedHost` | Adresse geändert, `RAILWAY_PUBLIC_DOMAIN` passt nicht | Domain in Railway prüfen; sie wird automatisch in `ALLOWED_HOSTS` übernommen |
| Seite ohne Gestaltung | `collectstatic` fehlgeschlagen | Protokoll der Veröffentlichung lesen; tritt lokal ohne `collectstatic` als Warnung auf und ist dort ohne Bedeutung |
| Daten nach Veröffentlichung verschwunden | `DATA_DIR` fehlt, Datei liegt im Container | `DATA_DIR=/data` setzen, Volume prüfen, Abschnitt 4 Schritte 5–6 |
| Anmeldung schlägt fehl, obwohl Kennwort stimmt | Verwechslung von lokaler Umgebung und Server; beide haben getrennte Datenbestände | Adresse prüfen |
| Anwendung nicht erreichbar, keine Fehlermeldung | Guthaben aufgebraucht oder Dienst angehalten | Tarif und Guthaben im Railway-Dashboard prüfen |

**Bekanntes Risiko: Ende des Testguthabens.** Das kostenlose Guthaben endet
am 01.10.2026, die Abgabe erfolgt am 28.09.2026. Ohne Wechsel auf einen
bezahlten Tarif wäre die Anwendung während der Bewertung nicht erreichbar,
und die Anforderung, dass der Tutor sie ohne Installation bedienen kann,
wäre verletzt. Das Team hat deshalb den Wechsel auf das kostenpflichtige
Programm beschlossen. [ANNAHME: Der Wechsel ist zum Zeitpunkt dieses Standes
noch nicht vollzogen – bitte Datum ergänzen, sobald er erfolgt ist.]

---

## 9 Grenzen des Betriebskonzepts

Zur Einordnung, was hier bewusst *nicht* geleistet wird:

- **Keine Überwachung.** Ein Ausfall fällt auf, wenn jemand die Seite
  aufruft. Für eine Anwendung mit fünf Testkonten ist das angemessen.
- **Kein Bereitschaftsdienst,** keine Reaktionszeiten, keine Eskalation.
- **Ein Dienst ohne Ausfallsicherheit.** SQLite auf einem Volume lässt sich
  nicht auf mehrere Instanzen verteilen. Für den Prototyp ist das richtig;
  bei wachsender Nutzerzahl wäre der Wechsel auf PostgreSQL der erste
  Schritt, und die Anwendung ist darauf vorbereitet, weil ausschließlich
  der ORM von Django verwendet wird.
- **Kein Postausgang.** Das Zurücksetzen von Kennwörtern läuft über das
  Protokoll und den Administrator.

[EIGENE EINSCHÄTZUNG: Hier gehört ein Satz hin, was du im Betrieb dieser
vier Wochen tatsächlich als lästig oder riskant empfunden hast – etwa das
manuelle Nachladen der Testdaten nach jedem Neuaufbau oder die Abhängigkeit
von einem einzigen Anbieter. Das ist der Teil, den nur du beantworten
kannst.]
