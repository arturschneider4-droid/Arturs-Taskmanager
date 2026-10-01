from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QMainWindow, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from .design_tokens import Density, DesignTokens, build_stylesheet
from .dashboard import DashboardFilter, ExecutiveDashboard, WeeklyFocusPanel
from .board_views import EisenhowerView, KanbanView
from .calendar_view import CalendarView
from .detail_panel import DetailPanel
from .follow_up import AssignmentDialog, DelegatedView, FollowUpService, WaitingView
from .navigation import Navigation, ROUTE_LABELS, Route
from .quick_capture import InboxView, QuickCaptureOverlay
from .shortcuts import CommandSearchOverlay, ShortcutAction, ShortcutController
from .settings import HelpView, SettingsRepository, SettingsView, WindowsAutostartAdapter
from .task_list import MyDayView, NextSevenDaysView, RowAction, TaskListView
from .task_model import ControlMode, TaskDraft
from .task_store import ChangeSet, DeleteTask, SaveTask, TaskStore
from dataclasses import replace
from .weekly_review import WeeklyReviewService, WeeklyReviewView


class LayoutMode(str, Enum):
    WIDE = "wide"
    COMPACT = "compact"
    OVERLAY = "overlay"


class RoutePage(QWidget):
    def __init__(self, route: Route, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(ROUTE_LABELS[route][1]))
        self.scroll_area = QScrollArea()
        content = QWidget()
        content.setMinimumHeight(1800)
        self.scroll_area.setWidget(content)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area, 1)


