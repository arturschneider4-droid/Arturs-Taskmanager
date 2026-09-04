# V7 Professional Desktop UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the V6.5 dashboard-like shell with a restrained, professional Windows productivity UI while preserving all existing task-management behavior.

**Architecture:** Keep the existing PySide6 widgets, SQLite data layer, signal wiring, and secondary workspaces. Replace the visual shell and layout with a compact navigation rail, central task workspace, and persistent right-side editor/detail area; use QSS only for visual language and small shell helpers for layout.

**Tech Stack:** Python, PySide6, SQLite, existing test suite, GitHub Actions Windows build.

**Spec:** Approved V7 Professional Desktop / Linear × Microsoft Planner design discussed in chat on 2026-09-04.

## Global Constraints

- Preserve all existing task, subtask, priority, status, due-date, theme, Kanban, Eisenhower, Planning, export, backup, undo, and offline behavior.
- Do not migrate from Python/PySide6 + SQLite + Windows EXE.
- Use a restrained TÜV-inspired blue/white palette; avoid dashboard-heavy KPI cards and oversized header/sidebar elements.
- Keep the application usable at normal Windows desktop sizes with no clipping.
- Use TDD for behavior changes and run the full test suite before claiming completion.

---

### Task 1: Establish V7 shell contract with tests

**Files:**
- Test: `tests/test_v7_shell.py`

- [ ] Write failing tests asserting compact top toolbar, navigation entries, central workspace, right detail region, and removal of V6.5 KPI-heavy shell identifiers.
- [ ] Run targeted tests and confirm they fail against V6.5.
- [ ] Commit the failing tests.

### Task 2: Implement the new professional shell

**Files:**
- Create: `taskmanager/style_v7.py`
- Modify: `taskmanager/app.py`

- [ ] Implement a compact Windows-style shell with narrow navigation, clean task workspace, and right-side detail panel using existing functional widgets.
- [ ] Keep existing signal connections intact; do not duplicate task-management logic.
- [ ] Add restrained QSS: white workspace, neutral separators, blue active states, compact controls, subtle selection/hover states.
- [ ] Wire existing navigation and scope controls into the new shell.
- [ ] Update application version to 7.0 and apply V7 style after legacy styles without changing database behavior.
- [ ] Run targeted shell tests and fix failures.
- [ ] Commit the implementation.

### Task 3: Refine task/detail presentation

**Files:**
- Modify: `taskmanager/style_v7.py`
- Modify: `taskmanager/ui.py` only if a layout hook is required
- Test: `tests/test_v7_shell.py`

- [ ] Ensure selected task remains visible while editing and the detail area is visually subordinate but persistent.
- [ ] Make priority/status/due-date controls compact and readable.
- [ ] Ensure filters and search do not consume disproportionate vertical space.
- [ ] Add regression tests for key existing controls remaining present.
- [ ] Run targeted tests and then the complete pytest suite.
- [ ] Commit the refinement.

### Task 4: Windows verification

**Files:**
- Modify: `.github/workflows/build-windows.yml` only if required by V7 version/build discovery.

- [ ] Push the V7 branch and let GitHub Actions run tests and Windows EXE packaging.
- [ ] Verify workflow conclusion is successful and artifacts are produced.
- [ ] Verify no clipping/layout regressions can be inferred from build/test output.
- [ ] Report the exact commit, workflow run, and artifact status.
