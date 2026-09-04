# V6.4 Premium Enterprise Visual Design

## Goal

Transform Arturs Taskmanager from a functional Qt application into a polished, coherent desktop product with a premium enterprise visual language while preserving all existing task-management functionality.

## Product direction

The visual target is a restrained combination of Linear-style clarity, Microsoft Planner-style task orientation, and Notion-style information hierarchy, adapted to a TÜV-Rheinland-inspired blue/white identity. The application should feel deliberate, calm, modern, and professional rather than like a default Qt desktop application.

## Visual principles

1. **Hierarchy over decoration** — typography, spacing, grouping, and restrained color carry meaning.
2. **Blue is identity, not wallpaper** — deep blue is primarily used for navigation/brand accents; the main workspace stays light and neutral.
3. **Information density without clutter** — task rows remain compact but have sufficient vertical room and never clip text or controls.
4. **Consistent geometry** — use a small spacing/radius system throughout the application.
5. **Meaningful color** — red/yellow/green indicate priority/status only; neutral UI remains neutral.
6. **No accidental Qt styling** — remove visual artifacts caused by default Fusion controls where practical.

## Main workspace

### Top bar

Keep the product name “Arturs Taskmanager” as the primary brand element. Use a quiet version badge and compact global actions. The top bar should be visually lighter and less button-heavy than the current version.

### Task list

Replace the visual feel of the current spreadsheet-like table with a modern task-list treatment while retaining the existing QTableWidget implementation where practical. Rows should have clear hierarchy, generous but efficient vertical spacing, subtle separators, strong title typography, readable metadata, and a restrained selected/hover state.

Columns remain functionally equivalent: completion control, task, topic, priority, due date, status, actions. The task title should be visually dominant; subtask progress should be secondary metadata.

### Detail editor

The right panel becomes a polished detail surface with clear section hierarchy: title, topic, priority, due date, status, description, subtasks, actions. Inputs and cards must never clip. Priority cards must have sufficient height for indicator dots and complete labels. The bottom actions must remain visually distinct.

### Topics

Topic badges should be compact, readable, and never clip. Topic selection and filtering should feel like a deliberate product feature rather than a database control.

## Sidebar

Use a deep enterprise blue with restrained contrast. Navigation is grouped into primary views and utility areas. Active navigation should be obvious but elegant. Topic list and overview should have clear headings and enough spacing. Avoid large blocks of competing blue controls.

The existing “Themengebiete” navigation item will later be made functional as its own view; this visual redesign must not regress that work.

## Typography

Use Segoe UI where available. Establish a consistent hierarchy approximately as follows:

- Page titles: 22–24 pt, bold.
- Task titles / primary content: 11–13 pt, medium/semi-bold.
- Metadata: 9–10 pt.
- Section labels: 8–9 pt, uppercase, tracked/semibold.

## Geometry

Adopt consistent values approximately in this range:

- Main card radius: 10–12 px.
- Control radius: 7–9 px.
- Standard spacing: 6, 8, 12, 16, 20, 24 px.
- Task row height: about 56–60 px.
- Priority selector height: about 84–90 px.

Exact values may be tuned during implementation to avoid clipping at the supported minimum window size.

## Interaction states

Every interactive surface should have explicit normal, hover, pressed, focused, selected, and disabled states where relevant. Focus states must remain accessible and visible. Hover effects should be subtle and must not cause layout movement.

## Functional constraints

Do not remove or redesign the underlying data model. Preserve tasks, subtasks, priorities, due dates, statuses, topic assignment, search, filters, Kanban, Eisenhower, planning, overview counts/navigation, Excel export, backup, and undo behavior.

## Versioning

This redesign is V6.4. The window title and visible version indicator must use V6.4 consistently.

## Testing and verification

Add or update static/regression tests for critical visual invariants such as version string, priority-card sizing, topic badge sizing, and task-row sizing. Run the repository test suite and the Windows GitHub Actions build. Because PySide6 is not available in the local Linux environment, GUI execution cannot be claimed locally; Windows CI is the authoritative build verification.
