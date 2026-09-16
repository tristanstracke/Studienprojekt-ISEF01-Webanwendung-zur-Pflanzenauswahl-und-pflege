# 0006 – Qualitätstor in der Auslieferungspipeline

**Status:** angenommen · **Datum:** 2026-09-07

## Kontext

In MS 3 ist festgelegt, dass Änderungen nur über Pull Requests mit Review
auf den Hauptzweig gelangen und dass vor jeder Auslieferung statische
Prüfung und Testreihe bestehen müssen. Bis zum 07.09.2026 war das eine
Absprache; ihre Einhaltung ließ sich weder erzwingen noch belegen.

## Geprüfte Alternativen

1. **Bei der Absprache bleiben.** Kein Aufwand, aber unter Zeitdruck fällt
   sie als Erstes, und im Bericht steht eine Behauptung ohne Beleg.
2. **Prüfung nur in der Pipeline, ohne Zweigschutz.** Der Fehlschlag wäre
   sichtbar, ein direkter Push auf den Hauptzweig aber weiterhin möglich.
3. **Zweigschutz mit erzwungenem Statuscheck.**

## Entscheidung

Ein Ruleset auf dem Standardzweig verlangt einen Pull Request mit einer
Freigabe, verlangt das Bestehen des Statuschecks
`Statische Pruefung und Tests` und verbietet erzwungene Pushes. Die Regel
gilt auch für den Eigentümer des Repositorys. In der Pipeline hängt der
Auslieferungsauftrag über `needs` am Prüfauftrag.

## Begründung

Ein Prozess, dessen Einhaltung von Disziplin abhängt, ist im Bericht nicht
belegbar. Als Serverregel ist er nachweisbar und im Abschlussvideo zeigbar.

## Konsequenzen

Auch kleine Korrekturen brauchen einen Pull Request; bei drei Personen ist
das vertretbar. Eine Lücke bleibt: Mit einem lokal vorhandenen
Railway-Token wäre eine Veröffentlichung an der Pipeline vorbei möglich.
Sie ist in der Betriebsdokumentation benannt und ließe sich nur schließen,
indem das Token ausschließlich der Pipeline zur Verfügung steht.
