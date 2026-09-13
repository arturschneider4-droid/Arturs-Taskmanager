# V8 Premium Enterprise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete V8 as a stable premium enterprise desktop UI while preserving the existing task-management contract and verifying the Windows release path.

**Architecture:** Keep Python + PySide6 + SQLite and layer the V8 shell around focused modules already introduced by the V8 branch. Reuse existing persistence and business logic; route selection through a shared detail panel and keep Kanban, Eisenhower and Planning as dedicated workspaces. Make responsive behavior explicit and regression-tested rather than relying on widget clipping.

**Tech Stack:** Python, PySide6, SQLite, pytest, GitHub Actions, Windows packaging.

**Spec:** `docs/superpowers/specs/2026-09-11-v8-premium-enterprise-ui-design.md`

## Global Constraints

- Native Windows desktop application remains Python + PySide6 + SQLite.
- Offline/local data behavior remains unchanged.
- No existing functional capability may be removed.
- Existing task data, themes/topics, priorities, due dates, statuses, subtasks, recurrence, export, backup and undo behavior remain supported.
- V8 must not introduce horizontal clipping of task information at supported window sizes.
- The initial V8 theme is light only; dark mode is out of scope.
- Visual redesign must not silently alter business semantics.
- Windows EXE/ZIP packaging must remain successful through GitHub Actions.

## File Map

- `taskmanager/app.py`: application startup and V8 shell integration.
- `taskmanager/ui.py`: main-window composition, navigation, task surface and selection wiring.
- `taskmanager/style_v8.py`: V8 visual language and reusable widget styling.
- `taskmanager/v8_detail_panel.py`: shared task inspector and responsive sizing.
- `taskmanager/v8_interactions.py`: cross-workspace selection and interaction helpers.
- `taskmanager/v8_kanban.py`: Kanban workspace.
- `taskmanager/v8_eisenhower.py`: Eisenhower workspace.
- `taskmanager/v8_planning.py`: Planning workspace.
- `taskmanager/responsive_table_v7.py`: retained responsive task-table primitives where still required.
- `taskmanager/db.py`, `dialogs.py`, `priority_sync.py`: existing persistence/editor contracts; change only where audit proves a defect.
- `tests/test_v8_*.py`: V8 shell, detail panel, workspace and release-contract coverage.
- `tests/test_*.py`: existing regression suite; no existing test should be weakened to make V8 pass.
- `.github/workflows/build-windows.yml`: release packaging verification.

### Task 1: Establish V8 Baseline and Release Guard

**Files:**
- Inspect: `taskmanager/*.py`, `tests/*.py`, `.github/workflows/build-windows.yml`
- Test: existing V8 tests and full suite

- [ ] Run the existing V8-focused tests and record failures without modifying production code.
- [ ] Run the complete pytest suite and classify failures into V8 regressions, pre-existing failures, and environment failures.
- [ ] Inspect the Windows workflow for Python/PySide6 packaging assumptions and confirm the V8 entry point is packaged.
- [ ] Commit only if baseline documentation or test-contract corrections are required.

### Task 2: Harden the V8 Shell and Navigation

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/app.py`
- Modify: `taskmanager/style_v8.py`
- Test: `tests/test_v8_shell.py`, `tests/test_v8_task_surface.py`, `tests/test_v8_ux_consistency.py`

- [ ] Add/extend failing tests for the four-part shell, active navigation, icon-rail collapse and light-only V8 styling.
- [ ] Run those tests and confirm the new assertions fail for missing behavior.
- [ ] Implement the smallest shell/navigation changes needed to satisfy the specification.
- [ ] Verify navigation remains connected to the existing view-selection handlers rather than duplicating business logic.
- [ ] Run the focused V8 shell tests and then the existing navigation/theme tests.
- [ ] Commit the shell increment with a focused message.

### Task 3: Complete the Task Surface and Responsive Rules

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/style_v8.py`
- Modify: `taskmanager/responsive_table_v7.py` only if required
- Test: `tests/test_v8_task_surface.py`, `tests/test_responsive_table_v7.py`, new focused responsive tests if needed

- [ ] Add failing tests for task information hierarchy, primary `+ Aufgabe` action, selection state and no horizontal clipping at representative widths.
- [ ] Implement compact task-row presentation while retaining checkbox, title, description preview, theme, subtasks, priority, due date and status semantics.
- [ ] Ensure the central workspace receives width before the detail panel and does not depend on hidden overflow.
- [ ] Verify focused task editing continues through the existing persistence path.
- [ ] Run focused task-surface and responsive tests, then relevant task interaction regressions.
- [ ] Commit the task-surface increment.

### Task 4: Finish the Shared Detail Panel

**Files:**
- Modify: `taskmanager/v8_detail_panel.py`
- Modify: `taskmanager/v8_interactions.py`
- Modify: `taskmanager/ui.py`
- Test: `tests/test_v8_detail_panel.py`, `tests/test_v8_interactions.py`

- [ ] Add failing tests for open/close, selected-task retention, minimum/maximum width, resize persistence during the session, and automatic hiding at narrow widths.
- [ ] Implement the inspector state model without introducing a second task persistence model.
- [ ] Route edits through the existing editor/save mechanisms.
- [ ] Preserve subtask add/edit/delete/check behavior and progress calculation.
- [ ] Verify reopening the panel restores the current selected task and does not discard unsaved UI state unless the existing save contract requires it.
- [ ] Run focused detail-panel tests and task-editor regressions.
- [ ] Commit the inspector increment.

