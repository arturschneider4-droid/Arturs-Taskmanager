# Arturs Taskmanager V10 – Executive Command Center

**Status:** Vom Nutzer in fünf Designabschnitten freigegeben  
**Zielversion:** V10  
**Ausgangsbasis:** V9.2, Branch `release/v9.2-test`  
**Zielgruppe:** Ein einzelner Geschäftsführer; lokaler Offline-Betrieb unter Windows

## 1. Zielbild

V10 entwickelt den bestehenden Taskmanager zu einem persönlichen „Executive Command Center“ weiter. Die Anwendung bildet nicht nur offene Aufgaben ab, sondern den vollständigen persönlichen Steuerungsprozess:

1. Eingang erfassen,
2. Aufgabe klären,
3. selbst bearbeiten oder einplanen,
4. delegieren oder auf Rückmeldung warten,
5. zum richtigen Zeitpunkt wieder vorlegen,
6. Tages- und Wochenfokus steuern,
7. Ergebnisse nachvollziehbar abschließen.

Die Anwendung bleibt vollständig lokal, offline, schnell und für einen Benutzer ausgelegt. Mehrbenutzerverwaltung, Chat, Kommentare, Freigabeworkflows und Team-Ressourcenplanung gehören ausdrücklich nicht zum Umfang.

## 2. Verbindliche Produktprinzipien

### 2.1 Funktion vor Dekoration

Jedes sichtbare Bedienelement muss eine vollständige, verständliche Funktion besitzen. Dies gilt insbesondere für Buttons, Menüpunkte, Filter, Navigationspunkte, Kontextmenüs, Schnellaktionen, Shortcuts, Drag-and-drop-Ziele, Dashboard-Karten und Einstellungsoptionen.

Ein Bedienelement ist nur fertig, wenn:

- die beabsichtigte Aktion implementiert ist,
- der Benutzer eine sichtbare Rückmeldung erhält,
- leere und ungültige Zustände behandelt werden,
- Fehler verständlich angezeigt werden,
- die Aktion per automatisiertem Interaktionstest geprüft wird,
- die Aktion in der Windows-EXE genauso funktioniert wie im Entwicklungsbetrieb.

Nicht zulässig sind Attrappen, deaktivierte Platzhalter ohne Erklärung, Menüpunkte mit reinen Informationsdialogen anstelle der erwarteten Funktion oder Schaltflächen, die nur das Aussehen ändern, ohne den dazugehörigen Zustand korrekt zu speichern.

### 2.2 Progressive Offenlegung

Häufig benötigte Informationen sind sofort sichtbar. Selten benötigte Felder bleiben eingeklappt. Neue Funktionen dürfen die Erfassung einer einfachen Aufgabe nicht verlangsamen.

### 2.3 Geschwindigkeit

Ansichtswechsel aktualisieren ausschließlich die betroffenen Oberflächenbereiche. Vollständige Neuaufbauten aller Ansichten sind zu vermeiden.

### 2.4 Datensicherheit

Bestehende V9.2-Daten müssen vollständig erhalten bleiben. Migrationen laufen transaktionsbasiert und werden durch ein automatisches Backup abgesichert.

## 3. Visuelles Design

### 3.1 Grundlayout

V10 verwendet die freigegebene Variante A „Executive Split View“ in Anlehnung an den bereitgestellten Asana-Screenshot:

- **links:** dunkelblau-graue Navigation und Themengebiete,
- **Mitte:** aktive Liste, Dashboard oder Arbeitsansicht,
- **rechts:** permanentes Kontextpanel.

Das rechte Panel zeigt in der Startansicht den Wochenfokus. Nach Auswahl einer Aufgabe zeigt es deren Details. Beim Schließen oder Abwählen der Aufgabe erscheint erneut der Wochenfokus.

### 3.2 Gestaltungsregeln

- dunkelblau-graue Navigation,
- sehr heller Arbeitsbereich,
- Türkis als primäre Akzentfarbe,
- Rot ausschließlich für Risiken, überfällige Deadlines und fällige Eskalationen,
- feine Trennlinien statt flächiger Kartenrahmen,
- kompakte, gut lesbare Typografie,
- großzügige Weißräume,
- konsistente Abstände und Interaktionszustände,
- keine Farbverläufe oder dekorativen Effekte ohne Informationswert,
- klare Hover-, Fokus-, Aktiv-, Deaktiviert- und Fehlerzustände.

