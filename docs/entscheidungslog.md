# Entscheidungslog

Fortlaufende Kurzdokumentation der Entscheidungen der Rolle Entwickler.
Format: Datum / Entscheidung / geprüfte Alternativen / Begründung.

Der Log ist die vollständige Chronik: Er enthält auch kleine Entscheidungen,
Korrekturen und Irrtümer. Die tragenden Architekturentscheidungen sind
zusätzlich als Architecture Decision Records in `docs/adr/` verdichtet – dort
in fester Gliederung und einzeln zitierbar, hier in zeitlicher Reihenfolge.
Ablage und Format sind in MS 3, Abschnitt 1.2, festgelegt.

---

**2026-08-31 – Serverseitig gerenderte Webanwendung mit Django**
Alternativen: React-Frontend mit Node.js/Express und REST-API; Flask.
Begründung: Eine Codebasis statt zwei bei einem Entwickler und 20 Arbeitstagen.
Django liefert Authentifizierung, ORM, Migrationen, Formularvalidierung und eine
Administrationsoberfläche mit; bei Express wäre jeder dieser Punkte Eigenbau.
Die Administrationsoberfläche deckt den in MS 4 geforderten Admin-Zugang ohne
eigene Entwicklung ab. Eine REST-Schnittstelle hätte nur einen Konsumenten und
wäre Selbstzweck. Der Entwickler hat in keiner der Alternativen Vorerfahrung,
sodass die geringere Lernlast den Ausschlag gibt.

**2026-08-31 – Auslieferung als Monolith**
Alternativen: Aufteilung in mehrere Dienste.
Begründung: Fachliche Grenzen sind bei zwei Anwendungsfällen nicht belastbar
bestimmbar. Ein Deployment-Artefakt reduziert die Zahl der Fehlerquellen an der
kritischsten Stelle, dem Zugriff des Tutors über den Browser. Vorgehen nach dem
Grundsatz "Monolith First" (Fowler, 2015).

**2026-08-31 – SQLite als Datenbank auf persistentem Volume**
Alternativen: PostgreSQL als eigener Dienst.
Begründung: Kein zusätzlicher Dienst zu betreiben und zu überwachen. Die
Datenmenge und die Zahl gleichzeitiger Zugriffe liegen weit unterhalb der Grenzen
von SQLite. Bedingung ist ein persistentes Volume, da die Datei sonst bei jeder
Veröffentlichung verloren geht.

**2026-08-31 – Vorgehensmodell Kanban**
Alternativen: Scrum in vollem Umfang; sequenzielles Phasenmodell.
Begründung: Bei drei Beteiligten und vier Wochen Laufzeit steht der Aufwand für
Sprint Planning, Daily Scrum, Sprint Review und Retrospektive nicht im Verhältnis
zum Nutzen. Übernommen werden aus Scrum nur Product Backlog und Review, das
Rollenmodell entfällt. Ein sequenzielles Modell scheidet aus, weil die technische
Umsetzbarkeit bei fehlender Framework-Erfahrung nicht vorab feststeht.

**2026-08-31 – Technische Dokumentation nach arc42, auf sieben Kapitel reduziert**
Alternativen: vollständige arc42-Struktur mit zwölf Kapiteln; freie Gliederung.
Begründung: Verwendet werden Randbedingungen, Kontextabgrenzung,
Lösungsstrategie, Bausteinsicht, Verteilungssicht, Querschnittskonzepte und
Architekturentscheidungen. Qualitätsanforderungen werden in der Qualitätsplanung
geführt, Laufzeitsicht, Risiken und Glossar trägen bei diesem Systemumfang keine
Aussage. Die Reduktion folgt der Empfehlung von arc42, nur aussagekräftige
Kapitel zu füllen.

**2026-08-31 – Entwicklungsumgebung Visual Studio Code**
Alternativen: PyCharm.
Begründung: Kostenfrei, plattformübergreifend, Debugger und Testintegration über
die Python-Erweiterung. Der komfortablere Django-Support von PyCharm liegt in der
kostenpflichtigen Variante; eine zweite Einarbeitung neben dem Framework selbst
ist im Zeitbudget nicht darstellbar.

