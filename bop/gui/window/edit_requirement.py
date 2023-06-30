from tkinter import *
from tkinter import ttk

from bop.db.data import BaseIdentifiedRecord as BRecord
from bop.db.data import Requirement
from bop.gui.widget.hierarchy_tree import HierarchyTree
from bop.app.env import AppEnv

class BopShowImpactWindow(Toplevel):
	def __init__(self,elt : Requirement, master = None):
		super().__init__(master)

		self._base_elt = elt
		self.setup()
		self.refresh()

	def setup(self):
		content_frame = LabelFrame(self,text="Properties")
		content_frame.pack()
		self.tree = HierarchyTree(self, show_type=True)
		self.tree.grid(column=0,row=0, sticky="NSEW")

	def refresh(self):
		self.tree.redisplay([self.impact_root],AppEnv().prj.get_impact_tree(self.impact_root))