### 3.3 Responsives Verhalten

- Ab breiten Desktopfenstern bleiben alle drei Spalten sichtbar.
- Bei mittlerer Breite wird die Navigation auf Symbole reduziert.
- Bei kleiner Breite wird das Detailpanel als ein- und ausblendbares Overlay dargestellt.
- Kein Bedienelement darf abgeschnitten oder unerreichbar werden.
- Die Mindestgröße wird anhand des kleinsten vollständig bedienbaren Layouts definiert.

### 3.4 Verbindlicher Professional-UI-Qualitätsstandard

V10 muss wie eine moderne, professionell entwickelte Business-Anwendung wirken und darf nicht den Eindruck einer technisch erweiterten Standard-Qt-Oberfläche vermitteln. Der bereitgestellte Asana-Screenshot definiert die gewünschte visuelle Qualitätsrichtung: ruhig, klar, hochwertig, kompakt und konsequent hierarchisiert.

Hierfür wird ein zentrales Designsystem eingeführt, das mindestens folgende Tokens und Komponenten verbindlich festlegt:

- Farbpalette für Navigation, Flächen, Text, Akzent, Erfolg, Warnung und Risiko,
- Typografiestufen für Seitentitel, Abschnittstitel, Aufgaben, Metadaten und Hilfetexte,
- ein 4/8-Pixel-Abstandsraster,
- einheitliche Radien, Linienbreiten und Schatten,
- definierte Höhen und Innenabstände für Eingabefelder und Buttons,
- konsistente Symbolgröße und Strichstärke,
- Hover-, Fokus-, Aktiv-, Gedrückt-, Deaktiviert-, Lade-, Leer- und Fehlerzustände,
- einheitliche Komponenten für Navigation, Aufgabenzeilen, Chips, Kennzahlen, Menüs, Dialoge, Toasts und Detailfelder.

Die Anwendung verwendet soweit unter Windows verfügbar Segoe UI Variable beziehungsweise Segoe UI. Icons stammen aus einem konsistenten, lokal eingebetteten Outline-Symbolsatz. Gemischte Unicode-Symbole, uneinheitliche Emoji-Icons und improvisierte Schriftzeichen werden aus der Hauptoberfläche entfernt.

### 3.5 Visuelle Hierarchie und Mikrointeraktionen

- Pro Ansicht gibt es genau eine visuell führende Primäraktion.
- Sekundäraktionen sind zurückhaltend und erscheinen möglichst kontextbezogen.
- Aufgabenzeilen besitzen eine klare Informationsreihenfolge und keine konkurrierenden Farbsignale.
- Animationen werden sparsam eingesetzt und dauern typischerweise 120–180 ms.
- Panelwechsel, Hoverzustände und Speicherrückmeldungen dürfen nicht springen oder flackern.
- Ladezustände zeigen stabile Platzhalter oder dezente Fortschrittsanzeigen statt eingefrorener Oberflächen.
- Leere Ansichten erklären knapp den nächsten sinnvollen Schritt und bieten eine funktionierende Aktion an.
- Erfolgsmeldungen erscheinen dezent als Toast; blockierende Dialoge werden nur für irreversible oder sicherheitsrelevante Entscheidungen verwendet.

### 3.6 Visuelle Abnahme

Für Dashboard, Mein Tag, Eingang, Aufgabenliste, Warten auf, Delegiert, Eisenhower, Kanban, Kalender, Wochenreview, Einstellungen und Hilfe werden Referenz-Screenshots definiert. Die echte Windows-EXE wird bei mindestens drei Fenstergrößen geprüft:

- 1920 × 1080,
- 1366 × 768,
- definierte Mindestfenstergröße.

Abgenommen werden insbesondere Ausrichtung, Abstände, Textkürzung, Kontrast, Fokuszustände, sichtbare Scrollbereiche, konsistente Icons und das Fehlen abgeschnittener Bedienelemente. Ein funktional korrekter, aber sichtbar unfertiger oder inkonsistenter Bildschirm blockiert den Release.

## 4. Navigation und Startansicht

### 4.1 Persönliche Steuerung

- Executive-Dashboard
- Mein Tag
- Eingang
- Nächste 7 Tage
- Warten auf
- Delegiert
- Alle Aufgaben

