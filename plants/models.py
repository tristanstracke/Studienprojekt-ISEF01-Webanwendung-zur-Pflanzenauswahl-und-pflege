"""
Datenmodell "Care for Plants".
Entwurfsstand fuer UC1 (Standorte, Wunschliste, Eignungspruefung)
und UC2 (Pflegeaufgaben, Kalender).
"""

from django.conf import settings
from django.db import models

# --------------------------------------------------------------------------
# Skalen
#
# Licht und Feuchtigkeit sind Ordinalskalen: Die Zahlenwerte sind geordnet,
# damit sich Angebot und Bedarf direkt vergleichen lassen
# (z. B. "Standort bietet 2, Pflanze braucht 3" -> eine Stufe zu dunkel).
# Deshalb IntegerChoices und nicht TextChoices.
# --------------------------------------------------------------------------


class Licht(models.IntegerChoices):
    SCHATTIG = 1, "schattig"
    HALBSCHATTIG = 2, "halbschattig"
    HELL = 3, "hell, ohne direkte Sonne"
    VOLLSONNIG = 4, "vollsonnig"


class Feuchtigkeit(models.IntegerChoices):
    TROCKEN = 1, "trocken"
    NORMAL = 2, "normal"
    FEUCHT = 3, "feucht"


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
    Eigene Tabelle, weil eine Pflanze mehrere Bodenarten vertraegt.
    Eine kommaseparierte Liste im Textfeld waere eine Verletzung
    der ersten Normalform und liesse sich nicht sauber abfragen.
    """

    name = models.CharField("Bezeichnung", max_length=50, unique=True)

    class Meta:
        verbose_name = "Bodenart"
        verbose_name_plural = "Bodenarten"

    def __str__(self):
        return self.name


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
        "fuer Kinder oder Haustiere erreichbar",
        default=False,
        help_text="Angehakt, wenn Kinder oder Haustiere an die Pflanzen herankommen.",
    )

    class Meta:
        verbose_name = "Standort"
        verbose_name_plural = "Standorte"
        constraints = [
            models.UniqueConstraint(fields=["besitzer", "name"], name="standortname_je_benutzer")
        ]

    def __str__(self):
        return self.name


class Pflanze(models.Model):
    """
    Wunschliste und Bestand liegen in derselben Tabelle und werden ueber
    das Feld 'status' unterschieden. Das Anschaffen einer Pflanze ist damit
    ein Statuswechsel mit Standortzuordnung und kein Umkopieren von Daten.
    """

    class Status(models.TextChoices):
        WUNSCH = "wunsch", "auf der Wunschliste"
        BESTAND = "bestand", "im Bestand"

    besitzer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pflanzen"
    )
    name = models.CharField("Name", max_length=80)
    botanischer_name = models.CharField("botanischer Name", max_length=120, blank=True)

    # Anforderungen an den Standort -> Eingangsgroessen der Eignungspruefung
    lichtbedarf = models.IntegerField("Lichtbedarf", choices=Licht.choices)
    temperaturuntergrenze = models.IntegerField(
        "vertraegt Temperaturen bis (Grad Celsius)",
        help_text="Tiefste Temperatur, die die Pflanze dauerhaft ohne Schaden uebersteht.",
    )
    feuchtigkeitsbedarf = models.IntegerField("Feuchtigkeitsbedarf", choices=Feuchtigkeit.choices)
    geeignete_bodenarten = models.ManyToManyField(
        Bodenart, verbose_name="geeignete Bodenarten", related_name="pflanzen"
    )
    giftig = models.BooleanField("giftig", default=False)

    # weitere Eigenschaften, nicht Teil der Eignungspruefung
    wasserbedarf = models.IntegerField("Wasserbedarf", choices=Feuchtigkeit.choices)
    endwuchshoehe_cm = models.PositiveIntegerField("Endwuchshoehe in cm", null=True, blank=True)

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

    class Meta:
        verbose_name = "Pflanze"
        verbose_name_plural = "Pflanzen"

    def __str__(self):
        return self.name


# --------------------------------------------------------------------------
# UC2
# --------------------------------------------------------------------------


class Pflegevorlage(models.Model):
    """
    Beschreibt eine wiederkehrende Taetigkeit je Pflanze, z. B.
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
    Folgeaufgabe mit Faelligkeit = Erledigungsdatum + Intervall.
    Erledigte Aufgaben bleiben als Pflegehistorie erhalten.
    """

    vorlage = models.ForeignKey(Pflegevorlage, on_delete=models.CASCADE, related_name="aufgaben")
    faelligkeit = models.DateField("faellig am")
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
