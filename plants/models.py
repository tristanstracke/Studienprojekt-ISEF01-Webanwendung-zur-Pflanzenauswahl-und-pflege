"""
Datenmodell "Care for Plants".

Grundunterscheidung: Eine Pflanzenart beschreibt die botanischen Anforderungen
einer Art ("Ein Fensterblatt braucht helles Licht"). Eine Pflanze ist der
Eintrag einer Person ("mein Fensterblatt im Wohnzimmer"). Die Eignungsprüfung
vergleicht die Anforderungen der Art mit den Gegebenheiten des Standorts.
"""

from django.conf import settings
from django.db import models

# --------------------------------------------------------------------------
# Skalen
#
# Licht, Feuchtigkeit und Wasserbedarf sind Ordinalskalen: Die Werte sind
# geordnet, damit sich Angebot und Bedarf vergleichen lassen
# (z. B. "Standort bietet 3, Pflanze braucht 4" -> eine Stufe zu dunkel).
# Deshalb IntegerChoices und nicht TextChoices.
# --------------------------------------------------------------------------


class Licht(models.IntegerChoices):
    SEHR_SCHATTIG = 1, "sehr schattig"
    SCHATTIG = 2, "schattig"
    HALBSCHATTIG = 3, "halbschattig"
    HELL = 4, "hell"
    SONNIG = 5, "sonnig"


class Feuchtigkeit(models.IntegerChoices):
    """Luftfeuchtigkeit. Wird zwischen Standort und Pflanzenart abgeglichen."""

    TROCKEN = 1, "trocken"
    NORMAL = 2, "normal"
    FEUCHT = 3, "feucht"


class Wasserbedarf(models.IntegerChoices):
    """
    Giessbedarf. Geht nicht in die Eignungsprüfung ein, sondern in die
    Pflegeplanung. Eigene Skala, weil hier fuenf Stufen fachlich
    unterscheidbar sind, bei der Luftfeuchtigkeit aber nicht.
    """

    SEHR_GERING = 1, "sehr gering"
    GERING = 2, "gering"
    MITTEL = 3, "mittel"
    HOCH = 4, "hoch"
    SEHR_HOCH = 5, "sehr hoch"


class Standortart(models.TextChoices):
    INNENRAUM = "innen", "Innenraum"
    BALKON = "balkon", "Balkon"
    GARTEN = "garten", "Garten"


class Taetigkeit(models.TextChoices):
    GIESSEN = "giessen", "Gießen"
    DUENGEN = "duengen", "Düngen"
    UMTOPFEN = "umtopfen", "Umtopfen"
    SCHNEIDEN = "schneiden", "Zurückschneiden"
    VERMEHREN = "vermehren", "Vermehren"


class Bodenart(models.Model):
    """
    Stammdaten, vom Administrator gepflegt.
    Eigene Tabelle, weil eine Pflanzenart mehrere Bodenarten verträgt.
    Eine kommaseparierte Liste im Textfeld wäre eine Verletzung der ersten
    Normalform und liesse sich nicht sauber abfragen.
    """

    name = models.CharField("Bezeichnung", max_length=50, unique=True)
    # Fachliche Beschreibung aus der Recherche. Sie steht neben dem
    # geläufigen Namen, damit die Auswahl fachlich eindeutig bleibt und
    # trotzdem von einer Privatperson beantwortet werden kann.
    beschreibung = models.CharField("Beschreibung", max_length=100, blank=True)

    class Meta:
        verbose_name = "Bodenart"
        verbose_name_plural = "Bodenarten"
        ordering = ["name"]

    def __str__(self):
        return self.name


# --------------------------------------------------------------------------
# Katalog
# --------------------------------------------------------------------------


