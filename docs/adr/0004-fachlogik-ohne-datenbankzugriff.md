# 0004 – Fachlogik als reine Funktionen ohne Datenbankzugriff

**Status:** angenommen · **Datum:** 2026-09-01

## Kontext

Die beiden fachlich anspruchsvollen Stellen sind die Eignungsprüfung
(fünf Kriterien, dreistufige Bewertung, Gesamturteil) und die
Pflegeableitung (erste Fälligkeit, Folgetermin nach Erledigung). Die
Qualitätsplanung fordert für die Bewertungslogik eine Anweisungsüberdeckung
von mindestens 90 Prozent.

## Geprüfte Alternativen

1. **Bewertung als Methoden der Modellklassen.** Nah an den Daten, aber
   jeder Test benötigt Datenbankobjekte und damit eine Datenbank.
2. **Bewertung in den Ansichten.** Kürzester Weg, aber nur über
   HTTP-Anfragen prüfbar; einzelne Kriterien wären nicht isoliert testbar.
3. **Reine Funktionen in eigenen Modulen**, die einfache Werte entgegennehmen
   und zurückgeben.

## Entscheidung

`plants/eignung.py` und `plants/pflege.py` enthalten die Fachlogik als
Funktionen ohne Datenbank- und ohne Anfragebezug. Die Ansichten übersetzen
Modellwerte in einfache Werte und rufen diese Funktionen auf.

## Begründung

Reine Funktionen sind ohne Datenbank prüfbar. Das erlaubt viele kleine
Tests statt weniger großer und macht es praktikabel, jede Kombination von
Kriterien einzeln abzudecken. Die geforderte Überdeckung von 90 Prozent
wird für die Bewertungslogik nachweislich mit 100 Prozent erreicht.

## Konsequenzen

In den Ansichten steht ein Übersetzungsschritt zwischen Modell und
Fachfunktion. Diese zusätzliche Stelle ist der Preis für die Prüfbarkeit
und bei Änderungen am Datenmodell mitzuführen.
