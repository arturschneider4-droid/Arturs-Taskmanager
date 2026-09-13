# V8 Release Candidate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing V8 premium branch into a release candidate with a coherent V8 UI identity, hardened core workflows, regression coverage, and a verified Windows package.

**Architecture:** Preserve Python/PySide6 + SQLite and the existing V8 modular workspace architecture (`v8_detail_panel`, `v8_kanban`, `v8_eisenhower`, `v8_planning`, `v8_interactions`). Make targeted fixes rather than rewriting stable V7 infrastructure, and keep all behavioral changes regression-tested.

**Tech Stack:** Python, PySide6, SQLite, pytest, GitHub Actions, PyInstaller.

**Spec:** Existing V8 premium branch direction and the V7.1 complete functional audit scope in `docs/superpowers/plans/2026-09-10-v71-complete-functional-audit.md`.

## Global Constraints

- Keep Python/PySide6 + SQLite and offline/local operation.
- Preserve task management capabilities and existing database compatibility.
- V8 must present V8 branding consistently instead of stale V6/V7 labels.
- Every behavioral fix gets a regression test where practical.
- Do not claim release-candidate completion until pytest and the Windows build both succeed.

### Task 1: Establish V8 baseline

**Files:** `taskmanager/ui.py`, `taskmanager/style_v8.py`, `taskmanager/v8_detail_panel.py`, `taskmanager/v8_kanban.py`, `taskmanager/v8_eisenhower.py`, `taskmanager/v8_planning.py`, `taskmanager/v8_interactions.py`, `tests/`

- [ ] Review V8 wiring and existing tests.
- [ ] Identify stale branding, dead controls, and uncovered V8 workflows.
- [ ] Record concrete defects before modifying behavior.

### Task 2: V8 shell and branding consistency

**Files:** `taskmanager/ui.py`, `taskmanager/style_v8.py`, focused V8 shell test.

- [ ] Add a failing test asserting V8-facing title/version/primary shell identity.
- [ ] Update stale V6.2/V7 labels and V8 shell references.
- [ ] Run the focused test and then the existing UI contract tests.
- [ ] Commit the change.

### Task 3: Detail panel and task editing workflow

**Files:** `taskmanager/v8_detail_panel.py`, `taskmanager/v8_interactions.py`, `taskmanager/ui.py`, `tests/test_task_editor_behavior_v7.py` or focused V8 regression test.

- [ ] Verify select/edit/save/delete/check subtask behavior.
- [ ] Verify status, priority, due date and theme persistence.
- [ ] Add failing regressions for any uncovered behavior.
- [ ] Implement the smallest fixes and rerun focused tests.
- [ ] Commit.

### Task 4: Workspace correctness

**Files:** `taskmanager/v8_kanban.py`, `taskmanager/v8_eisenhower.py`, `taskmanager/v8_planning.py`, `taskmanager/v8_interactions.py`, focused workspace tests.

- [ ] Verify valid drag/drop changes the intended field.
- [ ] Verify rejected drops do not emit false updates.
- [ ] Verify planning groups and due-date semantics.
- [ ] Add regressions and fix only proven defects.
- [ ] Commit.

### Task 5: Filters, navigation and secondary actions

**Files:** `taskmanager/ui.py`, `taskmanager/db.py`, `taskmanager/overview.py`, focused tests.

- [ ] Verify search/filter combinations and refresh state.
- [ ] Verify navigation to every V8 workspace and overview scope.
- [ ] Verify export, settings, help and keyboard shortcuts where testable.
- [ ] Add regressions and fix defects.
- [ ] Commit.

### Task 6: Undo, backup and responsive behavior

**Files:** `taskmanager/ui.py`, `taskmanager/db.py`, `taskmanager/responsive_table_v7.py`, focused tests.

- [ ] Verify undo availability and restoration semantics.
- [ ] Verify representative responsive widths keep key task columns accessible.
- [ ] Add regressions and fix defects.
- [ ] Commit.

### Task 7: Full release verification

**Files:** `.github/workflows/build-windows.yml`, tests only if verification exposes a defect.

- [ ] Run the complete pytest suite.
- [ ] Build the Windows EXE with the existing workflow.
- [ ] Verify V8 packaging output and ZIP/EXE artifacts.
- [ ] Record final SHA, workflow run and artifact hashes.
- [ ] Report any remaining limitations honestly.
