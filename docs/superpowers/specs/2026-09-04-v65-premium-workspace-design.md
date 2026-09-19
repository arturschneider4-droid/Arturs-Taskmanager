# V6.5 Premium Workspace Design

## Goal
Replace the V6.4 presentation-only treatment with a visibly rebuilt desktop workspace while preserving the existing offline task-management behavior.

## Design direction
The application should feel like a deliberate enterprise productivity product: calm white workspace, deep TÜV-inspired blue navigation rail, strong typographic hierarchy, compact semantic controls, generous but efficient spacing, and clear separation between navigation, context, content and detail.

## Shell
- Rebuild the central shell rather than merely recoloring the existing layout.
- Keep the application title and version in a restrained top bar.
- Make primary navigation visually distinct from secondary actions.
- Treat Themengebiete as a first-class workspace.
- Make Übersicht a compact KPI/navigation area with readable counts.

## Task workspace
- Use a clear page header followed by a compact filter/action toolbar.
- Preserve task metadata: theme, priority, due date and status.
- Increase visual hierarchy of task titles and semantic badges.
- Provide a clear empty state when filters return no tasks.
- Keep the editor visible as the detail pane when a task is selected.

## Secondary workspaces
- Kanban, Eisenhower and Planung use the same surface/card language.
- Themes gets a dedicated workspace with theme cards and direct actions.

## Constraints
- Preserve SQLite/offline operation and existing task/subtask logic.
- Preserve keyboard shortcuts, drag/drop, backup/undo and Excel export.
- No new network dependency.
- Supported minimum window size remains usable without clipping.
- Windows packaging remains through GitHub Actions.
