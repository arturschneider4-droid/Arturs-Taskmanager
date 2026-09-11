# Arturs Taskmanager V8 – Premium Enterprise UI Design Specification

**Date:** 2026-09-11  
**Status:** Design approved in conversation; implementation not yet approved  
**Base:** V7.1 / `feature/v7-professional-desktop-ui`

## 1. Goal

V8 is a major visual redesign of Arturs Taskmanager into a compact, information-dense, premium enterprise desktop application inspired by the TÜV Rheinland visual language. Existing functionality and data behavior must remain available; the visible UI may be substantially rebuilt.

The result should feel like a professional work application rather than a conventional to-do table or dashboard.

## 2. Non-Negotiable Constraints

- Native Windows desktop application remains Python + PySide6 + SQLite.
- Offline/local data behavior remains unchanged.
- No migration to web, Base44, browser UI, or another application stack.
- No existing functional capability may be removed.
- Existing task data, themes/topics, priorities, due dates, statuses, subtasks, recurrence, export, backup and undo behavior remain supported.
- V8 must not introduce horizontal clipping of task information at supported window sizes.
- The initial V8 theme is light only. Dark mode is explicitly out of scope for V8.
- Visual redesign must not silently alter business semantics.

## 3. Overall Visual Language

### 3.1 Character

The UI should be:

- compact and information-dense;
- calm and professional;
- clearly structured without heavy boxes;
- predominantly white/off-white;
- typography-led rather than decoration-led;
- restrained in its use of color;
- suitable for sustained desktop work.

Avoid dashboard/KPI-card aesthetics, excessive rounded cards, excessive shadows, emoji-based semantics, and oversized whitespace.

### 3.2 Color

- Base/background: very light off-white.
- Work surfaces: white.
- Primary text: dark anthracite.
- TÜV-inspired blue: reserved for primary actions, active navigation, focus and important interaction states.
- Priority/status colors: semantic and subdued; used only where they communicate meaning.
- No large saturated color blocks merely for decoration.

### 3.3 Typography and density

Use a clean Windows-native sans-serif appearance, preferably Segoe UI through Qt styling. Maintain clear heading/body/meta hierarchy while favoring compact row heights and efficient use of vertical space.

## 4. Application Shell

V8 uses a four-part adaptive shell:

1. slim top bar;
2. collapsible left navigation;
3. central workspace;
4. optional right detail panel.

The shell must support the following wide-window state:

`Navigation | Central workspace | Detail panel`

When no task is selected, the central workspace may expand into the available right-side space. When a task is selected, the detail panel opens or remains visible.

At narrow widths, the detail panel automatically hides first, preserving a fully usable central workspace. The navigation may also collapse automatically.

## 5. Proposed UI Components

The visible V8 shell should be organized around focused responsibilities. Names are design-level component names and may map to Python classes/modules during implementation:

- `V8Shell`
- `V8Navigation`
- `V8Toolbar`
- `V8FilterBar`
- `V8TaskList`
- `V8TaskRow`
- `V8DetailPanel`
- `V8ThemeNavigation`
- view-specific workspaces for Kanban, Eisenhower and Planning

Existing functional widgets may be reused internally where this reduces risk, but the visible presentation should follow the V8 design.

## 6. Top Bar

The top bar is slim and unobtrusive.

It should contain:

- application identity: `Arturs Taskmanager`;
- version/offline information where useful;
- global search if retained from the existing implementation;
- no large decorative logo area.

The previously used top-right logo treatment is not part of V8.

## 7. Left Navigation

### 7.1 Normal state

Approximate width: 220–240 px.

Navigation groups:

**ARBEITSBEREICH**
- Aufgaben
- Heute
- Diese Woche
- Später
- Erledigt

**ANSICHTEN**
- Kanban
- Eisenhower
- Planung

**THEMENGEBIETE**
- live list of existing themes/topics;
- `+ Neues Themengebiet`.

Utility functions such as export, settings and help remain reachable, but should not visually dominate the work navigation.

### 7.2 Collapsed state

