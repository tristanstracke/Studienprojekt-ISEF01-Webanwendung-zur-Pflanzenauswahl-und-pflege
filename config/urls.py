from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Anmeldung, Abmeldung und Kennwortänderung liefert Django mit.
    path("konten/", include("django.contrib.auth.urls")),
    path("", include("plants.urls")),
]
