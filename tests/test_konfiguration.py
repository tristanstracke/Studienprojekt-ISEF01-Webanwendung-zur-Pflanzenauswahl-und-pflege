"""
Tests der Konfigurationshilfen.

Geprueft wird das Einlesen der .env-Datei. Der Fall, der im Betrieb zaehlt:
Eine bereits gesetzte Umgebungsvariable darf die Datei nicht ueberschreiben,
sonst koennte eine vergessene lokale Datei die Einstellungen des Servers
verdraengen.
"""

import os

from config.settings import lies_env_datei


def test_werte_aus_der_datei_landen_in_der_umgebung(tmp_path, monkeypatch):
    datei = tmp_path / ".env"
    datei.write_text("BEISPIEL_SCHALTER=1\n", encoding="utf-8")
    monkeypatch.delenv("BEISPIEL_SCHALTER", raising=False)
    lies_env_datei(datei)
    assert os.environ["BEISPIEL_SCHALTER"] == "1"


def test_gesetzte_variable_hat_vorrang(tmp_path, monkeypatch):
    datei = tmp_path / ".env"
    datei.write_text("BEISPIEL_SCHALTER=aus-der-datei\n", encoding="utf-8")
    monkeypatch.setenv("BEISPIEL_SCHALTER", "aus-der-umgebung")
    lies_env_datei(datei)
    assert os.environ["BEISPIEL_SCHALTER"] == "aus-der-umgebung"


def test_kommentare_leerzeilen_und_anfuehrungszeichen(tmp_path, monkeypatch):
    datei = tmp_path / ".env"
    datei.write_text(
        '# ein Kommentar\n\nBEISPIEL_TEXT="mit Anfuehrungszeichen"\nohne_gleichheitszeichen\n',
        encoding="utf-8",
    )
    monkeypatch.delenv("BEISPIEL_TEXT", raising=False)
    lies_env_datei(datei)
    assert os.environ["BEISPIEL_TEXT"] == "mit Anfuehrungszeichen"


def test_fehlende_datei_ist_kein_fehler(tmp_path):
    lies_env_datei(tmp_path / "gibt-es-nicht")
