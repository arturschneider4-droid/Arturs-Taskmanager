# Arturs Taskmanager V10 – Executive Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den bestehenden V9.2-Taskmanager in ein schnelles, professionelles persönliches Executive Command Center V10 überführen und als verifizierte Windows-EXE im ZIP ausliefern.

**Architecture:** Die vorhandene PySide6-/SQLite-Anwendung wird inkrementell weiterentwickelt. Neue Domänenlogik, Abfragen und Ansichten entstehen in fokussierten V10-Modulen; `ui.py` bleibt während der Migration kompatibel, wird aber nicht weiter mit Fachlogik belastet. Ein zentraler Store veröffentlicht gezielte Änderungsereignisse, sodass Ansichten nur betroffene Daten neu laden.

**Tech Stack:** Python 3.12, PySide6 6.8+, SQLite, pytest/pytest-qt, openpyxl, PyInstaller, GitHub Actions Windows

**Spec:** `docs/superpowers/specs/2026-09-26-v10-executive-command-center-design.md`

## Global Constraints

- Lokaler Offline-Einbenutzerbetrieb unter Windows; keine Cloud- oder Mehrbenutzerfunktionen.
- Bestehende V9.2-Daten werden vor jeder Migration automatisch gesichert und transaktionsbasiert verlustfrei übernommen.
- `due_date` wird zur V10-Deadline; Planungsdatum und Deadline bleiben unabhängig.
- Jedes sichtbare interaktive Element benötigt reale Aktion, Rückmeldung, Fehlerbehandlung und bestandenen GUI-Test.
- Keine Attrappen, Emoji-/Unicode-Ersatzicons oder reine Informationsdialoge anstelle erwarteter Funktionen.
- Start unter 2 s; Ansichtswechsel unter 150 ms bei 1.000 Aufgaben; Suche unter 200 ms.
- Windows-Referenzgrößen: 1920 × 1080, 1366 × 768 und definierte Mindestgröße; Skalierung 100 %, 125 % und 150 %.
- V10 wird nur freigegeben, wenn Tests, Bedienelement-Matrix, visuelle Abnahme, EXE-Smoke-Test und ZIP-Prüfung erfolgreich sind.

## Review Focus

- Eine abgebrochene oder fehlerhafte Migration darf weder Originaldaten noch Backup beschädigen; Task 2 testet Commit und Rollback mit echten V9.2-Fixtures.
- Schnelle Mehrfachklicks und Autosave dürfen keine älteren Werte über neuere schreiben; Task 5 testet Reihenfolge, Fehlererhalt und Debouncing.
- Shortcuts dürfen in Textfeldern nicht auslösen; Task 8 testet Fokuskontexte für sämtliche globalen Befehle.
- 5.000 Aufgaben und schnelle Ansichtswechsel dürfen keine Voll-Refresh-Kaskaden oder UI-Blockaden verursachen; Tasks 4 und 14 instrumentieren Abfragen und Refreshes.
- Kleine Fenster, lange Titel und Windows-Skalierung dürfen keine Bedienelemente abschneiden; Tasks 3 und 15 testen Mindestgröße, Elision, Fokus- und Scroll-Erreichbarkeit.

## Dateistruktur und Verantwortlichkeiten

| Bereich | Dateien | Verantwortung |
|---|---|---|
| Datenkern | `taskmanager/task_model.py`, `taskmanager/repositories.py`, `taskmanager/migrations.py` | Validierung, typisierte Modelle, atomare Datenzugriffe und Migrationen |
| Zustandsfluss | `taskmanager/task_store.py`, `taskmanager/undo.py` | gezielte Änderungsereignisse, Cache-Invaliderung, mehrstufiges Undo |
| Designsystem | `taskmanager/design_tokens.py`, `taskmanager/components.py`, `taskmanager/assets/icons/` | Tokens, Icons und wiederverwendbare professionelle Controls |
| Shell | `taskmanager/v10_shell.py`, `taskmanager/navigation.py`, `taskmanager/shortcuts.py` | Split View, responsive Navigation, Routing und Tastaturbefehle |
| Kernansichten | `taskmanager/dashboard.py`, `taskmanager/task_list.py`, `taskmanager/detail_panel.py` | Dashboard, performante Aufgabenliste und Autosave-Editor |
| Führungsworkflows | `taskmanager/quick_capture.py`, `taskmanager/follow_up.py`, `taskmanager/weekly_review.py` | Eingang, Parser, Delegation, Warten, Personenagenda und Review |
| Spezialansichten | `taskmanager/calendar_view.py`, `taskmanager/board_views.py`, `taskmanager/notifications.py` | Kalender, Kanban, Eisenhower und Erinnerungen |
| Betrieb | `taskmanager/settings.py`, `taskmanager/backup_restore.py`, `.github/workflows/build-windows.yml` | Einstellungen, Wiederherstellung und Release-Build |
| Qualität | `tests/v10/`, `docs/releases/V10-BEDIENMATRIX.md`, `docs/releases/V10-DESIGN-CHECKLIST.md` | Funktions-, Performance-, Screenshot- und Release-Nachweise |

