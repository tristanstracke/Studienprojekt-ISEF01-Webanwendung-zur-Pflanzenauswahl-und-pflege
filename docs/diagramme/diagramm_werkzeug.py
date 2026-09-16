"""
Erzeugt die Diagramme der Dokumentation als SVG.

Warum ein Generator und keine handgeschriebenen Dateien: Kastenbreite und
Kastenhoehe haengen von Textlaenge und Zeilenzahl ab. Von Hand gesetzte Masse
passen nach jeder Textaenderung nicht mehr, und genau daraus entstanden die
ueberlaufenden Beschriftungen der ersten Fassung. Hier werden die Masse
berechnet, das Layout folgt einem festen Raster.

Massgabe fuer die Lesbarkeit: Die Diagramme werden im Dokument auf etwa
15,5 cm Breite skaliert. Eine Schrift von 30 Einheiten bei einer Bildbreite
von 1500 Einheiten ergibt damit rund 9 Punkt auf dem Papier.
"""

from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "bilder"

SCHRIFT = 30  # Grundschrift im Koordinatenraum
FELD = 26  # Attributzeile im Entitaetenkasten
MARKE = 26  # Beschriftung an Kanten
ZEICHENBREITE = 0.55  # mittlere Zeichenbreite von Helvetica, Anteil der Schrift
ZEILENHOEHE = 40
FELDZEILE = 34
KOPFHOEHE = 54

KOPF = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {b} {h}" width="{b}" height="{h}"
     font-family="Helvetica, Arial, sans-serif">
  <defs>
    <marker id="pfeil" markerWidth="11" markerHeight="11" refX="9.5" refY="3.6"
            orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,7.2 L10,3.6 z" fill="#1d2b1f"/>
    </marker>
    <style>
      .kasten  {{ fill: #ffffff; stroke: #1d2b1f; stroke-width: 2.4; }}
      .betont  {{ fill: #eef1ec; stroke: #1d2b1f; stroke-width: 3.6; }}
      .raute   {{ fill: #eef1ec; stroke: #1d2b1f; stroke-width: 2.4; }}
      .rahmen  {{ fill: #fafbf9; stroke: #1d2b1f; stroke-width: 2.2;
                 stroke-dasharray: 10 7; }}
      .kopf    {{ fill: #eef1ec; stroke: #1d2b1f; stroke-width: 2.4; }}
      .txt     {{ font-size: {s}px; fill: #1d2b1f; }}
      .fett    {{ font-size: {s}px; font-weight: 700; fill: #1d2b1f; }}
      .feld    {{ font-size: {f}px; fill: #3d4a3f; }}
      .kante   {{ fill: none; stroke: #1d2b1f; stroke-width: 2.4;
                 marker-end: url(#pfeil); }}
      .linie   {{ fill: none; stroke: #1d2b1f; stroke-width: 2.4; }}
      .marke   {{ font-size: {m}px; fill: #5f6d60; }}
      .karte   {{ font-size: {m}px; font-weight: 700; fill: #1d2b1f; }}
      .rolle   {{ font-size: {m}px; fill: #5f6d60; font-style: italic; }}
    </style>
  </defs>
"""


def breite_von(zeilen, schrift=SCHRIFT, polster=48):
    """Schaetzt die noetige Breite aus der laengsten Zeile."""
    laenge = max(len(z) for z in zeilen)
    return round(laenge * schrift * ZEICHENBREITE + polster)


def kasten(cx, y, zeilen, art="kasten", breite=None, hoehe=None, radius=8, erste_fett=False):
    """Kasten mit zentriertem Text. cx ist die Mitte, y die Oberkante.

    Rueckgabe: (svg, links, rechts, unterkante)
    """
    b = breite or breite_von(zeilen)
    h = hoehe or (len(zeilen) * ZEILENHOEHE + 36)
    x = cx - b / 2
    teile = [
        f'<rect class="{art}" x="{x:.0f}" y="{y}" width="{b}" height="{h:.0f}" rx="{radius}"/>'
    ]
    start = y + h / 2 - (len(zeilen) - 1) * ZEILENHOEHE / 2 + SCHRIFT * 0.34
    for i, zeile in enumerate(zeilen):
        klasse = "fett" if (erste_fett and i == 0) else "txt"
        teile.append(
            f'<text class="{klasse}" x="{cx}" '
            f'y="{start + i * ZEILENHOEHE:.0f}" '
            f'text-anchor="middle">{zeile}</text>'
        )
    return "".join(teile), round(x), round(x + b), round(y + h)


def raute(cx, cy, text, hoehe=118):
    """Verzweigung. Rueckgabe: (svg, links, rechts, oben, unten)"""
    b = breite_von([text], polster=210)
    p = f"{cx},{cy - hoehe / 2} {cx + b / 2},{cy} {cx},{cy + hoehe / 2} {cx - b / 2},{cy}"
    svg = (
        f'<polygon class="raute" points="{p}"/>'
        f'<text class="txt" x="{cx}" y="{cy + SCHRIFT * 0.34:.0f}" '
        f'text-anchor="middle">{text}</text>'
    )
    return svg, round(cx - b / 2), round(cx + b / 2), round(cy - hoehe / 2), round(cy + hoehe / 2)


def entitaet(cx, y, titel, felder, breite):
    """Entitaet im ER-Diagramm: Kopfzeile mit Name, darunter die Attribute.

    Rueckgabe: (svg, links, rechts, unterkante)
    """
    x = cx - breite / 2
    h = len(felder) * FELDZEILE + 26
    teile = [
        f'<rect class="kopf" x="{x:.0f}" y="{y}" width="{breite}" height="{KOPFHOEHE}" rx="6"/>',
        f'<rect class="kasten" x="{x:.0f}" y="{y + KOPFHOEHE}" width="{breite}" height="{h}"/>',
        f'<text class="fett" x="{cx}" y="{y + 38}" text-anchor="middle">{titel}</text>',
    ]
    for i, feld in enumerate(felder):
        teile.append(
            f'<text class="feld" x="{x + 20:.0f}" '
            f'y="{y + KOPFHOEHE + 36 + i * FELDZEILE}">{feld}</text>'
        )
    return "".join(teile), round(x), round(x + breite), round(y + KOPFHOEHE + h)


def marke(x, y, text, anker="start", klasse="marke"):
    return f'<text class="{klasse}" x="{x:.0f}" y="{y:.0f}" text-anchor="{anker}">{text}</text>'


def kante(pfad, gerichtet=True):
    return f'<path class="{"kante" if gerichtet else "linie"}" d="{pfad}"/>'


def schreibe(name, breite, hoehe, teile):
    ZIEL.mkdir(exist_ok=True)
    inhalt = "".join(teile) if not isinstance(teile, str) else teile
    (ZIEL / name).write_text(
        KOPF.format(b=breite, h=hoehe, s=SCHRIFT, f=FELD, m=MARKE) + inhalt + "</svg>",
        encoding="utf-8",
    )
    print(f"{name}: {breite}x{hoehe}")
