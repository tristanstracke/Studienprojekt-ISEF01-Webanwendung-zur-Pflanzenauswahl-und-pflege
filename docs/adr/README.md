# Architecture Decision Records

Jede tragende Architekturentscheidung steht hier in einer eigenen Datei,
fortlaufend nummeriert und nach der Entscheidung benannt. Die Form folgt
Michael Nygard (2011), *Documenting Architecture Decisions*.

**Bewusste Abwandlung.** Nygard sieht die Abschnitte Titel, Status, Kontext,
Entscheidung und Konsequenzen vor. Verwendet werden hier zusätzlich
*Geprüfte Alternativen* als eigener Abschnitt, weil die Prüfungsleistung
ausdrücklich verlangt, Alternativen nachvollziehbar zu machen. Der Abschnitt
*Status* bleibt einfach: Für ein Projekt von vier Wochen genügen die Werte
angenommen und abgelöst; einen Vorschlagszustand mit Umlaufverfahren gibt es
nicht.

Der fortlaufende Entscheidungslog in `docs/entscheidungslog.md` bleibt
daneben bestehen. Er enthält alle Entscheidungen einschließlich der kleinen
und der zurückgenommenen; die ADR sind die verdichtete Fassung der
tragenden.

| Nr. | Entscheidung | Status |
|---|---|---|
| [0001](0001-django-als-rahmenwerk.md) | Django als Rahmenwerk | angenommen |
| [0002](0002-sqlite-auf-volume.md) | SQLite auf dauerhaftem Volume | angenommen |
| [0003](0003-serverseitiges-rendern.md) | Serverseitiges Rendern statt Einzelseitenanwendung | angenommen |
| [0004](0004-fachlogik-ohne-datenbankzugriff.md) | Fachlogik als reine Funktionen | angenommen |
| [0005](0005-fail-safe-konfiguration.md) | Sichere Voreinstellungen mit Startabbruch | angenommen |
| [0006](0006-qualitaetstor-in-der-pipeline.md) | Qualitätstor in der Auslieferungspipeline | angenommen |
