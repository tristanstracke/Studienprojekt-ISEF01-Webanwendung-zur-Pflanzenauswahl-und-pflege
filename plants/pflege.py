"""
Ableitung der Pflege aus den Empfehlungen einer Pflanzenart.

Beim Anschaffen einer Pflanze entstehen aus den recherchierten Empfehlungen
der Art die Pflegevorlagen dieser einen Pflanze. Ab diesem Zeitpunkt sind
beide unabhaengig: Wer sein Fensterblatt seltener giesst, aendert seine
Vorlage, nicht die Empfehlung fuer alle.

Die Funktionen stehen bewusst nicht im Modell. Eine Methode auf Pflanze
waere naheliegend, wuerde die Regel aber zwischen Datenhaltung und Fachlogik
vermischen; als eigene Datei laesst sie sich ohne Umweg lesen und pruefen.
"""

from datetime import date, timedelta

from django.utils import timezone

from .models import Pflegeaufgabe, Pflegevorlage


def heute() -> date:
    """
    Das heutige Datum in der eingestellten Zeitzone.

    Nicht date.today(): Das liest die Zeitzone des Servers, und der laeuft
    nach UTC. Zwischen Mitternacht und zwei Uhr waere dort noch der Vortag,
    und eine Aufgabe erschiene einen Tag zu frueh als faellig.
    """
    return timezone.localdate()


def erzeuge_pflegevorlagen(pflanze, ab_datum: date | None = None) -> int:
    """
    Legt fuer jede Empfehlung der Art eine Vorlage samt erster Aufgabe an.

    Vorhandene Vorlagen bleiben unberuehrt: Wird eine Pflanze versehentlich
    zweimal angeschafft, entstehen keine doppelten Eintraege. Die Anzahl der
    neu angelegten Vorlagen wird zurueckgegeben.
    """
    ab_datum = ab_datum or heute()
    vorhandene = set(pflanze.pflegevorlagen.values_list("taetigkeit", flat=True))
    angelegt = 0

    for empfehlung in pflanze.art.pflegeempfehlungen.all():
        if empfehlung.taetigkeit in vorhandene:
            continue
        vorlage = Pflegevorlage.objects.create(
            pflanze=pflanze,
            taetigkeit=empfehlung.taetigkeit,
            intervall_tage=empfehlung.intervall_tage,
            hinweis=empfehlung.hinweis,
        )
        # Die erste Aufgabe faellt ein volles Intervall nach dem Anschaffen an.
        # Alles sofort faellig zu stellen, waere fachlich falsch: Eine frisch
        # gekaufte Pflanze ist in der Regel gegossen und gedüngt.
        Pflegeaufgabe.objects.create(
            vorlage=vorlage,
            faelligkeit=ab_datum + timedelta(days=empfehlung.intervall_tage),
        )
        angelegt += 1

    return angelegt


def hake_ab(aufgabe: Pflegeaufgabe, erledigt_am: date | None = None) -> Pflegeaufgabe | None:
    """
    Markiert eine Aufgabe als erledigt und legt die Folgeaufgabe an.

    Die neue Faelligkeit rechnet ab dem Tag der Erledigung, nicht ab der
    urspruenglichen Faelligkeit. Wer drei Tage zu spaet giesst, soll danach
    wieder ein volles Intervall Zeit haben; andernfalls bliebe der Rueckstand
    dauerhaft bestehen und die Aufgabe waere sofort wieder ueberfaellig.

    Eine bereits erledigte Aufgabe bleibt unveraendert und liefert None
    zurueck. Das faengt den Fall ab, dass jemand zweimal auf abhaken drueckt
    oder die Seite neu laedt.
    """
    if aufgabe.erledigt_am is not None:
        return None

    aufgabe.erledigt_am = erledigt_am or heute()
    aufgabe.save(update_fields=["erledigt_am"])

    return Pflegeaufgabe.objects.create(
        vorlage=aufgabe.vorlage,
        faelligkeit=aufgabe.erledigt_am + timedelta(days=aufgabe.vorlage.intervall_tage),
    )


def offene_aufgaben(benutzer):
    """
    Alle noch nicht erledigten Aufgaben einer Person, die faelligste zuerst.

    Pflanze, Art und Standort werden mitgeladen, weil die Kalenderansicht sie
    zu jeder Zeile anzeigt - ohne das entstuende je Aufgabe eine eigene
    Abfrage.
    """
    return (
        Pflegeaufgabe.objects.filter(vorlage__pflanze__besitzer=benutzer, erledigt_am__isnull=True)
        .select_related(
            "vorlage", "vorlage__pflanze", "vorlage__pflanze__art", "vorlage__pflanze__standort"
        )
        .order_by("faelligkeit")
    )


def nach_faelligkeit(aufgaben, stichtag: date | None = None):
    """
    Teilt Aufgaben in vier Gruppen: ueberfaellig, heute, diese Woche, spaeter.

    Die Einteilung geschieht hier und nicht in der Vorlage, damit sie
    pruefbar ist und in der Ansicht keine Datumsrechnung steht.
    """
    stichtag = stichtag or heute()
    wochenende = stichtag + timedelta(days=7)
    gruppen = {"ueberfaellig": [], "heute": [], "woche": [], "spaeter": []}
    for aufgabe in aufgaben:
        if aufgabe.faelligkeit < stichtag:
            gruppen["ueberfaellig"].append(aufgabe)
        elif aufgabe.faelligkeit == stichtag:
            gruppen["heute"].append(aufgabe)
        elif aufgabe.faelligkeit <= wochenende:
            gruppen["woche"].append(aufgabe)
        else:
            gruppen["spaeter"].append(aufgabe)
    return gruppen
