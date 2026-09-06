"""
Tests der Wunschliste und der eigenen Pflanzenarten.

Schwerpunkt ist erneut die Zugriffstrennung, hier aber in einer zweiten
Auspraegung: Beim Standort geht es darum, dass fremde Datensaetze nicht
erreichbar sind. Bei den Pflanzenarten kommt hinzu, dass der mitgelieferte
Katalog fuer alle sichtbar ist und nur die selbst angelegten Arten privat
sind. Ein zu weiter Filter faellt in der Oberflaeche nicht auf, weil beide
Faelle dort gleich aussehen.
"""

import pytest
from django.urls import reverse

from plants.models import Bodenart, Feuchtigkeit, Licht, Pflanze, Pflanzenart, Wasserbedarf


@pytest.fixture
def blumenerde(db):
    return Bodenart.objects.create(name="Blumenerde", beschreibung="locker und durchlässig")


@pytest.fixture
def anna(db, django_user_model):
    return django_user_model.objects.create_user("anna", "anna@example.org", "geheim-123")


@pytest.fixture
def bernd(db, django_user_model):
    return django_user_model.objects.create_user("bernd", "bernd@example.org", "geheim-123")


def art_anlegen(bodenarten, name="Fensterblatt", erstellt_von=None):
    art = Pflanzenart.objects.create(
        name=name,
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=15,
        feuchtigkeitsbedarf=Feuchtigkeit.NORMAL,
        wasserbedarf=Wasserbedarf.MITTEL,
        erstellt_von=erstellt_von,
    )
    art.geeignete_bodenarten.set(bodenarten)
    return art


def angemeldet(client, benutzer):
    client.force_login(benutzer)
    return client


# --- Sichtbarkeit der Arten ----------------------------------------------


def test_katalog_ist_fuer_alle_sichtbar(client, anna, bernd, blumenerde):
    art_anlegen([blumenerde], "Fensterblatt")  # ohne Ersteller = Katalog
    for person in (anna, bernd):
        antwort = angemeldet(client, person).get(reverse("pflanzenart_liste"))
        assert "Fensterblatt" in antwort.content.decode()


def test_eigene_art_sieht_nur_die_anlegende_person(client, anna, bernd, blumenerde):
    art_anlegen([blumenerde], "Annas Zimmerlinde", erstellt_von=anna)

    inhalt_anna = angemeldet(client, anna).get(reverse("pflanzenart_liste")).content.decode()
    assert "Annas Zimmerlinde" in inhalt_anna

    inhalt_bernd = angemeldet(client, bernd).get(reverse("pflanzenart_liste")).content.decode()
    assert "Annas Zimmerlinde" not in inhalt_bernd


def test_fremde_art_laesst_sich_nicht_merken(client, anna, bernd, blumenerde):
    """
    Der entscheidende Fall: Bernd kennt die Nummer von Annas Art und ruft die
    Adresse direkt auf. Ohne Einschraenkung koennte er sie uebernehmen und
    saehe damit ihre Angaben.
    """
    fremde = art_anlegen([blumenerde], "Annas Zimmerlinde", erstellt_von=anna)
    antwort = angemeldet(client, bernd).get(reverse("pflanze_hinzufuegen", args=[fremde.pk]))
    assert antwort.status_code == 404


def test_suche_findet_ueber_botanischen_namen(client, anna, blumenerde):
    art = art_anlegen([blumenerde], "Fensterblatt")
    art.botanischer_name = "Monstera deliciosa"
    art.save()
    antwort = angemeldet(client, anna).get(reverse("pflanzenart_liste"), {"suche": "monstera"})
    assert "Fensterblatt" in antwort.content.decode()


# --- Wunschliste ----------------------------------------------------------


def test_merken_legt_eintrag_mit_status_wunsch_an(client, anna, blumenerde):
    art = art_anlegen([blumenerde])
    antwort = angemeldet(client, anna).post(
        reverse("pflanze_hinzufuegen", args=[art.pk]),
        {"eigener_name": "die im Flur", "notiz": ""},
    )
    assert antwort.status_code == 302
    pflanze = Pflanze.objects.get()
    assert pflanze.besitzer == anna
    assert pflanze.status == Pflanze.Status.WUNSCH
    assert pflanze.standort is None


