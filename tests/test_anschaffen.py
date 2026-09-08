"""
Tests der Eignungsansicht und des Anschaffens.

Der wichtigste Fall steht am Ende: Beim Anschaffen wird ein Standort per
Formular uebergeben. Ohne Pruefung liesse sich dort die Nummer eines fremden
Standorts eintragen - die eigene Pflanze staende dann an einem Ort, der einer
anderen Person gehoert, und deren Standortdaten waeren aus der Bestandsliste
ablesbar. In der Oberflaeche ist von dieser Luecke nichts zu sehen.
"""

import pytest
from django.urls import reverse

from plants.models import (
    Bodenart,
    Feuchtigkeit,
    Licht,
    Pflanze,
    Pflanzenart,
    Pflegeempfehlung,
    Standort,
    Standortart,
    Taetigkeit,
    Wasserbedarf,
)


@pytest.fixture
def blumenerde(db):
    return Bodenart.objects.create(name="Blumenerde", beschreibung="locker und durchlässig")


@pytest.fixture
def anna(db, django_user_model):
    return django_user_model.objects.create_user("anna", "anna@example.org", "geheim-123")


@pytest.fixture
def bernd(db, django_user_model):
    return django_user_model.objects.create_user("bernd", "bernd@example.org", "geheim-123")


@pytest.fixture
def art(db, blumenerde):
    a = Pflanzenart.objects.create(
        name="Fensterblatt",
        lichtbedarf=Licht.HELL,
        temperaturuntergrenze=15,
        feuchtigkeitsbedarf=Feuchtigkeit.NORMAL,
        wasserbedarf=Wasserbedarf.MITTEL,
    )
    a.geeignete_bodenarten.set([blumenerde])
    Pflegeempfehlung.objects.create(art=a, taetigkeit=Taetigkeit.GIESSEN, intervall_tage=7)
    Pflegeempfehlung.objects.create(art=a, taetigkeit=Taetigkeit.DUENGEN, intervall_tage=28)
    return a


def standort(besitzer, bodenart, name="Wohnzimmer", licht=Licht.HELL, minimum=18):
    return Standort.objects.create(
        besitzer=besitzer,
        name=name,
        art=Standortart.INNENRAUM,
        lichtangebot=licht,
        minimaltemperatur=minimum,
        luftfeuchtigkeit=Feuchtigkeit.NORMAL,
        bodenart=bodenart,
    )


def angemeldet(client, benutzer):
    client.force_login(benutzer)
    return client


# --- Eignungsansicht ------------------------------------------------------


def test_ansicht_zeigt_urteil_und_begruendung(client, anna, art, blumenerde):
    standort(anna, blumenerde)
    inhalt = (
        angemeldet(client, anna).get(reverse("eignung_pruefen", args=[art.pk])).content.decode()
    )
    assert "geeignet" in inhalt
    assert "Das Lichtangebot entspricht dem Bedarf der Pflanze." in inhalt
    assert "Die Pflanze ist ungiftig." in inhalt


def test_ansicht_zeigt_nur_eigene_standorte(client, anna, bernd, art, blumenerde):
    standort(anna, blumenerde, "Annas Fenster")
    standort(bernd, blumenerde, "Bernds Fenster")
    inhalt = (
        angemeldet(client, anna).get(reverse("eignung_pruefen", args=[art.pk])).content.decode()
    )
    assert "Annas Fenster" in inhalt
    assert "Bernds Fenster" not in inhalt


def test_geeigneter_standort_steht_oben(client, anna, art, blumenerde):
    """Bei mehreren Orten soll der beste zuerst kommen, nicht der erstangelegte."""
    standort(anna, blumenerde, "Dunkle Ecke", licht=Licht.SEHR_SCHATTIG)
    standort(anna, blumenerde, "Helles Fenster", licht=Licht.HELL)
    inhalt = (
        angemeldet(client, anna).get(reverse("eignung_pruefen", args=[art.pk])).content.decode()
    )
    assert inhalt.index("Helles Fenster") < inhalt.index("Dunkle Ecke")


