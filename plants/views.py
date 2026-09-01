from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def start(request):
    """
    Vorlaeufige Startseite. Sie belegt, dass Anmeldung, Vorlagen und
    Veroeffentlichung zusammenspielen, bevor die Fachlichkeit entsteht.
    """
    return render(request, "plants/start.html")
