from django.urls import path

from . import views

urlpatterns = [
    path("", views.start, name="start"),
    path("standorte/", views.standort_liste, name="standort_liste"),
    path("standorte/neu/", views.standort_anlegen, name="standort_anlegen"),
    path("standorte/<int:pk>/", views.standort_bearbeiten, name="standort_bearbeiten"),
    path("standorte/<int:pk>/loeschen/", views.standort_loeschen, name="standort_loeschen"),
]