### 4.2 Arbeitsansichten

- Aufgabenliste
- Kanban
- Eisenhower
- Kalender
- Wochenreview

### 4.3 Themengebiete

Themengebiete bleiben frei anlegbar. Beispiele sind Geschäftsführung, Vertrieb, Finanzen, Personal und Laborbetrieb. Jeder Eintrag filtert die aktuelle Arbeitsansicht und zeigt die Anzahl offener Aufgaben.

### 4.4 Executive-Dashboard

Das Executive-Dashboard ist die Startansicht. Die Mitte zeigt:

- Heute offen,
- Überfällig,
- fällige Wiedervorlagen,
- offene Delegationen,
- Top 3 des Tages,
- kritische Deadlines der nächsten sieben Tage,
- ungeklärte Aufgaben ohne Planung,
- Wochenfortschritt.

Alle Kennzahlen sind anklickbar und öffnen eine nachvollziehbare gefilterte Aufgabenliste. Ein Klick darf nicht nur optisches Feedback auslösen.

### 4.5 Wochenfokus im rechten Panel

Der Wochenfokus zeigt:

- drei frei definierbare Wochenziele,
- die nächste kritische Deadline,
- die älteste offene Delegation,
- die nächste Wiedervorlage,
- den Wochenfortschritt,
- die funktionsfähige Aktion „Wochenreview starten“.

## 5. Aufgabenmodell

### 5.1 Bestehende Felder

- Titel
- Beschreibung
- Themengebiet
- Eisenhower-Priorität
- Bearbeitungsstatus
- Unteraufgaben
- Wiederholungsregel
- Erstell- und Änderungszeitpunkt

### 5.2 Neue Planungsfelder

- Planungsdatum
- optionale Planungszeit
- verbindliche Deadline
- geschätzte Dauer in Minuten
- Tagespriorität/Top-3-Markierung
- individuelle Erinnerung aktiviert/deaktiviert
- Erinnerungszeitpunkt
- optionale Vorwarnzeit

Planungsdatum und Deadline sind voneinander unabhängig. Das Verschieben im Kalender ändert standardmäßig nur das Planungsdatum. Die Deadline ändert sich ausschließlich durch eine ausdrückliche Aktion.

### 5.3 Neue Nachverfolgungsfelder

- Steuerungsmodus: `self`, `delegated`, `waiting`
- verantwortliche Person oder Organisation
- delegiert am
- letzter Kontakt
- erwartete Rückmeldung
- Wiedervorlagedatum
- Personen-/Gesprächstags

Bearbeitungsstatus und Steuerungsmodus bleiben getrennt. Eine delegierte Aufgabe kann beispielsweise „In Arbeit“ sein, ohne in der eigenen Arbeitsliste zu erscheinen.

### 5.4 Wochenziele

Wochenziele werden separat gespeichert und besitzen Kalenderwoche, Jahr, Titel, Reihenfolge und Erledigt-Status. Pro Woche sind höchstens drei aktive Wochenziele vorgesehen.

## 6. Eingang und Schnellerfassung

### 6.1 Eingang

Neue Aufgaben dürfen ausschließlich mit einem Titel angelegt werden. Nicht eingeordnete Aufgaben landen im Eingang. Eine Aufgabe gilt als geklärt, sobald ein Steuerungsmodus und entweder ein Planungsdatum, eine Wiedervorlage oder ein expliziter Status „ohne Termin“ gesetzt wurden.

### 6.2 Schnellerfassung

`Strg + Leertaste` öffnet aus jeder Ansicht eine kompakte Eingabezeile. Die Eingabe unterstützt deutschsprachige Ausdrücke wie:

`Angebot Müller morgen #Vertrieb !wichtig 30min`

Erkannt werden mindestens:

- heute, morgen und Wochentage,
- nächste Woche,
- `#Themengebiet`,
- `!wichtig`, `!dringend` und definierte Prioritätskürzel,
- `@warten` und `@delegiert`,
- Zeitangaben wie `30min`, `1h` und `1h30`.

Nicht erkannte Bestandteile bleiben im Titel erhalten. Die Vorschau zeigt vor dem Speichern, welche Werte erkannt wurden. `Enter` speichert, `Esc` verwirft und `Tab` öffnet die erweiterten Felder.

## 7. Persönliche Steuerungsansichten

