from django.contrib import admin

from .models import (
    Bodenart,
    Pflanze,
    Pflanzenart,
    Pflegeaufgabe,
    Pflegeempfehlung,
    Pflegevorlage,
    Standort,
)


@admin.register(Bodenart)
class BodenartAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Pflanzenart)
class PflanzenartAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "botanischer_name",
        "lichtbedarf",
        "temperaturuntergrenze",
        "feuchtigkeitsbedarf",
        "giftig",
        "erstellt_von",
    ]
    list_filter = ["lichtbedarf", "feuchtigkeitsbedarf", "giftig"]
    search_fields = ["name", "botanischer_name"]
    filter_horizontal = ["geeignete_bodenarten"]


@admin.register(Pflegeempfehlung)
class PflegeempfehlungAdmin(admin.ModelAdmin):
    list_display = ["art", "taetigkeit", "intervall_tage"]
    list_filter = ["taetigkeit"]
    search_fields = ["art__name"]


@admin.register(Standort)
class StandortAdmin(admin.ModelAdmin):
    list_display = ["name", "art", "besitzer", "lichtangebot", "minimaltemperatur"]
    list_filter = ["art", "besitzer"]


@admin.register(Pflanze)
class PflanzeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "art", "status", "standort", "besitzer"]
    list_filter = ["status", "besitzer"]
    search_fields = ["eigener_name", "art__name"]


@admin.register(Pflegevorlage)
class PflegevorlageAdmin(admin.ModelAdmin):
    list_display = ["pflanze", "taetigkeit", "intervall_tage"]
    list_filter = ["taetigkeit"]


@admin.register(Pflegeaufgabe)
class PflegeaufgabeAdmin(admin.ModelAdmin):
    list_display = ["vorlage", "faelligkeit", "erledigt_am"]
    list_filter = ["faelligkeit"]
