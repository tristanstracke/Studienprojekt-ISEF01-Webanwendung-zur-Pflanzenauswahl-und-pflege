"""
Wandelt die recherchierten Pflanzendaten aus der Excel-Datei in eine
Django-Fixture um.

Aufruf:
    python werkzeuge/pflanzendaten_konvertieren.py <excel-datei>

Die erzeugte Fixture wird versioniert und in jeder Umgebung mit
    python manage.py loaddata bodenarten pflanzenarten
eingespielt. Der Umweg ueber eine Fixture statt eines direkten Imports hat
zwei Gruende: Die Anwendung braucht in der Produktion keine Excel-Bibliothek,
und der eingespielte Datenbestand ist im Repository nachvollziehbar.
"""

import json
import sys
from pathlib import Path

from openpyxl import load_workbook

# Die Recherche fasst die Bodenbeschreibungen zu fuenf Kategorien zusammen
# (Blatt "Hinweis zur Datenaufbereitung"). Der Bodenart-Code der Tabelle
# verweist unmittelbar auf diese Liste. Jede Kategorie traegt zusaetzlich
# einen gelaeufigen Namen: Die fachliche Beschreibung allein - etwa
# "humos, feucht" - kann eine Privatperson ueber ihren Balkon nicht
# beantworten, und genau diese Angabe verlangt die Eignungspruefung.
BODENARTEN = [
    ("Blumenerde", "locker und durchlässig"),
    ("Kakteenerde oder Sandboden", "trocken und sehr durchlässig"),
    ("Humose Blumenerde", "nährstoffreich und locker"),
    ("Humose Feuchterde", "nährstoffreich und gleichmäßig feucht"),
    ("Orchideensubstrat", "luftig und grob"),
]


def ganzzahl(zeile, index):
    """Liefert den Wert, wenn es eine positive ganze Zahl ist, sonst None."""
    if index is None:
        return None
    wert = zeile[index]
    return wert if isinstance(wert, int) and wert > 0 else None


def mittelwert(zeile, index_min, index_max):
    a = ganzzahl(zeile, index_min)
    b = ganzzahl(zeile, index_max)
    if a and b:
        return round((a + b) / 2)
    return a or b


def monate_in_tage(zeile, index):
    monate = ganzzahl(zeile, index)
    return monate * 30 if monate else None


def spaltenindex(kopfzeile, teil):
    """Sucht die Spalte. Eine genaue Uebereinstimmung geht vor, weil
    "Pflanze" sonst auf "Pflanzen-ID" treffen wuerde."""
    for i, wert in enumerate(kopfzeile):
        if wert and str(wert).strip().lower() == teil.lower():
            return i
    for i, wert in enumerate(kopfzeile):
        if wert and teil.lower() in str(wert).lower():
            return i
    return None