class Pflanzenart(models.Model):
    """
    Botanische Anforderungen einer Art. Die Einträge ohne Ersteller bilden
    den mitgelieferten Katalog und sind für alle sichtbar. Legt eine Person
    eine eigene Art an, weil ihre Pflanze nicht im Katalog steht, sieht nur
    sie diesen Eintrag.
    """

    name = models.CharField("Name", max_length=80)
    botanischer_name = models.CharField("botanischer Name", max_length=120, blank=True)

    # Eingangsgrößen der Eignungsprüfung
    lichtbedarf = models.IntegerField("Lichtbedarf", choices=Licht.choices)
    temperaturuntergrenze = models.IntegerField(
        "verträgt Temperaturen bis (Grad Celsius)",
        help_text="Tiefste Temperatur, die die Pflanze dauerhaft ohne Schaden übersteht.",
    )
    feuchtigkeitsbedarf = models.IntegerField("Luftfeuchtigkeit", choices=Feuchtigkeit.choices)
    geeignete_bodenarten = models.ManyToManyField(
        Bodenart, verbose_name="geeignete Bodenarten", related_name="pflanzenarten"
    )
    giftig = models.BooleanField("giftig", default=False)

    # weitere Eigenschaften, nicht Teil der Eignungsprüfung
    wasserbedarf = models.IntegerField("Wasserbedarf", choices=Wasserbedarf.choices)
    endwuchshoehe_cm = models.PositiveIntegerField("Endwuchshöhe in cm", null=True, blank=True)

    quelle = models.CharField(
        "Quelle",
        max_length=300,
        blank=True,
        help_text="Woher stammen die botanischen Angaben? Wird im Projektbericht belegt.",
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pflanzenarten",
        verbose_name="angelegt von",
        help_text="Leer bei den Arten des mitgelieferten Katalogs.",
    )

    class Meta:
        verbose_name = "Pflanzenart"
        verbose_name_plural = "Pflanzenarten"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def gehoert_zum_katalog(self) -> bool:
        return self.erstellt_von_id is None


class Pflegeempfehlung(models.Model):
    """
    Empfohlenes Pflegeintervall einer Art, aus der botanischen Recherche.
    Beim Anschaffen einer Pflanze entstehen daraus die Pflegevorlagen der
    jeweiligen Person, die sie anschließend an ihre Verhaeltnisse anpassen
    kann. Die Empfehlung bleibt davon unberuehrt.
    """

    art = models.ForeignKey(
        Pflanzenart, on_delete=models.CASCADE, related_name="pflegeempfehlungen"
    )
    taetigkeit = models.CharField("Tätigkeit", max_length=15, choices=Taetigkeit.choices)
    intervall_tage = models.PositiveIntegerField("Intervall in Tagen")
    hinweis = models.CharField("Hinweis", max_length=200, blank=True)

    class Meta:
        verbose_name = "Pflegeempfehlung"
        verbose_name_plural = "Pflegeempfehlungen"
        ordering = ["art__name", "taetigkeit"]
        constraints = [
            models.UniqueConstraint(
                fields=["art", "taetigkeit"], name="eine_empfehlung_je_art_und_taetigkeit"
            )
        ]

    def __str__(self):
        return f"{self.art}: {self.get_taetigkeit_display()} alle {self.intervall_tage} Tage"


# --------------------------------------------------------------------------
# UC1
# --------------------------------------------------------------------------


class Standort(models.Model):
    besitzer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="standorte"
    )
    name = models.CharField("Bezeichnung", max_length=80)
    art = models.CharField("Art", max_length=10, choices=Standortart.choices)

    lichtangebot = models.IntegerField("Lichtangebot", choices=Licht.choices)
    minimaltemperatur = models.IntegerField(
        "niedrigste Temperatur in Grad Celsius",
        help_text="Tiefster Wert, der am Standort im Jahresverlauf erreicht wird.",
    )
    luftfeuchtigkeit = models.IntegerField("Luftfeuchtigkeit", choices=Feuchtigkeit.choices)
    bodenart = models.ForeignKey(Bodenart, on_delete=models.PROTECT, verbose_name="Bodenart")
    erreichbar_fuer_kinder_haustiere = models.BooleanField(
        "für Kinder oder Haustiere erreichbar",
        default=False,
        help_text="Angehakt, wenn Kinder oder Haustiere an die Pflanzen herankommen.",
    )

    class Meta:
        verbose_name = "Standort"
        verbose_name_plural = "Standorte"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["besitzer", "name"], name="standortname_je_benutzer")
        ]

    def __str__(self):
        return self.name


