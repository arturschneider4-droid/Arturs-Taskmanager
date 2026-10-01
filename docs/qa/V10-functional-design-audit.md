# V10 Funktions- und Designprüfung – 01.10.2026

## Behobener Kanban-Fehler

Reproduziert: In den Details einer offenen Aufgabe eine Beschreibung eingeben,
vor Ablauf des Autosave-Timers die Aufgabe im Kanban nach „In Arbeit“ verschieben
und eine weitere Aufgabe anlegen. Der veraltete Formularstand setzte den Status zurück.
Die Details speichern jetzt ausschließlich tatsächlich geänderte Felder auf Basis
des neuesten Datenbankstands. Ein Regressionstest reproduziert diese Reihenfolge.
Schneller Aufgabenwechsel und Fensterschließen speichern ausstehende Änderungen;
fehlerhafte Eingaben verhindern das Verlassen, statt Änderungen still zu verlieren.

## Nutzungsszenarien und Felder

Die automatisierten GUI- und Repositorytests verwenden isolierte Testdatenbanken.

| Szenario | Geprüfte Bedienung und Ergebnis |
| --- | --- |
| Erfassen | Maus und Tastatur, Titel, Datum, Dauer, Themengebiet; ungültige Dauer abfangen |
| Bearbeiten | Titel, Status, Planungsdatum, Deadline, Aufwand, Priorität, Themengebiet, Top 3, Steuerung, Person, Wiedervorlage, Beschreibung, Unteraufgaben, Erinnerung, Wiederholung speichern und erneut laden |
| Kanban/Eisenhower | Karten öffnen, Status/Priorität ändern, Drag-and-drop persistieren; andere Aufgaben unverändert |
| Navigation | Details aus Listen, Eingang, Boards, Kalender und Wiedervorlagen öffnen |
| Kalender | Planung und Deadline unabhängig verschieben |
| Wiedervorlagen | Selbst verwaltete, delegierte und wartende Aufgaben; Dashboardfilter |
| Wiederholung | Folgetermin einschließlich Monatsende, Unteraufgaben zurücksetzen, keine doppelte Anlage, Rückgängig |
| Unteraufgaben | Erledigt-Markierungen bei anderen Änderungen erhalten |
| Wochenreview | Vor/zurück, Antworten erhalten, Ziele speichern, Zielabschluss anzeigen |
| Einstellungen | Dichte sofort anwenden, Erinnerungsvorgabe berücksichtigen |
| Datenpflege | Backup/Wiederherstellung aus Einstellungen, Ansichten aktualisieren; bestehende Export-/Restoretests |
| Suche | Öffnen, Treffer per Tastatur wählen, Escape schließen |
| Fenster | Alle 14 Ansichten mit Daten bei 1920×1080, 1366×768 und 720×640; Details ohne horizontales Scrollen im schmalen Fenster |

## Designprüfung

42 deterministische, mit realistischen Beispieldaten gefüllte Referenzbilder
ersetzen die bisherigen leeren Ansichten. Alle Ansichten wurden visuell geprüft.
Korrigiert wurden überlagerte alte Aufgabenzeilen, zu schmale Eisenhower-Spalten
(2×2-Anordnung), schlecht lesbare Navigation, Tabellenbreiten, große Leerabstände,
das zu schmale Detailformular und unnötige leere Scrollflächen.
Lange Titel bleiben über Tooltip und Details vollständig zugänglich.

Die Pixelvergleiche laufen unter Linux mit Qt Fusion. Windows führt Funktionstests,
EXE-Start und Starts bei 100/125/150 Prozent Skalierung aus; das ersetzt keine
visuelle Abnahme auf jedem individuellen Windows-Gerät. Erinnerungen setzen eine
laufende Anwendung voraus. Die Prüfung ist keine Garantie für Fehlerfreiheit.

## Reproduzierbare Prüfungen

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q
QT_QPA_PLATFORM=offscreen python tests/v10/windows_smoke.py
git diff --check
```

Die Windows-Pipeline `.github/workflows/build-windows.yml` erstellt ZIP, EXE-Ordner
und SHA256-Prüfsumme nach erfolgreichen Tests.
