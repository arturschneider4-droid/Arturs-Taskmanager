# Arturs Taskmanager

Offline Windows-Taskmanager für einen Benutzer.

## Ziel
Aufgaben nach Eisenhower-Priorität und Fälligkeit organisieren, Themengebieten zuordnen und über Aufgabenliste, Kanban und Planung bearbeiten.

## V6.2
Stabilitätsversion mit Fokus auf:
- synchrone Prioritätsanzeige zwischen Editor und Aufgabenliste
- funktionierende Unteraufgaben
- funktionierende Status- und Prioritätsänderungen
- lokale SQLite-Datenbank
- Windows-EXE-Build mit PyInstaller

## Tech Stack
- Python
- PySide6
- SQLite
- openpyxl

## Daten
Die lokale Datenbank liegt unter `%USERPROFILE%\TaskManager\tasks.db`.