Approximate width: 56–64 px.

- Icons remain visible.
- Text labels are hidden.
- Tooltips provide labels.
- Active state remains unmistakable.
- The collapsed state is remembered while the application is running and preferably persisted if the implementation already has an appropriate settings mechanism.

At sufficiently narrow window sizes the navigation may collapse automatically.

## 8. Task Workspace

The task list is the primary work surface and must not visually resemble a traditional spreadsheet-heavy `QTableWidget`.

### 8.1 Header

The workspace header contains:

- title: `Aufgaben`;
- current task count;
- scope tabs:
  - `Alle Aufgaben`
  - `Heute`
  - `Diese Woche`
  - `Später`
  - `Erledigt`
- compact actions:
  - `Filter`
  - `Sortieren`
  - `Gruppieren`
  - view switcher such as `Liste / Kompakt`.

The primary action is a clearly visible blue button at the upper right:

`+ Aufgabe`

This is the strongest visual call-to-action in the workspace.

### 8.2 Task rows

A task row should show, where applicable:

- completion checkbox;
- task title;
- optional description preview on a secondary line;
- theme/topic label;
- subtask progress;
- priority;
- due date;
- status.

Rows use subtle separators and compact vertical spacing. Hover can expose secondary actions. Selected rows receive a clear but restrained active treatment and open the right detail panel.

Priority is represented through a subtle traffic-light visual signal rather than emoji.

Due dates are semantic where useful:

- Heute
- Morgen
- Überfällig
- future date
- keine Fälligkeit

### 8.3 Responsive rule

The task list must never depend on clipping or hidden overflow to fit the desktop layout. The central task content receives available width dynamically. The right detail panel collapses before task information becomes unusable.

## 9. Filtering, Sorting and Grouping

### 9.1 Filters

`Filter` opens a compact popover rather than a permanent form.

Filter dimensions include:

- status;
- priority;
- due date;
- theme/topic.

Active filters are displayed as removable chips, e.g. `Priorität: Wichtig` or `Thema: Batterie`.

### 9.2 Sorting

`Sortieren` opens a compact popover. Existing supported sorting behavior must remain available; V8 changes presentation, not semantics.

### 9.3 Grouping

`Gruppieren` opens a compact popover. Existing grouping capabilities remain supported where present.

## 10. Right Detail Panel / Task Inspector

The detail panel is a reusable inspector used by all primary task views.

### 10.1 Behavior

- Opens when a task is selected.
- Remains associated with the current selection while navigating within the workspace.
- Can be closed/collapsed.
- Can be reopened without losing the selected task.
- At narrow widths it hides automatically.
- Reopening restores the current selected task and current editable state.
- Changes continue to use the existing save/data mechanisms.

### 10.2 Size

- Initial target width: approximately 380 px.
- User can resize it wider or narrower by dragging a divider/handle on its left edge.
- Enforce a practical minimum width.
- Preserve the user's chosen width when the panel is reopened.
- Resizing must not cause central task content to clip.

### 10.3 Content

The inspector should prioritize the information needed to work on a task:

1. task title;
2. status;
3. description;
4. theme/topic;
5. priority;
6. due date;
7. subtasks;
8. recurrence and other secondary details.

Fields should appear as clean, compact editable controls rather than a dense grid of framed form fields.

### 10.4 Subtasks

The subtask section must retain full existing functionality:

- add;
- edit;
- delete;
- check/uncheck;
- persistence;
- progress display.

Suggested presentation: `Unteraufgaben · 3/5`, compact rows with checkbox and text, hover actions, and a subtle progress indicator.

## 11. Other Task Views

Kanban, Eisenhower and Planning are distinct workspaces rather than forced variants of the task list.

### 11.1 Kanban

- task cards in status columns;
- existing drag/drop semantics retained;
- compact card design;
- selecting a card opens the common right detail panel.

### 11.2 Eisenhower

- four visually distinct quadrants;
- restrained semantic priority cues;
- task selection opens the common right detail panel;
- existing priority behavior remains authoritative.