### Task 5: Complete Filters, Sorting and Grouping

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: existing filter/query code only where necessary
- Test: existing filter tests plus `tests/test_v8_task_surface.py` or a new focused filter test module

- [ ] Add failing tests for status, priority, due-date and theme combinations and for clearing individual active filters.
- [ ] Implement compact popovers/chips over the existing query semantics.
- [ ] Preserve existing sort and group ordering semantics exactly.
- [ ] Run filter, database and task-surface regressions.
- [ ] Commit the filter/sort/group increment.

### Task 6: Integrate Kanban, Eisenhower and Planning

**Files:**
- Modify: `taskmanager/v8_kanban.py`
- Modify: `taskmanager/v8_eisenhower.py`
- Modify: `taskmanager/v8_planning.py`
- Modify: `taskmanager/v8_interactions.py`
- Test: `tests/test_v8_kanban.py`, `tests/test_v8_eisenhower.py`, `tests/test_v8_planning.py`, `tests/test_workspace_dragdrop_v7.py`

- [ ] Add failing tests for common task selection and inspector opening from each workspace.
- [ ] Verify Kanban drag/drop still updates status through the authoritative persistence path.
- [ ] Verify Eisenhower placement remains driven by priority rather than presentation-only state.
- [ ] Verify Planning drag/drop retains named-period and due-date semantics.
- [ ] Implement only missing V8 presentation/selection wiring; do not duplicate database mutation logic in the workspaces.
- [ ] Run all workspace and drag/drop tests.
- [ ] Commit the workspace integration increment.

### Task 7: Themes, Overview and Secondary Actions

**Files:**
- Modify: `taskmanager/ui.py`
- Modify: `taskmanager/app.py` only if startup wiring is affected
- Test: existing theme/overview tests plus V8 shell/task-surface coverage

- [ ] Add failing coverage for live Themengebiete refresh after create/edit/delete and task assignment.
- [ ] Verify overview navigation returns to the correct V8 workspace and refreshes visible counts.
- [ ] Verify export, settings and help remain reachable without dominating the primary navigation.
- [ ] Run theme, overview, export and control-wiring tests.
- [ ] Commit the secondary-action increment.

### Task 8: Undo, Backup, Editor and Functional Audit Closure

**Files:**
- Modify: `taskmanager/dialogs.py`, `taskmanager/db.py`, `taskmanager/priority_sync.py` only where tests prove a defect
- Test: existing editor/database tests plus new regression tests for any defect found

- [ ] Run the V7.1 functional audit areas for task editing, subtasks, due dates, status, priority, undo and backup.
- [ ] For each defect, write a failing regression test before changing production code.
- [ ] Preserve immediate priority synchronization, due-date semantics, undo behavior and backup/restore contracts.
- [ ] Run the full affected test groups after each fix.
- [ ] Commit functional-audit fixes separately from visual changes.

### Task 9: Packaging and Release Candidate Verification

**Files:**
- Inspect: `.github/workflows/build-windows.yml`
- Test: `tests/test_v8_packaging.py`, `tests/test_v8_release_candidate.py`, `tests/test_v8_runtime_compat.py`

- [ ] Run all local pytest tests and record the exact result.
- [ ] Validate the release-candidate tests against the V8 branch contents.
- [ ] Push the completed branch changes so GitHub Actions executes the Windows build.
- [ ] Verify the workflow run reaches success and produces the expected EXE/ZIP artifacts.
- [ ] Record the final commit SHA, workflow result and artifact names in the release notes/PR description.
- [ ] Do not label V8 stable if the Windows build is unavailable or failing.

### Task 10: Final Regression and Review Gate

**Files:**
- Modify: only files required by verified failures
- Test: full `tests/` suite

- [ ] Run the complete pytest suite after all implementation work.
- [ ] Re-run focused V8 shell/detail/workspace tests if the full suite exposes cross-module regressions.
- [ ] Review the acceptance criteria from the V8 design specification one by one.
- [ ] Verify no existing functionality was intentionally removed.
- [ ] Verify the final diff contains no debug output, placeholder UI, dead V8 modules or contradictory documentation.
- [ ] Commit only after all automated checks are green.

## Verification Matrix

| Area | Required evidence |
|---|---|
| V8 shell | focused shell tests pass |
| Navigation | collapse/active-state tests pass |
| Task surface | hierarchy + selection + responsive tests pass |
| Detail panel | open/close/resize/retention tests pass |
| Filters | combination/clear semantics pass |
| Kanban | drag/drop + inspector tests pass |
| Eisenhower | priority placement + inspector tests pass |
| Planning | due-period drag/drop + inspector tests pass |
| Themengebiete | live CRUD/navigation tests pass |
| Functional contract | existing regression suite passes |
| Packaging | GitHub Actions Windows EXE/ZIP succeeds |

## Completion Rule

V8 is not declared complete merely because the UI tests pass. Completion requires the full pytest suite, the release-candidate checks, and a successful Windows EXE/ZIP GitHub Actions build. Any limitation must be reported explicitly rather than inferred away.
