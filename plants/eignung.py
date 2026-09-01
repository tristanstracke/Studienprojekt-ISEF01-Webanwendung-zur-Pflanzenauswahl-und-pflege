"""
Eignungspruefung: Passt eine Pflanze zu einem Standort?

Die einzelnen Regeln arbeiten ausschliesslich mit einfachen Werten und kennen
weder Django noch die Datenbank. Nur die Funktion `pruefe_eignung` liest die
Werte aus den Modellobjekten aus. Dadurch laufen die Tests der Regeln ohne
Datenbank und damit in Millisekunden.
"""

from dataclasses import dataclass
from enum import Enum


class Bewertung(Enum):
    """Ergebnis eines einzelnen Kriteriums."""

    ERFUELLT = "erfuellt"
    GRENZWERTIG = "grenzwertig"
    VERFEHLT = "verfehlt"


class Urteil(Enum):
    """Gesamtergebnis der Pruefung."""

    GEEIGNET = "geeignet"
    BEDINGT_GEEIGNET = "bedingt geeignet"
    UNGEEIGNET = "ungeeignet"


@dataclass(frozen=True)
class Kriterium:
    bezeichnung: str
    bewertung: Bewertung
    begruendung: str


@dataclass(frozen=True)
class Ergebnis:
    urteil: Urteil
    kriterien: list[Kriterium]


# --------------------------------------------------------------------------
# Einzelne Kriterien
# --------------------------------------------------------------------------


def bewerte_licht(angebot: int, bedarf: int) -> Kriterium:
    """
    Licht ist eine Ordinalskala von 1 (schattig) bis 4 (vollsonnig).
    Eine Stufe Abweichung gilt als vertretbar, zwei nicht mehr.
    Zu viel Licht wird ebenso bewertet wie zu wenig, da direkte Sonne
    bei schattenliebenden Pflanzen zu Blattschaeden fuehrt.
    """
    abweichung = angebot - bedarf
    if abweichung == 0:
        return Kriterium(
            "Licht", Bewertung.ERFUELLT, "Das Lichtangebot entspricht dem Bedarf der Pflanze."
        )
    if abweichung == -1:
        return Kriterium(
            "Licht",
            Bewertung.GRENZWERTIG,
            "Der Standort ist eine Stufe dunkler als benoetigt. Die Pflanze waechst langsamer.",
        )
    if abweichung == 1:
        return Kriterium(
            "Licht",
            Bewertung.GRENZWERTIG,
            "Der Standort ist eine Stufe heller als benoetigt. "
            "Ein Platz etwas weiter vom Fenster entfernt ist guenstiger.",
        )
    if abweichung < -1:
        return Kriterium(
            "Licht", Bewertung.VERFEHLT, "Der Standort ist deutlich zu dunkel fuer diese Pflanze."
        )
    return Kriterium(
        "Licht", Bewertung.VERFEHLT, "Der Standort ist deutlich zu hell; es drohen Blattschaeden."
    )


def bewerte_temperatur(standortminimum: int, untergrenze: int) -> Kriterium:
    """
    Ausschlusskriterium ohne Toleranzstufe nach unten: Faellt die Temperatur
    unter die Untergrenze der Pflanze, erfriert sie. Das laesst sich durch
    Pflege nicht ausgleichen. Ein Abstand von weniger als zwei Grad gilt als
    grenzwertig, weil die erfassten Werte Schaetzungen des Nutzers sind.
    """
    puffer = standortminimum - untergrenze
    if puffer >= 2:
        return Kriterium(
            "Temperatur",
            Bewertung.ERFUELLT,
            f"Der Standort faellt auf {standortminimum} Grad; die Pflanze "
            f"vertraegt {untergrenze} Grad.",
        )
    if puffer >= 0:
        return Kriterium(
            "Temperatur",
            Bewertung.GRENZWERTIG,
            f"Mit {standortminimum} Grad liegt der Standort nur knapp ueber "
            f"der Untergrenze von {untergrenze} Grad.",
        )
    return Kriterium(
        "Temperatur",
        Bewertung.VERFEHLT,
        f"Der Standort faellt auf {standortminimum} Grad, die Pflanze "
        f"vertraegt nur {untergrenze} Grad.",
    )


