# Arturs Taskmanager

Offline Windows-Taskmanager für einen Benutzer.

## Ziel
Aufgaben nach Eisenhower-Priorität und Fälligkeit organisieren, Themengebieten zuordnen und über Aufgabenliste, Kanban und Planung bearbeiten.

## V10.0

Professioneller Offline-Taskmanager für die persönliche Aufgabensteuerung als Geschäftsführer:

- Executive Dashboard, Wochenfokus und geführtem Wochenreview
- „Mein Tag“, Top 3, Eingang und nächste sieben Tage
- Aufgabenliste, Kanban, Eisenhower-Matrix und Planungskalender
- Delegation, Warten auf, Wiedervorlagen und Personenagenda
- individuelle Erinnerungen und Tastatursteuerung
- lokaler SQLite-Datenbank, automatischen Backups und mehrstufigem Undo
- responsiver Oberfläche mit geprüften Referenzen für drei Fenstergrößen
- geprüftem Windows-EXE- und ZIP-Build mit PyInstaller

## Tech Stack
- Python
- PySide6
- SQLite
- openpyxl

## Daten
Die lokale Datenbank liegt unter `%USERPROFILE%\TaskManager\tasks.db`.

## Release

Der Windows-Workflow erzeugt `ArtursTaskmanager-V10.0-Windows.zip` und `SHA256SUMS-V10.0.txt`. Die ZIP-Datei enthält `ArtursTaskmanager.exe` samt Laufzeitdateien und benötigt keine separate Python-Installation.
