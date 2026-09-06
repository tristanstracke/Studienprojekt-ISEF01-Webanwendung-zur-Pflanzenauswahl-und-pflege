"""
Tests des Pflegekalenders.

Zwei Regeln stehen im Mittelpunkt. Erstens: Die Folgeaufgabe rechnet ab dem
Tag der Erledigung, nicht ab der urspruenglichen Faelligkeit - sonst bliebe
ein Rueckstand dauerhaft bestehen. Zweitens: Zweimaliges Abhaken darf keine
zweite Folgeaufgabe erzeugen; das passiert im Betrieb durch einen Doppelklick
oder ein erneutes Laden der Seite.
"""

from datetime import date, timedelta

import pytest
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
    Standortart,
    Taetigkeit,
    Wasserbedarf,
)
from plants.pflege import hake_ab, nach_faelligkeit


@pytest.fixture
def anna(db, django_user_model):
    return django_user_model.objects.create_user("anna", "anna@example.org", "geheim-123")


@pytest.fixture
def bernd(db, django_user_model):
    return django_user_model.objects.create_user("bernd", "bernd@example.org", "geheim-123")


@pytest.fixture
def erde(db):
    return Bodenart.objects.create(name="Blumenerde", beschreibung="locker und durchlässig")


def pflanze_mit_vorlage(
    besitzer, erde, intervall=7, taetigkeit=Taetigkeit.GIESSEN, faellig=None, name="Fensterblatt"
):
    art = Pflanzenart.objects.create(
        name=name,
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=15,
        feuchtigkeitsbedarf=Feuchtigkeit.NORMAL,
        wasserbedarf=Wasserbedarf.MITTEL,
    )
    art.geeignete_bodenarten.set([erde])
    ort = Standort.objects.create(
        besitzer=besitzer,
        name=f"Ort {Standort.objects.count() + 1}",
        art=Standortart.INNENRAUM,
        lichtangebot=Licht.HELL,
        minimaltemperatur=18,
        luftfeuchtigkeit=Feuchtigkeit.NORMAL,
        bodenart=erde,
    )
    pflanze = Pflanze.objects.create(
        besitzer=besitzer, art=art, status=Pflanze.Status.BESTAND, standort=ort
    )
    vorlage = Pflegevorlage.objects.create(
        pflanze=pflanze, taetigkeit=taetigkeit, intervall_tage=intervall
    )
    aufgabe = Pflegeaufgabe.objects.create(vorlage=vorlage, faelligkeit=faellig or date.today())
    return pflanze, vorlage, aufgabe


def angemeldet(client, benutzer):
    client.force_login(benutzer)
    return client


# --- Abhaken ---------------------------------------------------------------


def test_folgeaufgabe_rechnet_ab_dem_erledigungstag(anna, erde):
    """
    Drei Tage zu spaet gegossen: Der naechste Termin liegt sieben Tage nach
    der Erledigung, nicht sieben Tage nach dem urspruenglichen Termin. Sonst
    waere die Pflanze dauerhaft im Rueckstand.
    """
    _, _, aufgabe = pflanze_mit_vorlage(anna, erde, intervall=7, faellig=date(2026, 9, 1))
    folge = hake_ab(aufgabe, erledigt_am=date(2026, 9, 4))

    aufgabe.refresh_from_db()
    assert aufgabe.erledigt_am == date(2026, 9, 4)
    assert folge.faelligkeit == date(2026, 9, 11)


def test_zweites_abhaken_erzeugt_keine_zweite_folgeaufgabe(anna, erde):
    _, vorlage, aufgabe = pflanze_mit_vorlage(anna, erde)
    hake_ab(aufgabe)
    assert hake_ab(aufgabe) is None
    assert vorlage.aufgaben.count() == 2  # die erledigte und genau eine offene


def test_erledigte_aufgabe_bleibt_als_historie(anna, erde):
    _, vorlage, aufgabe = pflanze_mit_vorlage(anna, erde)
    hake_ab(aufgabe, erledigt_am=date(2026, 9, 4))
    assert vorlage.aufgaben.filter(erledigt_am__isnull=False).count() == 1


# --- Einteilung nach Faelligkeit ------------------------------------------


def test_einteilung_nach_faelligkeit(anna, erde):
    stichtag = date(2026, 9, 10)
    tage = [
        stichtag - timedelta(days=2),
        stichtag,
        stichtag + timedelta(days=3),
        stichtag + timedelta(days=20),
    ]
    aufgaben = []
    for i, tag in enumerate(tage):
        _, _, aufgabe = pflanze_mit_vorlage(anna, erde, faellig=tag, name=f"Art {i}")
        aufgaben.append(aufgabe)

    gruppen = nach_faelligkeit(aufgaben, stichtag=stichtag)
    assert gruppen["ueberfaellig"] == [aufgaben[0]]
    assert gruppen["heute"] == [aufgaben[1]]
    assert gruppen["woche"] == [aufgaben[2]]
    assert gruppen["spaeter"] == [aufgaben[3]]