**2026-08-31 – Eigene Pflanzenstammdaten statt externer Programmierschnittstelle**
Alternativen: Anbindung einer öffentlichen Pflanzendatenbank.
Begründung: Externe Schnittstellen bringen Verfügbarkeits- und
Zugriffsbeschränkungsrisiken in die Demonstration. Die für die Eignungsprüfung
benötigten normalisierten Merkmale liefert keine der geprüften Quellen in
verwertbarer Form. Vorgesehen ist ein Startdatenbestand von rund 25 Pflanzen.

**2026-08-31 – Eignungsprüfung mit fünf Kriterien und zwei Ausschlusskriterien**
Alternativen: Gewichtete Punktbewertung über alle Merkmale; lernendes Verfahren.
Begründung: Geprüft werden Licht, Minimaltemperatur, Luftfeuchtigkeit, Bodenart
und Giftigkeit. Minimaltemperatur und Giftigkeit sind Ausschlusskriterien, da sie
sich nicht durch Pflege ausgleichen lassen. Ein gewichtetes Punktverfahren wäre
in der Gewichtung willkürlich und dem Nutzer nicht erklärbar; ein lernendes
Verfahren scheitert am fehlenden Datenbestand. Das gewählte Verfahren ist
vollständig durch Modultests abdeckbar.

**2026-09-01 – Hostingplattform Railway mit persistentem Volume**
Alternativen: Render Free; Render mit kostenpflichtigem Disk; PythonAnywhere.
Begründung: Render Free scheidet aus, da kostenlose Web-Dienste kein persistentes
Dateisystem einbinden können, nach 15 Minuten ohne Zugriff pausieren und
kostenlose Datenbanken 30 Tage nach Erstellung verfallen. Bei einem Projekt,
dessen Abnahme durch den Tutor zeitlich nicht steuerbar ist, wäre das ein
Ausfall des Liefergegenstandes. Railway bindet ein Volume unter /data ein, auf
dem die SQLite-Datei liegt und eine Veröffentlichung übersteht.
Umgesetzt am 01.09.2026. Oeffentliche Adresse:
https://studienprojekt-isef01.up.railway.app

**offen – Wechsel vom Testguthaben auf den Hobby-Plan**
Das Projekt läuft derzeit auf dem einmaligen Testguthaben (30 Tage oder 5 USD).
Läuft es aus, ist die Anwendung nicht mehr erreichbar. Da der Tutor das Ticket
zu MS 4 möglicherweise erst Wochen nach Einreichung schließt und MS 6 noch
später bewertet wird, ist vor Ablauf auf den Hobby-Plan (5 USD monatlich) zu
wechseln. Fälligkeit: vor dem 01.10.2026.

**2026-09-01 – Veröffentlichung aus der Prüfpipeline statt über die
GitHub-Anbindung von Railway**
Alternativen: Beobachtung des Repositorys durch Railway (Standardweg);
manuelle Veröffentlichung.
Begründung: Der ursprüngliche Weg scheiterte daran, dass die GitHub-App von
Railway sich nicht installieren ließ; Railway meldete dauerhaft "GitHub Repo
not found". Statt diesen Weg zu reparieren, stößt nun GitHub Actions die
Veröffentlichung an, nachdem Ruff, Django-Systemcheck und die Modultests
bestanden wurden. Fachlich ist das die bessere Lösung: Der Standardweg
veröffentlicht jeden Push unabhängig vom Testergebnis, während die Pipeline
ein echtes Qualitätstor vor der Auslieferung setzt. Damit entspricht der
Betrieb der in MS 3 formulierten Definition of Done, in der die bestandene
Prüfung der Veröffentlichung vorausgeht. Umgesetzt über einen
Projekt-Token, der als verschlüsseltes Repository-Geheimnis hinterlegt ist.
Erster erfolgreicher Durchlauf am 01.09.2026, Gesamtdauer 1:19 Minuten.

**2026-09-01 – Oeffentliche Adresse gekürzt**
Alternativen: automatisch erzeugte Adresse beibehalten.
Begründung: Die von Railway vergebene Adresse enthielt den vollständigen
Repositorynamen und war schwer lesbar. Da der Link im MS-4-Ticket steht und vom
Tutor aufgerufen wird, wurde er auf studienprojekt-isef01.up.railway.app
gekürzt. Nach der Änderung war eine erneute Veröffentlichung nötig, weil
Django über ALLOWED_HOSTS nur Anfragen an bekannte Hostnamen beantwortet und
die Anwendung bis dahin die alte Adresse kannte (Fehler 400).

