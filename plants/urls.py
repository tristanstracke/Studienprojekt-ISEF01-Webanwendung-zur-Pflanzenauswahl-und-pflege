from django.urls import path

from . import views

urlpatterns = [
    path("", views.start, name="start"),
    path("standorte/", views.standort_liste, name="standort_liste"),
    path("standorte/neu/", views.standort_anlegen, name="standort_anlegen"),
    path("standorte/<int:pk>/", views.standort_bearbeiten, name="standort_bearbeiten"),
    path("standorte/<int:pk>/loeschen/", views.standort_loeschen, name="standort_loeschen"),
    path("pflanzenarten/", views.pflanzenart_liste, name="pflanzenart_liste"),
    path("pflanzenarten/neu/", views.pflanzenart_anlegen, name="pflanzenart_anlegen"),
    path(
        "pflanzenarten/<int:art_pk>/merken/",
        views.pflanze_hinzufuegen,
        name="pflanze_hinzufuegen",
    ),
    path("wunschliste/", views.wunschliste, name="wunschliste"),
    path("wunschliste/<int:pk>/entfernen/", views.pflanze_entfernen, name="pflanze_entfernen"),
    path(
        "pflanzenarten/<int:art_pk>/eignung/",
        views.eignung_pruefen,
        name="eignung_pruefen",
    ),
    path(
        "wunschliste/<int:pk>/anschaffen/",
        views.pflanze_anschaffen,
        name="pflanze_anschaffen",
    ),
    path("bestand/", views.bestand, name="bestand"),
    path("kalender/", views.kalender, name="kalender"),
    path("aufgaben/<int:pk>/abhaken/", views.aufgabe_abhaken, name="aufgabe_abhaken"),
    path("bestand/<int:pflanze_pk>/pflege/", views.pflegeplan, name="pflegeplan"),
    path(
        "bestand/<int:pflanze_pk>/pflege/neu/",
        views.pflegevorlage_anlegen,
        name="pflegevorlage_anlegen",
    ),
    path(
        "pflege/<int:pk>/aendern/",
        views.pflegevorlage_bearbeiten,
        name="pflegevorlage_bearbeiten",
    ),
    path(
        "pflege/<int:pk>/entfernen/",
        views.pflegevorlage_loeschen,
        name="pflegevorlage_loeschen",
    ),
]
