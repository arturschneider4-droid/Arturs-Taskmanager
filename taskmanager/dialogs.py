
from PySide6.QtCore import QDate,Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QComboBox,QDateEdit,QTextEdit,QListWidget,QListWidgetItem,QPushButton,QHBoxLayout,QDialogButtonBox,QLabel,QInputDialog
from .constants import PRIORITIES,STATUS,RECURRENCE
from .db import connect,subs
class TaskDialog(QDialog):
 def __init__(self,parent,task=None,default_project=None):
  super().__init__(parent);self.setWindowTitle("Aufgabe bearbeiten" if task else "Neue Aufgabe");self.resize(620,620);root=QVBoxLayout(self);form=QFormLayout()
  self.title=QLineEdit(task["title"] if task else "");self.project=QComboBox();self.project.addItem("Kein Themengebiet",None);c=connect()
  for r in c.execute("SELECT id,name FROM projects ORDER BY name"):self.project.addItem(r["name"],r["id"])
  c.close();pid=task["project_id"] if task else default_project
  if pid is not None:
   i=self.project.findData(pid)
   if i>=0:self.project.setCurrentIndex(i)
  self.priority=QComboBox()
  for k,v in PRIORITIES.items():self.priority.addItem(v,k)
  if task:self.priority.setCurrentIndex(max(0,self.priority.findData(task["priority"])))
  self.due=QDateEdit();self.due.setCalendarPopup(True);self.due.setDisplayFormat("dd.MM.yyyy");self.due.setDate(QDate.fromString(task["due_date"],"yyyy-MM-dd") if task and task["due_date"] else QDate.currentDate())
  self.status=QComboBox();self.status.addItems(STATUS)
  if task:self.status.setCurrentText(task["status"])
  self.recurrence=QComboBox()
  for k,v in RECURRENCE.items():self.recurrence.addItem(v,k)
  if task:self.recurrence.setCurrentIndex(max(0,self.recurrence.findData(task["recurrence"])))
  self.desc=QTextEdit(task["description"] if task else "");self.desc.setMinimumHeight(90)
  for label,w in [("Aufgabe",self.title),("Themengebiet",self.project),("Priorität",self.priority),("Fälligkeit",self.due),("Status",self.status),("Wiederholung",self.recurrence),("Beschreibung",self.desc)]:form.addRow(label,w)
  root.addLayout(form);root.addWidget(QLabel("Unteraufgaben"));row=QHBoxLayout();self.subs=QListWidget()
  if task:
   for r in subs(task["id"]):
    it=QListWidgetItem(r["title"]);it.setCheckState(Qt.Checked if r["done"] else Qt.Unchecked);self.subs.addItem(it)
  row.addWidget(self.subs,1);col=QVBoxLayout();a=QPushButton("+ Hinzufügen");a.clicked.connect(self.add_sub);d=QPushButton("Löschen");d.clicked.connect(self.remove_sub);col.addWidget(a);col.addWidget(d);col.addStretch();row.addLayout(col);root.addLayout(row)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);b.accepted.connect(self.accept);b.rejected.connect(self.reject);root.addWidget(b);self.title.setFocus()
 def add_sub(self):
  t,ok=QInputDialog.getText(self,"Unteraufgabe","Unteraufgabe:")
  if ok and t.strip():it=QListWidgetItem(t.strip());it.setCheckState(Qt.Unchecked);self.subs.addItem(it)
 def remove_sub(self):
  i=self.subs.currentRow()
  if i>=0:self.subs.takeItem(i)
 def values(self):
  return {"title":self.title.text().strip(),"project_id":self.project.currentData(),"priority":self.priority.currentData(),"due_date":self.due.date().toString("yyyy-MM-dd"),"status":self.status.currentText(),"recurrence":self.recurrence.currentData(),"description":self.desc.toPlainText().strip(),"subtasks":[(self.subs.item(i).text(),self.subs.item(i).checkState()==Qt.Checked) for i in range(self.subs.count())]}
class ProjectDialog(QDialog):
 def __init__(self,parent,name=""):
  super().__init__(parent);self.setWindowTitle("Themengebiet");l=QVBoxLayout(self);l.addWidget(QLabel("Name des Themengebiets"));self.edit=QLineEdit(name);l.addWidget(self.edit);b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);b.accepted.connect(self.accept);b.rejected.connect(self.reject);l.addWidget(b);self.edit.setFocus()
 def name(self):return self.edit.text().strip()
