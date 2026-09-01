from django.contrib import admin

from .models import Bodenart, Pflanze, Pflegeaufgabe, Pflegevorlage, Standort


@admin.register(Bodenart)
class BodenartAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Standort)
class StandortAdmin(admin.ModelAdmin):
    list_display = ["name", "art", "besitzer", "lichtangebot", "minimaltemperatur"]
    list_filter = ["art", "besitzer"]


@admin.register(Pflanze)
class PflanzeAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "standort", "besitzer", "giftig"]
    list_filter = ["status", "giftig", "besitzer"]
    search_fields = ["name", "botanischer_name"]


@admin.register(Pflegevorlage)
class PflegevorlageAdmin(admin.ModelAdmin):
    list_display = ["pflanze", "taetigkeit", "intervall_tage"]
    list_filter = ["taetigkeit"]


@admin.register(Pflegeaufgabe)
class PflegeaufgabeAdmin(admin.ModelAdmin):
    list_display = ["vorlage", "faelligkeit", "erledigt_am"]
    list_filter = ["faelligkeit"]
