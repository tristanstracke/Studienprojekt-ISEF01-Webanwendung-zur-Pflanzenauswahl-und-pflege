"""
Baut die Word-Referenzvorlage nach den IU-Richtlinien fuer die Gestaltung
wissenschaftlicher Arbeiten, Stand 01.10.2025, Abschnitt 2.

Umgesetzte Vorgaben:
  Flaeche      Rand exakt 2,00 cm auf allen vier Seiten
  Grundschrift Arial 11 pt, schwarz, Blocksatz, Zeilenabstand 1,5
  Absatz       keine Einrueckung der ersten Zeile, 6 pt Abstand danach
  Ueberschrift linksbuendig fett; Stufe 1: 16 pt, Stufe 2: 14 pt, Stufe 3: 11 pt
               Abstaende: Stufe 1 je 12 pt vor und nach, Stufe 2 und 3
               12 pt vor und 6 pt nach
  Fussnoten    Arial 10 pt, Blocksatz
  Verzeichnis  linksbuendig
  Seitenzahl   zentriert am Seitenende

Masseinheiten in der Datei: 1 cm = 567 Twips, 1 pt = 20 Twips,
Schriftgroessen in halben Punkten.
"""

import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ET.register_namespace("w", W)
ET.register_namespace("r", R)

DOCS = Path(os.environ.get("CFP_DOCS", Path(__file__).resolve().parent.parent))
ARBEIT = DOCS / "bau" / "ausgabe"
BAU = ARBEIT / "vorlage"
ZIEL = ARBEIT / "reference-iu.docx"

SCHRIFT = "Arial"
RAND = 1134  # 2,00 cm
ZEILE = "360"  # 1,5-zeilig
PT6, PT12 = "120", "240"


def w(name):
    return f"{{{W}}}{name}"


def kind(eltern, name):
    """Holt ein Kindelement oder legt es an."""
    gefunden = eltern.find(w(name))
    if gefunden is None:
        gefunden = ET.SubElement(eltern, w(name))
    return gefunden


def setze(eltern, name, **attribute):
    el = kind(eltern, name)
    for schluessel, wert in attribute.items():
        el.set(w(schluessel), wert)
    return el


def absatz(stil, ausrichtung="both", vor=None, nach=PT6, zeile=ZEILE):
    """Absatzformat eines Formatvorlagen-Elements setzen."""
    ppr = kind(stil, "pPr")
    for alt in ppr.findall(w("ind")):
        ppr.remove(alt)
    abstand = {"after": nach, "line": zeile, "lineRule": "auto"}
    if vor:
        abstand["before"] = vor
    setze(ppr, "spacing", **abstand)
    setze(ppr, "jc", val=ausrichtung)
    setze(ppr, "ind", firstLine="0", left="0")


def zeichen(stil, groesse_halbpunkte, fett=False):
    rpr = kind(stil, "rPr")
    setze(rpr, "rFonts", ascii=SCHRIFT, hAnsi=SCHRIFT, cs=SCHRIFT)
    setze(rpr, "sz", val=groesse_halbpunkte)
    setze(rpr, "szCs", val=groesse_halbpunkte)
    setze(rpr, "color", val="000000")
    for name in ("b", "bCs"):
        vorhanden = rpr.find(w(name))
        if fett and vorhanden is None:
            ET.SubElement(rpr, w(name))
        elif not fett and vorhanden is not None:
            rpr.remove(vorhanden)