def test_ohne_standort_erscheint_ein_hinweis(client, anna, art):
    inhalt = (
        angemeldet(client, anna).get(reverse("eignung_pruefen", args=[art.pk])).content.decode()
    )
    assert "noch keinen Standort" in inhalt


# --- Anschaffen -----------------------------------------------------------


def test_anschaffen_setzt_status_und_erzeugt_pflege(client, anna, art, blumenerde):
    ort = standort(anna, blumenerde)
    pflanze = Pflanze.objects.create(besitzer=anna, art=art)

    antwort = angemeldet(client, anna).post(
        reverse("pflanze_anschaffen", args=[pflanze.pk]), {"standort": ort.pk}
    )
    assert antwort.status_code == 302

    pflanze.refresh_from_db()
    assert pflanze.status == Pflanze.Status.BESTAND
    assert pflanze.standort == ort
    assert pflanze.pflegevorlagen.count() == 2
    assert all(v.aufgaben.count() == 1 for v in pflanze.pflegevorlagen.all())


def test_fremder_standort_wird_abgewiesen(client, anna, bernd, art, blumenerde):
    """Der Kern: Bernds Standort per Formular an Annas Pflanze zu haengen."""
    fremder = standort(bernd, blumenerde, "Bernds Fenster")
    pflanze = Pflanze.objects.create(besitzer=anna, art=art)

    antwort = angemeldet(client, anna).post(
        reverse("pflanze_anschaffen", args=[pflanze.pk]), {"standort": fremder.pk}
    )
    assert antwort.status_code == 404

    pflanze.refresh_from_db()
    assert pflanze.status == Pflanze.Status.WUNSCH
    assert pflanze.standort is None


def test_fremde_pflanze_ist_nicht_anschaffbar(client, anna, bernd, art, blumenerde):
    standort(bernd, blumenerde)
    fremde = Pflanze.objects.create(besitzer=anna, art=art)
    antwort = angemeldet(client, bernd).get(reverse("pflanze_anschaffen", args=[fremde.pk]))
    assert antwort.status_code == 404


def test_bereits_angeschaffte_pflanze_nicht_erneut(client, anna, art, blumenerde):
    ort = standort(anna, blumenerde)
    pflanze = Pflanze.objects.create(
        besitzer=anna, art=art, status=Pflanze.Status.BESTAND, standort=ort
    )
    antwort = angemeldet(client, anna).get(reverse("pflanze_anschaffen", args=[pflanze.pk]))
    assert antwort.status_code == 404


def test_auch_ein_ungeeigneter_standort_ist_waehlbar(client, anna, art, blumenerde):
    """
    Die Anwendung beraet, sie bevormundet nicht: Wer eine Pflanze bewusst an
    einen ungeeigneten Ort stellt, darf das - er sieht nur vorher, warum.
    """
    zu_kalt = standort(anna, blumenerde, "Kalter Flur", minimum=5)
    pflanze = Pflanze.objects.create(besitzer=anna, art=art)
    antwort = angemeldet(client, anna).post(
        reverse("pflanze_anschaffen", args=[pflanze.pk]), {"standort": zu_kalt.pk}
    )
    assert antwort.status_code == 302
    pflanze.refresh_from_db()
    assert pflanze.standort == zu_kalt


def test_bestand_zeigt_nur_eigene_pflanzen(client, anna, bernd, art, blumenerde):
    Pflanze.objects.create(
        besitzer=anna,
        art=art,
        eigener_name="Annas Exemplar",
        status=Pflanze.Status.BESTAND,
        standort=standort(anna, blumenerde, "A"),
    )
    Pflanze.objects.create(
        besitzer=bernd,
        art=art,
        eigener_name="Bernds Exemplar",
        status=Pflanze.Status.BESTAND,
        standort=standort(bernd, blumenerde, "B"),
    )
    inhalt = angemeldet(client, anna).get(reverse("bestand")).content.decode()
    assert "Annas Exemplar" in inhalt
    assert "Bernds Exemplar" not in inhalt