**2026-09-02 – Trennung von Pflanzenart und Pflanze**
Alternativen: ein einziges Modell, bei dem jede Person die botanischen Merkmale
ihrer Pflanze selbst erfasst (ursprünglicher Entwurf).
Begründung: Die recherchierten Pflanzendaten beschreiben Arten, nicht die
Exemplare einzelner Nutzender. Im ursprünglichen Modell hätten Nutzende
Lichtbedarf, Temperaturuntergrenze, Luftfeuchtigkeit, Bodenarten, Giftigkeit
und Wuchshöhe je Pflanze selbst eintragen müssen, womit die Recherche
ungenutzt geblieben wäre. Eingeführt wurde daher das Modell Pflanzenart als
Katalog; die Pflanze einer Person verweist darauf. Arten ohne Ersteller bilden
den mitgelieferten Katalog, selbst angelegte Arten sind nur für die
anlegende Person sichtbar - damit bleibt die Forderung der Themenstellung
erfüllt, Eigenschaften nachträglich ergänzen zu können. Der Umbau erfolgte
am zweiten Projekttag, solange die Datenbank außer Stammdaten nichts enthielt.

**2026-09-02 – Bodenarten auf fünf Kategorien zusammengefasst**
Alternativen: die 14 recherchierten Bodenbeschreibungen unverändert
übernehmen.
Begründung: Die Eignungsprüfung vergleicht die Bodenart des Standorts mit
den verträglichen Bodenarten der Art. Beschreibungen wie "humos, feucht,
durchlässig" kann eine Privatperson über ihren Balkon nicht angeben, sodass
der Abgleich ins Leere liefe. Zusammengefasst wurde auf Blumenerde,
Kakteenerde, Orchideensubstrat, saure Erde und lehmiger Gartenboden. Die
Zuordnungstabelle ist in werkzeuge/pflanzendaten_konvertieren.py dokumentiert
und wurde der recherchierenden Rolle zur fachlichen Prüfung vorgelegt.

**2026-09-02 – Stammdaten als versionierte Fixture statt direktem Excel-Import**
Alternativen: Einlesen der Excel-Datei zur Laufzeit.
Begründung: Die Anwendung benötigt in der Produktion keine
Tabellenkalkulationsbibliothek, und der eingespielte Datenbestand ist als
JSON-Datei im Repository nachvollziehbar und zwischen Umgebungen identisch
reproduzierbar.

**offen – Luftfeuchtigkeit und Quellenangaben der Pflanzendaten**
Die Luftfeuchtigkeit ist bei allen 20 Arten nicht recherchiert und vorläufig
auf die mittlere Stufe gesetzt; sie ist eines der fünf Prüfkriterien.
Zu 14 der 20 Arten fehlt die Quellenangabe. Beides ist vor MS 4
nachzuliefern, da sonst ein Prüfkriterium auf Platzhalterwerten beruht und
die botanischen Angaben im Projektbericht nicht belegbar sind.

**2026-09-04 – MS 3 gegenüber MS 1 konsistent gemacht statt MS 1 nachträglich zu ändern**
Alternativen: Korrektur der bereits abgegebenen Projektkonfiguration (MS 1);
Widersprüche unkommentiert stehen lassen.
Begründung: MS 1 ist am 03.09. bereitgestellt. Ein nachträgliches Glätten
abgegebener Dokumente verdeckt den Erkenntnisgewinn zwischen den
Meilensteinen, der im Projektbericht gerade darzustellen ist. Die
Abweichungen wurden deshalb in MS 3 aufgelöst und dort, wo MS 3 bewusst
abweicht, als Präzisierung kenntlich gemacht. Betroffen sind fünf Stellen:
Antwortzeiten, Vermehrung, Benachrichtigungen, Anlage eigener Pflanzenarten
und die Rolle des IU-Redmine.