class V10Shell(QMainWindow):
    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.layout_mode = LayoutMode.WIDE
        self.current_route = Route.DASHBOARD
        self.active_dashboard_filter = None
        self.setWindowTitle("Arturs Taskmanager V10.0")
        self.setMinimumSize(720, 640)
        self.setStyleSheet(build_stylesheet(DesignTokens(), Density.COMPACT))
        root = QWidget()
        root.setObjectName("v10Root")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.navigation = Navigation()
        self.navigation.route_requested.connect(self.navigate)
        root_layout.addWidget(self.navigation)
        center = QWidget(); center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(20, 16, 20, 16)
        toolbar = QHBoxLayout()
        self.page_title = QLabel("Executive Dashboard"); self.page_title.setObjectName("pageTitle")
        toolbar.addWidget(self.page_title, 1)
        self.search_button = QPushButton("Suchen"); self.search_button.setObjectName("global_search")
        self.search_button.clicked.connect(lambda: self.command_search.open())
        self.new_button = QPushButton("Neue Aufgabe"); self.new_button.setObjectName("new_task")
        self.new_button.setProperty("variant", "primary")
        self.new_button.clicked.connect(self.show_quick_capture)
        toolbar.addWidget(self.search_button); toolbar.addWidget(self.new_button)
        center_layout.addLayout(toolbar)
        self.pages = QStackedWidget()
        self.pages.setObjectName("v10Pages")
        self._pages = {}
        self.follow_up_service = FollowUpService(store)
        center_layout.addWidget(self.pages, 1)
        self.center = center
        root_layout.addWidget(center, 1)
        self.context_stack = QStackedWidget()
        self.context_stack.setObjectName("v10Context")
        self.context_stack.setMinimumWidth(300)
        self.weekly_focus = WeeklyFocusPanel(store)
        self.weekly_focus.review_requested.connect(lambda: self.navigate(Route.WEEKLY_REVIEW))
        self.detail_panel = DetailPanel(store)
        self.context_stack.addWidget(self.weekly_focus)
        self.context_stack.addWidget(self.detail_panel)
        self.detail_panel.opened.connect(self._show_detail)
        self.detail_panel.close_requested.connect(self._close_detail)
        root_layout.addWidget(self.context_stack)
        self.setCentralWidget(root)
        self.quick_capture = QuickCaptureOverlay(store, parent=self)
        self.quick_capture.setFixedWidth(560)
        self.quick_capture.hide()
        self.quick_capture.advanced_requested.connect(self._open_advanced_capture)
        self.command_search = CommandSearchOverlay(store, parent=self)
        self.command_search.setFixedSize(620, 420)
        self.command_search.hide()
        self.command_search.task_selected.connect(self._open_search_result)
        self.shortcut_controller = ShortcutController(self)
        self.shortcut_controller.dispatched.connect(self._dispatch_shortcut)
        settings = SettingsRepository(self.store.repository.db_path.parent / "settings.json").load()
        self._apply_settings(settings)
        self.navigate(Route.DASHBOARD)
        from .notifications import ReminderScheduler, DueReminderDialog
        class InAppBackend:
            def show(_self, title, message): self.statusBar().showMessage(f"{title}: {message}", 15000)
        self._reminder_dialogs = {}
        self.reminder_scheduler = ReminderScheduler(self.store, InAppBackend(), parent=self)
        self.reminder_scheduler.reminder_due.connect(self._show_reminder)
        self.reminder_scheduler.start()

    def page_for(self, route: Route) -> RoutePage:
        route = Route(route)
        if route not in self._pages:
            page = self._create_page(route)
            self._pages[route] = page
            self.pages.addWidget(page)
            if hasattr(page, "task_selected"):
                page.task_selected.connect(self.detail_panel.open_task)
            if isinstance(page, TaskListView):
                page.action_performed.connect(self._handle_row_action)
            if isinstance(page, SettingsView):
                from .backup_restore import BackupService
                page.settings_saved.connect(self._apply_settings)
                page.enable_backup_controls(BackupService(self.store.repository.db_path, self.store.repository.db_path.parent / "backups"), self.detail_panel.flush)
                page.restored.connect(self._after_restore)
            if isinstance(page, WeeklyReviewView):
                page.completed.connect(lambda _summary: self._review_completed())
                page.paused.connect(lambda: self.navigate(Route.DASHBOARD))
            if isinstance(page, ExecutiveDashboard):
                page.filter_requested.connect(self._open_dashboard_filter)
        return self._pages[route]

    def _create_page(self, route: Route):
        if route is Route.DASHBOARD: return ExecutiveDashboard(self.store)
        if route is Route.INBOX: return InboxView(self.store)
        if route is Route.MY_DAY: return MyDayView(self.store)
        if route is Route.NEXT_SEVEN: return NextSevenDaysView(self.store)
        if route is Route.WAITING: return WaitingView(self.follow_up_service)
        if route is Route.DELEGATED: return DelegatedView(self.follow_up_service)
        if route is Route.WEEKLY_REVIEW: return WeeklyReviewView(WeeklyReviewService(self.store.repository.db_path))
        if route is Route.KANBAN: return KanbanView(self.store)
        if route is Route.EISENHOWER: return EisenhowerView(self.store)
        if route is Route.CALENDAR: return CalendarView(self.store)
        if route is Route.SETTINGS: return SettingsView(SettingsRepository(self.store.repository.db_path.parent / "settings.json"), WindowsAutostartAdapter())
        if route is Route.HELP: return HelpView()
        if route in {Route.TASKS, Route.ALL_TASKS}: return TaskListView(self.store)
        return RoutePage(route)

    def navigate(self, route: Route) -> None:
        route = Route(route)
        self.current_route = route
        self.page_title.setText(ROUTE_LABELS[route][1])
        page = self.page_for(route)
        if getattr(page, "metric_filter", None) is not None:
            page.metric_filter = None; page.refresh()
        self.pages.setCurrentWidget(page)
        page.show()
        self.navigation.set_active(route)

    def _open_dashboard_filter(self, dashboard_filter: DashboardFilter) -> None:
        self.active_dashboard_filter = dashboard_filter
        routes = {
            DashboardFilter.TODAY: Route.MY_DAY,
            DashboardFilter.OVERDUE: Route.TASKS,
            DashboardFilter.FOLLOW_UPS: Route.WAITING,
            DashboardFilter.DELEGATED: Route.DELEGATED,
            DashboardFilter.TOP_THREE: Route.MY_DAY,
            DashboardFilter.CRITICAL_DEADLINES: Route.TASKS,
            DashboardFilter.UNPLANNED: Route.TASKS,
            DashboardFilter.WEEK_PROGRESS: Route.TASKS,
        }
        self.navigate(routes[dashboard_filter])
        page = self.page_for(self.current_route)
        page.metric_filter = dashboard_filter.value
        page.refresh()
        self.page_title.setText(dashboard_filter.label)

    def _apply_settings(self, settings):
        try: density = Density(settings.density)
        except ValueError: density = Density.COMPACT
        self.setStyleSheet(build_stylesheet(DesignTokens(), density))
        self.detail_panel.default_reminder_minutes = settings.default_reminder_minutes

    def _after_restore(self):
        from .undo import UndoManager
        from .migrations import migrate_to_v10
        import sqlite3
        connection = sqlite3.connect(self.store.repository.db_path)
        columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}; connection.close()
        if "planning_date" not in columns:
            migrate_to_v10(self.store.repository.db_path, self.store.repository.db_path.parent / "backups")
        self.detail_panel._save_timer.stop()
        self.detail_panel.task_id = None; self.detail_panel.record = None
        self.store.undo_manager = UndoManager(self.store.repository)
        self._close_detail()
        self.store.changed.emit(ChangeSet(frozenset(), frozenset({"tasks", "dashboard"})))

    def _review_completed(self):
        self.store.changed.emit(ChangeSet(frozenset(), frozenset({"dashboard"})))
        self.navigate(Route.DASHBOARD)

    def _show_reminder(self, task_id):
        from .notifications import DueReminderDialog
        dialog = DueReminderDialog(self.store, task_id, parent=self)
        dialog.snooze_minutes.setValue(max(5, self.detail_panel.default_reminder_minutes))
        self._reminder_dialogs[task_id] = dialog
        dialog.finished.connect(lambda _result: self._reminder_dialogs.pop(task_id, None))
        dialog.show()

    def _show_detail(self, _task_id):
        self.context_stack.setCurrentWidget(self.detail_panel)
        self.context_stack.show()
        if self.layout_mode is LayoutMode.OVERLAY:
            self.center.hide()

    def _close_detail(self):
        if not self.detail_panel.flush(): return
        self.context_stack.setCurrentWidget(self.weekly_focus)
        self.center.show()
        self.context_stack.setVisible(self.layout_mode is not LayoutMode.OVERLAY)

    def closeEvent(self, event):
        if self.detail_panel.flush():
            self.reminder_scheduler.stop()
            event.accept()
        else: event.ignore()

    def show_quick_capture(self) -> None:
        self.quick_capture.adjustSize()
        self.quick_capture.move(max(12, (self.width() - self.quick_capture.width()) // 2), 72)
        self.quick_capture.show()
        self.quick_capture.raise_()
        self.quick_capture.input.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _open_advanced_capture(self) -> None:
        preview = self.quick_capture._preview()
        if preview.estimated_minutes is not None and preview.estimated_minutes <= 0:
            self.quick_capture.preview_label.setText("Geschätzte Dauer muss positiv sein"); return
        if not preview.title:
            self.quick_capture.preview_label.setText("Titel erforderlich")
            return
        result = self.store.apply(SaveTask(TaskDraft(
            title=preview.title, project_id=self.quick_capture._project_ids.get(preview.project), planning_date=preview.planning_date,
            priority=preview.priority, estimated_minutes=preview.estimated_minutes,
        )))
        if result.ok:
            self.quick_capture.hide()
            self.quick_capture.input.clear()
            self.detail_panel.open_task(result.task_id)
            if preview.control_mode is not ControlMode.SELF:
                self.detail_panel.control_combo.setCurrentIndex(self.detail_panel.control_combo.findData(preview.control_mode.value))
                self.detail_panel.person_edit.setFocus()

    def _open_search_result(self, task_id: int) -> None:
        self.command_search.hide()
        self.detail_panel.open_task(task_id)

    def _handle_row_action(self, task_id: int, action: RowAction) -> None:
        modes = {RowAction.DELEGATE: ControlMode.DELEGATED, RowAction.WAIT: ControlMode.WAITING}
        if action not in modes:
            return
        self.assignment_dialog = AssignmentDialog(self.follow_up_service, task_id, modes[action], self)
        self.assignment_dialog.show()

    def _dispatch_shortcut(self, action: ShortcutAction) -> None:
        if action in {ShortcutAction.QUICK_CAPTURE, ShortcutAction.NEW_TASK}:
            self.show_quick_capture()
            return
        if action is ShortcutAction.COMMAND_SEARCH:
            self.command_search.open()
            return
        if action is ShortcutAction.UNDO:
            self.store.undo()
            return
        page = self.page_for(self.current_route)
        if not isinstance(page, TaskListView) or page.selected_task_id is None:
            return
        mapping = {
            ShortcutAction.TODAY: RowAction.TODAY,
            ShortcutAction.TOMORROW: RowAction.TOMORROW,
            ShortcutAction.DELEGATE: RowAction.DELEGATE,
            ShortcutAction.WAIT: RowAction.WAIT,
            ShortcutAction.COMPLETE: RowAction.COMPLETE,
        }
        if action in mapping:
            page.perform_action(page.selected_task_id, mapping[action])
        elif action in {ShortcutAction.PRIORITY_1, ShortcutAction.PRIORITY_2, ShortcutAction.PRIORITY_3, ShortcutAction.PRIORITY_4}:
            priorities = {
                ShortcutAction.PRIORITY_1: "important_urgent", ShortcutAction.PRIORITY_2: "important_not_urgent",
                ShortcutAction.PRIORITY_3: "not_important_urgent", ShortcutAction.PRIORITY_4: "not_important_not_urgent",
            }
            record = self.store.repository.get(page.selected_task_id)
            if record: self.store.apply(SaveTask(replace(record.draft, priority=priorities[action]), record.id))
        elif action is ShortcutAction.DELETE:
            self.store.apply(DeleteTask(page.selected_task_id)); page.selected_task_id = None

    def resizeEvent(self, event):
        width = event.size().width()
        if width >= 1280:
            mode = LayoutMode.WIDE
        elif width >= 900:
            mode = LayoutMode.COMPACT
        else:
            mode = LayoutMode.OVERLAY
        self.layout_mode = mode
        self.navigation.set_compact(mode is not LayoutMode.WIDE)
        self.navigation.setFixedWidth(240 if mode is LayoutMode.WIDE else 64)
        if mode is LayoutMode.OVERLAY:
            self.context_stack.setMinimumWidth(0)
            self.context_stack.setMaximumWidth(16777215)
        else:
            self.context_stack.setFixedWidth(340 if mode is LayoutMode.WIDE else 300)
        detail_open = self.context_stack.currentWidget() is self.detail_panel
        self.context_stack.setVisible(mode is not LayoutMode.OVERLAY or detail_open)
        self.center.setVisible(mode is not LayoutMode.OVERLAY or not detail_open)
        super().resizeEvent(event)
