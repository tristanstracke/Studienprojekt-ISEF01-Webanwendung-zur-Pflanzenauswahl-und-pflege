# 0002 – SQLite auf dauerhaftem Volume

**Status:** angenommen · **Datum:** 2026-08-31

## Kontext

Der Datenbestand muss eine Neuveröffentlichung überstehen – andernfalls
wären die Testzugänge des Tutors nach jeder Auslieferung leer. Zu erwarten
sind wenige gleichzeitige Nutzer. Das Team hat keine Erfahrung im Betrieb
von Datenbankdiensten, und die Einrichtung soll an einem Tag zu leisten
sein.

## Geprüfte Alternativen

1. **Verwalteter PostgreSQL-Dienst bei Railway.** Ausgelegt für
   nebenläufige Schreibzugriffe, mit Sicherungen im höheren Tarif. Kostet
   einen zweiten Dienst, Zugangsdaten und eine Netzwerkverbindung, die
   ausfallen kann.
2. **SQLite im Container.** Keine Einrichtung, aber der Datenbestand wäre
   nach jeder Veröffentlichung verloren. Ausgeschlossen.
3. **SQLite auf einem eingehängten Volume.** Eine Datei an einem Ort, der
   die Veröffentlichung überdauert.

## Entscheidung

SQLite, Datenbankdatei unter `/data/db.sqlite3` auf einem eingehängten
Volume. Der Pfad kommt aus der Umgebungsvariablen `DATA_DIR`; ohne sie
liegt die Datei lokal im Projektverzeichnis.

## Begründung

Die Einschränkungen von SQLite – ein Schreibzugriff zur Zeit, keine
Verteilung auf mehrere Instanzen – treffen bei fünf Testkonten nicht zu.
Dem steht der Wegfall eines ganzen Ausfallpunkts gegenüber. Da
ausschließlich der ORM von Django verwendet wird und keine SQL-Anweisungen
von Hand geschrieben werden, wäre ein späterer Wechsel auf PostgreSQL eine
Änderung der Konfiguration und keine Änderung des Quelltextes.

## Konsequenzen

Sicherungen erfolgen nicht automatisch, sondern durch Kopieren der Datei;
Railway bietet Volume-Sicherungen erst im Pro-Tarif an. Der Datenbestand
lässt sich mit `manage.py testdaten` in einem Befehl wiederherstellen. Ein
Betrieb mit echten personenbezogenen Daten wäre auf dieser Grundlage nicht
vertretbar.
