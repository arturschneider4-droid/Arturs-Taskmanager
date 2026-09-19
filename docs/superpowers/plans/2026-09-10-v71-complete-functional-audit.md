# V7.1 Complete Functional Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Systematically verify and harden every important V7.1 user workflow without changing the approved professional desktop design or replacing the Python/PySide6 + SQLite stack.

**Architecture:** Keep the existing UI and database architecture. Add focused behavioral tests around task editing, subtasks, filters, navigation, themes, drag/drop, undo/backup and export; fix only proven defects, preferably in small focused modules. Preserve the V7 shell's existing legacy-widget lifetime guard and responsive table behavior.

**Tech Stack:** Python, PySide6, SQLite, pytest, GitHub Actions, PyInstaller.

**Spec:** Existing V7 professional desktop design and the previously approved complete functional audit scope in the project conversation.

## Global Constraints

- Keep Python/PySide6 + SQLite and offline/local operation.
- Do not replace the application with Base44 or a web stack.
- Preserve the V7 professional desktop UI direction and TÜV-inspired restrained blue/white styling.
- Do not remove existing task-management capabilities while fixing the audit findings.
- Every behavioral fix gets a regression test before implementation where practical.
- Do not claim completion until pytest and the Windows build both succeed.

---

### Task 1: Establish audit baseline

**Files:**
- Inspect: `taskmanager/ui.py`
- Inspect: `taskmanager/dialogs.py`
- Inspect: `taskmanager/db.py`
- Inspect: `taskmanager/overview.py`
- Inspect: `taskmanager/responsive_table_v7.py`
- Inspect: `taskmanager/style_v7.py`
- Inspect: `tests/`

**Interfaces:**
- Produces a written list of verified workflows, known gaps and candidate defects for the following tasks.

- [ ] Step 1: Review current tests and production wiring.
- [ ] Step 2: Map every user-facing control to its handler and persistence path.
- [ ] Step 3: Identify uncovered workflows; do not modify production code in this task.
- [ ] Step 4: Record findings in a compact audit note or issue-oriented commits as appropriate.

---

