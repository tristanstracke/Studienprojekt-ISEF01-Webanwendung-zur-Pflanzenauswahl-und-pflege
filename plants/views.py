from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StandortForm
from .models import Standort


@login_required
def start(request):
    """Einstiegsseite mit den Kennzahlen des angemeldeten Kontos."""
    return render(
        request,
        "plants/start.html",
        {"anzahl_standorte": Standort.objects.filter(besitzer=request.user).count()},
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
