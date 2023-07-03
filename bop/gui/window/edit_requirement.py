from tkinter import *
from tkinter import ttk

from bop.db.data import BaseIdentifiedRecord as BRecord
from bop.db.data import Requirement
from bop.gui.widget.hierarchy_tree import HierarchyTree
from bop.gui.widget import IdentifiedRecordEdit

from bop.app.env import AppEnv


class BopEditRequirementWindow(Toplevel):
	def __init__(self, master = None, elt : Requirement = None):
		super().__init__(master)

		self._content_frame = LabelFrame(self, text="Properties")
		self.editor = IdentifiedRecordEdit(self._content_frame,elt,Requirement)
		self.setup()
		self.refresh()

	def setup(self):
		self._content_frame.pack()
		self.editor.pack(fill=BOTH)
		self._content_frame.pack(fill=BOTH)

		btn_frame = Frame(self)
		btn_frame.pack(side=BOTTOM,fill=X)
		Button(btn_frame,text="OK", command=self.do_save_and_exit).pack(fill=X)

	def do_save_and_exit(self):
		init_code = self.editor.element.code
		self.editor.save()
		req = self.editor.element
		command = f'update requirement "{init_code}" -c "{req.code}" -n "{req.name}" -d "{req.descr}"'
		with AppEnv().cmd_queue_lock :
			AppEnv().cmd_control_queue.put_nowait(command)
		self.destroy()

	def refresh(self):
		self.editor.refresh()