### 7.1 Mein Tag

Die Ansicht enthält:

1. Top 3,
2. weitere heute geplante Aufgaben,
3. überfällige Aufgaben,
4. heute fällige Wiedervorlagen.

Top 3 ist auf drei aktive Aufgaben begrenzt. Das Hinzufügen einer vierten Aufgabe erfordert die Auswahl einer Aufgabe, die aus Top 3 entfernt wird.

### 7.2 Nächste 7 Tage

Die Ansicht gruppiert Aufgaben nach Planungsdatum. Deadlines werden zusätzlich angezeigt und optisch von Planungsdaten unterschieden.

### 7.3 Warten auf

Die Ansicht zeigt Aufgabe, Person/Organisation, letzten Kontakt, Wiedervorlagedatum und Wartezeit. Überfällige Wiedervorlagen werden als Risiko markiert. Schnellaktionen erlauben Nachfassen, Verschieben der Wiedervorlage oder Rücknahme in die eigene Bearbeitung.

### 7.4 Delegiert

Delegierte Aufgaben werden primär nach verantwortlicher Person gruppiert. Sichtbar sind erwartete Rückmeldung, letzter Kontakt und Überfälligkeitsstatus. Ein Nachfassen aktualisiert den letzten Kontakt und kann eine neue Wiedervorlage setzen.

### 7.5 Personen- und Gesprächsagenda

Eine Personenansicht bündelt:

- offene Delegationen,
- wartende Rückmeldungen,
- offene Gesprächspunkte,
- zuletzt erledigte Punkte,
- Erfassung eines neuen Gesprächspunkts.

## 8. Arbeitsansichten

### 8.1 Aufgabenliste

Eine Zeile zeigt nur Erledigt-Kreis, Titel, Themengebiet, Planungsdatum oder Deadline und einen kompakten Hinweis auf Delegiert/Warten. Weitere Daten befinden sich im Detailpanel.

Beim Überfahren erscheinen funktionsfähige Schnellaktionen:

- Heute
- Morgen
- Delegieren
- Warten
- Erledigen
- Mehr

Die Liste behält Auswahl und Scrollposition bei, wenn eine Aufgabe rechts geöffnet oder gespeichert wird.

### 8.2 Kanban

Kanban bleibt statusbasiert. Drag-and-drop aktualisiert den Bearbeitungsstatus. Filter, Suche und Themengebiet gelten konsistent zur Listenansicht.

### 8.3 Eisenhower

Die vier Quadranten bleiben erhalten. Drag-and-drop ändert die Priorität. Die Top-3-Markierung bleibt davon unabhängig.

### 8.4 Kalender

- Türkis: Planungsdatum
- Rot: Deadline
- Grau: wiederkehrende Aufgabe
- Glockensymbol: Erinnerung aktiv

Drag-and-drop verschiebt standardmäßig das Planungsdatum. Das Verschieben einer Deadline erfordert eine separate, ausdrücklich beschriftete Aktion.

### 8.5 Wochenreview

Der Review führt schrittweise durch:

1. Eingang klären,
2. überfällige Aufgaben entscheiden,
3. Warten-auf-Punkte prüfen,
4. Delegationen prüfen,
5. wichtige Aufgaben ohne Planung einordnen,
6. drei Wochenziele definieren,
7. nächste Woche planen.

Der Fortschritt wird gespeichert. Nach Abschluss zeigt die Anwendung eine Zusammenfassung der geprüften, geplanten, delegierten und erledigten Aufgaben.

## 9. Detailpanel und Speichern

Das Detailpanel gliedert sich in:

1. Titel und Erledigt-Status,
2. Planung und Deadline,
3. Themengebiet und Priorität,
4. Selbst/Delegiert/Warten,
5. Wiedervorlage und Person,
6. Beschreibung,
7. Unteraufgaben,
8. Erinnerung und Wiederholung.

Änderungen werden nach validierter Eingabe automatisch gespeichert. Eine sichtbare Statusanzeige unterscheidet „Änderungen offen“, „Speichern …“, „Gespeichert“ und „Fehler“. Bei einem Speicherfehler bleiben die eingegebenen Daten im Panel erhalten.

## 10. Erinnerungen

