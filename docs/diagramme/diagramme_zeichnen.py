"""Zeichnet die fuenf Diagramme der Dokumentation.

Layoutregeln, damit die Bilder ruhig wirken:
- Ablaufdiagramme: eine senkrechte Hauptachse, Nebenzweige nach aussen,
  Rueckfuehrungen ausserhalb der Kastenspalten. Keine Kante kreuzt einen Kasten.
- Datenmodell: vier Ebenen, drei Spalten. Beziehungsnamen stehen oberhalb,
  Kardinalitaeten unterhalb beziehungsweise neben der Linie.
- Bildbreite hoechstens 1550 Einheiten, damit die Schrift im Dokument bei
  15,5 cm Satzbreite rund 9 Punkt gross bleibt.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagramm_werkzeug import (  # noqa: E402
    breite_von,
    entitaet,
    kante,
    kasten,
    marke,
    raute,
    schreibe,
)

# =========================================================== Ablauf UC 1

ACHSE, NEBEN = 470, 1120
t = []

s, _, _, u1 = kasten(ACHSE, 40, ["Standort anlegen"])
t.append(s)
s, _, _, u2 = kasten(ACHSE, 170, ["Katalog durchsuchen"])
t.append(s)
s, rl, rr, ro, ru = raute(ACHSE, 330, "Art im Katalog?")
t.append(s)
s, nl, _, nu = kasten(NEBEN, 294, ["Eigene Art anlegen"])
t.append(s)
s, _, _, u3 = kasten(ACHSE, 470, ["Auf die Wunschliste"])
t.append(s)
s, _, _, u4 = kasten(ACHSE, 600, ["Eignung prüfen"])
t.append(s)
s, _, _, u5 = kasten(ACHSE, 730, ["Urteil je Standort", "mit Begründung"])
t.append(s)
s, el, er, eo, eu = raute(ACHSE, 960, "Entscheidung")
t.append(s)
s, *_ = kasten(ACHSE, 1090, ["Anschaffen – weiter in UC 2"], art="betont", radius=40)
t.append(s)
s, *_ = kasten(NEBEN, 1090, ["Von der Liste entfernen"], art="betont", radius=40)
t.append(s)

t += [
    kante(f"M{ACHSE},{u1} L{ACHSE},162"),
    kante(f"M{ACHSE},{u2} L{ACHSE},{ro - 8}"),
    # nein: nach rechts zur eigenen Art
    kante(f"M{rr},330 L{nl - 8},330"),
    marke(rr + 22, 314, "nein"),
    # ja: senkrecht weiter
    kante(f"M{ACHSE},{ru} L{ACHSE},462"),
    marke(ACHSE - 18, 412, "ja", anker="end"),
    # eigene Art wieder auf die Achse
    kante(f"M{NEBEN},{nu} L{NEBEN},432 L{ACHSE + 10},432"),
    kante(f"M{ACHSE},{u3} L{ACHSE},592"),
    kante(f"M{ACHSE},{u4} L{ACHSE},722"),
    kante(f"M{ACHSE},{u5} L{ACHSE},{eo - 8}"),
    # Entscheidung
    kante(f"M{ACHSE},{eu} L{ACHSE},1082"),
    marke(ACHSE + 20, eu + 42, "anschaffen"),
    kante(f"M{er},960 L{NEBEN},960 L{NEBEN},1082"),
    marke(er + 22, 944, "verwerfen"),
]
schreibe("ablauf-uc1.svg", 1400, 1200, t)

# =========================================================== Ablauf UC 2

ACHSE, LINKS, RECHTS = 470, 250, 1080
t = []

s, _, _, b1 = kasten(ACHSE, 40, ["Pflanze anschaffen"])
t.append(s)
s, _, _, b2 = kasten(ACHSE, 170, ["Standort zuweisen"])
t.append(s)
s, _, _, b3 = kasten(ACHSE, 300, ["Pflegevorlagen aus den", "Pflegeempfehlungen"])
t.append(s)
s, _, _, b4 = kasten(ACHSE, 470, ["Erster Termin:", "heute plus Intervall"])
t.append(s)
s, kl, kr, b5 = kasten(ACHSE, 640, ["Pflegekalender", "in vier Gruppen"], art="betont")
t.append(s)
s, vl, vr, vo, vu = raute(ACHSE, 860, "Nächster Schritt?")
t.append(s)
s, _, _, c1 = kasten(LINKS, 990, ["Erledigungsdatum", "setzen"])
t.append(s)
s, _, _, c2 = kasten(LINKS, 1150, ["Neuer Termin ab", "Erledigungstag"])
t.append(s)
s, _, _, d1 = kasten(RECHTS, 990, ["Vorlage anpassen,", "Termin verschieben"])
t.append(s)

KM = 695  # Hoehe der beiden Rueckfuehrungen, oberhalb der Verzweigung
t += [
    kante(f"M{ACHSE},{b1} L{ACHSE},162"),
    kante(f"M{ACHSE},{b2} L{ACHSE},292"),
    kante(f"M{ACHSE},{b3} L{ACHSE},462"),
    kante(f"M{ACHSE},{b4} L{ACHSE},632"),
    kante(f"M{ACHSE},{b5} L{ACHSE},{vo - 8}"),
    # Zweig links: Aufgabe abhaken
    kante(f"M{vl},860 L{LINKS},860 L{LINKS},982"),
    marke(vl - 22, 844, "abhaken", anker="end"),
    kante(f"M{LINKS},{c1} L{LINKS},1142"),
    kante(f"M{LINKS},{c2} L{LINKS},1290 L70,1290 L70,{KM} L{kl - 8},{KM}"),
    # Zweig rechts: Intervall aendern
    kante(f"M{vr},860 L{RECHTS},860 L{RECHTS},982"),
    marke(vr + 22, 844, "Intervall ändern"),
    kante(f"M{RECHTS},{d1} L{RECHTS},1210 L1330,1210 L1330,{KM} L{kr + 8},{KM}"),
]
schreibe("ablauf-uc2.svg", 1400, 1340, t)

# ========================================================= Bausteinsicht

t = [
    '<rect class="rahmen" x="30" y="30" width="1440" height="340" rx="10"/>',
    '<text class="fett" x="62" y="88">Care for Plants (Django-Projekt)</text>',
]
s, _, r1, _ = kasten(
    290, 130, ["config", "settings · urls", "wsgi"], breite=440, hoehe=200, erste_fett=True
)
t.append(s)
s, l2, r2, _ = kasten(
    750,
    130,
    ["plants", "models · views · forms", "eignung · pflege"],
    breite=420,
    hoehe=200,
    erste_fett=True,
)
t.append(s)
s, l3, _, _ = kasten(
    1220,
    130,
    ["templates", "Seitengerüst und", "Ansichten je Fall"],
    breite=420,
    hoehe=200,
    erste_fett=True,
)
t.append(s)
t += [kante(f"M{r1},230 L{l2 - 8},230"), kante(f"M{r2},230 L{l3 - 8},230")]
schreibe("bausteinsicht.svg", 1500, 400, t)

# ======================================================= Verteilungssicht
# Obere Reihe: Weg des Quelltextes. Untere Reihe: Laufzeitumgebung.

t = []


def umgebung(x, y, breite, hoehe, titel):
    return (
        f'<rect class="rahmen" x="{x}" y="{y}" width="{breite}" '
        f'height="{hoehe}" rx="10"/>'
        f'<text class="fett" x="{x + 30}" y="{y + 46}">{titel}</text>'
    )


E = ["Python 3.12", "SQLite lokal", "Entwicklungsserver"]
G = ["Repository", "Actions: Ruff,", "pytest, Systemcheck", "Auslieferung"]
C = ["Container", "Gunicorn und Django"]
V = ["Volume /data", "db.sqlite3"]
be, bg, bc, bv = (breite_von(z) for z in (E, G, C, V))

# Reihe 1
r1 = max(be + 60, breite_von(["Entwicklungsrechner"], polster=60))
r2 = bg + 60
t += [
    umgebung(30, 30, r1, 300, "Entwicklungsrechner"),
    umgebung(30 + r1 + 100, 30, r2, 300, "GitHub"),
]
cx_e = 30 + r1 // 2
cx_g = 30 + r1 + 100 + r2 // 2
s, _, e_r, _ = kasten(cx_e, 105, E, breite=be, hoehe=190)
t.append(s)
s, _, _, g_u = kasten(cx_g, 105, G, breite=bg, hoehe=190)
t.append(s)
# Reihe 2
r3 = bc + bv + 130
t.append(umgebung(30, 420, r3, 230, "Railway"))
cx_c = 30 + 30 + bc // 2
cx_v = 30 + 30 + bc + 40 + bv // 2
s, _, c_r, c_u = kasten(cx_c, 490, C, breite=bc, hoehe=130)
t.append(s)
s, v_l, *_ = kasten(cx_v, 505, V, breite=bv, hoehe=100, art="betont")
t.append(s)
bb = breite_von(["Browser des Nutzers"])
cx_b = 30 + r3 + 60 + bb // 2
s, _, _, b_u = kasten(cx_b, 490, ["Browser des Nutzers"])
t.append(s)
t += [
    kante(f"M{e_r},200 L{30 + r1 + 92},200"),
    marke(30 + r1 + 50, 182, "push", anker="middle"),
    kante(f"M{cx_g},{g_u} L{cx_g},370 L{cx_c},370 L{cx_c},412"),
    marke(cx_c + 200, 354, "deploy"),
    kante(f"M{c_r},555 L{v_l - 8},555"),
    kante(f"M{cx_b},{b_u} L{cx_b},700 L{cx_c},700 L{cx_c},628"),
    marke(cx_c + 200, 684, "https"),
]
schreibe("verteilungssicht.svg", cx_b + bb // 2 + 40, 750, t)

# =========================================================== Datenmodell

SP1, SP2, SP3 = 230, 750, 1270
B1, B2, B3 = 360, 320, 360
E1, E2, E3 = 40, 300, 700  # Oberkanten der Ebenen
K1, K2 = 500, 1000  # senkrechte Korridore zwischen den Spalten
t = []

s, ben_l, ben_r, ben_u = entitaet(SP2, E1, "BENUTZER", ["Benutzername", "Kennwort"], B2)
t.append(s)
s, _, sta_r, sta_u = entitaet(
    SP1,
    E2,
    "STANDORT",
    [
        "Bezeichnung",
        "Art (innen oder Balkon)",
        "Lichtangebot",
        "Minimaltemperatur",
        "Luftfeuchtigkeit",
        "für Kinder erreichbar",
    ],
    B1,
)
t.append(s)
s, pfl_l, pfl_r, pfl_u = entitaet(SP2, E2, "PFLANZE", ["Bezeichnung", "Status", "Notiz"], B2)
t.append(s)
s, art_l, _, art_u = entitaet(
    SP3,
    E2,
    "PFLANZENART",
    ["Name", "Lichtbedarf", "Temperaturuntergrenze", "Wasserbedarf", "giftig", "erstellt von"],
    B3,
)
t.append(s)
s, _, _, bod_u = entitaet(SP1, E3, "BODENART", ["Bezeichnung", "Beschreibung"], B1)
t.append(s)
s, _, _, vor_u = entitaet(
    SP2, E3, "PFLEGEVORLAGE", ["Tätigkeit", "Intervall in Tagen", "Hinweis"], B2
)
t.append(s)
s, *_ = entitaet(SP3, E3, "PFLEGEEMPFEHLUNG", ["Tätigkeit", "Intervall in Tagen", "Hinweis"], B3)
t.append(s)
E4 = 980
s, *_ = entitaet(SP2, E4, "PFLEGEAUFGABE", ["Fälligkeit", "erledigt am"], B2)
t.append(s)


def senkrecht(x, y1, y2, oben, unten, rolle):
    """Senkrechte Beziehung mit Kardinalitaeten an den Enden."""
    return [
        kante(f"M{x},{y1} L{x},{y2}", gerichtet=False),
        marke(x + 14, y1 + 32, oben, klasse="karte"),
        marke(x + 14, y2 - 12, unten, klasse="karte"),
        marke(x + 46, (y1 + y2) // 2 + 8, rolle, klasse="rolle"),
    ]


def waagerecht(y, x1, x2, links, rechts, rolle):
    """Waagerechte Beziehung: Name oberhalb, Kardinalitaeten unterhalb."""
    return [
        kante(f"M{x1},{y} L{x2},{y}", gerichtet=False),
        marke(x1 + 14, y + 34, links, klasse="karte"),
        marke(x2 - 14, y + 34, rechts, anker="end", klasse="karte"),
        marke((x1 + x2) // 2, y - 16, rolle, anker="middle", klasse="rolle"),
    ]


t += senkrecht(SP2, ben_u, E2, "1", "n", "besitzt")
t += senkrecht(SP1, sta_u, E3, "n", "1", "hat")
t += senkrecht(SP3, art_u, E3, "1", "n", "empfiehlt")
t += senkrecht(SP2, pfl_u, E3, "1", "n", "hat")
t += senkrecht(SP2, vor_u, E4, "1", "n", "erzeugt")
t += waagerecht(450, sta_r, pfl_l, "1", "n", "beherbergt")
t += waagerecht(450, pfl_r, art_l, "n", "1", "hat die Art")

t += [
    # BENUTZER 1:n STANDORT, ueber den linken Korridor
    kante(f"M{ben_l},112 L{K1},112 L{K1},345 L{sta_r},345", gerichtet=False),
    marke(ben_l - 14, 104, "1", anker="end", klasse="karte"),
    marke(sta_r + 14, 337, "n", klasse="karte"),
    marke(K1 + 18, 240, "legt an", klasse="rolle"),
    # BENUTZER 1:n PFLANZENART, ueber den rechten Korridor
    kante(f"M{ben_r},112 L{K2},112 L{K2},345 L{art_l},345", gerichtet=False),
    marke(ben_r + 14, 104, "1", klasse="karte"),
    marke(art_l - 14, 337, "n", anker="end", klasse="karte"),
    marke(K2 + 18, 240, "legt eigene an", klasse="rolle"),
    # PFLANZENART n:m BODENART, unterhalb aller Kaesten gefuehrt
    kante(f"M{art_l},555 L{K2},555 L{K2},1200 L{SP1},1200 L{SP1},{bod_u}", gerichtet=False),
    marke(art_l - 14, 547, "n", anker="end", klasse="karte"),
    marke(SP1 + 14, bod_u + 32, "m", klasse="karte"),
    marke(760, 1184, "gedeiht in", anker="middle", klasse="rolle"),
]
schreibe("datenmodell.svg", 1550, 1250, t)
