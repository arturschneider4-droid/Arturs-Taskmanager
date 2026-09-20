"""Production startup and persistence regression checks from the release audit."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import taskmanager.db as db

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('script', ['v8_deep_audit.py', 'v8_dialog_audit.py'])
def test_repeated_production_workflows(script):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'docs/audits/v8-functional-review' / script)],
        cwd=ROOT, env={**os.environ, 'QT_QPA_PLATFORM':'offscreen', 'PYTHONPATH':str(ROOT)},
        capture_output=True, text=True, timeout=90,
    )
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout.split('SUMMARY')[0])
    failures = [r for r in rows if not (r['passed'] if isinstance(r,dict) else r[2])]
    assert not failures, failures

@pytest.mark.parametrize('frequency,due,expected', [
    ('daily','2026-12-31','2027-01-01'),
    ('weekly','2026-12-31','2027-01-07'),
    ('monthly','2027-01-31','2027-02-28'),
    ('monthly','2028-01-31','2028-02-29'),
])
@pytest.mark.parametrize('editor_save',[False,True])
def test_recurrence_dates_transaction_and_undo(tmp_path,monkeypatch,frequency,due,expected,editor_save):
    monkeypatch.setattr(db,'APP_DIR',tmp_path)
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'tasks.db')
    monkeypatch.setattr(db,'BACKUP_DIR',tmp_path/'backups')
    db.init_db()
    data=dict(title='Serie',description='',project_id=None,priority='important_urgent',due_date=due,status='Offen',recurrence=frequency,subtasks=[('Teil',True)])
    tid=db.save(data,make_backup=False)
    if editor_save:
        data['status']='Erledigt';db.save(data,tid)
    else:db.update_status(tid,'Erledigt')
    backup=db.latest_backup()
    following=[r for r in db.tasks() if r['id']!=tid]
    assert len(following)==1
    assert following[0]['due_date']==expected
    assert following[0]['status']=='Offen'
    assert db.subs(following[0]['id'])[0]['done']==0
    db.update_status(tid,'Erledigt')
    assert len(db.tasks())==2
    db.restore_backup(backup)
    assert len(db.tasks())==1
    assert db.task(tid)['status']=='Offen'

@pytest.fixture
def production_window(tmp_path,monkeypatch):
    from PySide6.QtWidgets import QApplication
    from taskmanager.ui import MainWindow
    from taskmanager.app import configure_main_window
    monkeypatch.setattr(db,'APP_DIR',tmp_path)
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'tasks.db')
    monkeypatch.setattr(db,'BACKUP_DIR',tmp_path/'backups')
    db.init_db()
    app=QApplication.instance() or QApplication([])
    window=configure_main_window(MainWindow())
    window.resize(1440,900);window.show();app.processEvents()
    yield window
    window.close();window.deleteLater();app.processEvents()

def test_resize_retains_selection_and_unsaved_draft(production_window):
    w=production_window
    tid=db.save(dict(title='Original',description='',project_id=None,priority='important_urgent',due_date=None,status='Offen',recurrence='none',subtasks=[]),make_backup=False)
    w._v8_detail_panel.set_task_id(tid);w._v8_detail_panel.set_panel_open(True)
    w.e_title.setText('Entwurf')
    w._v8_detail_panel.handle_window_width(980)
    w._v8_detail_panel.handle_window_width(1440)
    assert w._v8_detail_panel.task_id==tid
    assert w.e_title.text()=='Entwurf'
    assert db.task(tid)['title']=='Original'

def test_table_status_change_does_not_get_overwritten_by_editor_save(production_window):
    w=production_window
    tid=db.save(dict(title='Original',description='',project_id=None,priority='important_urgent',due_date=None,status='Offen',recurrence='none',subtasks=[]),make_backup=False)
    w.select_task(tid);w.e_title.setText('Entwurf');w.set_status(tid,'In Arbeit');w.save_editor()
    assert db.task(tid)['status']=='In Arbeit'
    assert db.task(tid)['title']=='Entwurf'


def test_navigation_after_deferred_widget_deletion(production_window):
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QLabel
    from taskmanager.style_v8 import _navigate
    w = production_window
    for _ in range(3):
        for key, expected in [('kanban', 'Kanban'), ('eisenhower', 'Eisenhower-Matrix'), ('planning', 'Planung'), ('tasks', 'Aufgaben')]:
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            _navigate(w, key)
            assert w.findChild(QLabel, 'v8HeaderTitle').text() == expected
            assert next(b for k,b in w._v8_nav_items if k == key).isChecked()
            w.refresh_all()
