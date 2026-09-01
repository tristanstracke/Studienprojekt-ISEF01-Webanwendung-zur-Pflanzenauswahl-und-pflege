"""
Tests der Eignungslogik.

Keine Datenbank noetig, weil die Regeln nur mit einfachen Werten arbeiten.
Geprueft wird jede Regel an ihren Grenzen: genau passend, eine Stufe daneben,
zwei Stufen daneben. Fehler treten erfahrungsgemaess an diesen Uebergaengen auf,
nicht in der Mitte eines Wertebereichs.
"""

import pytest

from plants.eignung import (
    Bewertung,
    Kriterium,
    Urteil,
    bewerte_bodenart,
    bewerte_feuchtigkeit,
    bewerte_giftigkeit,
    bewerte_licht,
    bewerte_temperatur,
    bilde_urteil,
)

# --- Licht ---------------------------------------------------------------


@pytest.mark.parametrize(
    "angebot, bedarf, erwartet",
    [
        (3, 3, Bewertung.ERFUELLT),  # genau passend
        (1, 1, Bewertung.ERFUELLT),  # unteres Ende der Skala
        (5, 5, Bewertung.ERFUELLT),  # oberes Ende der Skala
        (2, 3, Bewertung.GRENZWERTIG),  # eine Stufe zu dunkel
        (4, 3, Bewertung.GRENZWERTIG),  # eine Stufe zu hell
        (4, 5, Bewertung.GRENZWERTIG),  # eine Stufe zu dunkel am oberen Rand
        (1, 3, Bewertung.VERFEHLT),  # zwei Stufen zu dunkel
        (5, 1, Bewertung.VERFEHLT),  # vier Stufen zu hell, groesste Abweichung
        (1, 5, Bewertung.VERFEHLT),  # vier Stufen zu dunkel
    ],
)
def test_licht(angebot, bedarf, erwartet):
    assert bewerte_licht(angebot, bedarf).bewertung is erwartet


# --- Temperatur ----------------------------------------------------------


@pytest.mark.parametrize(
    "standort, pflanze, erwartet",
    [
        (15, 5, Bewertung.ERFUELLT),  # deutlicher Abstand
        (7, 5, Bewertung.ERFUELLT),  # Abstand genau 2 Grad
        (6, 5, Bewertung.GRENZWERTIG),  # Abstand 1 Grad
        (5, 5, Bewertung.GRENZWERTIG),  # exakt auf der Untergrenze
        (4, 5, Bewertung.VERFEHLT),  # ein Grad zu kalt
        (-5, 5, Bewertung.VERFEHLT),  # Frost
    ],
)
def test_temperatur(standort, pflanze, erwartet):
    assert bewerte_temperatur(standort, pflanze).bewertung is erwartet


# --- Luftfeuchtigkeit ----------------------------------------------------


@pytest.mark.parametrize(
    "angebot, bedarf, erwartet",
    [
        (2, 2, Bewertung.ERFUELLT),
        (1, 2, Bewertung.GRENZWERTIG),
        (3, 2, Bewertung.GRENZWERTIG),
        (1, 3, Bewertung.VERFEHLT),
        (3, 1, Bewertung.VERFEHLT),
    ],
)
def test_feuchtigkeit(angebot, bedarf, erwartet):
    assert bewerte_feuchtigkeit(angebot, bedarf).bewertung is erwartet


# --- Bodenart ------------------------------------------------------------


def test_bodenart_passend():
    k = bewerte_bodenart("Blumenerde", {"Blumenerde", "Kakteenerde"}, austauschbar=True)
    assert k.bewertung is Bewertung.ERFUELLT


def test_bodenart_unpassend_im_topf_ist_grenzwertig():
    k = bewerte_bodenart("Kakteenerde", {"Blumenerde"}, austauschbar=True)
    assert k.bewertung is Bewertung.GRENZWERTIG


def test_bodenart_unpassend_im_garten_ist_verfehlt():
    k = bewerte_bodenart("lehmiger Gartenboden", {"saure Erde"}, austauschbar=False)
    assert k.bewertung is Bewertung.VERFEHLT


# --- Giftigkeit ----------------------------------------------------------


@pytest.mark.parametrize(
    "giftig, erreichbar, erwartet",
    [
        (False, True, Bewertung.ERFUELLT),  # ungiftig, Erreichbarkeit egal
        (False, False, Bewertung.ERFUELLT),
        (True, False, Bewertung.ERFUELLT),  # giftig, aber ausser Reichweite
        (True, True, Bewertung.VERFEHLT),  # giftig und erreichbar
    ],
)
def test_giftigkeit(giftig, erreichbar, erwartet):
    assert bewerte_giftigkeit(giftig, erreichbar).bewertung is erwartet


# --- Gesamturteil --------------------------------------------------------


def _k(bewertung):
    return Kriterium("Test", bewertung, "")


def test_urteil_alle_erfuellt():
    assert bilde_urteil([_k(Bewertung.ERFUELLT)] * 5) is Urteil.GEEIGNET


def test_urteil_ein_grenzwertiges_kriterium():
    kriterien = [_k(Bewertung.ERFUELLT)] * 4 + [_k(Bewertung.GRENZWERTIG)]
    assert bilde_urteil(kriterien) is Urteil.BEDINGT_GEEIGNET


def test_urteil_ein_verfehltes_kriterium_schlaegt_alles_andere():
    """Kriterien werden nicht gegeneinander verrechnet."""
    kriterien = [_k(Bewertung.ERFUELLT)] * 4 + [_k(Bewertung.VERFEHLT)]
    assert bilde_urteil(kriterien) is Urteil.UNGEEIGNET


def test_urteil_verfehlt_hat_vorrang_vor_grenzwertig():
    kriterien = [_k(Bewertung.GRENZWERTIG), _k(Bewertung.VERFEHLT)]
    assert bilde_urteil(kriterien) is Urteil.UNGEEIGNET
