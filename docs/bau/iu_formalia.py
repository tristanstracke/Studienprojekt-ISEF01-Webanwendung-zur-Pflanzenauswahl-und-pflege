"""
Setzt die Formalia der IU auf die Dokumentation an, waehrend die Fassung im
Repository schlank bleibt.

Warum als Umformung und nicht in der Quelle: Die Markdown-Dateien in docs/
sind Entwicklerdokumentation und werden auf GitHub gelesen. Beschriftungen der
Form "Tab. 3 ..." samt "Quelle: Eigene Darstellung." gehoeren in die
Pruefungsabgabe, nicht in eine Datei, die jemand beim Einstieg ins Projekt
aufschlaegt. Dasselbe Muster benutzt bereits handbuch_bilder.py fuer die
Bildschirmfotos.

Umgesetzte Vorgaben (Allgemeiner Zitierleitfaden der IU, Abschnitt 2.2.5):
  - Abbildungen und Tabellen tragen die Bezeichnung als UEBERSCHRIFT,
    beginnend mit "Abb." beziehungsweise "Tab." und der Nummer.
  - Unter der Abbildung oder Tabelle steht die Quelle.
Und aus den Richtlinien fuer die Gestaltung, Abschnitt 3.1:
  - Abbildungsverzeichnis ab drei Abbildungen, Tabellenverzeichnis ab drei
    Tabellen, dazu ein Abkuerzungsverzeichnis.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Pfade relativ zum Skript: docs/bau/ enthaelt die Skripte, docs/ die
# Quellen, docs/bau/ausgabe die gebauten Dateien. Eine gesetzte Variable
# CFP_DOCS gewinnt, damit sich der Bau auch auf eine Arbeitskopie richten
# laesst.
DOCS = Path(os.environ.get("CFP_DOCS", Path(__file__).resolve().parent.parent))
QUELLE = DOCS
ZIEL = DOCS / "bau" / "ausgabe"

QUELLENANGABE = "Quelle: Eigene Darstellung."

# Titel der Tabellen in der Reihenfolge ihres Auftretens je Datei.
TABELLEN = {
    "benutzerhandbuch.md": [
        "Zugänge für die Prüfung",
        "Felder des Standortformulars",
        "Stufen des Eignungsurteils",
    ],
    "fachliche-dokumentation.md": [
        "Abgrenzung zu vergleichbaren Produkten",
        "Begriffe der Anwendung",
        "Bewertung der Abweichung beim Licht",
        "Bewertung des Abstands zur Temperaturuntergrenze",
        "Bewertung der Bodenart",
        "Bewertung der Giftigkeit",
        "Bildung des Gesamturteils aus den Einzelbewertungen",
        "Bewusst nicht umgesetzte Anforderungen",
    ],
    "technische-dokumentation.md": [
        "Nicht verwendete Kapitel des arc42-Rahmens",
        "Beteiligte im Systemkontext",
        "Ziele der Lösungsstrategie und ihre Umsetzung",
        "Bausteine innerhalb der Anwendung",
        "Tabellen des Datenmodells",
    ],
    "betriebsdokumentation.md": [
        "Bausteine der Laufzeitumgebung",
        "Umgebungsvariablen der Anwendung",
        "Zugänge des Systems",
        "Störungen und ihre Behebung",
    ],
}

# Kandidaten fuer das Abkuerzungsverzeichnis. Aufgenommen wird nur, was im
# jeweiligen Dokument tatsaechlich vorkommt.
ABKUERZUNGEN = [
    ("ADR", "Architecture Decision Record"),
    ("API", "Application Programming Interface"),
    ("CI", "Continuous Integration"),
    ("CSS", "Cascading Style Sheets"),
    ("ER", "Entity-Relationship"),
    ("HSTS", "HTTP Strict Transport Security"),
    ("HTML", "Hypertext Markup Language"),
    ("HTTP", "Hypertext Transfer Protocol"),
    ("HTTPS", "Hypertext Transfer Protocol Secure"),
    ("ISO", "International Organization for Standardization"),
    ("IEC", "International Electrotechnical Commission"),
    ("MS", "Meilenstein"),
    ("ORM", "Object-Relational Mapping"),
    ("REST", "Representational State Transfer"),
    ("SQL", "Structured Query Language"),
    ("UC", "Use Case (Anwendungsfall)"),
    ("UTC", "Coordinated Universal Time"),
    ("WCAG", "Web Content Accessibility Guidelines"),
]


def beschriftung(text):
    """Ein Absatz in der Formatvorlage Caption."""
    return ["", '::: {custom-style="Caption"}', text, ":::", ""]


def ist_trennzeile(zeile):
    return bool(re.match(r"^\|[\s:|-]+\|\s*$", zeile))


def umformen(name, text):
    """Setzt Beschriftungen und Quellenangaben und sammelt die Verzeichnisse."""
    zeilen = text.splitlines()
    titel = list(TABELLEN.get(name, []))
    ergebnis, abbildungen, tabellen = [], [], []
    i = 0
    while i < len(zeilen):
        zeile = zeilen[i]

        # Abbildung: ![Titel](pfad) wird zu Ueberschrift, Bild, Quelle.
        treffer = re.match(r"^!\[(.*?)\]\((.*?)\)(\{.*\})?\s*$", zeile)
        if treffer:
            roh, pfad, attribute = treffer.groups()
            sauber = re.sub(r"^Abbildung\s*\d+:\s*", "", roh).strip()
            nummer = len(abbildungen) + 1
            abbildungen.append(sauber)
            ergebnis += beschriftung(f"Abb. {nummer} {sauber}")
            # Word bettet SVG nicht zuverlaessig ein. Fuer die Wortfassung
            # wird die erzeugte PNG-Umsetzung gesetzt und auf Satzbreite
            # skaliert, damit Word nicht ueber die Bildhoehe verkleinert.
            if pfad.endswith(".svg"):
                pfad = pfad[:-4] + ".png"
                attribute = "{ width=15.5cm }"
            ergebnis.append(f"![]({pfad}){attribute or ''}")
            ergebnis += beschriftung(QUELLENANGABE)
            i += 1
            continue

        # Tabelle: Kopfzeile erkennen an der Trennzeile darunter.
        if zeile.startswith("|") and i + 1 < len(zeilen) and ist_trennzeile(zeilen[i + 1]):
            nummer = len(tabellen) + 1
            name_der_tabelle = titel.pop(0) if titel else f"Übersicht {nummer}"
            tabellen.append(name_der_tabelle)
            ergebnis += beschriftung(f"Tab. {nummer} {name_der_tabelle}")
            while i < len(zeilen) and zeilen[i].startswith("|"):
                ergebnis.append(zeilen[i])
                i += 1
            ergebnis += beschriftung(QUELLENANGABE)
            continue

        ergebnis.append(zeile)
        i += 1

    if titel:
        raise SystemExit(f"{name}: Titel ohne Tabelle uebrig: {titel}")
    return "\n".join(ergebnis), abbildungen, tabellen


def verzeichnis(ueberschrift, eintraege, praefix, marken):
    """Ein Verzeichnis als zweispaltige Tabelle: Eintrag links, Seite rechts.

    Die Seitenzahl steht zunaechst als Marke; iu_bauen.py setzt sie nach dem
    ersten Durchlauf aus dem gerenderten PDF ein. Ein Feld im Sinne von Word
    kommt nicht in Frage: es bleibt beim Export nach PDF leer, solange niemand
    das Verzeichnis in Word von Hand aktualisiert.
    """
    zeilen = [f"## {ueberschrift}", "", "| | |", "|:---|---:|"]
    for nummer, eintrag in enumerate(eintraege, 1):
        text = f"{praefix} {nummer} {eintrag}"
        marke = f"@@{len(marken)}@@"
        marken.append(text)
        zeilen.append(f"| {text} | {marke} |")
    zeilen.append("")
    return zeilen


def inhaltsverzeichnis(zeilen_des_koerpers, marken):
    """Inhaltsverzeichnis aus den Ueberschriften; nur Stufe 1 wird fett."""
    eintraege = []
    im_block = False
    for zeile in zeilen_des_koerpers:
        if zeile.startswith("```"):
            im_block = not im_block
        if im_block or not zeile.startswith("#"):
            continue
        stufe = len(zeile) - len(zeile.lstrip("#"))
        text = zeile.lstrip("#").strip().replace("`", "")
        if stufe > 3:
            continue
        eintraege.append((stufe, text))
    if not eintraege:
        return []
    zeilen = ["## Inhaltsverzeichnis", "", "| | |", "|:---|---:|"]
    for stufe, text in eintraege:
        marke = f"@@{len(marken)}@@"
        marken.append(text)
        # Stufe 2 in der Quelle ist nach dem Anheben Stufe 1.
        gezeigt = f"**{text}**" if stufe == 2 else text
        einzug = "&nbsp;&nbsp;&nbsp;&nbsp;" if stufe == 3 else ""
        zeilen.append(f"| {einzug}{gezeigt} | {marke} |")
    zeilen.append("")
    return zeilen


def abkuerzungsverzeichnis(text):
    gefunden = [
        (k, lang)
        for k, lang in ABKUERZUNGEN
        if re.search(rf"(?<![A-Za-z]){re.escape(k)}(?![A-Za-z])", text)
    ]
    if not gefunden:
        return []
    zeilen = ["## Abkürzungsverzeichnis", "", "| Abkürzung | Bedeutung |", "|---|---|"]
    for kurz, lang in sorted(gefunden):
        zeilen.append(f"| {kurz} | {lang} |")
    zeilen.append("")
    return zeilen


def ebenen_anheben(zeilen):
    """Hebt die Gliederung um eine Stufe an und zieht den Titel heraus.

    Die Richtlinien messen "1 Ueberschrift" als Stufe 1 mit 16 pt. In der
    Repository-Fassung ist die erste Ebene der Dokumenttitel und die Kapitel
    liegen eine Stufe tiefer. Der Titel gehoert auf das Deckblatt, also wird
    er zu Metadaten und alles darunter rueckt eine Stufe hoch. Zeilen in
    Codebloecken bleiben unberuehrt, dort ist # ein Kommentarzeichen.
    """
    titel, ergebnis, im_block = "", [], False
    for zeile in zeilen:
        if zeile.startswith("```"):
            im_block = not im_block
            ergebnis.append(zeile)
            continue
        if im_block:
            ergebnis.append(zeile)
            continue
        if zeile.startswith("# ") and not titel:
            titel = zeile[2:].strip()
            continue
        if zeile.startswith("##"):
            # Dicktengleiche Auszeichnung in Ueberschriften entfernen: sie
            # bricht das einheitliche Schriftbild und zerlegt die Zeile im
            # Inhaltsverzeichnis.
            ergebnis.append(zeile[1:].replace("`", ""))
            continue
        ergebnis.append(zeile)
    return titel, ergebnis


def standdatum(text):
    """Setzt das Datum des Baus in die Kopfzeile.

    In der Quelle steht ein gewoehnliches Datum, damit die Zeile auf GitHub
    lesbar bleibt. Beim Bauen wird es ersetzt, sonst weist die Abgabe ein
    Datum aus, das nicht zum Inhalt passt - genau der Fehler, der in der
    Fassung vom 07.09. steckte.
    """
    heute = date.today().strftime("%d.%m.%Y")
    return re.sub(r"(?m)^(Stand: )\d{2}\.\d{2}\.\d{4}", rf"\g<1>{heute}", text)


def quelle_fuer(name):
    """Das Benutzerhandbuch bekommt zuerst die Bildschirmfotos eingesetzt."""
    if name == "benutzerhandbuch.md":
        mit_bildern = ZIEL / "benutzerhandbuch_mit_bildern.md"
        if not mit_bildern.is_file():
            raise SystemExit("Erst handbuch_bilder.py laufen lassen.")
        return mit_bildern
    return QUELLE / name


def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    for name in TABELLEN:
        quelle = quelle_fuer(name)
        roh = standdatum(quelle.read_text(encoding="utf-8"))
        koerper, abbildungen, tabellen = umformen(name, roh)

        # Der Titel des Dokuments bleibt die erste Ueberschrift; die
        # Verzeichnisse werden direkt dahinter eingefuegt.
        zeilen = koerper.splitlines()
        schnitt = 1
        while schnitt < len(zeilen) and not zeilen[schnitt].startswith("## "):
            schnitt += 1

        marken = []
        vorspann = inhaltsverzeichnis(zeilen[schnitt:], marken)
        vorspann += abkuerzungsverzeichnis(roh)
        if len(abbildungen) >= 3:
            vorspann += verzeichnis("Abbildungsverzeichnis", abbildungen, "Abb.", marken)
        if len(tabellen) >= 3:
            vorspann += verzeichnis("Tabellenverzeichnis", tabellen, "Tab.", marken)
        (ZIEL / (name + ".marken.json")).write_text(
            json.dumps(marken, ensure_ascii=False, indent=1), encoding="utf-8"
        )

        neu = zeilen[:schnitt] + [""] + vorspann + zeilen[schnitt:]
        titel, neu = ebenen_anheben(neu)
        kopf = ["---", f'title: "{titel}"', "lang: de-DE", "---", ""]
        (ZIEL / name).write_text("\n".join(kopf + neu) + "\n", encoding="utf-8")
        print(
            f"{name}: {len(abbildungen)} Abbildungen, {len(tabellen)} Tabellen, "
            f"Verzeichnisse: {'ja' if vorspann else 'nein'}"
        )


if __name__ == "__main__":
    sys.exit(main())
