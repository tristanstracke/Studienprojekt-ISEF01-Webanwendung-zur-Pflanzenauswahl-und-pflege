"""
Tests der Standortverwaltung.

Diese Tests brauchen eine Datenbank, weil sie das Zusammenspiel von Ansicht,
Formular und Datenhaltung pruefen. Der wichtigste Fall ist die
Zugriffstrennung: Ein fehlender Filter auf den Besitzer ist in der Oberflaeche
unsichtbar und faellt ohne Test niemandem auf.
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from plants.models import Bodenart, Standort


@pytest.fixture
def bodenart(db):
    return Bodenart.objects.create(name="Blumenerde")


@pytest.fixture
def anna(db):
    return User.objects.create_user("anna", password="geheim-12345")


@pytest.fixture
def bernd(db):
    return User.objects.create_user("bernd", password="geheim-12345")


def standort_anlegen(besitzer, bodenart, name="Wohnzimmer"):
    return Standort.objects.create(
        besitzer=besitzer,
        name=name,
        art="innen",
        lichtangebot=4,
        minimaltemperatur=18,
        luftfeuchtigkeit=2,
        bodenart=bodenart,
    )


# --- Zugriffsschutz ------------------------------------------------------


def test_ohne_anmeldung_umleitung_zur_anmeldung(client):
    antwort = client.get(reverse("standort_liste"))
    assert antwort.status_code == 302
    assert "/konten/login/" in antwort.url


def test_liste_zeigt_nur_eigene_standorte(client, anna, bernd, bodenart):
    standort_anlegen(anna, bodenart, "Annas Balkon")
    standort_anlegen(bernd, bodenart, "Bernds Balkon")

    client.force_login(anna)
    inhalt = client.get(reverse("standort_liste")).content.decode()

    assert "Annas Balkon" in inhalt
    assert "Bernds Balkon" not in inhalt


def test_fremder_standort_ist_nicht_aufrufbar(client, anna, bernd, bodenart):
    """
    Der Kernfall: Auch wer die Adresse eines fremden Datensatzes kennt, darf
    ihn nicht sehen. Erwartet wird 404 und nicht 403, damit die blosse
    Existenz des Datensatzes nicht erkennbar wird.
    """
    fremder = standort_anlegen(bernd, bodenart)

    client.force_login(anna)
    antwort = client.get(reverse("standort_bearbeiten", args=[fremder.pk]))

    assert antwort.status_code == 404


def test_fremder_standort_ist_nicht_aenderbar(client, anna, bernd, bodenart):
    fremder = standort_anlegen(bernd, bodenart)

    client.force_login(anna)
    client.post(
        reverse("standort_bearbeiten", args=[fremder.pk]),
        {
            "name": "Uebernommen",
            "art": "innen",
            "lichtangebot": 1,
            "minimaltemperatur": 0,
            "luftfeuchtigkeit": 1,
            "bodenart": bodenart.pk,
        },
    )

    fremder.refresh_from_db()
    assert fremder.name == "Wohnzimmer"


# --- Anlegen und Aendern -------------------------------------------------


def test_anlegen_setzt_den_angemeldeten_benutzer_als_besitzer(client, anna, bodenart):
    client.force_login(anna)
    antwort = client.post(
        reverse("standort_anlegen"),
        {
            "name": "Balkon Süd",
            "art": "balkon",
            "lichtangebot": 5,
            "minimaltemperatur": -5,
            "luftfeuchtigkeit": 2,
            "bodenart": bodenart.pk,
        },
    )

    assert antwort.status_code == 302
    standort = Standort.objects.get(name="Balkon Süd")
    assert standort.besitzer == anna


def test_gleicher_name_zweimal_wird_abgelehnt(client, anna, bodenart):
    standort_anlegen(anna, bodenart, "Balkon")

    client.force_login(anna)
    antwort = client.post(
        reverse("standort_anlegen"),
        {
            "name": "balkon",  # andere Schreibweise, gleiche Bedeutung
            "art": "balkon",
            "lichtangebot": 5,
            "minimaltemperatur": -5,
            "luftfeuchtigkeit": 2,
            "bodenart": bodenart.pk,
        },
    )

    assert antwort.status_code == 200  # Formular wird erneut angezeigt
    assert Standort.objects.filter(besitzer=anna).count() == 1


def test_gleicher_name_bei_verschiedenen_personen_ist_erlaubt(client, anna, bernd, bodenart):
    standort_anlegen(bernd, bodenart, "Balkon")

    client.force_login(anna)
    client.post(
        reverse("standort_anlegen"),
        {
            "name": "Balkon",
            "art": "balkon",
            "lichtangebot": 5,
            "minimaltemperatur": -5,
            "luftfeuchtigkeit": 2,
            "bodenart": bodenart.pk,
        },
    )

    assert Standort.objects.filter(name__iexact="Balkon").count() == 2