def formatvorlagen():
    baum = ET.parse(BAU / "word/styles.xml")
    wurzel = baum.getroot()
    nach_id = {s.get(w("styleId")): s for s in wurzel.findall(w("style"))}

    # Grundschrift des Dokuments
    standard = wurzel.find(w("docDefaults"))
    if standard is not None:
        rpr = standard.find(f"{w('rPrDefault')}/{w('rPr')}")
        if rpr is not None:
            setze(rpr, "rFonts", ascii=SCHRIFT, hAnsi=SCHRIFT, cs=SCHRIFT)
            setze(rpr, "sz", val="22")
            setze(rpr, "szCs", val="22")

    # Erst alle Vorlagen auf Arial und Schwarz ziehen. Pandocs Vorlage faerbt
    # Ueberschriften blau und setzt eine eigene Schrift; beides widerspricht
    # der Vorgabe "einfarbig schwarz" und "einheitliche Schriftart".
    # Ausgenommen bleiben die Vorlagen fuer Quelltext: dort traegt die
    # dicktengleiche Schrift Information (Einrueckung, Ausrichtung).
    quelltext = {
        "SourceCode",
        "VerbatimChar",
        "AttributeValue",
        "Keyword",
        "DataType",
        "Functions",
        "CommentVar",
        "StringTok",
        "CharTok",
        "NormalTok",
        "ControlFlowTok",
        "OperatorTok",
    }
    for kennung, stil in nach_id.items():
        if kennung in quelltext:
            continue
        rpr = kind(stil, "rPr")
        schriften = setze(rpr, "rFonts", ascii=SCHRIFT, hAnsi=SCHRIFT, cs=SCHRIFT)
        # Verweise auf die Themaschrift schlagen die ausdrueckliche Angabe.
        # Ohne dieses Aufraeumen bleiben Titel und Ueberschriften in der
        # Hausschrift von pandoc stehen.
        for thema in ("asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme"):
            schriften.attrib.pop(w(thema), None)
        setze(rpr, "color", val="000000")

    fliesstext = ("Normal", "BodyText", "FirstParagraph", "Compact", "BlockText")
    for kennung in fliesstext:
        stil = nach_id.get(kennung)
        if stil is None:
            continue
        zeichen(stil, "22")
        absatz(stil, "both")

    # Der Dokumenttitel steht spaeter auf dem Deckblatt. Hier bleibt er als
    # Zuordnungshilfe stehen und wird wie eine Ueberschrift erster Stufe
    # gesetzt, damit die Seite nicht zwei konkurrierende Schriftbilder zeigt.
    for kennung in ("Title", "Subtitle", "Author", "Date"):
        stil = nach_id.get(kennung)
        if stil is None:
            continue
        zeichen(stil, "32" if kennung == "Title" else "22", fett=(kennung == "Title"))
        absatz(stil, "left", nach=PT12)

    # Ueberschriften: Stufe 1 bis 3 nach Tabelle 1 der Richtlinien,
    # ab Stufe 4 wie Stufe 3 (kommt in den Dokumenten nicht vor).
    stufen = {
        "Heading1": ("32", PT12, PT12),
        "Heading2": ("28", PT12, PT6),
        "Heading3": ("22", PT12, PT6),
        "Heading4": ("22", PT12, PT6),
        "Heading5": ("22", PT12, PT6),
        "Heading6": ("22", PT12, PT6),
    }
    for kennung, (groesse, vor, nach) in stufen.items():
        stil = nach_id.get(kennung)
        if stil is None:
            continue
        zeichen(stil, groesse, fett=True)
        absatz(stil, "left", vor=vor, nach=nach)

    # Verzeichnisse und deren Ueberschriften linksbuendig
    for kennung in (
        "TOCHeading",
        "TOC1",
        "TOC2",
        "TOC3",
        "Caption",
        "ImageCaption",
        "TableCaption",
    ):
        stil = nach_id.get(kennung)
        if stil is None:
            continue
        zeichen(stil, "22", fett=(kennung == "TOCHeading"))
        absatz(stil, "left", nach=PT6)
    if "TOCHeading" in nach_id:
        zeichen(nach_id["TOCHeading"], "32", fett=True)

    # Fussnoten: Arial 10, Blocksatz
    for kennung in ("FootnoteText", "FootnoteBlockText"):
        stil = nach_id.get(kennung)
        if stil is None:
            continue
        zeichen(stil, "20")
        absatz(stil, "both", nach="0", zeile="240")

    baum.write(BAU / "word/styles.xml", encoding="UTF-8", xml_declaration=True)


