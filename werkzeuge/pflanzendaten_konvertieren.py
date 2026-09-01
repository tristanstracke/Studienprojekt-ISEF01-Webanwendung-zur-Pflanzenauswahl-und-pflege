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

# Die Recherche unterscheidet 14 Bodenbeschreibungen. Fuer die
# Eignungspruefung werden sie auf die Kategorien zusammengefasst, die auch
# ein Nutzender fuer seinen Standort auswaehlen kann - "humos, feucht,
# durchlaessig" kann niemand ueber seinen Balkon aussagen.
BODENART_ZUORDNUNG = {
    1: "Blumenerde",  # locker, durchlaessig
    2: "Kakteenerde",  # sehr durchlaessig
    3: "Blumenerde",  # locker, humos
    4: "Kakteenerde",  # sandig, sehr durchlaessig
    5: "Blumenerde",  # naehrstoffreich, humos
    6: "Kakteenerde",  # sandig, durchlaessig
    7: "lehmiger Gartenboden",  # kalkhaltig, durchlaessig
    8: "Blumenerde",  # humos, locker
    9: "Blumenerde",  # humos, feucht, durchlaessig
    10: "Kakteenerde",  # Kakteenerde, durchlaessig
    11: "Orchideensubstrat",  # Orchideensubstrat, luftig
    12: "Blumenerde",  # locker, gut durchlaessig
    13: "Kakteenerde",  # locker, sehr durchlaessig
    14: "Blumenerde",  # humos, durchlaessig
}

BODENARTEN = [
    "Blumenerde",
    "Kakteenerde",
    "Orchideensubstrat",
    "saure Erde",
    "lehmiger Gartenboden",
]

# Ohne recherchierten Wert wird die mittlere Stufe gesetzt und die Pflanze am
# Ende aufgelistet. Ein geschaetzter Wert waere schlimmer als ein erkennbar
# vorlaeufiger.
LUFTFEUCHTIGKEIT_PLATZHALTER = 2


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

    quellen = {}
    if "Quellen" in wb.sheetnames:
        for zeile in list(wb["Quellen"].values)[1:]:
            if zeile and zeile[0] is not None:
                quellen[zeile[0]] = zeile[1]

    bodenart_pk = {name: i for i, name in enumerate(BODENARTEN, start=1)}
    eintraege = [
        {"model": "plants.bodenart", "pk": pk, "fields": {"name": name}}
        for name, pk in bodenart_pk.items()
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
        bodenart = BODENART_ZUORDNUNG.get(boden_code, "Blumenerde")

        if sp["feuchte"] is not None and isinstance(zeile[sp["feuchte"]], int):
            feuchte = zeile[sp["feuchte"]]
        else:
            feuchte = LUFTFEUCHTIGKEIT_PLATZHALTER
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
                    "botanischer_name": "",
                    "lichtbedarf": licht,
                    "temperaturuntergrenze": zeile[sp["temp_min"]],
                    "feuchtigkeitsbedarf": feuchte,
                    "geeignete_bodenarten": [bodenart_pk[bodenart]],
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
            f"\nOhne recherchierte Luftfeuchtigkeit ({len(ohne_feuchte)}), "
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