Erinnerungen sind standardmäßig deaktiviert und werden individuell je Aufgabe aktiviert. Eine Erinnerung besitzt Zeitpunkt und optionale Vorwarnzeit. Windows-Benachrichtigungen dürfen den Programmstart nicht blockieren.

Ist die Anwendung zum Erinnerungszeitpunkt geschlossen, werden fällige Erinnerungen beim nächsten Start angezeigt. Eine Erinnerung kann als erledigt markiert oder auf einen späteren Zeitpunkt verschoben werden.

## 11. Tastatursteuerung

- `Strg + Leertaste`: Schnellerfassung
- `Strg + K`: globale Suche und Befehle
- `N`: neue vollständige Aufgabe
- `T`: heute einplanen
- `M`: morgen einplanen
- `D`: delegieren
- `W`: warten auf
- `1–4`: Eisenhower-Priorität
- `Leertaste`: erledigen
- `Entf`: löschen
- `Strg + Z`: rückgängig

Shortcuts wirken nur in einem eindeutigen Kontext und dürfen Texteingaben nicht überschreiben.

## 12. Einstellungen und Hilfe

Die Navigationspunkte „Einstellungen“ und „Hilfe“ werden nur angezeigt, wenn die zugehörigen Seiten vollständig implementiert sind.

Mindestens verfügbare Einstellungen:

- Startansicht (V10-Standard: Executive-Dashboard),
- Start der Anwendung mit Windows optional,
- Standarderinnerung und Vorwarnzeit,
- Arbeitswoche,
- Darstellung kompakt/komfortabel,
- Backup-Verzeichnis und manuelles Backup,
- Datenexport.

Die Hilfe enthält mindestens Shortcutübersicht, Erklärung von Planungsdatum/Deadline, Delegation/Wiedervorlage und Wiederherstellung aus einem Backup.

## 13. Datenmigration

### 13.1 Ablauf

1. Datenbankintegrität prüfen.
2. Automatisches Backup erzeugen.
3. Migration innerhalb einer Transaktion ausführen.
4. Schema und Daten prüfen.
5. Erst danach V10 starten.

Bei einem Fehler wird die Transaktion verworfen und V9.2 bleibt unverändert nutzbar.

### 13.2 Feldübernahme

- bisheriges `due_date` wird als V10-Deadline übernommen,
- bestehende Titel, Beschreibungen, Themengebiete, Prioritäten, Status, Wiederholungen und Unteraufgaben bleiben unverändert,
- neue Felder bleiben leer oder erhalten sichere Standardwerte,
- bestehende abgeschlossene Aufgaben bleiben abgeschlossen und durchsuchbar.

## 14. Technische Architektur

Neue Verantwortlichkeiten werden aus dem bisherigen großen UI-Modul herausgelöst:

- `dashboard.py` – Dashboardabfragen und Darstellung
- `task_model.py` – validiertes Aufgabenmodell
- `quick_capture.py` – Parser und Schnellerfassung
- `follow_up.py` – Delegation, Warten und Wiedervorlagen
- `weekly_review.py` – Reviewzustand und Ablauf
- `calendar_view.py` – Kalenderdarstellung und Umplanung
- `notifications.py` – Erinnerungsplanung und Windows-Ausgabe
- `v10_shell.py` – Navigation, Split View und Designsystem
- `migrations.py` – versionierte Schemaänderungen

Datenbankzugriff, Geschäftslogik und Darstellung bleiben getrennt. Ansichten erhalten vorbereitete Datenmodelle und führen keine verstreuten Einzelabfragen aus.

## 15. Leistungsziele

- Programmstart unter 2 Sekunden auf einem üblichen Windows-PC,
- Ansichtswechsel unter 150 ms bei 1.000 Aufgaben,
- Suche unter 200 ms,
- kein sichtbares Blockieren beim Speichern oder Verschieben,
- kein mehrfaches vollständiges Aktualisieren aufgrund eines einzelnen Klicks.

Dashboard-Zähler werden aggregiert abgefragt. Aufgabenzeilen werden wiederverwendet. Änderungen aktualisieren nur betroffene Ansichten und Datensätze. Sucheingaben werden entprellt.

## 16. Fehlerbehandlung und Wiederherstellung

