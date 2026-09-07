"""
Tests des Kommandos "testdaten".

Wichtig ist weniger, dass Daten entstehen, als dass ein zweiter Lauf nichts
verdoppelt: Das Kommando wird nach jedem Redeploy erneut ausgefuehrt.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from plants.models import (
    Bodenart,
    Pflanze,
    Pflanzenart,
    Pflegeaufgabe,
    Pflegeempfehlung,
    Taetigkeit,
)
from plants.pflege import heute


@pytest.fixture
def katalog(db):
    """Fuenf Arten und eine Bodenart, damit das Kommando arbeiten kann."""
    erde = Bodenart.objects.create(name="Blumenerde", beschreibung="locker")
    for nummer in range(5):
        art = Pflanzenart.objects.create(
            name=f"Testart {nummer}",
            lichtbedarf=4,
            temperaturuntergrenze=15,
            feuchtigkeitsbedarf=2,
            wasserbedarf=3,
        )
        art.geeignete_bodenarten.set([erde])
        Pflegeempfehlung.objects.create(art=art, taetigkeit=Taetigkeit.GIESSEN, intervall_tage=7)
        Pflegeempfehlung.objects.create(art=art, taetigkeit=Taetigkeit.DUENGEN, intervall_tage=28)
    return erde


def test_legt_vier_zugaenge_und_einen_administrator_an(katalog):
    call_command("testdaten")
    Benutzer = get_user_model()
    assert Benutzer.objects.count() == 5
    verwaltung = Benutzer.objects.get(username="admin")
    assert verwaltung.is_superuser and verwaltung.is_staff


def test_zweiter_lauf_verdoppelt_nichts(katalog):
    call_command("testdaten")
    anzahl_pflanzen = Pflanze.objects.count()
    anzahl_aufgaben = Pflegeaufgabe.objects.count()
    call_command("testdaten")
    assert Pflanze.objects.count() == anzahl_pflanzen
    assert Pflegeaufgabe.objects.count() == anzahl_aufgaben
    assert get_user_model().objects.count() == 5


def test_kalender_zeigt_ueberfaellige_und_heutige_aufgaben(katalog):
    call_command("testdaten")
    benutzer = get_user_model().objects.get(username="kai")
    offen = Pflegeaufgabe.objects.filter(
        vorlage__pflanze__besitzer=benutzer, erledigt_am__isnull=True
    )
    assert offen.filter(faelligkeit__lt=heute()).exists()
    assert offen.filter(faelligkeit=heute()).exists()


def test_leeres_konto_bleibt_leer(katalog):
    call_command("testdaten")
    benutzer = get_user_model().objects.get(username="kai-neu")
    assert not Pflanze.objects.filter(besitzer=benutzer).exists()


def test_anmeldung_mit_dem_dokumentierten_kennwort(client, katalog):
    call_command("testdaten")
    assert client.login(username="kai", password="Pflanze-Test-2026")


def test_ohne_katalog_bricht_das_kommando_ab(db, capsys):
    call_command("testdaten")
    assert get_user_model().objects.count() == 0
    assert "Pflanzenkatalog ist leer" in capsys.readouterr().err
