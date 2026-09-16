# Bau der Abgabefassungen

Die Dokumentation liegt in `docs/` als Markdown. Dieselben Dateien werden an
zwei Stellen gelesen: auf GitHub beim Einstieg ins Projekt und als
Word-Dokument in der Abgabe zu Meilenstein 4. Beide Zwecke vertragen sich
nicht in einer Datei, deshalb bleibt die Quelle schlank und die Formalia der
IU werden beim Bauen aufgesetzt.

    python3 docs/bau/iu_bauen.py

Das Ergebnis liegt danach in `docs/bau/ausgabe/` als vier Word-Dateien.

Voraussetzungen sind `pandoc`, `libreoffice` (für den Zwischenschritt nach
PDF, aus dem die Seitenzahlen der Verzeichnisse abgelesen werden) und
`pdftotext`. Die Diagramme liegen als PNG im Repository und müssen nicht
erzeugt werden; `iu_bauen.py` bricht ab, falls doch eines fehlt. Siehe
`docs/diagramme/README.md`.

## Was die einzelnen Skripte tun

| Skript | Aufgabe |
|---|---|
| `iu_vorlage.py` | baut die Referenzdatei mit dem Format der IU: Arial 11, Zeilenabstand 1,5, Blocksatz, Ränder 2,00 cm, Überschriften 16/14/11 Punkt fett, DIN A4, Seitenzahl zentriert unten |
| `handbuch_bilder.py` | setzt die Bildschirmfotos an den passenden Stellen in das Benutzerhandbuch |
| `iu_formalia.py` | Beschriftungen für Abbildungen und Tabellen, Abkürzungs-, Abbildungs- und Tabellenverzeichnis, Gliederungsebenen |
| `iu_bauen.py` | ruft die drei auf, baut zweimal und trennt die Seitenzählung |

## Zwei Durchläufe

Word kann Verzeichnisse als Feld führen, das beim Öffnen aktualisiert wird.
Wird das Dokument jedoch unmittelbar nach PDF exportiert – und so geht es an
den Tutor – bleibt an dieser Stelle nur die Überschrift stehen. Die
Verzeichnisse werden deshalb mit festen Seitenzahlen geschrieben: Der erste
Durchlauf erzeugt das Dokument mit Marken, daraus entsteht ein PDF, aus dem
die tatsächlichen Seiten abgelesen werden; der zweite Durchlauf setzt die
Zahlen ein.

## Umgesetzte Vorgaben

Richtlinien für die Gestaltung wissenschaftlicher Arbeiten an der IU,
Stand 01.10.2025, Abschnitte 2 und 3.1, sowie Allgemeiner Zitierleitfaden
der IU, Abschnitt 2.2.5.

Bewusst abweichend: Quelltext und Dateinamen stehen weiterhin in einer
dicktengleichen Schrift. Die Richtlinie verlangt eine einheitliche Schriftart;
in einer technischen Dokumentation trägt die dicktengleiche Schrift jedoch
Information, weil sie Einrückung und Ausrichtung sichtbar hält und Bezeichner
vom Fließtext trennt.

## Voraussetzungen

`pandoc`, `libreoffice` (für den Zwischenexport nach PDF) und `pdftotext`
aus den Poppler-Werkzeugen.
