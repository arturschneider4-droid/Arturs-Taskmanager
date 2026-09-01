PRIORITIES={
    "important_urgent":"Wichtig & dringend",
    "important_not_urgent":"Wichtig & nicht dringend",
    "not_important_urgent":"Nicht wichtig & dringend",
    "not_important_not_urgent":"Nicht wichtig & nicht dringend",
}
STATUS=["Offen","In Arbeit","Erledigt"]
RECURRENCE={"none":"Keine Wiederholung","daily":"Täglich","weekly":"Wöchentlich","monthly":"Monatlich"}

# TÜV Rheinland-inspired corporate palette: Pantone 300 is the primary brand blue.
# The actual logo is deliberately not embedded in this private task manager.
THEME_COLORS={
    "primary":"#0050A4",
    "foreground":"#0050a4",
    "primary_dark":"#003B63",
    "primary_light":"#E7F1FA",
    "background":"#F4F7F9",
    "surface":"#FFFFFF",
    "border":"#D9E2E8",
    "text":"#172B3A",
    "muted":"#657784",
    "red":"#E52329",
    "yellow":"#F5B400",
    "green":"#0A9F4D",
    "gray":"#C9D0D5",
}

# Three-dot traffic-light representation used consistently in the task list,
# editor, Eisenhower view and Kanban cards.
PRIORITY_LIGHTS={
    "important_urgent": ("red","red","red"),
    "important_not_urgent": ("red","yellow","gray"),
    "not_important_urgent": ("yellow","yellow","gray"),
    "not_important_not_urgent": ("green","gray","gray"),
}

# V6.1 reference UI specification (kept independent from Qt so it can be tested offline).
UI_SPEC = {
    "brand": "Arturs Taskmanager",
    "version": "V6.2",
    "sidebar_width": 238,
    "sidebar_section_spacing": 12,
    "theme_item_height": 40,
    "topbar_height": 80,
    "navigation": ["Aufgaben", "Kanban", "Eisenhower", "Planung", "Themengebiete", "Berichte & Export", "Einstellungen", "Hilfe & Info"],
    "scopes": ["Heute", "Diese Woche", "Später", "Alle"],
    "task_columns": ["Aufgabe", "Themengebiet", "Priorität", "Fälligkeit", "Status"],
    "editor_title": "Aufgabe bearbeiten",
}


EDITOR_PRIORITY_LABELS={
    "important_urgent":"Dringend & wichtig",
    "important_not_urgent":"Wichtig",
    "not_important_urgent":"Normal",
    "not_important_not_urgent":"Nicht wichtig",
}
EDITOR_SUBTASK_ACTIONS=["hinzufügen","abhaken","bearbeiten","löschen"]
