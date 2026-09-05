from django import forms

from .models import Bodenart, Standort


class BodenartAuswahl(forms.ModelChoiceField):
    """Zeigt neben dem Namen die fachliche Beschreibung, damit die
    Auswahl auch ohne Vorkenntnisse eindeutig ist."""

    def label_from_instance(self, obj):
        return f"{obj.name} – {obj.beschreibung}" if obj.beschreibung else obj.name


class StandortForm(forms.ModelForm):
    """
    Formular zum Anlegen und Ändern eines Standorts.

    Das Feld 'besitzer' ist bewusst nicht enthalten: Es wird in der Ansicht
    aus dem angemeldeten Konto gesetzt. Wäre es Teil des Formulars, könnte
    jemand beim Absenden eine fremde Benutzerkennung mitschicken und einen
    Standort in fremdem Namen anlegen.
    """

    bodenart = BodenartAuswahl(
        queryset=Bodenart.objects.all(),
        label="Bodenart",
        empty_label="bitte auswählen",
    )

    class Meta:
        model = Standort
        fields = [
            "name",
            "art",
            "lichtangebot",
            "minimaltemperatur",
            "luftfeuchtigkeit",
            "bodenart",
            "erreichbar_fuer_kinder_haustiere",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "z. B. Wohnzimmer Südfenster"}),
            "minimaltemperatur": forms.NumberInput(attrs={"min": -30, "max": 50}),
        }

    def clean_name(self):
        """
        Standortnamen sollen je Person eindeutig sein. Die Datenbank stellt
        das über eine Bedingung sicher; hier wird derselbe Fall abgefangen,
        damit die Person eine verständliche Meldung sieht statt eines
        Datenbankfehlers.
        """
        name = self.cleaned_data["name"].strip()
        vorhandene = Standort.objects.filter(besitzer=self.instance.besitzer_id, name__iexact=name)
        if self.instance.pk:
            vorhandene = vorhandene.exclude(pk=self.instance.pk)
        if vorhandene.exists():
            raise forms.ValidationError("Einen Standort mit diesem Namen gibt es bereits.")
        return name
