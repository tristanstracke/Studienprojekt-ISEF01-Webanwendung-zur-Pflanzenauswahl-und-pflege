from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Anmeldung, Abmeldung und Kennwortaenderung liefert Django mit.
    path("konten/", include("django.contrib.auth.urls")),
    path("", include("plants.urls")),
]
