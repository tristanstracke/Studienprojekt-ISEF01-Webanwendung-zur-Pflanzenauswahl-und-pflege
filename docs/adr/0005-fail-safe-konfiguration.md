# 0005 – Sichere Voreinstellungen mit Startabbruch

**Status:** angenommen · **Datum:** 2026-09-04

## Kontext

Die Anwendung ist öffentlich erreichbar. Zwei Einstellungen entscheiden
darüber, ob sie sicher betrieben wird: der Fehlersuchmodus `DEBUG` und der
Signaturschlüssel `SECRET_KEY`. Beide kommen aus Umgebungsvariablen und
können fehlen – beim Neuaufsetzen der Umgebung oder nach einer
Fehlbedienung im Dashboard.

## Geprüfte Alternativen

1. **Ersatzwerte hinterlegen** (`DEBUG=True` als Vorgabe, ein fester
   Schlüssel im Quelltext). Die Anwendung startet immer. Fehlt die Variable
   in der Produktion, steht sie mit eingeschaltetem Fehlersuchmodus oder
   einem öffentlich bekannten Schlüssel im Netz.
2. **Getrennte Einstellungsdateien je Umgebung.** Verbreitet, laufen
   erfahrungsgemäß auseinander, und die Auswahl der falschen Datei bleibt
   möglich.
3. **Sichere Vorgabe und Startabbruch.** `DEBUG` ist ohne Variable
   ausgeschaltet; fehlt dann der Schlüssel, bricht der Start mit
   `ImproperlyConfigured` ab.

## Entscheidung

Sichere Vorgabe und Startabbruch. Bei eingeschaltetem `DEBUG` wird lokal
je Start ein Zufallsschlüssel erzeugt, damit die Entwicklung ohne
Einrichtung möglich bleibt.

## Begründung

Von zwei Fehlerbildern ist der abgebrochene Start das deutlich harmlosere.
Eine Anwendung mit eingeschaltetem Fehlersuchmodus gibt Einstellungen,
Abfragen und Teile des Datenbestands preis, und der Fehler fällt niemandem
auf, weil die Anwendung funktioniert. Ein Startabbruch fällt sofort auf und
benennt die Ursache im Klartext.

## Konsequenzen

Die Pipeline muss für `manage.py check` einen Schlüssel erzeugen; das ist
im Workflow umgesetzt und beim ersten Lauf zunächst übersehen worden.
Lokal wird eine `.env`-Datei beim Start eingelesen, damit `DEBUG=1` nicht
in jedem Terminalfenster von Hand zu setzen ist.
