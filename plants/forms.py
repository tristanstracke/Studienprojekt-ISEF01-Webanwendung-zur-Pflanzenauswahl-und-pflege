from django import forms
from django.db import models

from .models import Bodenart, Pflanze, Pflanzenart, Pflegevorlage, Standort


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


class PflanzeForm(forms.ModelForm):
    """
    Uebernimmt eine Art aus dem Katalog auf die Wunschliste.

    Die Art wird in der Ansicht gesetzt, nicht im Formular: Sichtbar sind fuer
    eine Person nur der mitgelieferte Katalog und ihre eigenen Arten. Stuende
    das Feld im Formular, liesse sich beim Absenden die Nummer einer fremden
    Art unterschieben.
    """

    class Meta:
        model = Pflanze
        fields = ["eigener_name", "notiz"]
        widgets = {
            "eigener_name": forms.TextInput(attrs={"placeholder": "z. B. die große im Flur"}),
            "notiz": forms.Textarea(attrs={"rows": 3}),
        }


class PflanzenartForm(forms.ModelForm):
    """
    Anlage einer eigenen Pflanzenart, wenn eine Pflanze nicht im Katalog steht.

    Die Angaben sind dieselben, die auch der Katalog fuehrt, denn die
    Eignungspruefung braucht sie unabhaengig von der Herkunft der Art.
    'erstellt_von' fehlt bewusst und wird in der Ansicht gesetzt.
    """

    geeignete_bodenarten = forms.ModelMultipleChoiceField(
        queryset=Bodenart.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="geeignete Bodenarten",
        help_text="Mindestens eine auswählen.",
    )

    class Meta:
        model = Pflanzenart
        fields = [
            "name",
            "botanischer_name",
            "lichtbedarf",
            "temperaturuntergrenze",
            "feuchtigkeitsbedarf",
            "geeignete_bodenarten",
            "giftig",
            "wasserbedarf",
            "endwuchshoehe_cm",
            "quelle",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "z. B. Zimmerlinde"}),
            "botanischer_name": forms.TextInput(attrs={"placeholder": "z. B. Sparmannia africana"}),
            "temperaturuntergrenze": forms.NumberInput(attrs={"min": -30, "max": 40}),
            "quelle": forms.TextInput(attrs={"placeholder": "Woher stammen die Angaben?"}),
        }

    def clean_name(self):
        """
        Der Name muss innerhalb der sichtbaren Arten eindeutig sein, sonst
        stehen in der Auswahlliste zwei gleich benannte Eintraege.
        """
        name = self.cleaned_data["name"].strip()
        sichtbare = Pflanzenart.objects.filter(name__iexact=name).filter(
            models.Q(erstellt_von__isnull=True)
            | models.Q(erstellt_von=self.instance.erstellt_von_id)
        )
        if self.instance.pk:
            sichtbare = sichtbare.exclude(pk=self.instance.pk)
        if sichtbare.exists():
            raise forms.ValidationError(
                "Eine Pflanzenart mit diesem Namen gibt es bereits - "
                "entweder im Katalog oder unter deinen eigenen."
            )
        return name


class PflegevorlageForm(forms.ModelForm):
    """
    Eine wiederkehrende Pflegetaetigkeit einer Pflanze.

    Die Pflanze wird in der Ansicht gesetzt: Sie stammt aus der Adresse und
    ist dort bereits auf das angemeldete Konto eingeschraenkt.
    """

    class Meta:
        model = Pflegevorlage
        fields = ["taetigkeit", "intervall_tage", "hinweis"]
        widgets = {
            "intervall_tage": forms.NumberInput(attrs={"min": 1, "max": 730}),
            "hinweis": forms.TextInput(attrs={"placeholder": "z. B. nur von unten gießen"}),
        }
        help_texts = {
            "intervall_tage": "Nach wie vielen Tagen die Tätigkeit erneut ansteht.",
        }

    def clean(self):
        """
        Je Pflanze und Tätigkeit gibt es hoechstens eine Vorlage. Die Datenbank
        stellt das sicher; hier wird derselbe Fall abgefangen, damit eine
        verstaendliche Meldung erscheint statt eines Datenbankfehlers.
        """
        daten = super().clean()
        taetigkeit = daten.get("taetigkeit")
        if not taetigkeit:
            return daten
        vorhandene = Pflegevorlage.objects.filter(
            pflanze=self.instance.pflanze_id, taetigkeit=taetigkeit
        )
        if self.instance.pk:
            vorhandene = vorhandene.exclude(pk=self.instance.pk)
        if vorhandene.exists():
            raise forms.ValidationError(
                "Für diese Pflanze gibt es bereits eine Vorlage mit dieser Tätigkeit."
            )
        return daten
