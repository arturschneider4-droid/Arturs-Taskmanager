# V6.4 Premium Enterprise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the existing PySide6 task manager into a polished, modern enterprise desktop application while preserving its existing task-management behavior and offline SQLite architecture.

**Architecture:** Keep the existing data model and MainWindow behavior, but replace the presentation layer with a focused V6.4 design system. Prefer reusable Qt widgets/style helpers over scattered one-off styles; keep data access in `db.py` and interaction logic in `ui.py` unless a small presentation component deserves its own module. Build on a feature branch, validate with static/unit tests, then use GitHub Actions for the Windows build because PySide6 is not available in the local runtime.

**Tech Stack:** Python, PySide6/Qt, SQLite, openpyxl, pytest, PyInstaller, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-04-v64-premium-enterprise-design.md`

## Global Constraints

- Preserve offline/local SQLite operation and existing task data.
- Preserve task, subtask, priority, status, due-date, Kanban, Eisenhower, Planning, theme, export, backup and undo functionality.
- Do not introduce a network service or cloud dependency.
- Use the existing TÜV-inspired blue/white identity, with blue reserved primarily for navigation, actions and meaningful state.
- Eliminate clipped/overlapping controls at the supported minimum window size.
- Keep Windows EXE/ZIP packaging through the existing GitHub Actions workflow.

---

### Task 1: Establish V6.4 design-system layer

**Files:**
- Create: `taskmanager/style_v64.py`
- Modify: `taskmanager/app.py`
- Test: `tests/test_v64_style.py`

**Interfaces:**
- Produces `V64_STYLE` and `apply_v64_visuals(window)` for `app.py`.
- Consumes existing Qt object names/classes from `ui.py`; no database dependency.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_v64_style_defines_design_tokens_and_entrypoint():
    p = Path("taskmanager/style_v64.py")
    text = p.read_text(encoding="utf-8")
    assert "V64_STYLE" in text
    assert "apply_v64_visuals" in text
    assert "#0B5A7A" in text or "#0050A4" in text
    assert "QTableWidget" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_v64_style.py -v`
Expected: FAIL because the V6.4 style module does not yet exist.

- [ ] **Step 3: Implement the design system**

Create a presentation-only stylesheet with explicit tokens for background, surface, text, muted text, borders, primary blue, hover blue, selected blue, success, warning and critical states. Define consistent 6/8/10/12/16px spacing and 8/10/12px corner radii. Style the top bar, sidebar, navigation, overview, tabs, inputs, buttons, table, badges, cards, scrollbars, menus and focus states. Add helper adjustments for minimum heights and margins so the existing controls do not clip.

- [ ] **Step 4: Wire the style into the application**

Update `app.py` to import `V64_STYLE, apply_v64_visuals`, append `V64_STYLE` after the existing style, set `VERSION = "6.4"`, apply the visuals after constructing `MainWindow`, and set the title to `Arturs Taskmanager V6.4`.

- [ ] **Step 5: Run the test**

Run: `pytest tests/test_v64_style.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add taskmanager/style_v64.py taskmanager/app.py tests/test_v64_style.py
git commit -m "feat: add V6.4 premium design system"
```

---

### Task 2: Redesign the main shell and navigation

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/style_v64.py`
- Test: `tests/test_v64_shell.py`

**Interfaces:**
- Keeps `MainWindow.set_view`, `set_scope`, `set_project`, `refresh_all` signatures unchanged.
- Keeps existing sidebar navigation keys and behavior.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path


def test_v64_shell_has_clean_navigation_labels():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert '"☷   Aufgaben"' in text
    assert '"▱   Themengebiete"' in text
    assert 'Arturs Taskmanager' in text


def test_theme_navigation_is_real_navigation_not_focus_only():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert 'self.set_view("themes")' in text
```

- [ ] **Step 2: Run tests and verify the navigation test fails**

Run: `pytest tests/test_v64_shell.py -v`
Expected: the themes navigation assertion fails against the current `setFocus()` implementation.

- [ ] **Step 3: Implement shell changes**

Add a proper themes page to the stacked main content and map `themes` in `set_view`. Replace the current focus-only Themes button callback with `self.set_view("themes")`. Preserve the left-side theme list as a quick filter. Keep the sidebar readable at the minimum window size and make the active state visually distinct without large saturated blocks.

- [ ] **Step 4: Implement visual shell details**

Use a restrained dark-blue sidebar, quiet surface background, compact navigation groups, a clear page title area, and consistent active/hover states. Ensure overview rows are readable and clickable. Keep the global search and primary action visually dominant in the top bar.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_v64_shell.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add taskmanager/ui.py taskmanager/style_v64.py tests/test_v64_shell.py
git commit -m "feat: redesign V6.4 application shell"
```

---

### Task 3: Redesign the task workspace and rows

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/style_v64.py`
- Test: `tests/test_v64_task_rows.py`

**Interfaces:**
- Keeps `refresh_tasks`, `table_selected`, `select_task`, `cycle_priority`, `toggle_task` behavior intact.
- Continues storing task IDs in `Qt.UserRole`.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path


def test_task_rows_use_non_clipping_height():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert "self.table.setRowHeight(i, 60)" in text


def test_task_workspace_keeps_task_metadata_columns():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert '"Themengebiet"' in text
    assert '"Priorität"' in text
    assert '"Fälligkeit"' in text
    assert '"Status"' in text
