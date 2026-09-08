# 0001 – Django als Rahmenwerk

**Status:** angenommen · **Datum:** 2026-08-31

## Kontext

Umzusetzen sind zwei Anwendungsfälle in vier Wochen, bei rund zwanzig
Arbeitstagen für sieben Meilensteine und einer Person in der Rolle
Entwickler. Benötigt werden Benutzerkonten mit Anmeldung, Formulare mit
Eingabeprüfung, dauerhafte Speicherung, eine Administrationsoberfläche für
den in MS 4 geforderten Administratorzugang sowie ein Auslieferungsweg, den
ein Team ohne Erfahrung im Betrieb bedienen kann. Der Entwickler hat in
keinem der erwogenen Rahmenwerke nennenswerte Vorerfahrung.

## Geprüfte Alternativen

1. **Node.js mit Express und einem React-Frontend.** Zwei Codebasen, zwei
   Bauprozesse, zwei Auslieferungswege. Anmeldung, Rechteprüfung und
   Migrationen wären Eigenbau.
2. **Flask oder FastAPI.** Schlanker Kern, aber jede benötigte Fähigkeit
   müsste als Erweiterung ausgewählt, eingebunden und geprüft werden.
3. **Django.** Größerer Rahmen als erforderlich, bringt jedoch alle
   benötigten Fähigkeiten mit.

## Entscheidung

Django 5.2 mit Python 3.12.

## Begründung

Bei einem Zeitbudget von vier Wochen entscheidet, wie viel Zeit in die
Fachlichkeit statt in Infrastruktur fließt. Django liefert Anmeldung,
Rechteverwaltung, ORM, Migrationen, Formularprüfung und
Administrationsoberfläche als Bestandteil des Rahmenwerks. Insbesondere
deckt die Administrationsoberfläche die Anforderung aus MS 4 nach einem
Administratorzugang ohne eigene Entwicklung ab. Da in keiner Alternative
Vorerfahrung besteht, gibt die geringere Lernlast pro nutzbarer Fähigkeit
den Ausschlag.

## Konsequenzen

Der Rahmen ist größer als für zwei Anwendungsfälle nötig; nicht jeder Teil
wird verwendet. Die Vorgaben von Django zu Projektaufbau und Namensgebung
sind einzuhalten. Ein späterer Wechsel des Rahmenwerks wäre ein Neubau.