class Pflanze(models.Model):
    """
    Der Eintrag einer Person. Wunschliste und Bestand liegen in derselben
    Tabelle und werden über das Feld 'status' unterschieden. Das Anschaffen
    einer Pflanze ist damit ein Statuswechsel mit Standortzuordnung und kein
    Umkopieren von Daten.
    """

    class Status(models.TextChoices):
        WUNSCH = "wunsch", "auf der Wunschliste"
        BESTAND = "bestand", "im Bestand"

    besitzer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pflanzen"
    )
    art = models.ForeignKey(
        Pflanzenart,
        on_delete=models.PROTECT,
        related_name="pflanzen",
        verbose_name="Pflanzenart",
    )
    eigener_name = models.CharField(
        "eigene Bezeichnung",
        max_length=80,
        blank=True,
        help_text='Optional, zur Unterscheidung mehrerer Exemplare, z. B. "die große im Flur".',
    )
    status = models.CharField(
        "Status", max_length=10, choices=Status.choices, default=Status.WUNSCH
    )
    standort = models.ForeignKey(
        Standort,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pflanzen",
        verbose_name="Standort",
        help_text="Nur bei Pflanzen im Bestand gesetzt.",
    )
    notiz = models.TextField("Notiz", blank=True)

    class Meta:
        verbose_name = "Pflanze"
        verbose_name_plural = "Pflanzen"
        ordering = ["art__name"]

    def __str__(self):
        return self.eigener_name or self.art.name


# --------------------------------------------------------------------------
# UC2
# --------------------------------------------------------------------------


class Pflegevorlage(models.Model):
    """
    Beschreibt eine wiederkehrende Tätigkeit je Pflanze, z. B.
    "giessen alle 7 Tage". Aus der Vorlage entstehen die einzelnen Termine.
    """

    pflanze = models.ForeignKey(Pflanze, on_delete=models.CASCADE, related_name="pflegevorlagen")
    taetigkeit = models.CharField("Tätigkeit", max_length=15, choices=Taetigkeit.choices)
    intervall_tage = models.PositiveIntegerField("Intervall in Tagen")
    hinweis = models.CharField("Hinweis", max_length=200, blank=True)

    class Meta:
        verbose_name = "Pflegevorlage"
        verbose_name_plural = "Pflegevorlagen"

    def __str__(self):
        return f"{self.pflanze}: {self.get_taetigkeit_display()} alle {self.intervall_tage} Tage"


class Pflegeaufgabe(models.Model):
    """
    Ein konkreter Termin. Wird eine Aufgabe abgehakt, entsteht die
    Folgeaufgabe mit Fälligkeit = Erledigungsdatum + Intervall.
    Erledigte Aufgaben bleiben als Pflegehistorie erhalten.
    """

    vorlage = models.ForeignKey(Pflegevorlage, on_delete=models.CASCADE, related_name="aufgaben")
    faelligkeit = models.DateField("fällig am")
    erledigt_am = models.DateField("erledigt am", null=True, blank=True)

    class Meta:
        verbose_name = "Pflegeaufgabe"
        verbose_name_plural = "Pflegeaufgaben"
        ordering = ["faelligkeit"]

    def __str__(self):
        return f"{self.vorlage.get_taetigkeit_display()} am {self.faelligkeit}"

    @property
    def ist_erledigt(self) -> bool:
        return self.erledigt_am is not None
