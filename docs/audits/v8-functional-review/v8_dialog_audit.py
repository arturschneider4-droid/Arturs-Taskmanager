exec(open(__import__('pathlib').Path(__file__).with_name('v8_deep_audit.py')).read().split('for i in range(3):run(i+1)')[0].split('def run(repeat):')[0])
from taskmanager.dialogs import TaskDialog,ProjectDialog
from PySide6.QtWidgets import QDialog
out=[]
for iteration in range(3):
 root=Path(tempfile.mkdtemp());db.APP_DIR=root;db.DB_PATH=root/'db';db.BACKUP_DIR=root/'b';db.init_db();w=configure_main_window(MainWindow());w.show();app.processEvents()
 def ck(name,ok):out.append((iteration+1,name,bool(ok)))
 try:
  def project_exec(d):d.edit.setText('Gebiet');return QDialog.Accepted
  with patch.object(ProjectDialog,'exec',project_exec):w.new_project()
  pid=w.project_filter;ck('create_project',pid is not None)
  def task_exec(d):d.title.setText('Neue Aufgabe');d.no_due.setChecked(True);return QDialog.Accepted
  with patch.object(TaskDialog,'exec',task_exec):w.new_task()
  tid=w.selected_task;ck('create_task_dialog',db.task(tid)['title']=='Neue Aufgabe' and db.task(tid)['project_id']==pid)
  def edit_exec(d):d.title.setText('Geaendert');d.status.setCurrentText('In Arbeit');return QDialog.Accepted
  with patch.object(TaskDialog,'exec',edit_exec):w.edit_task(tid)
  ck('edit_task_dialog',db.task(tid)['title']=='Geaendert' and db.task(tid)['status']=='In Arbeit')
  with patch.object(TaskDialog,'exec',return_value=QDialog.Rejected):w.new_task()
  ck('cancel_new_task',len(db.tasks())==1)
  def rename_exec(d):d.edit.setText('Umbenannt');return QDialog.Accepted
  with patch.object(ProjectDialog,'exec',rename_exec):w.edit_project(pid)
  ck('rename_project',db.task(tid)['project_name']=='Umbenannt')
  with patch.object(QMessageBox,'question',return_value=QMessageBox.Yes):w.delete_project(pid)
  ck('delete_project_preserves_task',db.task(tid) is not None and db.task(tid)['project_id'] is None)
  w.global_search.setText('Geaendert');ck('visible_search_finds_task',w.table.rowCount()==1)
  w.global_search.setText('Nichts');ck('visible_search_excludes_task',w.table.rowCount()==0)
  w.global_search.clear();w.e_title.setFocus()
  action=next(x for x in w.actions() if x.shortcut().toString()=='Ctrl+F');action.trigger();app.processEvents();ck('search_shortcut_focuses_visible_field',w.global_search.hasFocus())
 finally:w.close();w.deleteLater();app.processEvents()
print(json.dumps(out,indent=2))
