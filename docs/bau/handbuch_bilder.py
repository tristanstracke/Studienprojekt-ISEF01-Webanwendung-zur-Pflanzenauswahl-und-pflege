"""
Fuegt die Bildschirmfotos an den passenden Stellen in das Benutzerhandbuch ein.

Die Zuordnung steht hier und nicht im Handbuchtext, damit die Markdown-Fassung
im Repository ohne Bildverweise lesbar bleibt und die Bilder erst beim Bauen
der Word-Fassung hinzukommen.
"""

import os
from pathlib import Path

DOCS = Path(os.environ.get("CFP_DOCS", Path(__file__).resolve().parent.parent))
QUELLE = DOCS / "benutzerhandbuch.md"
BILDER = DOCS / "bilder" / "handbuch"
ZIEL = DOCS / "bau" / "ausgabe" / "benutzerhandbuch_mit_bildern.md"

# Vor welcher Zeile welches Bild mit welcher Unterschrift steht.
EINFUEGUNGEN = [
    (
        "Nach der Anmeldung sehen Sie die **Übersicht**",
        "01-anmeldung.png",
        "Abbildung 1: Anmeldung",
    ),
    (
        "Abmelden können Sie sich jederzeit oben rechts.",
        "02-uebersicht.png",
        "Abbildung 2: Übersicht mit den vier Bereichen",
    ),
    (
        "**Navigation → Standorte → Standort anlegen.** Sie füllen aus:",
        "03-standorte.png",
        "Abbildung 3: Liste der angelegten Standorte",
    ),
    (
        "Sie können einen Standort jederzeit **Ändern**;",
        "04-standort-anlegen.png",
        "Abbildung 4: Formular zum Anlegen eines Standorts",
    ),
    (
        "Zu jeder Art gibt es zwei Möglichkeiten:",
        "05-pflanzenarten.png",
        "Abbildung 5: Pflanzenkatalog mit Suchfeld",
    ),
    (
        "**Die Wunschliste** erreichen Sie über die Navigation.",
        "06-eigene-art-anlegen.png",
        "Abbildung 6: Eigene Pflanzenart anlegen",
    ),
    (
        "Der Klick auf **Passt sie?** vergleicht die Ansprüche",
        "07-wunschliste.png",
        "Abbildung 7: Wunschliste",
    ),
    (
        "Darunter steht, **warum**. Geprüft werden fünf Merkmale:",
        "08-eignungspruefung.png",
        "Abbildung 8: Eignungsprüfung mit Urteil und Begründung je Standort",
    ),
    (
        "Beim Anschaffen geschieht zweierlei automatisch:",
        "09-anschaffen.png",
        "Abbildung 9: Pflanze anschaffen und Standort zuweisen",
    ),
    (
        "**Navigation → Pflegekalender.** Alle offenen Aufgaben",
        "10-meine-pflanzen.png",
        "Abbildung 10: Meine Pflanzen",
    ),
    (
        "Jede Zeile nennt Tätigkeit, Pflanze, Standort, Fälligkeit",
        "11-pflegekalender.png",
        "Abbildung 11: Pflegekalender mit vier Gruppen",
    ),
    (
        "**Meine Pflanzen → Pflegeplan** bei der jeweiligen Pflanze.",
        "12-pflegeplan.png",
        "Abbildung 12: Pflegeplan einer Pflanze",
    ),
]


def main() -> None:
    zeilen = QUELLE.read_text(encoding="utf-8").splitlines()
    ergebnis: list[str] = []
    offen = list(EINFUEGUNGEN)

    for zeile in zeilen:
        if offen and zeile.startswith(offen[0][0][:40]):
            _, datei, unterschrift = offen.pop(0)
            pfad = BILDER / datei
            if not pfad.is_file():
                raise SystemExit(f"Bild fehlt: {pfad}")
            ergebnis += ["", f"![{unterschrift}]({pfad}){{width=13cm}}", ""]
        ergebnis.append(zeile)

    if offen:
        raise SystemExit("Nicht zugeordnet: " + ", ".join(d for _, d, _ in offen))

    ZIEL.write_text("\n".join(ergebnis) + "\n", encoding="utf-8")
    print(f"{len(EINFUEGUNGEN)} Bilder eingefuegt")


if __name__ == "__main__":
    main()
