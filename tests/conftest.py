"""Gemeinsame Vorbereitung der Testlaeufe."""

import pytest


@pytest.fixture(autouse=True)
def ohne_https_weiterleitung(settings):
    """
    Die Tests laufen mit abgeschaltetem Fehlersuchmodus, also unter derselben
    Konfiguration wie die Produktion. Dort leitet Django jede Anfrage auf HTTPS
    um; der Testclient spricht aber nur HTTP und bekaeme deshalb bei jedem
    Aufruf eine Weiterleitung statt der Seite. Diese eine Einstellung wird
    daher für den Testlauf zurueckgenommen. Alle uebrigen
    Sicherheitseinstellungen bleiben aktiv und werden mitgeprueft.
    """
    settings.SECURE_SSL_REDIRECT = False
