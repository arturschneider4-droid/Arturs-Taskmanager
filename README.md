# Arturs Taskmanager

Offline Windows-Taskmanager für einen Benutzer.

## Ziel
Aufgaben nach Eisenhower-Priorität und Fälligkeit organisieren, Themengebieten zuordnen und über Aufgabenliste, Kanban und Planung bearbeiten.

## V9.2

Stabile Windows-Desktopversion mit:

- responsiver Premium-Enterprise-Oberfläche
- Aufgabenliste, Kanban, Eisenhower und Planung
- Themengebieten, Suche, Filtern, Sortieren und Gruppieren
- Detailpanel für Aufgaben und Unteraufgaben
- lokaler SQLite-Datenbank mit Backup und Rückgängig-Funktion
- Excel-Export
- geprüftem Windows-EXE- und ZIP-Build mit PyInstaller

## Tech Stack
- Python
- PySide6
- SQLite
- openpyxl

## Daten
Die lokale Datenbank liegt unter `%USERPROFILE%\TaskManager\tasks.db`.