def test_genau_sieben_tage_zaehlen_noch_zur_woche(anna, erde):
    stichtag = date(2026, 9, 10)
    _, _, aufgabe = pflanze_mit_vorlage(anna, erde, faellig=stichtag + timedelta(days=7))
    gruppen = nach_faelligkeit([aufgabe], stichtag=stichtag)
    assert gruppen["woche"] == [aufgabe]
    assert gruppen["spaeter"] == []


# --- Ansichten und Zugriffstrennung ---------------------------------------


def test_kalender_zeigt_nur_eigene_aufgaben(client, anna, bernd, erde):
    pflanze_mit_vorlage(anna, erde, name="Annas Pflanze")
    pflanze_mit_vorlage(bernd, erde, name="Bernds Pflanze")
    inhalt = angemeldet(client, anna).get(reverse("kalender")).content.decode()
    assert "Annas Pflanze" in inhalt
    assert "Bernds Pflanze" not in inhalt


def test_fremde_aufgabe_ist_nicht_abhakbar(client, anna, bernd, erde):
    _, _, fremde = pflanze_mit_vorlage(anna, erde)
    antwort = angemeldet(client, bernd).post(reverse("aufgabe_abhaken", args=[fremde.pk]))
    assert antwort.status_code == 404
    fremde.refresh_from_db()
    assert fremde.erledigt_am is None


def test_abhaken_nur_ueber_post(client, anna, erde):
    """Ein Aufruf per Adresszeile darf nichts veraendern."""
    _, _, aufgabe = pflanze_mit_vorlage(anna, erde)
    antwort = angemeldet(client, anna).get(reverse("aufgabe_abhaken", args=[aufgabe.pk]))
    assert antwort.status_code == 302
    aufgabe.refresh_from_db()
    assert aufgabe.erledigt_am is None


def test_abhaken_ueber_die_ansicht(client, anna, erde):
    _, vorlage, aufgabe = pflanze_mit_vorlage(anna, erde, intervall=7)
    antwort = angemeldet(client, anna).post(reverse("aufgabe_abhaken", args=[aufgabe.pk]))
    assert antwort.status_code == 302
    aufgabe.refresh_from_db()
    assert aufgabe.erledigt_am is not None
    assert vorlage.aufgaben.filter(erledigt_am__isnull=True).count() == 1


# --- Pflegeplan bearbeiten -------------------------------------------------


def test_fremder_pflegeplan_ist_nicht_aufrufbar(client, anna, bernd, erde):
    pflanze, _, _ = pflanze_mit_vorlage(anna, erde)
    antwort = angemeldet(client, bernd).get(reverse("pflegeplan", args=[pflanze.pk]))
    assert antwort.status_code == 404


def test_neues_intervall_verschiebt_den_offenen_termin(client, anna, erde):
    """
    Wer von sieben auf vierzehn Tage umstellt, soll das sofort im Kalender
    sehen und nicht erst nach dem naechsten Abhaken.
    """
    _, vorlage, aufgabe = pflanze_mit_vorlage(anna, erde, intervall=7)
    antwort = angemeldet(client, anna).post(
        reverse("pflegevorlage_bearbeiten", args=[vorlage.pk]),
        {"taetigkeit": Taetigkeit.GIESSEN, "intervall_tage": 14, "hinweis": ""},
    )
    assert antwort.status_code == 302
    aufgabe.refresh_from_db()
    assert aufgabe.faelligkeit == date.today() + timedelta(days=14)


def test_zweite_vorlage_mit_gleicher_taetigkeit_wird_abgelehnt(client, anna, erde):
    pflanze, _, _ = pflanze_mit_vorlage(anna, erde, taetigkeit=Taetigkeit.GIESSEN)
    antwort = angemeldet(client, anna).post(
        reverse("pflegevorlage_anlegen", args=[pflanze.pk]),
        {"taetigkeit": Taetigkeit.GIESSEN, "intervall_tage": 10, "hinweis": ""},
    )
    assert antwort.status_code == 200  # Formular wird erneut angezeigt
    assert pflanze.pflegevorlagen.count() == 1


def test_neue_vorlage_bekommt_sofort_einen_termin(client, anna, erde):
    """Vermehren steht in keiner Empfehlung und wird von Hand aufgenommen."""
    pflanze, _, _ = pflanze_mit_vorlage(anna, erde, taetigkeit=Taetigkeit.GIESSEN)
    angemeldet(client, anna).post(
        reverse("pflegevorlage_anlegen", args=[pflanze.pk]),
        {"taetigkeit": Taetigkeit.VERMEHREN, "intervall_tage": 365, "hinweis": ""},
    )
    neue = pflanze.pflegevorlagen.get(taetigkeit=Taetigkeit.VERMEHREN)
    assert neue.aufgaben.count() == 1
    assert neue.aufgaben.get().faelligkeit == date.today() + timedelta(days=365)


def test_vorlage_entfernen_loescht_die_termine(client, anna, erde):
    pflanze, vorlage, _ = pflanze_mit_vorlage(anna, erde)
    antwort = angemeldet(client, anna).post(reverse("pflegevorlage_loeschen", args=[vorlage.pk]))
    assert antwort.status_code == 302
    assert pflanze.pflegevorlagen.count() == 0
    assert Pflegeaufgabe.objects.count() == 0
