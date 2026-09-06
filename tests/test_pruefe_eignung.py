"""
Tests der Funktion `pruefe_eignung`.

Die einzelnen Regeln sind in test_eignung.py mit Zahlen geprueft. Hier geht es
um die Verdrahtung: Liest die Funktion die richtigen Felder aus Standort und
Pflanzenart, und uebergibt sie die Werte in der richtigen Reihenfolge? Ein
vertauschtes Argumentpaar - etwa Angebot und Bedarf beim Licht - bliebe von
den Regeltests unbemerkt, weil beide Werte dort einzeln gesetzt werden.
Deshalb pruefen diese Tests bewusst unsymmetrische Faelle: Vertauschte
Argumente ergaeben ein anderes Urteil.
"""

import pytest

from plants.eignung import Bewertung, Urteil, pruefe_eignung
from plants.models import (
    Bodenart,
    Feuchtigkeit,
    Licht,
    Pflanzenart,
    Standort,
    Standortart,
    Wasserbedarf,
)


@pytest.fixture
def blumenerde(db):
    return Bodenart.objects.create(name="Blumenerde", beschreibung="locker und durchlässig")


@pytest.fixture
def kakteenerde(db):
    return Bodenart.objects.create(name="Kakteenerde", beschreibung="sehr durchlässig")


@pytest.fixture
def person(db, django_user_model):
    return django_user_model.objects.create_user("anna", "anna@example.org", "geheim-123")


def art(bodenarten, *, licht=Licht.HELL, untergrenze=15, feuchte=Feuchtigkeit.NORMAL, giftig=False):
    a = Pflanzenart.objects.create(
        name="Testpflanze",
        lichtbedarf=licht,
        temperaturuntergrenze=untergrenze,
        feuchtigkeitsbedarf=feuchte,
        giftig=giftig,
        wasserbedarf=Wasserbedarf.MITTEL,
    )
    a.geeignete_bodenarten.set(bodenarten)
    return a


def ort(
    person,
    bodenart,
    *,
    licht=Licht.HELL,
    minimum=18,
    feuchte=Feuchtigkeit.NORMAL,
    standortart=Standortart.INNENRAUM,
    erreichbar=False,
):
    return Standort.objects.create(
        besitzer=person,
        name=f"Ort {Standort.objects.count() + 1}",
        art=standortart,
        lichtangebot=licht,
        minimaltemperatur=minimum,
        luftfeuchtigkeit=feuchte,
        bodenart=bodenart,
        erreichbar_fuer_kinder_haustiere=erreichbar,
    )


def bewertung_von(ergebnis, bezeichnung):
    return next(k.bewertung for k in ergebnis.kriterien if k.bezeichnung == bezeichnung)


def test_alle_kriterien_erfuellt_ergibt_geeignet(person, blumenerde):
    ergebnis = pruefe_eignung(art([blumenerde]), ort(person, blumenerde))
    assert ergebnis.urteil is Urteil.GEEIGNET
    assert len(ergebnis.kriterien) == 5
    assert {k.bezeichnung for k in ergebnis.kriterien} == {
        "Licht",
        "Temperatur",
        "Luftfeuchtigkeit",
        "Bodenart",
        "Giftigkeit",
    }


def test_licht_wird_nicht_vertauscht(person, blumenerde):
    """
    Standort dunkler als der Bedarf: schattig (2) gegen sonnig (5).
    Waeren Angebot und Bedarf vertauscht, lautete die Begruendung
    "zu hell" statt "zu dunkel".
    """
    ergebnis = pruefe_eignung(
        art([blumenerde], licht=Licht.SONNIG),
        ort(person, blumenerde, licht=Licht.SCHATTIG),
    )
    kriterium = next(k for k in ergebnis.kriterien if k.bezeichnung == "Licht")
    assert kriterium.bewertung is Bewertung.VERFEHLT
    assert "zu dunkel" in kriterium.begruendung
    assert ergebnis.urteil is Urteil.UNGEEIGNET


def test_temperatur_wird_nicht_vertauscht(person, blumenerde):
    """Standort faellt auf 5 Grad, die Pflanze vertraegt nur 15."""
    ergebnis = pruefe_eignung(
        art([blumenerde], untergrenze=15),
        ort(person, blumenerde, minimum=5),
    )
    kriterium = next(k for k in ergebnis.kriterien if k.bezeichnung == "Temperatur")
    assert kriterium.bewertung is Bewertung.VERFEHLT
    assert "5" in kriterium.begruendung and "15" in kriterium.begruendung
    assert ergebnis.urteil is Urteil.UNGEEIGNET


def test_luftfeuchtigkeit_wird_nicht_vertauscht(person, blumenerde):
    """Standort trocken (1), Pflanze braucht feucht (3)."""
    ergebnis = pruefe_eignung(
        art([blumenerde], feuchte=Feuchtigkeit.FEUCHT),
        ort(person, blumenerde, feuchte=Feuchtigkeit.TROCKEN),
    )
    kriterium = next(k for k in ergebnis.kriterien if k.bezeichnung == "Luftfeuchtigkeit")
    assert kriterium.bewertung is Bewertung.VERFEHLT
    assert "trocken" in kriterium.begruendung


def test_bodenart_liest_die_menge_der_art(person, blumenerde, kakteenerde):
    """Der Standort hat Blumenerde, die Art vertraegt nur Kakteenerde."""
    ergebnis = pruefe_eignung(art([kakteenerde]), ort(person, blumenerde))
    assert bewertung_von(ergebnis, "Bodenart") is Bewertung.GRENZWERTIG
    assert ergebnis.urteil is Urteil.BEDINGT_GEEIGNET


def test_bodenart_im_garten_ist_ausschluss(person, blumenerde, kakteenerde):
    """Im Freiland laesst sich das Substrat nicht tauschen."""
    ergebnis = pruefe_eignung(
        art([kakteenerde], untergrenze=-20),
        ort(person, blumenerde, standortart=Standortart.GARTEN, minimum=-10),
    )
    assert bewertung_von(ergebnis, "Bodenart") is Bewertung.VERFEHLT
    assert ergebnis.urteil is Urteil.UNGEEIGNET


def test_giftigkeit_beachtet_die_erreichbarkeit(person, blumenerde):
    giftige = art([blumenerde], giftig=True)
    unerreichbar = ort(person, blumenerde, erreichbar=False)
    erreichbar = ort(person, blumenerde, erreichbar=True)

    assert pruefe_eignung(giftige, unerreichbar).urteil is Urteil.GEEIGNET
    ergebnis = pruefe_eignung(giftige, erreichbar)
    assert bewertung_von(ergebnis, "Giftigkeit") is Bewertung.VERFEHLT
    assert ergebnis.urteil is Urteil.UNGEEIGNET


def test_mehrere_bodenarten_werden_alle_beruecksichtigt(person, blumenerde, kakteenerde):
    ergebnis = pruefe_eignung(art([blumenerde, kakteenerde]), ort(person, kakteenerde))
    assert bewertung_von(ergebnis, "Bodenart") is Bewertung.ERFUELLT


def test_ein_grenzwertiges_kriterium_ergibt_bedingt_geeignet(person, blumenerde):
    """Eine Stufe zu dunkel, sonst alles passend."""
    ergebnis = pruefe_eignung(
        art([blumenerde], licht=Licht.HELL),
        ort(person, blumenerde, licht=Licht.HALBSCHATTIG),
    )
    assert bewertung_von(ergebnis, "Licht") is Bewertung.GRENZWERTIG
    assert ergebnis.urteil is Urteil.BEDINGT_GEEIGNET