### Task 2: Harden task editor and subtasks

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/dialogs.py` only if dialog behavior is implicated
- Test: `tests/test_task_editor_behavior_v7.py`

**Interfaces:**
- `MainWindow.add_editor_sub`, `edit_editor_sub`, `remove_editor_sub`, `save_editor`.
- `TaskDialog.add_sub`, `edit_subtask`, `remove_sub`.

- [ ] Step 1: Add failing tests for selecting a subtask, editing it via the visible Bearbeiten button, deleting it, checking it and preserving it after save/reload.
- [ ] Step 2: Run the focused tests and confirm failures where the current implementation is incomplete.
- [ ] Step 3: Implement the smallest functional fix, including explicit button enable/disable state where needed.
- [ ] Step 4: Run focused tests again.
- [ ] Step 5: Commit the fix and regression tests.

---

### Task 3: Verify due dates, status and priority end-to-end

**Files:**
- Modify: `taskmanager/ui.py` if required
- Modify: `taskmanager/priority_sync.py` if required
- Modify: `taskmanager/db.py` if required
- Test: `tests/test_task_editor_behavior_v7.py`
- Test: `tests/test_db_behavior.py` or a focused new regression test

**Interfaces:**
- Task save/edit path, `update_status`, `update_priority`, `update_due`, task filtering and visual refresh.

- [ ] Step 1: Add behavior tests for future/today/overdue/no-due semantics.
- [ ] Step 2: Add behavior tests for status and priority changes persisting and appearing in the task table.
- [ ] Step 3: Run focused tests to expose defects.
- [ ] Step 4: Fix only the failing behavior.
- [ ] Step 5: Run focused tests and the existing priority/due tests.
- [ ] Step 6: Commit.

---

### Task 4: Verify all task filters and search combinations

**Files:**
- Inspect/modify: `taskmanager/db.py`
- Inspect/modify: `taskmanager/ui.py`
- Test: `tests/test_filters_v7.py`

**Interfaces:**
- `tasks(...)`, search field, theme/status/priority/due filters and sort state.

- [ ] Step 1: Create fixture tasks covering every status, priority, due-date class, theme and text-search case.
- [ ] Step 2: Add failing tests for each filter individually and important combinations.
- [ ] Step 3: Run focused tests.
- [ ] Step 4: Correct SQL/UI refresh behavior where required.
- [ ] Step 5: Run the full filter suite.
- [ ] Step 6: Commit.

---

### Task 5: Verify navigation, themes and overview behavior

**Files:**
- Modify: `taskmanager/style_v7.py` only if proven necessary
- Modify: `taskmanager/app.py` only if lifetime/navigation issues remain
- Inspect: `taskmanager/overview.py`
- Test: `tests/test_navigation_themes_v7.py`

**Interfaces:**
- `set_view`, theme list selection, create/edit/delete theme, overview navigation, shared stack and refresh behavior.

- [ ] Step 1: Add behavioral tests for every V7 navigation target.
- [ ] Step 2: Add tests that new/edit/delete theme operations update the visible theme list and filters.
- [ ] Step 3: Add tests for overview scopes and count consistency.
- [ ] Step 4: Run focused tests and reproduce any lifetime/runtime errors.
- [ ] Step 5: Fix only verified defects.
- [ ] Step 6: Commit.

---

### Task 6: Verify Kanban, Eisenhower and Planning drag/drop

**Files:**
- Modify: `taskmanager/ui.py`
- Test: `tests/test_workspace_dragdrop_v7.py`

**Interfaces:**
- `DropList.dropEvent`, `refresh_kanban`, `refresh_eisen`, `refresh_plan`, drag/drop signals and status/priority/due updates.

- [ ] Step 1: Add tests for valid drag/drop state changes in each workspace.
- [ ] Step 2: Add a regression test for invalid/non-accepted drops not emitting a false move.
- [ ] Step 3: Add planning-date tests for the intended "Diese Woche" and "Später" semantics.
- [ ] Step 4: Run focused tests.
- [ ] Step 5: Fix defects and rerun.
- [ ] Step 6: Commit.

---

### Task 7: Verify undo, backup and destructive operations

**Files:**
- Modify: `taskmanager/db.py`
- Modify: `taskmanager/ui.py`
- Test: `tests/test_undo_backup_v7.py`

**Interfaces:**
- `backup_db`, `latest_backup`, `restore_backup`, `undo_last`, task/project mutations and undo-button state.

- [ ] Step 1: Add tests for create/edit/delete/status/priority changes producing recoverable state.
- [ ] Step 2: Verify undo restores the expected previous database state.
- [ ] Step 3: Verify startup does not create a misleading user-visible undo state unless intended.
- [ ] Step 4: Fix redundant or incorrect backup/undo behavior only where tests demonstrate it.
- [ ] Step 5: Run focused tests.
- [ ] Step 6: Commit.

---

### Task 8: Verify Excel export and remaining secondary actions

**Files:**
- Inspect/modify: `taskmanager/ui.py`
- Test: `tests/test_export_and_actions_v7.py`

**Interfaces:**
- `export_excel`, reports/settings/help actions, window controls and keyboard shortcuts.

- [ ] Step 1: Add tests that export is callable and produces the expected workbook structure in a temporary directory or mocked file dialog.
- [ ] Step 2: Verify settings/help actions are functional and do not crash.
- [ ] Step 3: Verify keyboard shortcuts for search/new task where testable.
- [ ] Step 4: Fix verified defects.
- [ ] Step 5: Commit.

---

### Task 9: Responsive UI regression audit

**Files:**
- Modify: `taskmanager/responsive_table_v7.py` if required
- Modify: `taskmanager/style_v7.py` if required
- Test: `tests/test_responsive_table_v7.py`

**Interfaces:**
- Task table column widths, splitter sizing, horizontal scrolling policy and editor minimum/maximum widths.

- [ ] Step 1: Add tests for representative window widths around the supported minimum and normal desktop size.
- [ ] Step 2: Verify task, priority and due-date columns remain accessible without accidental horizontal clipping.
- [ ] Step 3: Fix any remaining geometry defect.
- [ ] Step 4: Run responsive tests.
- [ ] Step 5: Commit.

---

### Task 10: Full regression and Windows release verification

**Files:**
- Modify: only if verification reveals a final defect
- Test: complete `tests/` suite

- [ ] Step 1: Run the complete pytest suite in GitHub Actions.
- [ ] Step 2: Confirm the test job succeeds before accepting the build.
- [ ] Step 3: Build the Windows EXE with the existing workflow.
- [ ] Step 4: Confirm ZIP and EXE artifacts are produced successfully.
- [ ] Step 5: Record the final commit SHA, workflow run and artifact identifiers.
- [ ] Step 6: Report remaining limitations honestly; do not label untested behavior as verified.
