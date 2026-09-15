"""
Baut die vier Dokumente der MS-4-Abgabe im Format der IU.

Zwei Durchlaeufe: Der erste erzeugt das Dokument mit Marken statt Seitenzahlen
in den Verzeichnissen, daraus entsteht ein PDF, aus dem die tatsaechlichen
Seiten abgelesen werden. Der zweite Durchlauf setzt die Zahlen ein.

Warum nicht das Verzeichnisfeld von Word: Es bleibt leer, bis jemand das
Dokument in Word oeffnet und das Verzeichnis aktualisiert. Wird das Dokument
unmittelbar nach PDF exportiert - und so geht es an den Tutor - steht dort
nur die Ueberschrift. Statische Zahlen sind hier verlaesslicher.
"""

import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Pfade relativ zum Skript: docs/bau/ enthaelt die Skripte, docs/ die
# Quellen, docs/bau/ausgabe die gebauten Dateien. Eine gesetzte Variable
# CFP_DOCS gewinnt, damit sich der Bau auch auf eine Arbeitskopie richten
# laesst.
DOCS = Path(os.environ.get("CFP_DOCS", Path(__file__).resolve().parent.parent))
BAU = DOCS / "bau" / "ausgabe"
PDF = BAU / "pdf"
VORLAGE = BAU / "reference-iu.docx"
HIER = Path(__file__).resolve().parent

DOKUMENTE = {
    "benutzerhandbuch": "Benutzerhandbuch",
    "fachliche-dokumentation": "Fachliche_Dokumentation",
    "technische-dokumentation": "Technische_Dokumentation",
    "betriebsdokumentation": "Betriebsdokumentation",
}


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)
ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")


def wn(name):
    return f"{{{W}}}{name}"


def ist_erstes_kapitel(absatz):
    """Ueberschrift erster Stufe, deren Text mit einer Ziffer beginnt.

    Die Verzeichnisse im Vorspann tragen dieselbe Formatvorlage, aber keine
    Kapitelnummer. Daran lassen sie sich unterscheiden.
    """
    stil = absatz.find(f"{wn('pPr')}/{wn('pStyle')}")
    if stil is None or stil.get(wn("val")) != "Heading1":
        return False
    text = "".join(t.text or "" for t in absatz.iter(wn("t"))).strip()
    return bool(text) and text[0].isdigit()


def verzeichnistabellen_glaetten(koerper):
    """Nimmt den Verzeichnissen die leere Kopfzeile.

    Die Verzeichnisse entstehen als zweispaltige Tabelle, deren Kopfzeile
    leer bleibt - sie soll ja nur Eintrag und Seitenzahl nebeneinander
    stellen. Der Tabellenstil hebt die erste Zeile jedoch hervor und zieht
    eine Linie darunter, sodass im Dokument eine leere Zeile mit Strich
    steht. Also: Zeile entfernen und die Hervorhebung abschalten.
    """
    geglaettet = 0
    for tabelle in koerper.iter(wn("tbl")):
        zeilen = tabelle.findall(wn("tr"))
        if not zeilen:
            continue
        erste = "".join(t.text or "" for t in zeilen[0].iter(wn("t"))).strip()
        if erste:
            continue
        tabelle.remove(zeilen[0])
        pr = tabelle.find(wn("tblPr"))
        if pr is not None:
            for look in pr.findall(wn("tblLook")):
                look.set(wn("firstRow"), "0")
                look.set(wn("noHBand"), "1")
        geglaettet += 1
    return geglaettet


def seitenzaehlung_trennen(docx):
    """Vorspann roemisch, Textteil arabisch ab 1.

    Umgesetzt wird das mit einem Abschnittswechsel vor dem ersten Kapitel.
    In OOXML beschreibt ein sectPr im Absatz den Abschnitt, der mit diesem
    Absatz endet - der eingefuegte sectPr gilt also fuer den Vorspann.
    """
    bau = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(docx) as archiv:
        archiv.extractall(bau)

    baum = ET.parse(bau / "word/document.xml")
    koerper = baum.getroot().find(wn("body"))
    schluss = koerper.find(wn("sectPr"))
    if schluss is None:
        return

    verzeichnistabellen_glaetten(koerper)

    # Der Textteil zaehlt arabisch und beginnt neu bei 1.
    nummerierung = ET.SubElement(schluss, wn("pgNumType"))
    nummerierung.set(wn("fmt"), "decimal")
    nummerierung.set(wn("start"), "1")

    absaetze = list(koerper)
    for stelle, element in enumerate(absaetze):
        if element.tag != wn("p") or not ist_erstes_kapitel(element):
            continue
        vorspann = ET.Element(wn("p"))
        ppr = ET.SubElement(vorspann, wn("pPr"))
        eigener = copy.deepcopy(schluss)
        for alt in eigener.findall(wn("pgNumType")):
            eigener.remove(alt)
        roemisch = ET.SubElement(eigener, wn("pgNumType"))
        roemisch.set(wn("fmt"), "upperRoman")
        roemisch.set(wn("start"), "1")
        ppr.append(eigener)
        koerper.insert(stelle, vorspann)
        break

    baum.write(bau / "word/document.xml", encoding="UTF-8", xml_declaration=True)
    neu = docx.with_suffix(".neu.docx")
    with zipfile.ZipFile(neu, "w", zipfile.ZIP_DEFLATED) as archiv:
        for datei in sorted(bau.rglob("*")):
            if datei.is_file():
                archiv.write(datei, datei.relative_to(bau))
    shutil.move(neu, docx)
    shutil.rmtree(bau)


