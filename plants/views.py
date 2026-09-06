from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .eignung import Urteil, pruefe_eignung
from .forms import PflanzeForm, PflanzenartForm, StandortForm
from .models import Pflanze, Pflanzenart, Standort
from .pflege import erzeuge_pflegevorlagen


@login_required
def start(request):
    """Einstiegsseite mit den Kennzahlen des angemeldeten Kontos."""
    return render(
        request,
        "plants/start.html",
        {
            "anzahl_standorte": Standort.objects.filter(besitzer=request.user).count(),
            "anzahl_wunsch": Pflanze.objects.filter(
                besitzer=request.user, status=Pflanze.Status.WUNSCH
            ).count(),
            "anzahl_bestand": Pflanze.objects.filter(
                besitzer=request.user, status=Pflanze.Status.BESTAND
            ).count(),
        },
    )


# --------------------------------------------------------------------------
# Standorte
#
# Jede Abfrage ist auf das angemeldete Konto eingeschränkt. Das ist keine
# Bequemlichkeit, sondern die Zugriffstrennung: Ohne diese Einschränkung
# könnte über die Adresszeile ein fremder Datensatz erreicht werden.
# --------------------------------------------------------------------------


@login_required
def standort_liste(request):
    standorte = Standort.objects.filter(besitzer=request.user).select_related("bodenart")
    return render(request, "plants/standort_liste.html", {"standorte": standorte})


@login_required
def standort_anlegen(request):
    standort = Standort(besitzer=request.user)
    formular = StandortForm(request.POST or None, instance=standort)
    if request.method == "POST" and formular.is_valid():
        formular.save()
        messages.success(request, f"Standort {standort.name} wurde angelegt.")
        return redirect("standort_liste")
    return render(
        request,
        "plants/standort_formular.html",
        {"formular": formular, "überschrift": "Standort anlegen"},
    )


@login_required
def standort_bearbeiten(request, pk):
    # get_object_or_404 mit Filter auf den Besitzer: Ein fremder Standort
    # führt zu 404 und nicht zu 403, damit nicht einmal die Existenz eines
    # fremden Datensatzes erkennbar wird.
    standort = get_object_or_404(Standort, pk=pk, besitzer=request.user)
    formular = StandortForm(request.POST or None, instance=standort)
    if request.method == "POST" and formular.is_valid():
        formular.save()
        messages.success(request, f"Standort {standort.name} wurde geändert.")
        return redirect("standort_liste")
    return render(
        request,
        "plants/standort_formular.html",
        {"formular": formular, "überschrift": "Standort ändern", "standort": standort},
    )


@login_required
def standort_loeschen(request, pk):
    standort = get_object_or_404(Standort, pk=pk, besitzer=request.user)
    if request.method == "POST":
        name = standort.name
        standort.delete()
        messages.success(request, f"Standort {name} wurde gelöscht.")
        return redirect("standort_liste")
    return render(request, "plants/standort_loeschen.html", {"standort": standort})


# --------------------------------------------------------------------------
# Pflanzenarten und Wunschliste
#
# Sichtbar sind fuer eine Person die Arten des mitgelieferten Katalogs
# (erstellt_von ist leer) und ihre eigenen. Diese Regel steht in einer
# Funktion, damit sie nicht in jeder Ansicht neu formuliert wird - und damit
# ein vergessener Filter nicht an einer Stelle unbemerkt bleibt.
# --------------------------------------------------------------------------


def sichtbare_arten(benutzer):
    return Pflanzenart.objects.filter(Q(erstellt_von__isnull=True) | Q(erstellt_von=benutzer))


@login_required
def pflanzenart_liste(request):
    suche = request.GET.get("suche", "").strip()
    arten = sichtbare_arten(request.user).prefetch_related("geeignete_bodenarten")
    if suche:
        arten = arten.filter(Q(name__icontains=suche) | Q(botanischer_name__icontains=suche))
    return render(
        request,
        "plants/pflanzenart_liste.html",
        {"arten": arten, "suche": suche, "anzahl": arten.count()},
    )


@login_required
def pflanzenart_anlegen(request):
    """Eigene Art anlegen, wenn eine Pflanze nicht im Katalog steht."""
    art = Pflanzenart(erstellt_von=request.user)
    formular = PflanzenartForm(request.POST or None, instance=art)
    if request.method == "POST" and formular.is_valid():
        formular.save()
        messages.success(request, f"Die Pflanzenart {art.name} wurde angelegt.")
        return redirect("pflanze_hinzufuegen", art_pk=art.pk)
    return render(request, "plants/pflanzenart_formular.html", {"formular": formular})


