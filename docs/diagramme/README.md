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

## Rasterfassung für den Word-Bau

Word bettet SVG nicht zuverlässig ein, deshalb setzt `iu_formalia.py` in der
Wortfassung die PNG-Umsetzung ein. Diese fünf PNG liegen **mit im
Repository**, obwohl sie erzeugte Dateien sind. Die Begründung steht im
Entscheidungslog zum 15.09.2026: Die Wandlung braucht `cairosvg` und darunter
die Systembibliothek Cairo. Wer nur ein Dokument bauen will, müsste die erst
installieren – und ohne die PNG bricht der Bau ab. Die Diagramme ändern sich
im verbleibenden Projektumfang nicht mehr, der Preis für die Bequemlichkeit
ist also gering.

Ändert sich doch ein Diagramm, sind nach `diagramme_zeichnen.py` die PNG neu
zu erzeugen und mit zu committen:

    pip install cairosvg
    python3 -c "import cairosvg, glob; [cairosvg.svg2png(url=s, write_to=s[:-4]+'.png', scale=2.0) for s in glob.glob('docs/bilder/*.svg')]"

`iu_bauen.py` prüft vor dem Bau, ob zu jeder Abbildung die PNG vorliegt, und
bricht sonst mit einer Meldung ab. Ohne diese Prüfung entstünden Dokumente,
deren Abbildungsverzeichnis Einträge ohne zugehörige Abbildung enthält.
