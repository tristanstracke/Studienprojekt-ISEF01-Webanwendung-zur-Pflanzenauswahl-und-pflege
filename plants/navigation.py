"""
Ermittelt, welcher Punkt der Hauptnavigation zur aufgerufenen Seite gehoert.

Ohne diese Zuordnung waere in der Navigation nur die Startseite markierbar,
denn viele Ansichten haben keinen eigenen Menuepunkt: Der Pflegeplan gehoert
zu "Meine Pflanzen", die Eignungspruefung zu "Pflanzenarten". Die Zuordnung
steht hier und nicht in der Vorlage, damit sie an einer Stelle gepflegt und
geprueft werden kann.
"""

# Reihenfolge egal, die Praefixe ueberschneiden sich nicht:
# "pflanzenart_liste" beginnt nicht mit "pflanze_".
BEREICHE = (
    ("start", "start"),
    ("standort", "standorte"),
    ("pflanzenart", "arten"),
    ("eignung", "arten"),
    ("wunschliste", "wunschliste"),
    ("pflanze_", "wunschliste"),
    ("bestand", "bestand"),
    ("pflegeplan", "bestand"),
    ("pflegevorlage", "bestand"),
    ("kalender", "kalender"),
    ("aufgabe", "kalender"),
)


def bereich_der_seite(request):
    """Stellt jeder Vorlage den Namen des aktiven Navigationsbereichs bereit."""
    name = getattr(request.resolver_match, "url_name", "") or ""
    for praefix, kennung in BEREICHE:
        if name.startswith(praefix):
            return {"navigationsbereich": kennung}
    return {"navigationsbereich": ""}
