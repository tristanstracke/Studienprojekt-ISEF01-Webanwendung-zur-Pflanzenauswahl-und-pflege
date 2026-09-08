"""
Django-Einstellungen für "Care for Plants".

Alles, was sich zwischen lokaler Entwicklung und Produktion unterscheidet, kommt
aus Umgebungsvariablen. Dadurch liegt kein Geheimnis im Repository und es gibt
nur eine Einstellungsdatei statt mehrerer, die auseinanderlaufen können.
"""

import os
import secrets
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_flag(name: str, standard: bool = False) -> bool:
    return os.environ.get(name, str(standard)).lower() in {"1", "true", "yes"}


# --- Grundeinstellungen ---------------------------------------------------

# Beide Schalter sind bewusst sicher voreingestellt: Fehlt eine Variable, soll
# die Anwendung nicht offen weiterlaufen, sondern gar nicht erst starten.
# Lokal wird DEBUG=1 gesetzt (siehe README), in der Produktion nichts.
DEBUG = env_flag("DEBUG", standard=False)

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        # Nur für die lokale Entwicklung. Bei jedem Start neu, damit dieser
        # Wert niemals versehentlich in eine Produktionsumgebung geraet.
        SECRET_KEY = secrets.token_urlsafe(64)
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY ist nicht gesetzt. In der Produktion muss die "
            "Umgebungsvariable SECRET_KEY einen langen Zufallswert enthalten."
        )

# Railway stellt die öffentliche Adresse als Umgebungsvariable bereit.
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = []
if domain := os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
    ALLOWED_HOSTS.append(domain)
    CSRF_TRUSTED_ORIGINS.append(f"https://{domain}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "plants",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Liefert die statischen Dateien in der Produktion aus, damit kein
    # zusätzlicher Webserver nötig ist.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# --- Datenbank ------------------------------------------------------------

# In der Produktion zeigt DATA_DIR auf das eingehängte Volume. Ohne diese
# Variable läge die Datei im Container und wäre nach jeder Veröffentlichung
# leer. Lokal liegt sie im Projektverzeichnis.
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Anmeldung ------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "start"
LOGOUT_REDIRECT_URL = "login"


# --- E-Mail ---------------------------------------------------------------

# Die Anmeldung von Django bringt eine Strecke zum Zuruecksetzen des Kennworts
# mit, die eine E-Mail verschickt. Ein Postausgangsserver ist für den
# Prototyp nicht vorgesehen, deshalb wird die Nachricht in das Protokoll
# geschrieben. Der Administrator kann den Link dort ablesen und weitergeben;
# ohne diese Einstellung liefe der Aufruf in einen Serverfehler.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "care-for-plants@example.org"


# --- Sprache und Zeit -----------------------------------------------------

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True


# --- Statische Dateien ----------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Enthaelt die Wortmarke und das Browsersymbol. Der Ordner gehoert zum
# Repository, deshalb ist keine Bedingung noetig.
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}


# --- Sicherheit in der Produktion ----------------------------------------

# Greift nur, wenn DEBUG abgeschaltet ist. Lokal würde die Weiterleitung auf
# HTTPS die Entwicklung verhindern.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Bewusst kurz: Eine lange Dauer wuerde den Browser der Pruefenden auch
    # dann auf HTTPS festlegen, wenn die Anwendung spaeter unter einer anderen
    # Adresse laeuft. Für einen Prototyp mit vier Wochen Laufzeit genügt eine
    # Stunde. SECURE_HSTS_PRELOAD bleibt aus demselben Grund aus.
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
