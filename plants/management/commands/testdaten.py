"""
Legt die Testzugaenge und einen nachvollziehbaren Datenbestand an.

Die Zugaenge werden in MS 4 gefordert und dienen zugleich der gegenseitigen
Pruefung im Team. Sie von Hand anzulegen waere nicht wiederholbar: Nach einem
Redeploy ohne Datenbestand oder auf einem zweiten Rechner muesste jeder
dieselben Klicks erneut ausfuehren, und niemand koennte belegen, welche Daten
geprueft wurden. Als Verwaltungskommando steht der Aufbau im Repository, ist
in einem Befehl wiederherstellbar und in der Betriebsdokumentation zitierbar.

Aufruf:  python manage.py testdaten

Das Kommando ist mehrfach ausfuehrbar. Vorhandene Konten und Standorte werden
nicht verdoppelt; die Faelligkeiten der Pflegeaufgaben werden bei jedem Lauf
neu auf den Ausfuehrungstag bezogen, damit auch Wochen spaeter noch eine
ueberfaellige und eine heute faellige Aufgabe im Kalender stehen.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from plants.eignung import Urteil, pruefe_eignung
from plants.models import (
    Bodenart,
    Feuchtigkeit,
    Licht,
    Pflanze,
    Pflanzenart,
    Pflegeaufgabe,
    Standort,
    Standortart,
    Taetigkeit,
)
from plants.pflege import erzeuge_pflegevorlagen, heute

# Die Kennwoerter stehen bewusst im Klartext: Es sind Zugaenge zu einer
# Demonstrationsumgebung ohne echte Daten, und sie muessen in der
# Betriebsdokumentation genannt werden. Fuer einen Produktivbetrieb waere
# dieses Vorgehen nicht zulaessig.
KENNWORT = "Pflanze-Test-2026"
KENNWORT_ADMIN = "Pflanze-Admin-2026"

# Zwei Zugaenge je pruefender Person: einer mit Bestand, um beide
# Anwendungsfaelle sofort zu sehen, und einer ohne, um den Einstieg von null
# zu pruefen. Der Tutor bekommt eigene Konten, damit seine Pruefung nicht von
# Aenderungen des Teams beeinflusst wird - und umgekehrt.
KONTEN = [
    ("tutor", "tutor@example.org", True),
    ("tutor-neu", "tutor-neu@example.org", False),
    ("kai", "kai@example.org", True),
    ("kai-neu", "kai-neu@example.org", False),
    ("kilian", "kilian@example.org", True),
    ("kilian-neu", "kilian-neu@example.org", False),
]

STANDORTE = [
    {
        "name": "Wohnzimmer Südfenster",
        "art": Standortart.INNENRAUM,
        "lichtangebot": Licht.SONNIG,
        "minimaltemperatur": 19,
        "luftfeuchtigkeit": Feuchtigkeit.NORMAL,
        "erreichbar_fuer_kinder_haustiere": True,
    },
    {
        "name": "Schlafzimmer Nordfenster",
        "art": Standortart.INNENRAUM,
        "lichtangebot": Licht.HALBSCHATTIG,
        "minimaltemperatur": 17,
        "luftfeuchtigkeit": Feuchtigkeit.NORMAL,
        "erreichbar_fuer_kinder_haustiere": False,
    },
    {
        "name": "Balkon Ostseite",
        "art": Standortart.BALKON,
        "lichtangebot": Licht.HELL,
        "minimaltemperatur": 5,
        "luftfeuchtigkeit": Feuchtigkeit.FEUCHT,
        "erreichbar_fuer_kinder_haustiere": True,
    },
]

# Verschiebung der ersten Aufgabe je Taetigkeit, in Tagen ab heute. So liegt
# in jeder der vier Kalendergruppen mindestens ein Eintrag.
FAELLIGKEITEN = {
    Taetigkeit.GIESSEN: -2,
    Taetigkeit.DUENGEN: 0,
    Taetigkeit.SCHNEIDEN: 4,
    Taetigkeit.UMTOPFEN: 45,
    Taetigkeit.VERMEHREN: 60,
}


class Command(BaseCommand):
    help = "Legt die Testzugaenge samt Beispieldaten an (mehrfach ausfuehrbar)."

    def handle(self, *args, **optionen):
        arten = list(Pflanzenart.objects.filter(erstellt_von__isnull=True).order_by("name"))
        if len(arten) < 5 or not Bodenart.objects.exists():
            self.stderr.write(
                "Der Pflanzenkatalog ist leer. Zuerst die Stammdaten laden:\n"
                "  python manage.py loaddata pflanzenarten"
            )
            return

        with transaction.atomic():
            self.lege_administrator_an()
            for benutzername, adresse, mit_bestand in KONTEN:
                benutzer = self.lege_konto_an(benutzername, adresse)
                if mit_bestand:
                    self.bestuecke(benutzer, arten)

        self.stdout.write("")
        self.stdout.write("Testzugänge stehen bereit:")
        self.stdout.write(f"  admin / {KENNWORT_ADMIN}   (Administration)")
        for benutzername, _, mit_bestand in KONTEN:
            zusatz = "mit Standorten, Pflanzen und Pflegeaufgaben" if mit_bestand else "leer"
            self.stdout.write(f"  {benutzername} / {KENNWORT}   ({zusatz})")

    # --- Konten ------------------------------------------------------------

    def lege_administrator_an(self):
        Benutzer = get_user_model()
        konto, neu = Benutzer.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.org"}
        )
        konto.is_staff = True
        konto.is_superuser = True
        konto.set_password(KENNWORT_ADMIN)
        konto.save()
        self.stdout.write(f"admin {'angelegt' if neu else 'aktualisiert'}")

    def lege_konto_an(self, benutzername, adresse):
        Benutzer = get_user_model()
        konto, neu = Benutzer.objects.get_or_create(
            username=benutzername, defaults={"email": adresse}
        )
        konto.set_password(KENNWORT)
        konto.save()
        self.stdout.write(f"{benutzername} {'angelegt' if neu else 'aktualisiert'}")
        return konto

    # --- Daten -------------------------------------------------------------

    def bestuecke(self, benutzer, arten):
        erde = Bodenart.objects.order_by("id").first()
        standorte = []
        for angaben in STANDORTE:
            standort, _ = Standort.objects.get_or_create(
                besitzer=benutzer, name=angaben["name"], defaults={**angaben, "bodenart": erde}
            )
            standorte.append(standort)

        # Drei Arten in den Bestand, zwei auf die Wunschliste. Jede Art kommt
        # an den Standort, an dem sie am besten gedeiht. Das ist nicht nur
        # Kosmetik: Stuenden Beispielpflanzen an Standorten, die die
        # Eignungspruefung ablehnt, widerspraeche der Bestand der eigenen
        # Empfehlung - im Benutzerhandbuch waere das kaum zu erklaeren.
        for art in arten[:3]:
            standort = self.bester_standort(art, standorte)
            pflanze, neu = Pflanze.objects.get_or_create(
                besitzer=benutzer,
                art=art,
                status=Pflanze.Status.BESTAND,
                defaults={"standort": standort},
            )
            if neu:
                erzeuge_pflegevorlagen(pflanze)

        for art in arten[3:5]:
            Pflanze.objects.get_or_create(besitzer=benutzer, art=art, status=Pflanze.Status.WUNSCH)

        self.setze_faelligkeiten(benutzer)

    @staticmethod
    def bester_standort(art, standorte):
        """
        Waehlt den Standort mit dem guenstigsten Urteil.

        Gibt es keinen geeigneten, wird der am wenigsten schlechte genommen:
        Der Bestand soll auch dann bestueckt sein, wenn keine Art perfekt passt.
        """
        rang = {Urteil.GEEIGNET: 0, Urteil.BEDINGT_GEEIGNET: 1, Urteil.UNGEEIGNET: 2}
        return min(standorte, key=lambda ort: rang[pruefe_eignung(art, ort).urteil])

    def setze_faelligkeiten(self, benutzer):
        """
        Verteilt die offenen Aufgaben auf alle vier Kalendergruppen.

        Ohne diesen Schritt laegen alle Termine ein volles Intervall in der
        Zukunft - der Kalender saehe bei jeder Pruefung gleich leer aus, und
        weder das Abhaken noch die Gruppe "Überfällig" waere zu sehen.
        """
        stichtag = heute()
        offen = Pflegeaufgabe.objects.filter(
            vorlage__pflanze__besitzer=benutzer, erledigt_am__isnull=True
        ).select_related("vorlage")
        for aufgabe in offen:
            versatz = FAELLIGKEITEN.get(aufgabe.vorlage.taetigkeit, 30)
            aufgabe.faelligkeit = stichtag + timedelta(days=versatz)
            aufgabe.save(update_fields=["faelligkeit"])
