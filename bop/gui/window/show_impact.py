from tkinter import *
from tkinter import ttk

from bop.db.data import BaseIdentifiedRecord as BRecord
from bop.gui.widget.hierarchy_tree import HierarchyTree
from bop.app.env import AppEnv

class BopShowImpactWindow(Toplevel):
	def __init__(self,elt : BRecord, master = None):
		super().__init__(master)

		self.impact_root : BRecord= elt
		self.setup()
		self.refresh()

	def setup(self):
		self.tree = HierarchyTree(self, show_type=True)
		self.tree.grid(column=0,row=0, sticky="NSEW")

	def refresh(self):
		self.tree.redisplay([self.impact_root],AppEnv().prj.get_impact_tree(self.impact_root))