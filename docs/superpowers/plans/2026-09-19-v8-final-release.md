# V8 Final Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a verified V8.0 Windows release ZIP containing a startup-tested executable and all runtime dependencies.

**Architecture:** Keep the existing PySide6/SQLite application and V8 presentation layer. Close only proven release gaps, pin each correction with a behavioral regression test, then let the Windows workflow build and smoke-test the distributable before downloading the ZIP.

**Tech Stack:** Python 3.12, PySide6, SQLite, openpyxl, pytest, PyInstaller, GitHub Actions Windows runner

**Spec:** `docs/superpowers/specs/2026-09-11-v8-premium-enterprise-ui-design.md`

## Global Constraints

- Release identity is exactly `8.0` / `V8.0`.
- Existing local databases and user data must remain untouched.
- Full test suite, Windows PyInstaller build, module inspection, EXE smoke test and ZIP creation must all pass.
- No unrelated refactoring and no release claim without fresh evidence.

## Review Focus

- A clean installation must export a real `.xlsx` without a missing dependency.
- An enabled startup Undo button must perform an available restore rather than report no action.
- Filter/sort/group controls must expose their state clearly and preserve existing task semantics.
- A legacy database must migrate without changing task content.
- The packaged Windows EXE must remain running during the smoke-test interval.

---

### Task 1: Restore packaged Excel export

**Files:**
- Modify: `requirements.txt`
- Modify: `.github/workflows/build-windows.yml`
- Create: `tests/test_v8_export_release.py`

**Interfaces:**
- Consumes: `MainWindow.export_excel()`
- Produces: a packaged `openpyxl` runtime and verified XLSX export

- [ ] Write a test that creates a task, redirects the save dialog to a temporary path, calls `export_excel()`, and verifies the workbook content with `openpyxl.load_workbook()`.
- [ ] Run `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_v8_export_release.py -q` and verify failure because `openpyxl` is unavailable.
- [ ] Add `openpyxl>=3.1,<4` to `requirements.txt`; install it in the local virtual environment.
- [ ] Add a Windows post-build import/module assertion so a missing packaged dependency fails CI.
- [ ] Re-run the focused test and verify it passes.
- [ ] Commit as `fix(release): package Excel export dependency`.

### Task 2: Make startup Undo state truthful and functional

**Files:**
- Modify: `taskmanager/app.py`
- Test: `tests/test_v8_undo_contract.py`

**Interfaces:**
- Consumes: `latest_backup()` and `MainWindow._undo_available`
- Produces: identical visual and internal startup Undo availability

- [ ] Add a behavioral test that provides a startup backup and asserts both `undo_button.isEnabled()` and `_undo_available` are true.
- [ ] Run the focused test and verify the current state fails with `_undo_available is False`.
- [ ] Initialize `_undo_available` from the resolved startup backup and set the button from the same value.
- [ ] Add a no-backup case asserting both states are false.
- [ ] Run focused and full tests.
- [ ] Commit as `fix(v8): synchronize startup undo availability`.

### Task 3: Make V8 release identity consistent

**Files:**
- Modify: `taskmanager/__init__.py`
- Modify: `taskmanager/constants.py`
- Modify: `README.md`
- Test: `tests/test_v8_release_contract.py`

**Interfaces:**
- Produces: one authoritative user- and package-facing V8.0 identity

- [ ] Extend the release contract test to assert `taskmanager.__version__ == "8.0"`, `UI_SPEC["version"] == "V8.0"`, and a V8 README heading.
- [ ] Run the test and verify the three stale identities fail.
- [ ] Update only the current release metadata and README release section.
- [ ] Re-run the focused test and full suite.
- [ ] Commit as `docs(release): align V8 version identity`.

### Task 4: Complete V8 filter, sorting and grouping controls

**Files:**
- Modify: `taskmanager/style_v8.py`
- Modify: `tests/test_v8_gui_interactions.py`
- Modify: `tests/test_v8_shell.py`

**Interfaces:**
- Produces: `_show_sort_menu()`, visible removable active-filter chips, and explicit grouping state

- [ ] Add GUI tests that select a filter and observe a removable chip, choose a sorting mode through the menu action, and choose/clear grouping while preserving rows.
- [ ] Run the focused GUI tests and verify they fail against the current direct `cycle_sort` and chip-less UI.
- [ ] Implement a compact sort menu backed by existing `sort_mode` semantics.
- [ ] Add a compact chip row synchronized with the four existing filter widgets; chip removal resets only its own filter.
- [ ] Expose grouping state and visible group separators without changing database queries.
- [ ] Re-run focused tests, then the full suite at both wide and 980 px layouts.
- [ ] Commit as `fix(v8): complete filter sort and grouping interactions`.

### Task 5: Build and publish the verified Windows release artifact

**Files:**
- Modify if required: `.github/workflows/build-windows.yml`
- Update: `docs/releases/V8.0-RELEASE-CANDIDATE.md`

**Interfaces:**
- Produces: `ArtursTaskmanager-V8.0-Windows.zip` containing `ArtursTaskmanager.exe`

- [ ] Run the complete local test suite and verify zero failures.
- [ ] Run a clean local PyInstaller build, verify V8 and `openpyxl` module inclusion, and perform a binary startup smoke test.
- [ ] Verify the Git diff contains no databases, debug output, temporary files or unrelated changes.
- [ ] Push the verified release commit to the authorized release branch/main as agreed, without force-push.
- [ ] Observe the Windows workflow through tests, PyInstaller build, module inspection, 12-second EXE smoke test, ZIP creation and both uploads.
- [ ] Download the ZIP artifact, verify its SHA-256 digest and confirm the EXE exists inside it.
- [ ] Save the final ZIP as the user-facing deliverable and report commit SHA, workflow run, test count, smoke result and digest.

## Self-review

- Specification coverage: export, Undo, V8 identity, interaction gaps, migration regression, packaging and artifact delivery are covered.
- Placeholder scan: no deferred implementation placeholders remain.
- Type consistency: all changes use existing `MainWindow`, filter widgets and `sort_mode` contracts.
- Release gate: no step permits release labeling before Windows artifact verification.
