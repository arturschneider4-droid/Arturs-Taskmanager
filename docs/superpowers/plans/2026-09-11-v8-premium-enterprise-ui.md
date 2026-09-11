# Arturs Taskmanager V8 – Premium Enterprise UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the V7 presentation with the approved compact, information-dense V8 enterprise shell while preserving all existing task-management behavior and producing a verified Windows EXE/ZIP.

**Architecture:** Keep `ui.py` and `db.py` as the business-function source of truth. Add a focused `style_v8.py` presentation layer and small V8 interaction/state helpers so the visible shell can be rebuilt without a risky database rewrite. The V8 shell will reuse existing functional controls where safe, while task-view presentation, navigation, detail-panel state, responsive behavior and popovers are owned by V8.

**Tech Stack:** Python 3.12, PySide6 6.8+, SQLite, pytest, PyInstaller, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-11-v8-premium-enterprise-ui-design.md`

## Global Constraints

- Native Windows desktop application remains Python + PySide6 + SQLite.
- Offline/local data behavior remains unchanged.
- No existing functional capability may be removed.
- V8 is light-only; dark mode is out of scope.
- No horizontal clipping of usable task information at supported widths.
- Existing backup, undo, export, task, theme, priority, due-date, status, recurrence and subtask semantics remain authoritative.
- Every behavior change is developed test-first.
- Windows packaging must continue through `.github/workflows/build-windows.yml`.

## File Map

- Create: `taskmanager/style_v8.py` — V8 shell, navigation, task workspace, inspector, view layouts and visual styling.
- Create: `taskmanager/v8_interactions.py` — reusable state/formatting/responsive helpers with no database schema changes.
- Modify: `taskmanager/app.py` — install V8 after legacy functional construction and expose V8 version.
- Modify: `.github/workflows/build-windows.yml` — build the V8 branch automatically.
- Create/modify: `tests/test_v8_shell.py` — shell structure and version contracts.
- Create: `tests/test_v8_interactions.py` — pure state/formatting/responsive tests.
- Create: `tests/test_v8_detail_panel.py` — Qt offscreen inspector state tests.
- Extend: existing V7 regression tests only when required to prove compatibility.

### Task 1: V8 pure interaction contracts

**Files:**
- Create: `taskmanager/v8_interactions.py`
- Create: `tests/test_v8_interactions.py`

**Interfaces:**
- `format_due_date(value, today=None) -> str`
- `priority_label(priority) -> str`
- `scope_for_view(view_key) -> tuple[str, str]`
- `responsive_layout(width, detail_open, nav_collapsed) -> dict`
- `next_planning_due(target, today=None) -> str`

- [ ] Write failing tests for semantic due labels, all priority labels, supported scope/view keys, wide/medium/narrow layout decisions, and Planning target dates.
- [ ] Run `pytest tests/test_v8_interactions.py -q` and verify the new tests fail because the module/functions do not yet exist.
- [ ] Implement only the pure helpers required by those tests using the existing `date` semantics from `db.py` and `constants.py`.
- [ ] Run the focused test file and verify it passes.
- [ ] Commit `feat: add V8 interaction contracts`.

### Task 2: V8 shell skeleton and visual system

**Files:**
- Create: `taskmanager/style_v8.py`
- Create: `tests/test_v8_shell.py`

**Interfaces:**
- `V8_STYLE: str`
- `rebuild_v8_shell(window) -> QWidget`
- `install_v8_responsive_behavior(window) -> None`

- [ ] Write failing source-contract tests requiring V8 style, `V8Shell`, `V8Navigation`, `V8TaskList`, `V8DetailPanel`, the light palette, and the primary `+ Aufgabe` action.
- [ ] Run the focused tests and verify failure.
- [ ] Implement the V8 four-part shell: slim top bar, collapsible left navigation, central workspace and optional right inspector. Use compact Segoe UI styling, off-white/white surfaces, restrained TÜV blue and no emoji semantics.
- [ ] Keep the existing `MainWindow` functional object available behind the V8 presentation where existing refresh/edit/export/undo methods are still dependencies; do not delete functional widgets merely to simplify the shell.
- [ ] Run `pytest tests/test_v8_shell.py -q` and verify it passes.
- [ ] Commit `feat: add V8 enterprise shell`.

### Task 3: Task workspace and compact task rows

**Files:**
- Modify: `taskmanager/style_v8.py`
- Modify: `tests/test_v8_shell.py`

**Interfaces:**
- V8 task workspace must expose scope controls `Alle Aufgaben`, `Heute`, `Diese Woche`, `Später`, `Erledigt`.
- Task selection must publish the selected task id to the inspector.

- [ ] Add failing tests for the workspace header, count, scope tabs, `Filter`, `Sortieren`, `Gruppieren`, `Liste/Kompakt`, and `+ Aufgabe` controls.
- [ ] Run the focused tests and verify failure.
- [ ] Implement compact task rows with checkbox, title, optional description preview, theme, subtask progress, priority, due date and status; use subtle separators and semantic traffic-light priority indicators.
- [ ] Implement semantic due-date labels through `format_due_date` and ensure `Keine Fälligkeit` is distinct from `Später`.
- [ ] Implement the blue primary task button and route it to the existing `window.new_task` behavior.
- [ ] Verify the task list dynamically uses available width and never requires a horizontal scrollbar for its intended V8 columns.
- [ ] Run focused V8 tests and the existing responsive-table regression tests.
- [ ] Commit `feat: add V8 task workspace`.

### Task 4: Detail inspector with resize and persistence

**Files:**
- Modify: `taskmanager/style_v8.py`
- Create: `tests/test_v8_detail_panel.py`

**Interfaces:**
- Inspector methods/properties: `set_task_id(tid)`, `clear_task()`, `set_panel_open(open_)`, `set_panel_width(width)`, `task_id`, `panel_open`, `panel_width`.

- [ ] Write failing offscreen Qt tests for opening on selection, closing, reopening with the same task id, minimum/maximum width, resizing state retention, and automatic hiding at narrow width.
- [ ] Run the focused tests and verify failure.
- [ ] Implement `V8DetailPanel` as a reusable inspector using existing task/editor save and subtask functionality where possible; present title, status, description, theme, priority, due date, subtasks and secondary details in a compact vertical layout.
- [ ] Add a draggable splitter handle or `QSplitter` boundary with an initial width near 380 px and a practical minimum; preserve the chosen width while the window lives.
- [ ] Ensure closing the panel does not clear the selection; reopening restores the selected task.
- [ ] Add narrow-window behavior that hides the inspector before the task workspace becomes unusable.
- [ ] Run focused Qt tests and existing editor/subtask tests.
- [ ] Commit `feat: add V8 task inspector`.

### Task 5: Collapsible navigation and live Themengebiete

**Files:**
- Modify: `taskmanager/style_v8.py`
- Modify: `taskmanager/app.py`
- Modify: `tests/test_v8_shell.py`

- [ ] Write failing tests for expanded navigation width, collapsed icon-rail width, tooltips, active state and live Themengebiete creation/edit/delete visibility.
- [ ] Run focused tests and verify failure.
- [ ] Implement expanded 220–240 px navigation and collapsed 56–64 px icon rail; make collapse state reversible without losing the selected view/task.
- [ ] Replace visible `Projekte` wording with `Themengebiete` while continuing to use the existing project database/actions.
- [ ] Keep export, settings and help reachable but visually secondary.
- [ ] Wire `app.py` to install the V8 shell and update `VERSION` to `8.0` without removing the existing V7 helper imports until V8 proves their behavior is no longer needed.
- [ ] Run shell and existing theme/project regression tests.
- [ ] Commit `feat: add V8 adaptive navigation`.

### Task 6: Filters, sorting, grouping and view-specific workspaces

**Files:**
- Modify: `taskmanager/style_v8.py`
- Modify: `taskmanager/v8_interactions.py`
- Modify: `tests/test_v8_interactions.py`
- Modify: `tests/test_v8_shell.py`

- [ ] Write failing tests for filter state/chips, sort and group menu presence, and dedicated Kanban/Eisenhower/Planning workspace identifiers.
- [ ] Run focused tests and verify failure.
- [ ] Implement compact popovers for status, priority, due date and theme filters; active filters render as removable chips.
- [ ] Implement sort/group popovers while preserving existing supported ordering/grouping semantics.
- [ ] Implement dedicated compact Kanban columns/cards, four Eisenhower quadrants and Planning periods rather than forcing them into the task-list layout.
- [ ] Route selecting any card/task in these views to the same `V8DetailPanel`.
- [ ] Preserve existing Kanban and Planning drag/drop behavior, including named `Heute`, `Diese Woche` and `Später` semantics.
- [ ] Run V8 tests plus existing Kanban/Eisenhower/Planning/drag-drop regressions.
- [ ] Commit `feat: add V8 task views and controls`.

### Task 7: Responsive and keyboard/micro-interaction hardening

**Files:**
- Modify: `taskmanager/style_v8.py`
- Modify: `taskmanager/v8_interactions.py`
- Modify: `tests/test_v8_interactions.py`
- Modify: `tests/test_v8_detail_panel.py`

- [ ] Write failing tests for wide/medium/narrow state transitions, selection retention, icon tooltips, and primary keyboard shortcuts.
- [ ] Run focused tests and verify failure.
- [ ] Implement the responsive matrix: wide shows inspector when selected; medium permits user-controlled navigation and inspector widths; narrow auto-collapses inspector and, when necessary, navigation.
- [ ] Ensure task information remains readable without clipping or overlapping controls at the V8 supported minimum window.
- [ ] Add visible keyboard focus, icon-only tooltips and restrained hover actions; keep checkbox completion immediate and deletion compatible with existing undo.
- [ ] Run all tests.
- [ ] Commit `feat: harden V8 responsive interactions`.

### Task 8: V8 integration, CI and full verification

**Files:**
- Modify: `.github/workflows/build-windows.yml`
- Modify: `tests/test_v8_shell.py`

- [ ] Write failing integration assertions for V8 version wiring and CI branch coverage.
- [ ] Run the focused tests and verify failure.
- [ ] Add `feature/v8-premium-enterprise-ui` to the Windows workflow push branches while retaining the existing supported branches.
- [ ] Confirm `app.py` imports V8 and builds the V8 shell before `show()`.
- [ ] Run the complete `pytest -q` suite locally if the environment has PySide6; if not, use GitHub Actions as the authoritative Windows verification environment and report that limitation.
- [ ] Trigger GitHub Actions and verify every test/build/ZIP step succeeds.
- [ ] Download and inspect the generated Windows artifact; verify the ZIP contains the packaged application and EXE.
- [ ] Commit `build: enable V8 Windows packaging`.

### Final verification gate

- [ ] Run the complete test suite and record the exact result.
- [ ] Verify no intentional database/schema behavior change occurred.
- [ ] Verify task creation/edit/delete/completion, priority sync, due-date semantics, status, subtasks, recurrence, themes, overview, Kanban, Eisenhower, Planning, export, backup and undo remain represented by existing or new tests.
- [ ] Verify V8 visual acceptance criteria against the approved specification.
- [ ] Verify Windows EXE/ZIP packaging succeeds.
- [ ] Only after all checks are green, use `superpowers:finishing-a-development-branch` to present integration options.