def pandoc(quelle, ziel):
    subprocess.run(
        [
            "pandoc",
            str(quelle),
            "-f",
            "markdown-smart",
            "-t",
            "docx",
            "-V",
            "lang=de-DE",
            f"--reference-doc={VORLAGE}",
            "-o",
            str(ziel),
        ],
        check=True,
        cwd=BAU,
    )


def nach_pdf(docx):
    PDF.mkdir(exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(PDF), str(docx)],
        check=True,
        capture_output=True,
        timeout=300,
    )
    return PDF / (docx.stem + ".pdf")


def seiten_des_pdf(pdf):
    roh = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    return roh.split("\f")


def vereinfachen(text):
    """Fuer den Vergleich: Zeichen zusammenziehen, Formatierung entfernen."""
    text = re.sub(r"[*_`&]|nbsp;", "", text)
    return re.sub(r"\s+", "", text).lower()


def seite_suchen(marke_text, seiten, ab_seite=1):
    """Erste Seite, auf der der Eintrag vorkommt. Sucht ab ab_seite weiter.

    Die Verzeichnisse enthalten dieselben Zeichenfolgen wie der Text. Ohne
    das Weitersuchen ab der zuletzt gefundenen Seite wuerde jeder Eintrag auf
    der Verzeichnisseite selbst gefunden.
    """
    gesucht = vereinfachen(marke_text)
    for nummer in range(ab_seite, len(seiten) + 1):
        if gesucht and gesucht in vereinfachen(seiten[nummer - 1]):
            return nummer
    return None


def bilder_pruefen():
    """
    Bricht ab, wenn ein in der Markdown genanntes Bild fehlt.

    Ohne diese Pruefung baut pandoc klaglos weiter und setzt statt des Bildes
    dessen Beschriftung ein - die Warnung dazu geht in der uebrigen Ausgabe
    unter. Das Abbildungsverzeichnis entsteht aus der Markdown und listet die
    Abbildung trotzdem auf. Im fertigen Dokument steht dann ein Verzeichnis
    mit Eintraegen, zu denen es keine Abbildung gibt - und das sieht nicht
    nach einem vergessenen Schritt aus, sondern nach Schlamperei.
    """
    fehlend = []
    for kennung in DOKUMENTE:
        quelle = DOCS / f"{kennung}.md"
        for bezug in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", quelle.read_text(encoding="utf-8")):
            # Geprueft wird, was pandoc spaeter liest: Fuer SVG setzt
            # iu_formalia.py die PNG-Umsetzung ein, weil Word SVG nicht
            # zuverlaessig einbettet. Die SVG allein genuegt also nicht.
            gesucht = bezug[:-4] + ".png" if bezug.endswith(".svg") else bezug
            if not (DOCS / gesucht).exists():
                fehlend.append(f"{quelle.name}: {gesucht}")
    if fehlend:
        raise SystemExit(
            "Abbruch, folgende Bilder fehlen:\n  "
            + "\n  ".join(fehlend)
            + "\n\nDie Diagramme liegen als PNG unter docs/bilder/ im Repository. "
            "Sind sie\nnach einer Aenderung neu zu erzeugen, siehe docs/diagramme/README.md."
        )


def main():
    bilder_pruefen()

    # Die Diagramme als PNG neben die Markdown legen; die SVG sind die
    # Quelle der Darstellung, Word braucht die Rasterfassung.
    bilder = BAU / "bilder"
    bilder.mkdir(parents=True, exist_ok=True)
    for png in (DOCS / "bilder").glob("*.png"):
        shutil.copy2(png, bilder / png.name)

    subprocess.run([sys.executable, str(HIER / "iu_vorlage.py")], check=True)
    subprocess.run([sys.executable, str(HIER / "handbuch_bilder.py")], check=True)
    subprocess.run([sys.executable, str(HIER / "iu_formalia.py")], check=True)

    for kennung, ausgabe in DOKUMENTE.items():
        quelle = BAU / f"{kennung}.md"
        marken = json.loads((BAU / f"{kennung}.md.marken.json").read_text(encoding="utf-8"))
        text = quelle.read_text(encoding="utf-8")

        # Erster Durchlauf: Marken stehen noch drin.
        zwischen = BAU / f"{kennung}.roh.docx"
        pandoc(quelle, zwischen)
        seitenzaehlung_trennen(zwischen)
        seiten = seiten_des_pdf(nach_pdf(zwischen))

        # Das erste Kapitel markiert das Ende des Vorspanns; erst ab dort
        # wird gesucht, damit nicht die Verzeichnisseite selbst trifft.
        erste_textseite = 1
        for nummer, inhalt in enumerate(seiten, 1):
            if re.search(r"^\s*(0|1)\s+\S", inhalt, re.M) and nummer > 1:
                erste_textseite = nummer
                break

        # Die gesuchten Seiten sind physische Seiten. Gedruckt wird im
        # Textteil aber ab 1 neu gezaehlt, also den Vorspann abziehen.
        gefunden = 0
        for stelle, eintrag in enumerate(marken):
            seite = seite_suchen(eintrag, seiten, erste_textseite)
            gedruckt = str(seite - erste_textseite + 1) if seite else "–"
            text = text.replace(f"@@{stelle}@@", gedruckt)
            gefunden += seite is not None

        # Zweiter Durchlauf mit den echten Zahlen.
        endgueltig = BAU / f"{kennung}.md"
        endgueltig.write_text(text, encoding="utf-8")
        ziel = BAU / f"{ausgabe}.docx"
        pandoc(endgueltig, ziel)
        seitenzaehlung_trennen(ziel)
        zwischen.unlink()
        print(
            f"{ausgabe}.docx: {len(seiten)} Seiten, "
            f"{gefunden} von {len(marken)} Verzeichniseintraegen zugeordnet"
        )


if __name__ == "__main__":
    main()
