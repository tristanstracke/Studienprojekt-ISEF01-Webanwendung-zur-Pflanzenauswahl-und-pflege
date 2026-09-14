# Diagramme

Die Diagramme der fachlichen und der technischen Dokumentation werden aus
Quelltext erzeugt und nicht von Hand gezeichnet.

    python3 diagramme/diagramme_zeichnen.py

Das Skript schreibt fünf SVG-Dateien nach `docs/bilder/`:

| Datei                 | verwendet in                                |
|-----------------------|---------------------------------------------|
| `ablauf-uc1.svg`      | fachliche Dokumentation, Anwendungsfall 1   |
| `ablauf-uc2.svg`      | fachliche Dokumentation, Anwendungsfall 2   |
| `bausteinsicht.svg`   | technische Dokumentation, Bausteinsicht     |
| `verteilungssicht.svg`| technische Dokumentation, Verteilungssicht  |
| `datenmodell.svg`     | technische Dokumentation, Datenmodell       |

`diagramm_werkzeug.py` enthält die Bausteine (Kasten, Raute, Entität, Kante)
und berechnet Kastenbreite und Kastenhöhe aus dem Text. `diagramme_zeichnen.py`
enthält das Layout der einzelnen Diagramme.

Für den Word-Bau werden die SVG in PNG gewandelt, weil Word SVG nicht
zuverlässig einbettet. Die PNG sind erzeugte Dateien und liegen deshalb nicht
im Repository.
