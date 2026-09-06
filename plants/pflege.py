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

from .models import Pflegeaufgabe, Pflegevorlage


def erzeuge_pflegevorlagen(pflanze, ab_datum: date | None = None) -> int:
    """
    Legt fuer jede Empfehlung der Art eine Vorlage samt erster Aufgabe an.

    Vorhandene Vorlagen bleiben unberuehrt: Wird eine Pflanze versehentlich
    zweimal angeschafft, entstehen keine doppelten Eintraege. Die Anzahl der
    neu angelegten Vorlagen wird zurueckgegeben.
    """
    ab_datum = ab_datum or date.today()
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
