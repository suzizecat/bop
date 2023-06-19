from tkinter import *
from tkinter import ttk

from threading import Thread
from time import sleep
from bop.gui.widget.hierarchy_tree import HierarchyTree
from bop.app.env import AppEnv

class BopMainWindow(Tk) :
	def __init__(self):
		super().__init__()

		self.geometry("900x600")
		self.title("BOP")
		self.setup()

		self._update_monitor_thread = None

	def setup(self):
		self.tree = HierarchyTree(self)
		self.tree.grid(column=0,row=0, sticky="NSEW")


		btn_frame = Frame(self)
		ttk.Button(btn_frame,text="Collapse",command=lambda: self.tree.collapse_all()).pack(side=BOTTOM,expand=TRUE,fill=X)
		ttk.Button(btn_frame,text="Expand",command=lambda: self.tree.expand_all()).pack(side=BOTTOM,expand=TRUE,fill=X)
		ttk.Button(btn_frame,text="Refresh",command=self.refresh_tree_view).pack(side=BOTTOM,expand=TRUE,fill=X)

		btn_frame.grid(column=1, row=0,sticky="SEW")

		self.columnconfigure(0,weight=1)
		self.columnconfigure(1,weight=1)
		self.rowconfigure(0,weight=1)

		self.refresh_tree_view()

		self._update_monitor_thread = Thread(target=self._background_handler).start()
		
	def refresh_tree_view(self):
		full_tree = dict()
		roots = AppEnv().db.get_root_requirements()
		for elt in roots :
			full_tree.update(AppEnv().prj.get_hierarchy_tree(elt))
		self.tree.redisplay(AppEnv().db.get_root_requirements(), full_tree)

	def _background_handler(self):
		while 1 :
			# Blocking wait
			elt = AppEnv().gui_control_queue.get()

			if elt == "refresh":
				self.refresh_tree_view()