- verständliche Fehlermeldungen ohne rohe Tracebacks,
- Eingaben bleiben nach einem Fehler erhalten,
- beschädigte Einstellungen werden durch sichere Standardwerte ersetzt,
- Erinnerungsfehler verhindern keinen Programmstart,
- mehrere letzte Benutzeraktionen sind rückgängig machbar,
- automatische und manuelle Backups können über eine echte Wiederherstellungsoberfläche ausgewählt werden.

## 17. Test- und Abnahmekonzept

### 17.1 Automatisierte Tests

- vollständige Migration repräsentativer V9.2-Datenbanken,
- Eingang und Klärungsworkflow,
- Planungsdatum versus Deadline,
- Delegation, Warten und Wiedervorlagen,
- individuelle Erinnerungen,
- Top-3-Begrenzung,
- Wochenziele und Wochenreview,
- Schnellerfassungsparser,
- Personenagenda,
- Filter, Suche, Sortierung und Gruppierung,
- alle Drag-and-drop-Wege,
- Backup, Wiederherstellung und mehrstufiges Undo,
- Performance mit 100, 1.000 und 5.000 Aufgaben,
- Windows-EXE-Start und Release-ZIP.

### 17.2 Bedienelement-Matrix

Für jede Oberfläche wird eine prüfbare Matrix geführt:

| Element | erwartete Aktion | Zustandsänderung | Benutzerfeedback | automatisierter Test |
|---|---|---|---|---|
| Beispiel: „Heute“ | Planungsdatum setzen | Aufgabe erscheint in Mein Tag | Datum und Statusmeldung | GUI-Test |

Der Release ist blockiert, solange ein sichtbares interaktives Element keinen Eintrag und keinen bestandenen Test besitzt.

### 17.3 Manuelle Oberflächenprüfung

Alle Hauptabläufe werden wiederholt in der gebauten Windows-EXE geprüft:

- neue Aufgabe und Schnellerfassung,
- Bearbeiten und Autosave,
- Delegieren und Wiedervorlage,
- Top 3 und Wochenfokus,
- Wochenreview,
- Filter und Ansichtswechsel,
- Kalender und Drag-and-drop,
- Erinnerung,
- Backup und Wiederherstellung,
- Tastatur- und Mausbedienung,
- kompakte und kleine Fenstergrößen.

### 17.4 Visuelle Regression und Designabnahme

- automatisierte Screenshots aller Hauptansichten mit deterministischen Testdaten,
- Vergleich gegen freigegebene Referenzbilder mit definierter Toleranz,
- getrennte Referenzen für 1920 × 1080, 1366 × 768 und Mindestgröße,
- Prüfung aller Hover-, Fokus-, Leer-, Lade-, Fehler- und Deaktiviert-Zustände,
- Prüfung von Skalierungsfaktoren 100 %, 125 % und 150 % unter Windows,
- manuelle Schlussabnahme der gebauten EXE anhand einer Design-Checkliste.

Die Design-Checkliste bewertet mindestens visuelle Hierarchie, Konsistenz, Lesbarkeit, Abstände, Ausrichtung, Iconqualität, Farbverwendung, Informationsdichte, Interaktionsfeedback und professionellen Gesamteindruck.

## 18. Nicht im Umfang

- Mehrbenutzerbetrieb
- Cloud-Synchronisierung
- Chat und Kommentare
- Rollen- und Rechtesystem
- Gantt-Diagramme
- Dokumentenverwaltung
- frei definierbare Custom Fields
- Team-Kapazitätsplanung
- Timesheets
- KI-Assistent

Diese Funktionen dürfen V10 weder verzögern noch die Benutzeroberfläche belasten.

## 19. Release-Abnahmekriterien

V10 ist releasefähig, wenn:

1. alle freigegebenen Funktionen vollständig implementiert sind,
2. kein sichtbares Bedienelement funktionslos ist,
3. die Bedienelement-Matrix vollständig und grün ist,
4. V9.2-Daten verlustfrei migriert werden,
5. alle automatisierten Tests bestehen,
6. die Leistungsziele erreicht oder dokumentiert begründet werden,
7. die gebaute Windows-EXE den Start- und Hauptworkflowtest besteht,
8. das ZIP eine vollständige, ausführbare Anwendung enthält,
9. Oberfläche und Interaktionen in der finalen EXE manuell geprüft wurden,
10. alle visuellen Referenzprüfungen bestehen,
11. kein Hauptbildschirm in der Designabnahme als unfertig, inkonsistent oder unprofessionell bewertet wird.