def seitenraender_und_fusszeile():
    """Raender auf 2,00 cm und eine zentrierte Seitenzahl in der Fusszeile."""
    fusszeile = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W}">
  <w:p>
    <w:pPr><w:jc w:val="center"/>
      <w:rPr><w:rFonts w:ascii="{SCHRIFT}" w:hAnsi="{SCHRIFT}"/><w:sz w:val="22"/></w:rPr>
    </w:pPr>
    <w:r><w:rPr><w:rFonts w:ascii="{SCHRIFT}" w:hAnsi="{SCHRIFT}"/><w:sz w:val="22"/></w:rPr>
      <w:fldChar w:fldCharType="begin"/></w:r>
    <w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
    <w:r><w:fldChar w:fldCharType="end"/></w:r>
  </w:p>
</w:ftr>"""
    (BAU / "word/footer1.xml").write_text(fusszeile, encoding="utf-8")

    # Ohne Praefix-Registrierung schreibt ElementTree ein ns0: in die Datei,
    # das dort nicht deklariert ist. Word und LibreOffice lehnen sie dann ab.
    PAKET = "http://schemas.openxmlformats.org/package/2006/relationships"
    ET.register_namespace("", PAKET)
    rels = ET.parse(BAU / "word/_rels/document.xml.rels")
    wurzel = rels.getroot()
    kennungen = {e.get("Id") for e in wurzel}
    kennung = next(f"rId{n}" for n in range(900, 999) if f"rId{n}" not in kennungen)
    ET.SubElement(
        wurzel,
        f"{{{PAKET}}}Relationship",
        {
            "Id": kennung,
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer",
            "Target": "footer1.xml",
        },
    )
    rels.write(BAU / "word/_rels/document.xml.rels", encoding="UTF-8", xml_declaration=True)

    inhalt = (BAU / "[Content_Types].xml").read_text(encoding="utf-8")
    if "footer1.xml" not in inhalt:
        marke = "</Types>"
        eintrag = (
            '<Override PartName="/word/footer1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.footer+xml"/>'
        )
        (BAU / "[Content_Types].xml").write_text(
            inhalt.replace(marke, eintrag + marke), encoding="utf-8"
        )

    baum = ET.parse(BAU / "word/document.xml")
    koerper = baum.getroot().find(w("body"))
    sectpr = koerper.find(w("sectPr"))
    if sectpr is None:
        sectPr = ET.SubElement(koerper, w("sectPr"))
    else:
        sectPr = sectpr
    verweis = ET.Element(w("footerReference"))
    verweis.set(w("type"), "default")
    verweis.set(f"{{{R}}}id", kennung)
    sectPr.insert(0, verweis)
    # DIN A4 in Twips. Pandocs Vorlage liefert US Letter, was im PDF sofort
    # als Formfehler auffaellt.
    setze(sectPr, "pgSz", w="11906", h="16838")
    setze(
        sectPr,
        "pgMar",
        top=str(RAND),
        right=str(RAND),
        bottom=str(RAND),
        left=str(RAND),
        header="709",
        footer="709",
        gutter="0",
    )
    baum.write(BAU / "word/document.xml", encoding="UTF-8", xml_declaration=True)


def grundlage_holen():
    """Pandocs eigene Referenzdatei als Ausgangspunkt entpacken."""
    if BAU.exists():
        shutil.rmtree(BAU)
    BAU.mkdir(parents=True)
    roh = ARBEIT / "pandoc-standard.docx"
    with open(roh, "wb") as datei:
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.docx"], stdout=datei, check=True
        )
    subprocess.run(["unzip", "-oq", str(roh), "-d", str(BAU)], check=True)
    roh.unlink()


def main():
    grundlage_holen()
    formatvorlagen()
    seitenraender_und_fusszeile()
    if ZIEL.exists():
        ZIEL.unlink()
    subprocess.run(["zip", "-Xrq", str(ZIEL), "."], cwd=BAU, check=True)
    print(f"gebaut: {ZIEL}")


if __name__ == "__main__":
    main()
