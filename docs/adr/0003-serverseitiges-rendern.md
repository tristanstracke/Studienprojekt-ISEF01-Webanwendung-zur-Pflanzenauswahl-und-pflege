# 0003 – Serverseitiges Rendern statt Einzelseitenanwendung

**Status:** angenommen · **Datum:** 2026-08-31

## Kontext

Beide Anwendungsfälle bestehen aus Formularen, Listen und einer
Kalenderansicht. Der Tutor muss die Anwendung ohne Installation im Browser
bedienen können. Die Auslieferung soll ein Weg sein, den eine Person ohne
Betriebserfahrung beherrscht.

## Geprüfte Alternativen

1. **React oder Vue mit REST-Schnittstelle.** Getrennte Oberfläche mit
   eigenem Bauprozess, eigener Auslieferung und eigener Zustandsverwaltung.
   Die Schnittstelle hätte genau einen Konsumenten.
2. **Serverseitig erzeugtes HTML mit den Vorlagen von Django.** Eine
   Codebasis, ein Auslieferungsweg, keine Zustandsverwaltung im Browser.

## Entscheidung

Serverseitiges Rendern. JavaScript wird nur dort eingesetzt, wo eine
Aufgabe ohne es nicht lösbar wäre; derzeit an keiner Stelle.

## Begründung

Der fachliche Gewinn einer Einzelseitenanwendung wäre bei Formularen und
Listen gering, der Aufwand jedoch vollständig zusätzlich: zweiter
Bauprozess, zweite Auslieferung, Behandlung von Ladezuständen und Fehlern
im Browser. Eine Schnittstelle, die nur die eigene Oberfläche bedient, ist
Selbstzweck.

## Konsequenzen

Jede Interaktion ist ein vollständiger Seitenwechsel; Teilaktualisierungen
gibt es nicht. Für die vorliegenden Abläufe ist das ohne Bedeutung. Eine
spätere mobile Anwendung müsste eine Schnittstelle nachrüsten.