### 11.3 Planning

- planning-oriented layout for Heute / Diese Woche / Später and due-date placement;
- existing planning drag/drop behavior retained;
- selecting a task opens the common right detail panel.

## 12. Themes / Themengebiete

`Projekte` remains presented as **`Themengebiete`** in the V8 UI.

The navigation list must be live and immediately reflect:

- creation;
- editing;
- deletion;
- task assignment.

Existing project/topic database semantics remain unchanged unless an implementation task explicitly proves a required compatibility change.

## 13. Micro-interactions

- Hovering a task reveals secondary actions.
- Checkbox completion is immediate without an unnecessary confirmation dialog.
- Drag/drop provides a clear drop target indicator.
- Popovers are used for filters/sort/group instead of modal dialogs where practical.
- Detail panel transitions are short and restrained.
- New task creation focuses the relevant editor control.
- Deletion continues to support the existing undo behavior rather than adding intrusive confirmation dialogs.
- Important controls are keyboard accessible.
- Icon-only controls have tooltips.

Animations must remain subtle and must not interfere with desktop productivity.

## 14. Functional Compatibility Requirements

The redesign must preserve the current application's functional contract, including as applicable:

- task creation/editing/deletion;
- task completion;
- priorities and immediate priority synchronization;
- due dates including `Später` and `Keine Fälligkeit` semantics;
- statuses;
- themes/topic management;
- subtasks and progress;
- recurrence;
- overview counts/navigation;
- Kanban;
- Eisenhower;
- Planning and named-period drop behavior;
- Excel export;
- automatic local backups;
- undo;
- GitHub Actions Windows EXE/ZIP packaging.

The V8 implementation must add regression tests for new UI-state behavior where it can be tested without requiring a full interactive Windows desktop session.

## 15. Responsive Behavior Matrix

| Window condition | Navigation | Task workspace | Detail panel |
|---|---|---|---|
| Wide | expanded | normal | visible when selected |
| Medium | expanded or collapsed by user | full remaining width | visible/resizable |
| Narrow | auto-collapsed | full usable width | automatically hidden |
| Reopen panel | unchanged | selection retained | selected task restored |

No state should result in clipped task columns or overlapping controls.

## 16. Accessibility / Usability

- Minimum click targets must remain practical despite compact density.
- Keyboard focus must remain visible.
- Text must retain sufficient contrast against its background.
- Tooltips are required for icon-only actions.
- Semantic color must not be the sole representation of priority/status where a text label is already available.
- Dense layout must not become visually ambiguous.

## 17. Out of Scope for V8

- Dark mode.
- Replacing the native desktop technology stack.
- Cloud synchronization.
- Major database/schema redesign without a demonstrated compatibility requirement.
- New unrelated productivity features merely for visual completeness.

## 18. Acceptance Criteria

V8 design is considered successfully implemented only when:

1. The application presents the new light enterprise shell rather than the V7 visual shell.
2. Navigation can collapse to an icon rail.
3. The right task inspector can open, close and resize.
4. The inspector automatically hides at narrow widths without making the task workspace unusable.
5. The inspector can be reopened with the selected task intact.
6. Task rows expose the agreed information hierarchy without horizontal clipping.
7. `+ Aufgabe` is clearly the primary blue action.
8. Filters, sorting and grouping use compact popovers/chips.
9. Kanban, Eisenhower and Planning have dedicated V8 layouts and use the common inspector.
10. Themengebiete remain live and editable.
11. Existing functional regression tests continue to pass.
12. New responsive/detail-panel interaction behavior is covered by tests where practical.
13. Windows EXE/ZIP packaging remains successful through GitHub Actions.
14. No existing functionality is intentionally removed as part of the visual redesign.

## 19. Implementation Boundary

This document is the design specification only. No production code should be changed solely because this specification exists. The next step is a separate implementation plan that maps these requirements onto the current V7.1 codebase, defines incremental testable tasks, and identifies which existing V7 shell modules should be replaced, retained, or adapted.
