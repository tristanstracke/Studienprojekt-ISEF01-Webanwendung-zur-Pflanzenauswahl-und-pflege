"""
Tests der Standortverwaltung.

Diese Tests brauchen eine Datenbank, weil sie das Zusammenspiel von Ansicht,
Formular und Datenhaltung prüfen. Der wichtigste Fall ist die
Zugriffstrennung: Ein fehlender Filter auf den Besitzer ist in der Oberflaeche
unsichtbar und faellt ohne Test niemandem auf.
"""

from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from plants.models import (
    Bodenart,
    Feuchtigkeit,
    Licht,
    Pflanze,
    Pflanzenart,
    Pflegeaufgabe,
    Pflegevorlage,
    Standort,
    Taetigkeit,
    Wasserbedarf,
)


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


def test_formularseiten_zeigen_ihre_ueberschrift(client, anna):
    """
    Django meldet fehlende Vorlagenvariablen nicht, sondern setzt eine leere
    Zeichenkette ein. Ein Tippfehler im Namen bleibt dadurch unbemerkt, bis
    jemand die Seite ansieht - deshalb dieser Test.
    """
    client.force_login(anna)
    assert "Standort anlegen" in client.get(reverse("standort_anlegen")).content.decode()


# --- Loeschen ------------------------------------------------------------
#
# Diese Faelle fehlten lange. Dadurch blieb unbemerkt, dass das Loeschen
# eines Standorts mit Pflanzen im Bestand in einen Datenbankfehler lief:
# Die Fremdschluesselregel setzte die Zuordnung auf leer, die Bedingung
# standort_nur_bei_pflanzen_im_bestand verlangt dort aber einen Standort.


@pytest.fixture
def art(db, bodenart):
    a = Pflanzenart.objects.create(
        name="Aloe vera",
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=10,
        feuchtigkeitsbedarf=Feuchtigkeit.TROCKEN,
        wasserbedarf=Wasserbedarf.GERING,
    )
    a.geeignete_bodenarten.set([bodenart])
    return a


def test_leerer_standort_wird_geloescht(client, anna, bodenart):
    ort = standort_anlegen(anna, bodenart)
    client.login(username="anna", password="geheim-12345")

    antwort = client.post(reverse("standort_loeschen", args=[ort.pk]))

    assert antwort.status_code == 302
    assert not Standort.objects.filter(pk=ort.pk).exists()


def test_standort_mit_pflanzen_wird_samt_pflanzen_geloescht(client, anna, bodenart, art):
    ort = standort_anlegen(anna, bodenart)
    pflanze = Pflanze.objects.create(
        besitzer=anna, art=art, status=Pflanze.Status.BESTAND, standort=ort
    )
    vorlage = Pflegevorlage.objects.create(
        pflanze=pflanze, taetigkeit=Taetigkeit.GIESSEN, intervall_tage=7
    )
    Pflegeaufgabe.objects.create(vorlage=vorlage, faelligkeit=date.today())
    client.login(username="anna", password="geheim-12345")

    antwort = client.post(reverse("standort_loeschen", args=[ort.pk]))

    assert antwort.status_code == 302
    assert not Standort.objects.filter(pk=ort.pk).exists()
    assert not Pflanze.objects.filter(pk=pflanze.pk).exists()
    assert not Pflegeaufgabe.objects.exists()


def test_loeschseite_nennt_die_betroffenen_pflanzen(client, anna, bodenart, art):
    ort = standort_anlegen(anna, bodenart)
    Pflanze.objects.create(besitzer=anna, art=art, status=Pflanze.Status.BESTAND, standort=ort)
    client.login(username="anna", password="geheim-12345")

    antwort = client.get(reverse("standort_loeschen", args=[ort.pk]))

    assert "Aloe vera" in antwort.content.decode()
    assert "mitgelöscht" in antwort.content.decode()


def test_wunschpflanze_bleibt_beim_loeschen_erhalten(client, anna, bodenart, art):
    ort = standort_anlegen(anna, bodenart)
    wunsch = Pflanze.objects.create(besitzer=anna, art=art, status=Pflanze.Status.WUNSCH)
    client.login(username="anna", password="geheim-12345")

    client.post(reverse("standort_loeschen", args=[ort.pk]))

    assert Pflanze.objects.filter(pk=wunsch.pk).exists()
