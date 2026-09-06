"""
Tests der Ableitung von Pflegevorlagen aus den Empfehlungen einer Art.
"""

from datetime import date, timedelta

import pytest

from plants.models import (
    Feuchtigkeit,
    Licht,
    Pflanze,
    Pflanzenart,
    Pflegeempfehlung,
    Taetigkeit,
    Wasserbedarf,
)
from plants.pflege import erzeuge_pflegevorlagen


@pytest.fixture
def person(db, django_user_model):
    return django_user_model.objects.create_user("anna", "anna@example.org", "geheim-123")


@pytest.fixture
def art_mit_empfehlungen(db):
    art = Pflanzenart.objects.create(
        name="Fensterblatt",
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=15,
        feuchtigkeitsbedarf=Feuchtigkeit.NORMAL,
        wasserbedarf=Wasserbedarf.MITTEL,
    )
    Pflegeempfehlung.objects.create(art=art, taetigkeit=Taetigkeit.GIESSEN, intervall_tage=7)
    Pflegeempfehlung.objects.create(art=art, taetigkeit=Taetigkeit.DUENGEN, intervall_tage=28)
    return art


def test_aus_jeder_empfehlung_entsteht_eine_vorlage(person, art_mit_empfehlungen):
    pflanze = Pflanze.objects.create(besitzer=person, art=art_mit_empfehlungen)
    assert erzeuge_pflegevorlagen(pflanze) == 2
    assert set(pflanze.pflegevorlagen.values_list("taetigkeit", "intervall_tage")) == {
        (Taetigkeit.GIESSEN, 7),
        (Taetigkeit.DUENGEN, 28),
    }


def test_erste_aufgabe_liegt_ein_intervall_in_der_zukunft(person, art_mit_empfehlungen):
    """Eine frisch angeschaffte Pflanze ist versorgt - nichts ist sofort faellig."""
    pflanze = Pflanze.objects.create(besitzer=person, art=art_mit_empfehlungen)
    erzeuge_pflegevorlagen(pflanze, ab_datum=date(2026, 9, 1))
    giessen = pflanze.pflegevorlagen.get(taetigkeit=Taetigkeit.GIESSEN)
    assert giessen.aufgaben.get().faelligkeit == date(2026, 9, 8)
    duengen = pflanze.pflegevorlagen.get(taetigkeit=Taetigkeit.DUENGEN)
    assert duengen.aufgaben.get().faelligkeit == date(2026, 9, 29)


def test_zweiter_aufruf_legt_nichts_doppelt_an(person, art_mit_empfehlungen):
    pflanze = Pflanze.objects.create(besitzer=person, art=art_mit_empfehlungen)
    erzeuge_pflegevorlagen(pflanze)
    assert erzeuge_pflegevorlagen(pflanze) == 0
    assert pflanze.pflegevorlagen.count() == 2


def test_eigene_aenderung_bleibt_beim_zweiten_aufruf_erhalten(person, art_mit_empfehlungen):
    """Wer sein Intervall anpasst, soll es nicht durch die Empfehlung verlieren."""
    pflanze = Pflanze.objects.create(besitzer=person, art=art_mit_empfehlungen)
    erzeuge_pflegevorlagen(pflanze)
    vorlage = pflanze.pflegevorlagen.get(taetigkeit=Taetigkeit.GIESSEN)
    vorlage.intervall_tage = 10
    vorlage.save()

    erzeuge_pflegevorlagen(pflanze)
    vorlage.refresh_from_db()
    assert vorlage.intervall_tage == 10


def test_art_ohne_empfehlungen_ergibt_keine_vorlagen(person, db):
    art = Pflanzenart.objects.create(
        name="Unbekanntes",
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=15,
        feuchtigkeitsbedarf=Feuchtigkeit.NORMAL,
        wasserbedarf=Wasserbedarf.MITTEL,
    )
    pflanze = Pflanze.objects.create(besitzer=person, art=art)
    assert erzeuge_pflegevorlagen(pflanze) == 0


def test_ohne_datum_wird_ab_heute_gerechnet(person, art_mit_empfehlungen):
    pflanze = Pflanze.objects.create(besitzer=person, art=art_mit_empfehlungen)
    erzeuge_pflegevorlagen(pflanze)
    giessen = pflanze.pflegevorlagen.get(taetigkeit=Taetigkeit.GIESSEN)
    assert giessen.aufgaben.get().faelligkeit == date.today() + timedelta(days=7)