@login_required
def pflanze_hinzufuegen(request, art_pk):
    """Uebernimmt eine sichtbare Art auf die Wunschliste."""
    art = get_object_or_404(sichtbare_arten(request.user), pk=art_pk)
    pflanze = Pflanze(besitzer=request.user, art=art, status=Pflanze.Status.WUNSCH)
    formular = PflanzeForm(request.POST or None, instance=pflanze)
    if request.method == "POST" and formular.is_valid():
        formular.save()
        messages.success(request, f"{art.name} steht jetzt auf deiner Wunschliste.")
        return redirect("wunschliste")
    return render(request, "plants/pflanze_formular.html", {"formular": formular, "art": art})


@login_required
def wunschliste(request):
    pflanzen = (
        Pflanze.objects.filter(besitzer=request.user, status=Pflanze.Status.WUNSCH)
        .select_related("art")
        .prefetch_related("art__geeignete_bodenarten")
    )
    return render(request, "plants/wunschliste.html", {"pflanzen": pflanzen})


@login_required
def pflanze_entfernen(request, pk):
    pflanze = get_object_or_404(Pflanze, pk=pk, besitzer=request.user)
    if request.method == "POST":
        name = str(pflanze)
        pflanze.delete()
        messages.success(request, f"{name} wurde von der Wunschliste entfernt.")
        return redirect("wunschliste")
    return render(request, "plants/pflanze_entfernen.html", {"pflanze": pflanze})


# --------------------------------------------------------------------------
# Eignungspruefung und Anschaffen
# --------------------------------------------------------------------------


@login_required
def eignung_pruefen(request, art_pk):
    """
    Prueft eine Art gegen alle Standorte der Person.

    Die Standorte werden mit ihrer Bodenart vorab geladen und die Bodenarten
    der Art ebenfalls, sonst entstuende je Standort eine eigene Abfrage.
    """
    art = get_object_or_404(
        sichtbare_arten(request.user).prefetch_related("geeignete_bodenarten"), pk=art_pk
    )
    standorte = Standort.objects.filter(besitzer=request.user).select_related("bodenart")

    ergebnisse = [(standort, pruefe_eignung(art, standort)) for standort in standorte]
    # Der beste Standort zuerst: geeignet vor bedingt geeignet vor ungeeignet.
    rang = {Urteil.GEEIGNET: 0, Urteil.BEDINGT_GEEIGNET: 1, Urteil.UNGEEIGNET: 2}
    ergebnisse.sort(key=lambda paar: (rang[paar[1].urteil], paar[0].name))

    return render(
        request,
        "plants/eignung.html",
        {
            "art": art,
            "ergebnisse": ergebnisse,
            "vorgemerkt": Pflanze.objects.filter(
                besitzer=request.user, art=art, status=Pflanze.Status.WUNSCH
            ).first(),
        },
    )


@login_required
def pflanze_anschaffen(request, pk):
    """
    Wechselt eine Pflanze von der Wunschliste in den Bestand.

    Der gewaehlte Standort wird gegen die Standorte der Person geprueft. Ohne
    diese Pruefung liesse sich beim Absenden die Nummer eines fremden
    Standorts unterschieben - in der Oberflaeche waere davon nichts zu sehen.
    """
    pflanze = get_object_or_404(
        Pflanze.objects.select_related("art"),
        pk=pk,
        besitzer=request.user,
        status=Pflanze.Status.WUNSCH,
    )
    standorte = Standort.objects.filter(besitzer=request.user).select_related("bodenart")

    if request.method == "POST":
        standort = get_object_or_404(standorte, pk=request.POST.get("standort") or 0)
        pflanze.standort = standort
        pflanze.status = Pflanze.Status.BESTAND
        pflanze.save()
        anzahl = erzeuge_pflegevorlagen(pflanze)
        messages.success(
            request,
            f"{pflanze} steht jetzt am Standort {standort.name}. "
            f"{anzahl} Pflegeaufgabe{'n' if anzahl != 1 else ''} wurde"
            f"{'n' if anzahl != 1 else ''} daraus angelegt.",
        )
        return redirect("bestand")

    bewertungen = [(s, pruefe_eignung(pflanze.art, s)) for s in standorte]
    return render(
        request,
        "plants/pflanze_anschaffen.html",
        {"pflanze": pflanze, "bewertungen": bewertungen},
    )


@login_required
def bestand(request):
    pflanzen = (
        Pflanze.objects.filter(besitzer=request.user, status=Pflanze.Status.BESTAND)
        .select_related("art", "standort")
        .prefetch_related("pflegevorlagen")
    )
    return render(request, "plants/bestand.html", {"pflanzen": pflanzen})