---

### Task 1: V10-Vertrag und isolierte Testbasis

**Files:**
- Create: `tests/v10/conftest.py`
- Create: `tests/v10/test_release_identity.py`
- Modify: `taskmanager/__init__.py`
- Modify: `taskmanager/app.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces: Fixture `v10_database(tmp_path) -> pathlib.Path`, Fixture `v10_window(qtbot, v10_database) -> MainWindow`, Konstante `taskmanager.__version__ == "10.0"`.

- [ ] **Step 1:** Failing Tests für Versionsidentität, temporäre Datenbank und fensterlokale Testisolation schreiben.
- [ ] **Step 2:** `QT_QPA_PLATFORM=offscreen pytest tests/v10/test_release_identity.py -q` ausführen; erwartetes Ergebnis: FAIL wegen V9.2-Identität/fehlender Fixtures.
- [ ] **Step 3:** `pytest-qt` als Testabhängigkeit aufnehmen, Version auf `10.0` umstellen und den Datenbankpfad per expliziter Testkonfiguration injizierbar machen, ohne den Produktionspfad zu verändern.
- [ ] **Step 4:** Den Test erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 5:** Commit: `test(v10): establish isolated application contract`.

### Task 2: Verlustfreie Schema-Migration und Domänenmodell

**Files:**
- Create: `taskmanager/task_model.py`
- Create: `taskmanager/migrations.py`
- Create: `taskmanager/repositories.py`
- Create: `tests/v10/fixtures/v92_representative.sql`
- Create: `tests/v10/test_migrations.py`
- Create: `tests/v10/test_task_model.py`
- Modify: `taskmanager/db.py`

**Interfaces:**
- Produces: `TaskRecord`, `TaskDraft`, `ControlMode`; `migrate_to_v10(db_path: Path, backup_dir: Path) -> MigrationResult`; `TaskRepository.get/save/delete/query`.
- `TaskDraft` enthält exakt die Felder aus Spezifikation §5; Datumswerte sind `date | None`, Zeitpunkte `datetime | None`.

- [ ] **Step 1:** Failing Tests für V9.2-Feldübernahme, neue sichere Defaults, Wochenziele, Reviewzustand, Kontakte/Tags, Integritätsfehler und transaktionales Rollback schreiben.
- [ ] **Step 2:** `pytest tests/v10/test_migrations.py tests/v10/test_task_model.py -q` ausführen; erwartetes Ergebnis: FAIL wegen fehlender V10-Typen und Migration.
- [ ] **Step 3:** Versionierte Migration mit Tabellen `schema_versions`, `weekly_goals`, `review_sessions`, `task_people`, `undo_log` und indizierten neuen Taskfeldern implementieren.
- [ ] **Step 4:** Validierung implementieren: Titel nicht leer, Top-3-Grenze über Repository-Transaktion, Erinnerungszeit nur bei aktivierter Erinnerung und Follow-up-Pflichtfelder je Steuerungsmodus.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS einschließlich Prüfsummenvergleich der Legacy-Daten und erzwungenem Rollback.
- [ ] **Step 6:** Commit: `feat(v10): add safe migration and task domain model`.

### Task 3: Professionelles Designsystem und Komponentenbibliothek

**Files:**
- Create: `taskmanager/design_tokens.py`
- Create: `taskmanager/components.py`
- Create: `taskmanager/assets/icons/*.svg`
- Create: `tests/v10/test_design_system.py`
- Create: `tests/v10/test_components_gui.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces: `DesignTokens`, `build_stylesheet(tokens: DesignTokens, density: Density) -> str`, `IconRegistry.icon(name: str) -> QIcon`, Komponenten `PrimaryButton`, `IconButton`, `TaskRow`, `Chip`, `MetricCard`, `Toast`, `EmptyState`.

- [ ] **Step 1:** Failing Tests für feste Farb-/Typografie-/Abstands-/Größentokens, vollständig vorhandene SVG-Namen, Zustände und Tastaturfokus der Komponenten schreiben.
- [ ] **Step 2:** `pytest tests/v10/test_design_system.py tests/v10/test_components_gui.py -q` ausführen; erwartetes Ergebnis: FAIL wegen fehlender Komponenten.
- [ ] **Step 3:** Tokens mit 4/8-Pixel-Raster, Segoe-UI-Fallback, zentralem Türkis-Akzent, Risiko-Rot und Dichten `compact`/`comfortable` implementieren.
- [ ] **Step 4:** Lokale, lizenzkompatible Outline-SVGs samt Lizenzdatei einbetten und die Komponenten ohne Emoji-/Unicode-Icons erstellen.
- [ ] **Step 5:** Zustände normal, hover, pressed, focus, disabled, loading, empty und error automatisiert rendern und Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): introduce professional design system`.

### Task 4: Ereignisbasierter Store und Performancefundament

**Files:**
- Create: `taskmanager/task_store.py`
- Create: `tests/v10/test_task_store.py`
- Create: `tests/v10/test_query_performance.py`
- Modify: `taskmanager/repositories.py`

**Interfaces:**
- Produces: `TaskStore.changed: Signal[ChangeSet]`, `TaskStore.apply(command: TaskCommand) -> CommandResult`, `DashboardRepository.metrics(today: date) -> DashboardMetrics`, `TaskRepository.query(spec: QuerySpec) -> list[TaskSummary]`.

- [ ] **Step 1:** Failing Tests für gezielte `ChangeSet`-IDs, Dashboard-Aggregatabfrage, Query-Spezifikationen, Suche und 100/1.000/5.000-Datensatz-Benchmarks schreiben.
- [ ] **Step 2:** `pytest tests/v10/test_task_store.py tests/v10/test_query_performance.py -q` ausführen; erwartetes Ergebnis: FAIL wegen fehlendem Store.
- [ ] **Step 3:** Store, vorbereitete Aggregatabfragen, benötigte Indizes und 180-ms-Such-Debounce implementieren; keine Ansicht darf direkt verstreute SQL-Abfragen ausführen.
- [ ] **Step 4:** Tests erneut ausführen; erwartetes Ergebnis: PASS, Query-Ziele innerhalb der im Test dokumentierten Schwellen und genau ein relevantes Änderungsereignis pro Befehl.
- [ ] **Step 5:** Commit: `perf(v10): add targeted store and aggregate queries`.

### Task 5: Split-View-Shell, Navigation und stabiles Detailpanel

**Files:**
- Create: `taskmanager/v10_shell.py`
- Create: `taskmanager/navigation.py`
- Create: `taskmanager/detail_panel.py`
- Create: `tests/v10/test_shell_gui.py`
- Create: `tests/v10/test_detail_panel_gui.py`
- Modify: `taskmanager/app.py`

**Interfaces:**
- Consumes: `DesignTokens`, `TaskStore`, `TaskRecord`.
- Produces: `V10Shell.navigate(route: Route)`, `DetailPanel.open_task(task_id: int)`, `DetailPanel.save_state: SaveState`.

- [ ] **Step 1:** Failing GUI-Tests für alle Navigationsrouten, aktive Markierung, breite/kompakte/Overlay-Modi, Rückkehr zum Wochenfokus und Auswahl-/Scroll-Erhalt schreiben.
- [ ] **Step 2:** Failing GUI-Tests für Detailabschnitte, validiertes Autosave, Zustände offen/speichern/gespeichert/Fehler, schnelle Änderungsfolgen und Datenerhalt bei Fehler schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_shell_gui.py tests/v10/test_detail_panel_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Neue Shell als alleinigen Produktionspfad verdrahten; V6–V8-Stile nicht mehr stapeln, Legacy-Ansichten aber bis zu ihrer Ablösung adapterbasiert einhängen.
- [ ] **Step 5:** Detailpanel mit 250-ms-Autosave-Debounce und monotoner Revisionsnummer implementieren, sodass verspätete Antworten keine neueren Eingaben überschreiben.
- [ ] **Step 6:** Tests erneut ausführen; erwartetes Ergebnis: PASS ohne Full-Window-Rebuild beim Wechsel.
- [ ] **Step 7:** Commit: `feat(v10): build responsive executive split shell`.

### Task 6: Executive-Dashboard und Wochenfokus

**Files:**
- Create: `taskmanager/dashboard.py`
- Create: `tests/v10/test_dashboard.py`
- Create: `tests/v10/test_dashboard_gui.py`

**Interfaces:**
- Consumes: `DashboardRepository.metrics`, `V10Shell.navigate`.
- Produces: `ExecutiveDashboard`, `WeeklyFocusPanel`, `DashboardFilter` für jede anklickbare Kennzahl.

- [ ] **Step 1:** Failing Tests für acht Dashboard-Kennzahlen, drei Wochenziele, kritische Deadline, älteste Delegation, nächste Wiedervorlage und Wochenfortschritt schreiben.
- [ ] **Step 2:** Failing Parametertests schreiben, die jede Karte anklicken und die exakt passende gefilterte Aufgabenliste sowie einen zugänglichen Namen nachweisen.
- [ ] **Step 3:** `pytest tests/v10/test_dashboard.py tests/v10/test_dashboard_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Dashboard und Wochenfokus mit gezielten Store-Abonnements, funktionierender Primäraktion und erklärenden Empty States implementieren.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): add executive dashboard and weekly focus`.

### Task 7: Eingang und deutschsprachige Schnellerfassung

**Files:**
- Create: `taskmanager/quick_capture.py`
- Create: `tests/v10/test_quick_capture_parser.py`
- Create: `tests/v10/test_inbox_gui.py`

**Interfaces:**
- Produces: `parse_capture(text: str, today: date, projects: Sequence[str]) -> CapturePreview`, `QuickCaptureOverlay`, `InboxView`.

- [ ] **Step 1:** Parametrisierte Failing Tests für heute, morgen, Wochentage, nächste Woche, `#Thema`, Prioritätskürzel, `@warten`, `@delegiert`, `30min`, `1h`, `1h30` und unbekannte Titelteile schreiben.
- [ ] **Step 2:** GUI-Tests für `Strg+Leertaste`, Vorschau, Enter, Esc, Tab, reine Titelerfassung und Klärungskriterien schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_quick_capture_parser.py tests/v10/test_inbox_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Deterministischen Parser ohne externe Dienste sowie Overlay und Inbox-Workflow implementieren.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): add inbox and German quick capture`.

### Task 8: Mein Tag, Top 3, Aufgabenliste und Tastatursteuerung

**Files:**
- Create: `taskmanager/task_list.py`
- Create: `taskmanager/shortcuts.py`
- Create: `tests/v10/test_my_day_gui.py`
- Create: `tests/v10/test_task_list_gui.py`
- Create: `tests/v10/test_shortcuts_gui.py`

**Interfaces:**
- Produces: `TaskListView.set_query(QuerySpec)`, `MyDayView`, `ShortcutController.dispatch(action: ShortcutAction)`.

- [ ] **Step 1:** Failing Tests für Mein-Tag-Gruppen, Top-3-Grenze samt Ersetzungsdialog, Nächste-7-Tage-Gruppierung und getrennte Anzeige von Planung/Deadline schreiben.
- [ ] **Step 2:** Parametertests für Zeilenaktionen Heute/Morgen/Delegieren/Warten/Erledigen/Mehr sowie Auswahl- und Scroll-Erhalt schreiben.
- [ ] **Step 3:** Parametertests für alle Shortcuts aus §11 schreiben; jeder Test wiederholt sich mit Fokus in `QLineEdit`/`QTextEdit` und erwartet dort keine globale Aktion.
- [ ] **Step 4:** `pytest tests/v10/test_my_day_gui.py tests/v10/test_task_list_gui.py tests/v10/test_shortcuts_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 5:** Wiederverwendete/virtualisierte Aufgabenzeilen, Quick Actions, Top-3-Transaktion und kontextsensitiven Shortcut-Controller implementieren.
- [ ] **Step 6:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 7:** Commit: `feat(v10): deliver personal planning surfaces`.

### Task 9: Delegation, Warten auf und Personenagenda

**Files:**
- Create: `taskmanager/follow_up.py`
- Create: `tests/v10/test_follow_up.py`
- Create: `tests/v10/test_follow_up_gui.py`

**Interfaces:**
- Produces: `FollowUpService.delegate/wait/follow_up/reclaim`, `WaitingView`, `DelegatedView`, `PeopleAgendaView`.

- [ ] **Step 1:** Failing Domänentests für getrennte Status-/Steuerungsmodi, Wartezeit, überfällige Wiedervorlage, Nachfassen und Rücknahme schreiben.
- [ ] **Step 2:** GUI-Tests für Gruppierung nach Person, sichtbare Pflichtspalten, Schnellaktionen und neue Gesprächspunkte schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_follow_up.py tests/v10/test_follow_up_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Service und drei Ansichten implementieren; Nachfassen aktualisiert letzten Kontakt atomar und bietet eine neue Wiedervorlage an.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): add executive follow-up workflows`.

### Task 10: Wochenreview mit fortsetzbarem Fortschritt

**Files:**
- Create: `taskmanager/weekly_review.py`
- Create: `tests/v10/test_weekly_review.py`
- Create: `tests/v10/test_weekly_review_gui.py`

**Interfaces:**
- Produces: `WeeklyReviewService.start/resume/advance/complete`, `WeeklyReviewView`, `ReviewSummary`.

- [ ] **Step 1:** Failing Tests für die sieben Schritte, persistiertes Fortsetzen, maximal drei Wochenziele und korrekte Abschlusszahlen schreiben.
- [ ] **Step 2:** GUI-Tests für Zurück/Weiter, Abbruch/Fortsetzen, leere Schritte, Validierungsfehler und Abschlussnavigation schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_weekly_review.py tests/v10/test_weekly_review_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Review-Service und geführte Ansicht implementieren; Fortschritt nach jeder bestätigten Entscheidung speichern.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): add guided weekly review`.

### Task 11: Kanban, Eisenhower und Kalender

**Files:**
- Create: `taskmanager/board_views.py`
- Create: `taskmanager/calendar_view.py`
- Create: `tests/v10/test_board_views_gui.py`
- Create: `tests/v10/test_calendar_gui.py`

**Interfaces:**
- Produces: `KanbanView`, `EisenhowerView`, `CalendarView.move_planning_date`, `CalendarView.move_deadline_explicitly`.

- [ ] **Step 1:** Failing Drag-and-drop-Tests für Status, Priorität, ungültige Drops, konsistente Filter/Suche und unabhängige Top-3-Markierung schreiben.
- [ ] **Step 2:** Failing Kalender-Tests für Farb-/Iconsemantik, Planung-Drop ohne Deadline-Änderung und separat beschriftete Deadline-Aktion schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_board_views_gui.py tests/v10/test_calendar_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Legacy-Boards durch storebasierte Views ersetzen und Monats-/Wochenkalender mit expliziten Drop-Zielen implementieren.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): modernize boards and add planning calendar`.

### Task 12: Individuelle Erinnerungen und robuste Windows-Benachrichtigungen

**Files:**
- Create: `taskmanager/notifications.py`
- Create: `tests/v10/test_notifications.py`
- Create: `tests/v10/test_notifications_gui.py`

**Interfaces:**
- Produces: `ReminderScheduler.start/stop/reconcile`, `NotificationBackend.show`, `DueReminderDialog`.

- [ ] **Step 1:** Failing Tests für standardmäßig deaktivierte Erinnerungen, Vorwarnzeit, verpasste Erinnerung beim nächsten Start, Erledigen und Verschieben schreiben.
- [ ] **Step 2:** Failing Test schreiben, der einen Backend-Fehler erzwingt und trotzdem erfolgreichen App-Start sowie verständliches nichtblockierendes Feedback erwartet.
- [ ] **Step 3:** `pytest tests/v10/test_notifications.py tests/v10/test_notifications_gui.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Scheduler und ein austauschbares Backend auf Basis von `QSystemTrayIcon.showMessage` implementieren; Tests verwenden ein Fake-Backend und keine echte Systembenachrichtigung.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): add per-task reminder scheduling`.

### Task 13: Einstellungen, Backup/Wiederherstellung, Export und mehrstufiges Undo

**Files:**
- Create: `taskmanager/settings.py`
- Create: `taskmanager/backup_restore.py`
- Create: `taskmanager/undo.py`
- Create: `tests/v10/test_settings_gui.py`
- Create: `tests/v10/test_backup_restore.py`
- Create: `tests/v10/test_undo.py`
- Modify: `taskmanager/db.py`

**Interfaces:**
- Produces: `SettingsRepository.load/save`, `BackupService.create/list/restore`, `UndoManager.push/undo/can_undo`; Seiten `SettingsView`, `HelpView`, `RestoreDialog`.

- [ ] **Step 1:** Failing Tests für sämtliche Einstellungen, beschädigte Konfiguration, Windows-Autostart-Adapter und Datenexport schreiben.
- [ ] **Step 2:** Failing Tests für manuelles/automatisches Backup, Vorschau/Auswahl/Wiederherstellung und mehrere Undo-Schritte über Bearbeiten, Verschieben und Löschen schreiben.
- [ ] **Step 3:** `pytest tests/v10/test_settings_gui.py tests/v10/test_backup_restore.py tests/v10/test_undo.py -q` ausführen; erwartetes Ergebnis: FAIL.
- [ ] **Step 4:** Echte Einstellungs-/Hilfeseiten, atomare Wiederherstellung und befehlsbasiertes Undo implementieren; Navigationspunkte erst danach sichtbar machen.
- [ ] **Step 5:** Tests erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Commit: `feat(v10): complete settings recovery and undo`.

### Task 14: Vollständige Bedienelement-Matrix und End-to-End-Stabilität

**Files:**
- Create: `docs/releases/V10-BEDIENMATRIX.md`
- Create: `tests/v10/control_manifest.py`
- Create: `tests/v10/test_control_manifest.py`
- Create: `tests/v10/test_end_to_end.py`
- Create: `tests/v10/test_performance_acceptance.py`

**Interfaces:**
- Produces: `CONTROL_MANIFEST`, wobei jeder Eintrag Oberfläche, Objektname, Aktion, Zustandsänderung, Feedback und Test-ID enthält.

- [ ] **Step 1:** Manifest aus allen sichtbaren Controls der produktiven Routen erstellen und Failing Test schreiben, der fehlende, doppelte oder nicht sichtbare Objekt-Namen sowie fehlende Test-IDs ablehnt.
- [ ] **Step 2:** Mehrfach wiederholte E2E-Tests für Capture→Planung→Delegation→Nachfassen→Review→Abschluss sowie Speichern, Neustart und Wiederherstellung schreiben.
- [ ] **Step 3:** Instrumentierte Performance-Tests schreiben: Start <2 s, Wechsel <150 ms/1.000 Aufgaben, Suche <200 ms, höchstens ein View-Refresh pro Änderung.
- [ ] **Step 4:** `pytest tests/v10/test_control_manifest.py tests/v10/test_end_to_end.py tests/v10/test_performance_acceptance.py -q` ausführen und konkrete Lücken/Regressionen protokollieren; erwartetes Erstergebnis: FAIL bis alle Controls erfasst sind.
- [ ] **Step 5:** Ausschließlich nachgewiesene Verdrahtungs-, Stabilitäts- und Performanceursachen beheben und die drei Dateien erneut ausführen; erwartetes Ergebnis: PASS.
- [ ] **Step 6:** Vollsuite dreimal frisch ausführen: `QT_QPA_PLATFORM=offscreen pytest -q`; erwartetes Ergebnis: drei Läufe mit jeweils 0 Fehlern.
- [ ] **Step 7:** Commit: `test(v10): enforce complete functional acceptance`.

### Task 15: Visuelle Referenzen und professionelle Designabnahme

**Files:**
- Create: `tests/v10/test_visual_regression.py`
- Create: `tests/v10/visual_fixtures.py`
- Create: `tests/v10/baselines/`
- Create: `docs/releases/V10-DESIGN-CHECKLIST.md`
- Modify: `.github/workflows/build-windows.yml`

**Interfaces:**
- Produces: deterministische Screenshots pro Hauptroute, Größe und Zustand; Pixelvergleich mit dokumentierter Toleranz und Diff-Bildern.

- [ ] **Step 1:** Deterministische Testdaten und Screenshot-Harness für alle zwölf Hauptansichten sowie hover/focus/empty/loading/error/disabled definieren.
- [ ] **Step 2:** Referenzbilder bei 1920×1080, 1366×768 und Mindestgröße erzeugen, einzeln visuell prüfen und erst danach als Baselines aufnehmen.
- [ ] **Step 3:** Failing Tests für Pixelabweichung, Text-Elision, erreichbare Scrollflächen, Fokusrahmen und Control-Geometrien schreiben.
- [ ] **Step 4:** `pytest tests/v10/test_visual_regression.py -q` ausführen; erwartetes Ergebnis: PASS gegen die freigegebenen Baselines und keine unreviewten neuen Bilder.
- [ ] **Step 5:** Echte Windows-EXE bei 100/125/150 % Skalierung prüfen und Checkliste für Hierarchie, Konsistenz, Lesbarkeit, Abstände, Icons, Farbe, Dichte und Feedback vollständig dokumentieren.
- [ ] **Step 6:** Commit: `test(v10): lock professional visual quality`.

### Task 16: Verifizierter V10-Windows-Release

**Files:**
- Modify: `.github/workflows/build-windows.yml`
- Modify: `README.md`
- Create: `docs/releases/V10.0-RELEASE.md`
- Create: `tests/v10/test_packaging_contract.py`

**Interfaces:**
- Produces: `ArtursTaskmanager-V10.0-Windows.zip` mit startfähigem `ArtursTaskmanager.exe` und `SHA256SUMS-V10.0.txt`.

- [ ] **Step 1:** Failing Packaging-Test für V10-Dateinamen, erforderliche Module/Assets, Workflow-Branch, Prüfsumme und ZIP-Inhalt schreiben.
- [ ] **Step 2:** `pytest tests/v10/test_packaging_contract.py -q` ausführen; erwartetes Ergebnis: FAIL wegen V9.2-Workflow.
- [ ] **Step 3:** Windows-Workflow auf V10 umstellen: Vollsuite, PyInstaller-Build, Modul-/Assetprüfung, 12-s-Starttest, Hauptworkflow-Smoke-Test, ZIP und SHA-256-Artefakte.
- [ ] **Step 4:** Vollsuite lokal frisch ausführen und `git diff --check`; erwartetes Ergebnis: 0 Fehler.
- [ ] **Step 5:** Nach gesonderter Push-Freigabe den V10-Release-Branch ohne Force-Push veröffentlichen und den vollständigen Windows-Workflow beobachten.
- [ ] **Step 6:** ZIP herunterladen, SHA-256 verifizieren, entpacken und EXE-Start sowie Kernworkflow auf Windows prüfen.
- [ ] **Step 7:** Releasebericht mit Testzahlen, Performancewerten, visueller Abnahme, bekannten Einschränkungen und Hash abschließen.
- [ ] **Step 8:** Commit: `release: finalize Arturs Taskmanager V10.0`.

## Vorgeschriebene Ausführungsreihenfolge

Tasks 1–5 bilden das technische Fundament und werden strikt sequenziell umgesetzt. Danach können Dashboard/Capture und Follow-up/Review fachlich getrennt entwickelt werden, müssen aber jeweils einzeln geprüft und integriert werden. Tasks 14–16 sind harte Release-Gates; keine EXE wird als V10 freigegeben, solange eines dieser Gates rot ist.