def test_wunschliste_zeigt_nur_eigene_pflanzen(client, anna, bernd, blumenerde):
    art = art_anlegen([blumenerde])
    Pflanze.objects.create(besitzer=anna, art=art, eigener_name="Annas Exemplar")
    Pflanze.objects.create(besitzer=bernd, art=art, eigener_name="Bernds Exemplar")

    inhalt = angemeldet(client, anna).get(reverse("wunschliste")).content.decode()
    assert "Annas Exemplar" in inhalt
    assert "Bernds Exemplar" not in inhalt


def test_fremde_pflanze_ist_nicht_entfernbar(client, anna, bernd, blumenerde):
    art = art_anlegen([blumenerde])
    fremde = Pflanze.objects.create(besitzer=anna, art=art)
    antwort = angemeldet(client, bernd).post(reverse("pflanze_entfernen", args=[fremde.pk]))
    assert antwort.status_code == 404
    assert Pflanze.objects.filter(pk=fremde.pk).exists()


# --- Eigene Pflanzenart anlegen -------------------------------------------


def test_eigene_art_wird_dem_anlegenden_konto_zugeordnet(client, anna, blumenerde):
    antwort = angemeldet(client, anna).post(
        reverse("pflanzenart_anlegen"),
        {
            "name": "Zimmerlinde",
            "botanischer_name": "Sparmannia africana",
            "lichtbedarf": Licht.HELL,
            "temperaturuntergrenze": 12,
            "feuchtigkeitsbedarf": Feuchtigkeit.NORMAL,
            "geeignete_bodenarten": [blumenerde.pk],
            "wasserbedarf": Wasserbedarf.MITTEL,
            "quelle": "eigene Beobachtung",
        },
    )
    assert antwort.status_code == 302
    art = Pflanzenart.objects.get(name="Zimmerlinde")
    assert art.erstellt_von == anna
    assert not art.gehoert_zum_katalog


def test_name_einer_katalogart_wird_abgelehnt(client, anna, blumenerde):
    art_anlegen([blumenerde], "Fensterblatt")
    antwort = angemeldet(client, anna).post(
        reverse("pflanzenart_anlegen"),
        {
            "name": "fensterblatt",  # Gross- und Kleinschreibung darf nichts aendern
            "lichtbedarf": Licht.HELL,
            "temperaturuntergrenze": 15,
            "feuchtigkeitsbedarf": Feuchtigkeit.NORMAL,
            "geeignete_bodenarten": [blumenerde.pk],
            "wasserbedarf": Wasserbedarf.MITTEL,
        },
    )
    assert antwort.status_code == 200  # Formular wird erneut angezeigt
    assert Pflanzenart.objects.filter(erstellt_von=anna).count() == 0


def test_gleicher_name_bei_verschiedenen_personen_ist_erlaubt(client, anna, bernd, blumenerde):
    """Bernd darf eine eigene Art so nennen wie Anna ihre - sie sehen sich nicht."""
    art_anlegen([blumenerde], "Zimmerlinde", erstellt_von=anna)
    antwort = angemeldet(client, bernd).post(
        reverse("pflanzenart_anlegen"),
        {
            "name": "Zimmerlinde",
            "lichtbedarf": Licht.HELL,
            "temperaturuntergrenze": 12,
            "feuchtigkeitsbedarf": Feuchtigkeit.NORMAL,
            "geeignete_bodenarten": [blumenerde.pk],
            "wasserbedarf": Wasserbedarf.MITTEL,
        },
    )
    assert antwort.status_code == 302
    assert Pflanzenart.objects.filter(name="Zimmerlinde").count() == 2


# --- Ohne Anmeldung -------------------------------------------------------


@pytest.mark.parametrize("adresse", ["pflanzenart_liste", "wunschliste", "pflanzenart_anlegen"])
def test_ohne_anmeldung_umleitung_zur_anmeldung(client, db, adresse):
    antwort = client.get(reverse(adresse))
    assert antwort.status_code == 302
    assert "/konten/login/" in antwort.url