```

- [ ] **Step 2: Run tests to verify the row-height assertion fails**

Run: `pytest tests/test_v64_task_rows.py -v`
Expected: FAIL before the V6.4 row sizing change.

- [ ] **Step 3: Implement task-row presentation**

Increase row height to 60px, improve cell margins and alignment, keep the checkbox vertically centered, and make task titles visually dominant. Render theme, priority and status as compact badges/indicators with sufficient padding. Keep the three-dot actions control subtle. Remove visual dependence on dense gridlines.

- [ ] **Step 4: Add empty-state presentation without changing data logic**

When no tasks match the current filters, show a centered explanatory empty state in the task workspace while retaining the normal table for populated results. Do not change query semantics.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_v64_task_rows.py -v && pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add taskmanager/ui.py taskmanager/style_v64.py tests/test_v64_task_rows.py
git commit -m "feat: redesign V6.4 task workspace"
```

---

### Task 4: Redesign the task detail editor

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/style_v64.py`
- Test: `tests/test_v64_editor.py`

**Interfaces:**
- Keeps `populate_editor`, `save_editor`, `_editor_priority`, `add_editor_sub`, `edit_editor_sub`, `remove_editor_sub` signatures compatible with existing behavior.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path


def test_priority_cards_are_not_clipped():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert "self.setMinimumHeight(88)" in text


def test_editor_sections_have_explicit_spacing():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert "rl.setSpacing(10)" in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_v64_editor.py -v`
Expected: FAIL against the current 72px priority-card height and default editor spacing.

- [ ] **Step 3: Implement the editor visual hierarchy**

Use a compact section-label hierarchy: title, theme, priority, due date, status, description, subtasks, actions. Give priority cards at least 88px height, enough width for all labels, and explicit 8px grid spacing. Use a clear selected state and preserve the four priority meanings. Increase date-row spacing and keep the no-due checkbox fully visible.

- [ ] **Step 4: Improve subtasks and action footer**

Give the subtasks list a clean card-like surface with visible check states, consistent row height and clear add/edit/delete actions. Keep Save as the primary action and Cancel as secondary, with sufficient bottom margin so neither is clipped.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_v64_editor.py -v && pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add taskmanager/ui.py taskmanager/style_v64.py tests/test_v64_editor.py
git commit -m "feat: redesign V6.4 task editor"
```

---

### Task 5: Apply the visual system consistently to Kanban, Eisenhower, Planning and Themes

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/style_v64.py`
- Test: `tests/test_v64_views.py`

**Interfaces:**
- Keeps `kanban_page`, `eisen_page`, `plan_page`, `make_list`, `drop_moved`, `refresh_kanban`, `refresh_eisen`, `refresh_plan` behavior intact.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path


def test_all_primary_views_have_v64_card_structure():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    for name in ("kanban_page", "eisen_page", "plan_page"):
        assert f"def {name}" in text
        assert 'setObjectName("card")' in text


def test_theme_view_exists():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    assert "themes_page" in text
```

- [ ] **Step 2: Run tests and verify the themes assertion fails**

Run: `pytest tests/test_v64_views.py -v`
Expected: FAIL until the dedicated themes page is added.

- [ ] **Step 3: Implement polished view cards**

Give Kanban columns strong headers and calm card surfaces; make draggable task cards readable and compact. Give Eisenhower quadrants distinct but restrained semantic accents. Give Planning columns clear date-group headers and consistent cards. Keep drag/drop behavior unchanged.

- [ ] **Step 4: Implement the Themes page**

Add a dedicated main-page list/grid of themes with theme name, task count, and direct actions for new/edit/delete. Clicking a theme applies the existing project filter and returns to the task view. Keep the left sidebar list synchronized.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_v64_views.py -v && pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add taskmanager/ui.py taskmanager/style_v64.py tests/test_v64_views.py
git commit -m "feat: polish V6.4 secondary views"
```

---

### Task 6: Final visual regression and packaging verification

**Files:**
- Modify: `.github/workflows/build-windows.yml` only if required by the V6.4 version/build output.
- Test: existing `tests/` plus `tests/test_v64_style.py`, `tests/test_v64_shell.py`, `tests/test_v64_task_rows.py`, `tests/test_v64_editor.py`, `tests/test_v64_views.py`.

**Interfaces:**
- Produces the V6.4 Windows EXE/ZIP through the existing CI workflow.

- [ ] **Step 1: Run the full local test suite**

Run: `pytest -q`
Expected: all tests pass. Do not claim GUI runtime success locally because PySide6 is unavailable in the current runtime.

- [ ] **Step 2: Run static compilation**

Run: `python -m compileall taskmanager main.py`
Expected: no syntax errors.

- [ ] **Step 3: Push the completed feature branch and start the Windows build**

Use the repository's existing GitHub Actions workflow for the feature branch. Verify that dependency installation, tests, PyInstaller and ZIP creation all complete successfully.

- [ ] **Step 4: Inspect workflow job and artifact status**

Verify the build job concludes `success` and both the Windows ZIP and EXE-folder artifacts are present before reporting completion.

- [ ] **Step 5: Commit any packaging-only fix if needed**

```bash
git add .github/workflows/build-windows.yml
git commit -m "build: package V6.4 Windows release"
```

- [ ] **Step 6: Create the final release candidate artifact**

Download the successful Windows ZIP artifact and provide it to the user. State clearly which checks were executed and distinguish CI GUI/build verification from local GUI verification.
