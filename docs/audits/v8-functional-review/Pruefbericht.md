# V8 Funktionsprüfung – ursprüngliche Befunde und Korrekturstand

Geprüfter Produktstand: lokaler Commit e28b1c6, entsprechender Remote-Commit dbb401596dc4c0fc3e13f9b83ac650b41bc2965c.

## Ursprüngliches Ergebnis vor Korrektur

Keine Releasefreigabe. Die bestehende Testsuite besteht mit 125 Tests. Zusätzlich 35 Prüfszenarien jeweils dreimal mit frischer Datenbank: 105 Ausführungen, 63 erfolgreich und 42 mit Abweichungen. Alle Ergebnisse wiederholten sich in den drei Durchläufen. Filterprüfung umfasst zusätzlich 100 Kombinationen pro Durchlauf, insgesamt 300. Dies sind Szenarioprüfungen, keine Aussage über vollständige Codeabdeckung.

## Reproduzierbare Abweichungen

1. Rückgängig nach Editor-Speichern, Tabellen-Prioritätswechsel und Duplizieren funktioniert bei zuvor leerer Backup-Historie nicht. Button und internes `_undo_available` werden unterschiedlich gesetzt. Duplizieren legt außerdem über `save` bei neuer ID kein eigenes Vorher-Backup an.
2. Suche während einer ungespeicherten Titeländerung überschreibt diese Eingabe ohne Rückfrage. `refresh_tasks` lädt den ausgewählten Datensatz erneut in den Editor.
3. Prioritätswahl im Editor schreibt sofort in die Datenbank; erneutes Laden (auch durch Abbrechen) stellt den ursprünglichen Wert nicht wieder her. Andere Editorfelder werden erst mit Speichern persistiert.
4. Wöchentliche Wiederholung wird gespeichert, erzeugt beim Erledigen aber keine Folgeaufgabe. Die Codeprüfung findet keine Ausführung der Wiederholungsregel. Falls automatische Wiederholung nicht vorgesehen sein sollte, ist die UI-Bezeichnung zu klären.
5. Kartenwahl in Kanban, Eisenhower und Planung synchronisiert die Aufgaben-ID, macht den Editor aber nicht sichtbar. Der Editor liegt weiterhin auf der ausgeblendeten Aufgabenseite. `panel_open=True` beweist keine Sichtbarkeit.
6. Gruppierung nach Fälligkeit ordnet den formatierten Datumstext lexikografisch: 01.02.2027 vor 31.01.2027. Die separate Sortierung nach Fälligkeit funktioniert.
7. Kartenansichten ignorieren den aktiven Statusfilter, während die Aufgabenliste ihn berücksichtigt. Die gemeinsame Filterdarstellung suggeriert eine einheitliche Wirkung.
8. Nach Entfernen des Statusfilters bleibt `scope=Erledigt`, obwohl wieder offene Aufgaben angezeigt werden.
9. Liste/Kompakt ändert die bereits vorhandenen explizit gesetzten Zeilenhöhen nicht.
10. Strg+F führt nicht zum sichtbaren globalen Suchfeld; der Handler fokussiert das alte Suchwidget.

## Erfolgreich geprüfte Abläufe

Aufgaben über echten Dialog anlegen, bearbeiten, Neuanlage abbrechen; Editorwerte einschließlich Unteraufgaben persistieren; Themengebiete anlegen, umbenennen, löschen mit Erhalt der Aufgaben; sichtbare Suche mit Treffer und ohne Treffer; Rückgängig nach Statuswechsel, Löschen und Planungsänderung; Planungsziele Heute, Diese Woche und Später; interne Karten-Auswahlsynchronisation in allen drei Ansichten; drei Sortiermodi; sämtliche 100 Kombinationen von Priorität, Status und Fälligkeit in der Aufgabenliste; Excel-Datei schreiben und wieder einlesen; SQLite-Integritätsprüfung.

## Methodik und Grenzen

Linux/Qt-Offscreen mit QApplication, configure_main_window, temporären SQLite-Datenbanken und Produktionseinbindungen einschließlich priority_sync. Dialogeingaben und Bestätigungen werden automatisiert; Persistenz und UI-Handler sind echt. Keine Produktcodeänderungen. Gespeicherte Diagnoseprogramme dienen als reproduzierbare Prüfhilfen.

Nicht als bestanden behauptet: vollständige Windows-EXE-Prüfung, physische Maus-Drag-and-drop-Strecken, sämtliche Tastatur-/Fokusfolgen, Bildschirm-Skalierungen, Langzeitbetrieb, alle Modal-/Dateisystemfehler, jede beliebige Filterkombination über sämtliche Ansichten. Die Release-ZIP wurde nicht neu gebaut.

Die frühere Releasefähigkeitsbehauptung war nicht ausreichend belegt. Tests auf Quelltextfragmente, interne Zustände und Komponenten allein sichern das reale Gesamtverhalten nicht ab. Vor Freigabe brauchen insbesondere alle oben genannten Abweichungen reproduzierbare Regressionstests und Reparaturen sowie eine Prüfung des neu gebauten Windows-Artefakts.

## Reproduktion

Im Projektverzeichnis:

```sh
QT_QPA_PLATFORM=offscreen PYTHONPATH=. .venv/bin/python docs/audits/v8-functional-review/v8_deep_audit.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=. .venv/bin/python docs/audits/v8-functional-review/v8_dialog_audit.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
```


## Korrekturstand nach direkter Codeanpassung

Die zehn aufgelisteten Befundgruppen wurden im Produktcode bearbeitet. Ergebnis: 135 Tests bestanden einschließlich der beiden dreifach ausgeführten Diagnoseprogramme (105 Szenario-Ausführungen, sämtliche erfolgreich; darin 300 Filterkombinationsprüfungen). Die gemeinsamen Detailansichten sind nun Geschwister des View-Stacks; Kanban und Editor wurden zusätzlich gleichzeitig sichtbar gerendert. Editorentwürfe werden bei Suche und responsivem Größenwechsel nicht neu geladen. Editorprioritäten bleiben bis Speichern ungespeichert. Rückgängig-Aktivierung ist vereinheitlicht, Duplizieren erstellt ein Vorher-Backup. Wiederholungen werden innerhalb derselben Datenbanktransaktion beim Erledigen erzeugt; Monatsende, Schaltjahr, wiederholtes Setzen auf Erledigt und Wiederherstellung sind getestet. Automatische Wiederholung ohne Datum orientiert sich am heutigen Datum. Folge-Unteraufgaben beginnen unerledigt.

Die Windows-EXE/ZIP wurde in dieser Korrekturrunde nicht neu gebaut. Daraus folgt keine vollständige Windows-Releasefreigabe. Die oben dokumentierten Fehlresultate sind historische Vorher-Belege.