**2026-09-04 – Redmine nur für Abgabe und Tutorkommunikation**
Alternativen: Aufgabensteuerung in Redmine wie in MS 1 vorgesehen;
Doppelführung in Redmine und Teams Planner.
Begründung: Zwei parallel gepflegte Ticketsysteme erzeugen bei drei
Beteiligten und vier Wochen Laufzeit Pflegeaufwand ohne Erkenntnisgewinn und
laufen erfahrungsgemäß auseinander. Der Teams Planner ist im Team bereits
etabliert. Die Einschränkung ist in MS 3, Abschnitt 1.2, als Abweichung
gegenüber MS 1 ausgewiesen.

**2026-09-04 – Anlage eigener Pflanzenarten wird umgesetzt**
Alternativen: ausschließlich Auswahl aus dem mitgelieferten Katalog, die
Anforderung aus MS 1 als überholt dokumentieren.
Begründung: MS 1 sagt zu, dass Nutzende Pflanzen mit eigenen Eigenschaften
erfassen können; die Themenbeschreibung führt dies unter Anwendungsfall 1.
Das Datenmodell ist bereits darauf ausgelegt (Pflanzenart.erstellt_von ist
beim Katalog leer und wird bei einem eigenen Eintrag gesetzt, der nur für
die anlegende Person sichtbar ist), sodass lediglich Formular, Ansicht und
Tests fehlen. Der Aufwand von etwa einem halben Tag ist geringer als der
Begründungsaufwand für eine nicht erfüllte Zusage.

**2026-09-04 – Vermehren ohne artbezogene Intervallempfehlung**
Alternativen: Vermehrungsintervalle je Art nachrecherchieren lassen;
Vermehrung aus dem Funktionsumfang streichen.
Begründung: Vermehren ist im Modell bereits als Tätigkeit vorgesehen, in
den recherchierten Stammdaten aber nicht enthalten; die 78 Empfehlungen
decken Gießen, Düngen, Umtopfen und Zurückschneiden ab. Eine
Nachrecherche in der laufenden Woche würde die Rolle Qualitätssicherung
von der Testvorbereitung abziehen. Die Pflegevorlage für das Vermehren
legt die nutzende Person daher selbst an. In MS 3, Kapitel 2, ist dies so
festgehalten.

**2026-09-04 – Antwortzeit unter zwei Sekunden als Stichprobe statt Messziel**
Alternativen: Lastmessung mit Werkzeugunterstützung; Anforderung aus MS 1
fallen lassen.
Begründung: MS 1 nennt eine Antwortzeit unter zwei Sekunden als
Qualitätsanforderung, während MS 3 die Leistungseffizienz nach
ISO/IEC 25010 als nicht vertieft geprüftes Merkmal einstuft. Bei einem
Datenbestand von 20 Pflanzenarten und wenigen Nutzerkonten ist eine
Lastmessung ohne Aussagekraft. Die Anforderung wird deshalb stichprobenartig
im manuellen Test geprüft und im Testabschlussbericht vermerkt.

**2026-09-05 – Wortmarke aus dem Projektvideo in die Anwendung übernommen**
Alternativen: Bildausschnitt aus dem Video verwenden; Schriftzug als Text mit
einer Webschrift setzen; auf eine Wortmarke verzichten.
Begründung: Der Ausschnitt aus dem Video ist perspektivisch verzerrt, liegt
auf einem Verlauf und trägt Kompressionsspuren, taugt also nicht als
Bildmarke. Eine Webschrift von einem fremden Dienst widerspräche der Zusage
in MS 3, keine extern gehosteten Schriftarten einzubinden. Die Wortmarke ist
deshalb aus der Schrift Poppins Bold (SIL Open Font License) in Pfade
umgewandelt und liegt als SVG im Repository; damit ist weder eine
Schriftdatei noch ein externer Abruf nötig. Die Blattmarke ist
nachgezeichnet. Ein einheitliches Erscheinungsbild zwischen Video und
Anwendung stützt die Wiedererkennung in der Ergebnispräsentation.