def konvertieren(pfad: Path):
    wb = load_workbook(pfad, data_only=True)
    ws = wb["Pflanzendaten"]
    zeilen = list(ws.values)
    kopf = list(zeilen[0])

    sp = {
        "id": spaltenindex(kopf, "ID"),
        "name": spaltenindex(kopf, "Pflanze"),
        "licht": spaltenindex(kopf, "Lichtbedarf"),
        "wasser": spaltenindex(kopf, "Wasserbedarf"),
        "giftig": spaltenindex(kopf, "Giftig"),
        "hoehe": spaltenindex(kopf, "Größe"),
        "temp_min": spaltenindex(kopf, "Temperatur min"),
        "boden": spaltenindex(kopf, "Bodenart-Code"),
        "feuchte": spaltenindex(kopf, "Luftfeuchtigkeit"),
        "giessen_min": spaltenindex(kopf, "Gießen min"),
        "giessen_max": spaltenindex(kopf, "Gießen max"),
        "duengen": spaltenindex(kopf, "Düngen"),
        "umtopfen": spaltenindex(kopf, "Umtopfen"),
        "rueckschnitt": spaltenindex(kopf, "Rückschnitt"),
    }

    # Das Quellenblatt fuehrt je Art die Institution, den Link und den
    # botanischen Namen. Belegt wird mit Institution und Link, damit die
    # Angabe im Projektbericht nachvollziehbar ist.
    quellen, botanisch = {}, {}
    if "Quellen" in wb.sheetnames:
        q = list(wb["Quellen"].values)
        qkopf = list(q[0])
        s_art = spaltenindex(qkopf, "Pflanze")
        s_inst = spaltenindex(qkopf, "Institution")
        s_link = spaltenindex(qkopf, "Direktlink")
        for zeile in q[1:]:
            if not zeile or not isinstance(zeile[0], int):
                continue
            teile = [zeile[i] for i in (s_inst, s_link) if i is not None and zeile[i]]
            quellen[zeile[0]] = ", ".join(str(t).strip() for t in teile)[:300]
            if s_art is not None and zeile[s_art] and "(" in str(zeile[s_art]):
                botanisch[zeile[0]] = str(zeile[s_art]).split("(", 1)[1].rstrip(") ").strip()

    eintraege = [
        {
            "model": "plants.bodenart",
            "pk": i,
            "fields": {"name": name, "beschreibung": beschreibung},
        }
        for i, (name, beschreibung) in enumerate(BODENARTEN, start=1)
    ]

    ohne_feuchte = []
    ohne_quelle = []
    empfehlungen = []
    pk = 0
    empfehlung_pk = 0

    for zeile in zeilen[1:]:
        name = zeile[sp["name"]] if sp["name"] is not None else None
        licht = zeile[sp["licht"]] if sp["licht"] is not None else None
        # Legendenzeilen am Tabellenende haben keinen Zahlenwert beim Licht.
        if not name or not isinstance(licht, int):
            continue

        pk += 1
        art_id = zeile[sp["id"]]
        boden_code = zeile[sp["boden"]]
        if not isinstance(boden_code, int) or not 1 <= boden_code <= len(BODENARTEN):
            sys.exit(f"Unbekannter Bodenart-Code {boden_code!r} bei {name}")

        feuchte = zeile[sp["feuchte"]] if sp["feuchte"] is not None else None
        if not isinstance(feuchte, int):
            feuchte = 2
            ohne_feuchte.append(name)

        quelle = quellen.get(art_id, "")
        if not quelle:
            ohne_quelle.append(name)

        # Aus der Recherche stammen Spannen ("giessen alle 7 bis 10 Tage").
        # Uebernommen wird die Mitte, weil die Anwendung ein festes Intervall
        # braucht; die Person kann es an ihrer Pflanze anpassen.
        # Ein Wert von 0 bedeutet in der Recherche "nicht vorgesehen".
        for taetigkeit, tage in [
            ("giessen", mittelwert(zeile, sp["giessen_min"], sp["giessen_max"])),
            ("duengen", ganzzahl(zeile, sp["duengen"])),
            ("umtopfen", monate_in_tage(zeile, sp["umtopfen"])),
            ("schneiden", ganzzahl(zeile, sp["rueckschnitt"])),
        ]:
            if tage:
                empfehlung_pk += 1
                empfehlungen.append(
                    {
                        "model": "plants.pflegeempfehlung",
                        "pk": empfehlung_pk,
                        "fields": {
                            "art": pk,
                            "taetigkeit": taetigkeit,
                            "intervall_tage": tage,
                            "hinweis": "",
                        },
                    }
                )

        eintraege.append(
            {
                "model": "plants.pflanzenart",
                "pk": pk,
                "fields": {
                    "name": str(name).strip(),
                    "botanischer_name": botanisch.get(art_id, ""),
                    "lichtbedarf": licht,
                    "temperaturuntergrenze": zeile[sp["temp_min"]],
                    "feuchtigkeitsbedarf": feuchte,
                    "geeignete_bodenarten": [boden_code],
                    "giftig": bool(zeile[sp["giftig"]]),
                    "wasserbedarf": zeile[sp["wasser"]],
                    "endwuchshoehe_cm": zeile[sp["hoehe"]],
                    "quelle": quelle or "",
                    "erstellt_von": None,
                },
            }
        )

    ziel = Path("plants/fixtures/pflanzenarten.json")
    ziel.write_text(
        json.dumps(eintraege + empfehlungen, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(
        f"{pk} Pflanzenarten, {len(BODENARTEN)} Bodenarten und "
        f"{empfehlung_pk} Pflegeempfehlungen geschrieben nach {ziel}"
    )
    if ohne_feuchte:
        print(
            f"\nACHTUNG - ohne recherchierte Luftfeuchtigkeit ({len(ohne_feuchte)}), "
            f"vorlaeufig auf 'normal' gesetzt:"
        )
        print("  " + ", ".join(ohne_feuchte))
    if ohne_quelle:
        print(f"\nOhne Quellenangabe ({len(ohne_quelle)}):")
        print("  " + ", ".join(ohne_quelle))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python werkzeuge/pflanzendaten_konvertieren.py <excel-datei>")
    konvertieren(Path(sys.argv[1]))
