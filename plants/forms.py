from django import forms

from .models import Standort


class StandortForm(forms.ModelForm):
    """
    Formular zum Anlegen und Aendern eines Standorts.

    Das Feld 'besitzer' ist bewusst nicht enthalten: Es wird in der Ansicht
    aus dem angemeldeten Konto gesetzt. Waere es Teil des Formulars, koennte
    jemand beim Absenden eine fremde Benutzerkennung mitschicken und einen
    Standort in fremdem Namen anlegen.
    """

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
        das ueber eine Bedingung sicher; hier wird derselbe Fall abgefangen,
        damit die Person eine verstaendliche Meldung sieht statt eines
        Datenbankfehlers.
        """
        name = self.cleaned_data["name"].strip()
        vorhandene = Standort.objects.filter(besitzer=self.instance.besitzer_id, name__iexact=name)
        if self.instance.pk:
            vorhandene = vorhandene.exclude(pk=self.instance.pk)
        if vorhandene.exists():
            raise forms.ValidationError("Einen Standort mit diesem Namen gibt es bereits.")
        return name