**2026-09-05 – Kopfzeile bleibt grün, Korallton nur als Akzent**
Alternativen: Kopfzeile im Korallton des Videos.
Begründung: Weiße Schrift auf dem Korallton (#EF8348) erreicht ein
Kontrastverhältnis von etwa 2,6 zu 1 und verfehlt die Anforderung von
4,5 zu 1 für Beschriftungen. Benutzbarkeit ist eines der vier vertieft
geprüften Qualitätsmerkmale, deshalb hat die Lesbarkeit Vorrang vor der
Farbtreue zum Video. Der Korallton erscheint als schmaler Markenstreifen
über der Kopfzeile und großflächig auf der Anmeldeseite, wo er keine
Beschriftung hinterlegt. Zusätzlich bleibt er dadurch von den Ampelfarben
der Eignungsprüfung unterscheidbar.

**2026-09-05 – Bodenarten nach fachlicher Vorgabe neu geschnitten**
Alternativen: bisherige Zuordnung von 14 Bodenbeschreibungen auf Handelsnamen
beibehalten; die fünf Kategorien der Qualitätssicherung wörtlich als
Bezeichnung übernehmen.
Begründung: Die Rolle Qualitätssicherung hat die Bodenbeschreibungen im
Review des Pull Requests auf fünf Kategorien festgelegt und die Zuordnung
je Art korrigiert; die ursprüngliche Einordnung von Lavendel auf lehmigen
Gartenboden war fachlich falsch. Die Kategorienamen bestehen nun aus einem
geläufigen Namen und der fachlichen Beschreibung ("Kakteenerde oder
Sandboden – trocken und sehr durchlässig"), weil die Beschreibung allein
von einer Privatperson nicht beantwortbar ist, der Handelsname allein aber
die fachliche Festlegung verlieren würde. Die Beschreibung ist als eigenes
Feld modelliert und erscheint in der Auswahlliste des Standortformulars.
Die Kategorie "saure Erde" entfällt, da sie von keiner Art des Katalogs
benötigt wird und damit weder demonstrierbar noch testbar wäre.

**2026-09-05 – Luftfeuchtigkeit und Quellenangaben vollständig**
Der Platzhalter für die Luftfeuchtigkeit entfällt: Alle 20 Arten tragen
einen recherchierten Wert, damit ist das fünfte Prüfkriterium der
Eignungsprüfung wirksam. Alle 20 Arten sind mit Institution und Direktlink
belegt (Royal Horticultural Society, NC State Extension); die botanischen
Namen wurden aus dem Quellenblatt übernommen. Der früher offene Eintrag
zu diesen beiden Lücken ist damit erledigt.

**offen – zwei Widersprüche und eine fragliche Temperaturangabe**
In der Datei V2 weicht die Luftfeuchtigkeit zwischen Datenblatt und
Quellenblatt bei zwei Arten ab (Friedenslilie 2 gegen 3, Yucca-Palme 2 gegen
1); eingespielt ist der Wert des Datenblatts. Ferner trägt der
Weihnachtskaktus eine Temperaturuntergrenze von 21 Grad Celsius und wäre
damit in nahezu jedem Wohnraum ungeeignet, da die Temperatur ein
Ausschlusskriterium ohne Toleranzstufe ist. Beides ist mit der Rolle
Qualitätssicherung zu klären.

**2026-09-05 – Konfiguration bricht ab, statt unsicher weiterzulaufen**
Alternativen: Ersatzwerte für SECRET_KEY und DEBUG beibehalten; Prüfung nur
in der Betriebsdokumentation beschreiben.
Begründung: Bisher war der Fehlersuchmodus voreingestellt und für den
Signaturschlüssel stand ein Ersatzwert im Repository. Eine fehlende oder
falsch gesetzte Umgebungsvariable hätte die Anwendung nicht angehalten,
sondern in der Produktion mit sichtbaren Fehlermeldungen und einem
öffentlich bekannten Schlüssel weiterlaufen lassen; Sitzungs- und
CSRF-Merkmale wären fälschbar gewesen. Die Voreinstellung ist deshalb
umgekehrt: Ohne DEBUG gilt Produktionsbetrieb, und fehlt dann der
Schlüssel, endet der Start mit ImproperlyConfigured. Lokal wird bei
DEBUG=1 je Start ein Zufallswert erzeugt, der nicht in eine
Produktionsumgebung geraten kann. Die Testläufe verwenden dieselbe
Konfiguration wie die Produktion; lediglich die HTTPS-Weiterleitung ist
im Testlauf abgeschaltet, weil der Testclient kein TLS spricht.

**2026-09-05 – Eigene Tests für die Verdrahtung der Eignungsprüfung**
Alternativen: bei den bestehenden Regeltests bleiben.
Begründung: Die Abdeckungsmessung zeigte, dass ausschließlich die Funktion
pruefe_eignung ungetestet war, also genau die Stelle, die Modellfelder
ausliest und den fünf Regeln übergibt. Vertauschte Argumente, etwa Angebot
und Bedarf beim Licht, wären von den Regeltests nicht bemerkt worden, da
dort beide Werte einzeln gesetzt sind. Die neun ergänzten Tests prüfen
deshalb bewusst unsymmetrische Fälle, bei denen ein Vertauschen zu einem
anderen Urteil führte. Die Anweisungsüberdeckung der Bewertungslogik liegt
damit bei 100 Prozent und erfüllt die in MS 3 gesetzte Schwelle von 90
Prozent nachweislich.

**2026-09-05 – Kennwort-Zurücksetzen schreibt in das Protokoll**
Alternativen: die Strecke aus der Adressverwaltung entfernen; einen
Postausgangsserver anbinden.
Begründung: Die mitgelieferte Anmeldung von Django stellt eine Strecke zum
Zurücksetzen des Kennworts bereit, die eine E-Mail versendet. Ohne
konfigurierten Versand endete jeder Aufruf in einem Serverfehler. Ein
eigener Postausgangsserver steht für den Prototyp nicht zur Verfügung und
wäre für zwei Anwendungsfälle unverhältnismäßig. Die Nachricht wird daher
in das Protokoll geschrieben, wo der Administrator den Link ablesen und
weitergeben kann. Das Verfahren ist in der Betriebsdokumentation zu
beschreiben.

**2026-09-05 – Anzeigetexte der Eignungsprüfung mit Umlauten**
Die Begründungen, die nach jeder Prüfung angezeigt werden, enthielten
Umschreibungen wie "benoetigt" oder "Blattschaeden", teilweise im selben
Satz mit korrekt geschriebenen Wörtern. Da es sich um reine Anzeigetexte
handelt, wurden sie berichtigt. Gespeicherte Werte wie giessen und die
Bezeichner der Felder bleiben unverändert, da eine Änderung eine
Datenmigration erfordern würde.

**2026-09-06 – Einheitliche Schaltflächen, helle Variante nur für Nebenaktionen**
Alternativen: die bisherige Zweiteilung in kräftige und stille
Schaltflächen beibehalten; alle Schaltflächen ohne Ausnahme orange
einfärben.
Begründung: Die stille Variante war ohne Regel vergeben worden, weshalb
gleichrangige Schaltflächen unterschiedlich aussahen. Die Klasse wurde
entfernt; die Grundform ist nun orange mit dunkler Schrift. Zwei
begründete Ausnahmen bleiben: Die Prüfung "Passt sie?" steht neben der
Hauptaktion einer Zeile und tritt bewusst zurück, und die Schaltfläche
zum Abmelden liegt auf der orangen Kopfleiste, wo eine orange Fläche
nicht erkennbar wäre. Löschende Aktionen behalten die rote Auszeichnung,
da die Farbe dort eine Bedeutung trägt.

**2026-09-06 – Aktive Seite über aria-current auszeichnen**
Alternativen: eine eigene Gestaltungsklasse je Menüpunkt setzen; die
Zuordnung über Namensvergleiche in der Vorlage lösen.
Begründung: Die Hauptnavigation zeigte nicht, auf welcher Seite sich der
Benutzer befindet. Die Markierung hängt nun am Attribut aria-current, das
gleichzeitig Bildschirmleser bedient und als Aufhänger für die Gestaltung
dient; Auge und Hilfsmittel beziehen ihre Auskunft damit aus derselben
Quelle. Ausgezeichnet wird über Fläche und Schriftschnitt, nicht über
Farbe allein, entsprechend WCAG 1.4.1 (Use of Color). Die Zuordnung von
Ansicht zu Menüpunkt liegt als Kontextprozessor in plants/navigation.py,
weil mehrere Ansichten keinen eigenen Menüpunkt haben, etwa der
Pflegeplan unter "Meine Pflanzen". In der Vorlage wäre diese Zuordnung
nur als Kette von Zeichenkettenvergleichen abbildbar und nicht prüfbar
gewesen; als Kontextprozessor ist sie durch zwei Tests abgedeckt.

**2026-09-06 – Kalendergruppen benennen und leeren Tagesbestand erklären**
Alternativen: leere Gruppen mit dem Wert null anzeigen; die Bezeichnung
"Später" beibehalten.
Begründung: Der Kalender blendet leere Gruppen aus. Blieb nur die letzte
Gruppe übrig, stand die Überschrift "Später" ohne Bezugspunkt und war
nicht zu deuten; die Seite wirkte zudem unvollständig. Die Gruppe heißt
nun "Nach dieser Woche" und setzt die Reihe Überfällig, Heute, Diese
Woche fort. Steht weder etwas an noch aus, nennt eine Zeile über den
Gruppen das nächste Fälligkeitsdatum. Vier leere Gruppen anzuzeigen
wurde verworfen, da die Ansicht dadurch unruhig wird.

**2026-09-07 – .env-Datei wird beim Start eingelesen**
Alternativen: python-dotenv oder django-environ einbinden; bei der
bisherigen Lösung mit export DEBUG=1 je Terminalsitzung bleiben.
Begründung: Die sichere Voreinstellung (DEBUG aus, ohne SECRET_KEY kein
Start) führte in der Entwicklung wiederholt zu Startabbrüchen, deren
Ursache nicht erkennbar war, weil Umgebungsvariablen nur für das Fenster
gelten, in dem sie gesetzt wurden. Eine vorhandene .env wird nun beim
Start eingelesen; bereits gesetzte Variablen behalten Vorrang, damit eine
lokale Datei niemals Servereinstellungen verdrängt. Auf eine Bibliothek
wurde verzichtet, da die Aufgabe zehn Zeilen umfasst und jede weitere
Abhängigkeit gepflegt und auf Schwachstellen geprüft werden muss. Vier
Tests decken die Fälle ab, insbesondere den Vorrang der Umgebung.

**2026-09-07 – Testzugänge als Verwaltungskommando statt manuell angelegt**
Alternativen: die Konten über die Administrationsoberfläche anlegen; eine
Fixture-Datei mit fertigen Datensätzen ausliefern.
Begründung: MS 4 verlangt eine Liste von Testzugängen, und das Team
benötigt Zugänge zur gegenseitigen Prüfung. Von Hand angelegte Konten
sind nach einem Redeploy ohne Datenbestand verloren und auf einem
zweiten Rechner nicht reproduzierbar. Das Kommando "testdaten" legt vier
Zugänge (je zwei pro Prüfer, einer mit Bestand, einer leer) und einen
Administrator an, ist mehrfach ausführbar und bezieht die Fälligkeiten
der Pflegeaufgaben auf den Ausführungstag, sodass auch nach Wochen noch
eine überfällige und eine heute fällige Aufgabe im Kalender stehen. Eine
Fixture-Datei wurde verworfen, weil sie feste Datumsangaben enthielte.
Die Kennwörter stehen im Klartext im Quelltext; das ist für eine
Demonstrationsumgebung ohne echte Daten vertretbar und in der
Betriebsdokumentation als bewusste Abweichung zu benennen.

**2026-09-07 – Qualitätstor technisch durchsetzen statt nur vereinbaren**
Alternativen: bei der Absprache bleiben, dass niemand direkt auf main
committet; zusätzlich das Railway-Token aus den Arbeitsplätzen entfernen.
Begründung: In MS 3 ist festgehalten, dass Änderungen nur über Pull
Requests mit Review auf den Hauptzweig gelangen. Bislang war das eine
Absprache, deren Einhaltung sich nicht belegen ließ und die unter
Zeitdruck als Erstes fällt. Ein Ruleset auf dem Standardzweig verlangt nun
einen Pull Request mit einer Freigabe sowie das Bestehen des Statuschecks
"Statische Pruefung und Tests" und verbietet erzwungene Pushes; die Regel
gilt auch für den Eigentümer des Repositorys. Damit ist das
Qualitätstor aus der Prozessdokumentation nachweisbar wirksam. Als
verbliebene Lücke ist dokumentiert, dass eine Veröffentlichung mit einem
lokal vorhandenen Railway-Token weiterhin an der Pipeline vorbei möglich
wäre.

**2026-09-07 – Wechsel auf den Hobby-Tarif von Railway**
Alternativen: beim Testguthaben bleiben; auf den Pro-Tarif wechseln.
Begründung: Das Testguthaben endet am 01.10.2026, die Abgabe erfolgt am
28.09.2026. Da ein Meilenstein erst als erreicht gilt, wenn der Tutor das
Ticket schließt, und Rückfragen mehrere Tage dauern können, wäre die
Anwendung während der Bewertung möglicherweise nicht erreichbar gewesen –
ein Verstoß gegen die harte Anforderung, dass sie ohne Installation im
Browser bedienbar sein muss. Der Pro-Tarif wurde verworfen: Sein einziger
für uns relevanter Mehrwert sind Volume-Sicherungen, und der Datenbestand
lässt sich mit einem Kommando wiederherstellen.

**2026-09-07 – Katalogfassung V3 übernommen, Weihnachtskaktus korrigiert**
Beim Abgleich der Dokumentation mit dem geladenen Datenbestand fiel auf,
dass eine neuere Fassung der Pflanzenliste vorlag (V3 vom 07.09.2026), die
noch nicht importiert war. Sie enthält eine inhaltliche Korrektur: Beim
Weihnachtskaktus stand als Temperaturuntergrenze 21 Grad, was der
Wohlfühltemperatur entspricht und nicht der Untergrenze. Der Wert wurde auf
10 Grad berichtigt. Ohne die Korrektur wäre die Art für nahezu jeden
Wohnraum als bedingt geeignet oder ungeeignet bewertet worden – ein Fehler
in den Stammdaten, der sich als Fehler der Eignungslogik dargestellt hätte.
Zugleich wurde eine falsche Angabe in der fachlichen Dokumentation
berichtigt: Der Katalog umfasst 20 Arten, nicht rund hundert; die Zahl 102
bezeichnet die geladenen Objekte insgesamt (20 Arten, 77 Pflegeempfehlungen,
5 Bodenarten).

**2026-09-07 — Bildschirmfotos automatisiert statt von Hand aufgenommen**
Alternativen: die Bilder einzeln von Hand aufnehmen; auf Bilder im
Benutzerhandbuch verzichten.
Begründung: MS 3, Abschnitt 2.1, verlangt für jeden Abschnitt des
Benutzerhandbuchs eine bebilderte Schrittfolge. Von Hand aufgenommene
Bilder müssten nach jeder Änderung an der Oberfläche vollständig
wiederholt werden. Ein Skript baut daher eine Wegwerfumgebung auf, spielt
Katalog und Testdaten ein und nimmt die zwölf Ansichten in fester
Reihenfolge auf. Die Anmeldung erfolgt über einen unmittelbar erzeugten
Sitzungsschlüssel statt über das Formular, sodass keine Zugangsdaten
eingegeben werden. Der Lauf ist beliebig wiederholbar und liefert
identische Ausschnitte.

**2026-09-07 — Drei Befunde aus dem Abgleich der Bilder mit der Anwendung**
Beim Betrachten der Bilder fielen drei Mängel auf, die im Betrieb nicht
aufgefallen waren. Erstens war der Kontextschlüssel für die Überschrift der
Standortformulare als "überschrift" geschrieben, die Vorlage erwartete
jedoch "ueberschrift"; da Django fehlende Vorlagenvariablen stillschweigend
durch eine leere Zeichenkette ersetzt, blieben Seitentitel und Überschrift
unbemerkt leer. Ein Test prüft das nun. Zweitens stellten die Testdaten
Pflanzen an Standorte, welche die Eignungsprüfung ablehnt; die Zuordnung
wählt jetzt den Standort mit dem günstigsten Urteil, damit der
Beispielbestand der eigenen Empfehlung nicht widerspricht. Drittens saß die
Schaltfläche in den Karten je nach Textlänge mal oben, mal unten, weil sie
bei langen Angaben umbrach.