def bewerte_feuchtigkeit(angebot: int, bedarf: int) -> Kriterium:
    """Ordinalskala von 1 (trocken) bis 3 (feucht), Toleranz eine Stufe."""
    abweichung = angebot - bedarf
    if abweichung == 0:
        return Kriterium(
            "Luftfeuchtigkeit", Bewertung.ERFUELLT, "Die Luftfeuchtigkeit entspricht dem Bedarf."
        )
    if abweichung == -1:
        return Kriterium(
            "Luftfeuchtigkeit",
            Bewertung.GRENZWERTIG,
            "Es ist etwas zu trocken. Regelmaessiges Besprühen hilft.",
        )
    if abweichung == 1:
        return Kriterium(
            "Luftfeuchtigkeit",
            Bewertung.GRENZWERTIG,
            "Es ist etwas feuchter als noetig. Auf Luftbewegung achten.",
        )
    if abweichung < -1:
        return Kriterium(
            "Luftfeuchtigkeit", Bewertung.VERFEHLT, "Der Standort ist deutlich zu trocken."
        )
    return Kriterium(
        "Luftfeuchtigkeit",
        Bewertung.VERFEHLT,
        "Der Standort ist deutlich zu feucht; es droht Faeulnis.",
    )


def bewerte_bodenart(bodenart: str, geeignete: set[str], austauschbar: bool) -> Kriterium:
    """
    Im Topf laesst sich das Substrat wechseln, im Garten nicht. Deshalb ist eine
    unpassende Bodenart bei Topfpflanzen nur grenzwertig, im Beet aber ein
    Ausschluss.
    """
    if bodenart in geeignete:
        return Kriterium(
            "Bodenart", Bewertung.ERFUELLT, f"{bodenart} ist fuer diese Pflanze geeignet."
        )
    if austauschbar:
        return Kriterium(
            "Bodenart",
            Bewertung.GRENZWERTIG,
            f"{bodenart} passt nicht, laesst sich beim Umtopfen aber "
            f"gegen ein geeignetes Substrat tauschen.",
        )
    return Kriterium(
        "Bodenart",
        Bewertung.VERFEHLT,
        f"{bodenart} ist ungeeignet und im Freiland nicht austauschbar.",
    )


def bewerte_giftigkeit(giftig: bool, erreichbar: bool) -> Kriterium:
    """
    Ausschlusskriterium ohne Toleranzstufe: Eine giftige Pflanze in Reichweite
    von Kindern oder Haustieren ist keine Frage des Pflanzenwohls, sondern der
    Sicherheit.
    """
    if not giftig:
        return Kriterium("Giftigkeit", Bewertung.ERFUELLT, "Die Pflanze ist ungiftig.")
    if not erreichbar:
        return Kriterium(
            "Giftigkeit",
            Bewertung.ERFUELLT,
            "Die Pflanze ist giftig, der Standort aber fuer Kinder und Haustiere nicht erreichbar.",
        )
    return Kriterium(
        "Giftigkeit",
        Bewertung.VERFEHLT,
        "Die Pflanze ist giftig und der Standort fuer Kinder oder Haustiere erreichbar.",
    )


# --------------------------------------------------------------------------
# Gesamturteil
# --------------------------------------------------------------------------


def bilde_urteil(kriterien: list[Kriterium]) -> Urteil:
    """
    Ein verfehltes Kriterium genuegt fuer ein ablehnendes Urteil. Die Kriterien
    werden also nicht gegeneinander verrechnet: Ein Standort, an dem die Pflanze
    erfriert, wird nicht dadurch geeignet, dass Licht und Boden stimmen.
    """
    bewertungen = [k.bewertung for k in kriterien]
    if Bewertung.VERFEHLT in bewertungen:
        return Urteil.UNGEEIGNET
    if Bewertung.GRENZWERTIG in bewertungen:
        return Urteil.BEDINGT_GEEIGNET
    return Urteil.GEEIGNET


# --------------------------------------------------------------------------
# Einstiegspunkt: einzige Funktion, die die Modellobjekte kennt
# --------------------------------------------------------------------------

BODEN_AUSTAUSCHBAR = {"innen": True, "balkon": True, "garten": False}


def pruefe_eignung(pflanze, standort) -> Ergebnis:
    kriterien = [
        bewerte_licht(standort.lichtangebot, pflanze.lichtbedarf),
        bewerte_temperatur(standort.minimaltemperatur, pflanze.temperaturuntergrenze),
        bewerte_feuchtigkeit(standort.luftfeuchtigkeit, pflanze.feuchtigkeitsbedarf),
        bewerte_bodenart(
            standort.bodenart.name,
            {b.name for b in pflanze.geeignete_bodenarten.all()},
            BODEN_AUSTAUSCHBAR[standort.art],
        ),
        bewerte_giftigkeit(pflanze.giftig, standort.erreichbar_fuer_kinder_haustiere),
    ]
    return Ergebnis(bilde_urteil(kriterien), kriterien)
