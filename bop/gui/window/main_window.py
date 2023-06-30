from tkinter import *
from tkinter import ttk

from threading import Thread, Semaphore
from queue import Queue, Empty
from bop.gui.widget.hierarchy_tree import HierarchyTree
from .show_impact import BopShowImpactWindow
from bop.app.env import AppEnv


class BopMainWindowThread(Thread):
	def run(self):
		AppEnv().is_gui_up = True
		root = BopMainWindow()
		root.mainloop()
		AppEnv().is_gui_up = False

	def stop(self):
		with AppEnv().gui_queue_lock :
			AppEnv().gui_control_queue.put_nowait("close")


class BopMainWindow(Tk) :
	def __init__(self):
		super().__init__()
		self.geometry("900x600")
		self.title("BOP")

		self.setup()

	def setup(self):
		self.tree = HierarchyTree(self)
		self.tree.grid(column=0,row=0, sticky="NSEW")

		btn_frame = Frame(self)
		ttk.Button(btn_frame,text="Collapse",command=lambda: self.tree.collapse_all()).pack(side=BOTTOM,expand=TRUE,fill=X)
		ttk.Button(btn_frame,text="Expand",command=lambda: self.tree.expand_all()).pack(side=BOTTOM,expand=TRUE,fill=X)
		ttk.Button(btn_frame,text="Refresh",command=self.refresh_tree_view).pack(side=BOTTOM,expand=TRUE,fill=X)
		ttk.Button(btn_frame,text="Impact",command=lambda : self.do_show_impact(self.tree.selected_element)).pack(side=BOTTOM,expand=TRUE,fill=X)

		btn_frame.grid(column=1, row=0,sticky="SEW")

		self.columnconfigure(0,weight=1)
		self.columnconfigure(1,weight=1)
		self.rowconfigure(0,weight=1)

		self.event_queue_semaphore = Semaphore()

		# Mandatory to properly finish, avoid restarting the _poll_request_queue.
		self.protocol("WM_DELETE_WINDOW", self.close)

		self.refresh_tree_view()
		self._poll_request_queue()

		self.setup_menu()

	def setup_menu(self):
		tree_right_click_menu = Menu(self,tearoff=0)
		tree_right_click_menu.add_command(label="Impact", command=lambda : self.do_show_impact(self.tree.selected_element))
		def do_popup(event):
			try:
				y_position = self.winfo_pointery() - self.tree.winfo_rooty()
				row = self.tree.identify_row(y_position)
				self.tree.selection_set(row)
				self.tree.focus(row)
				tree_right_click_menu.tk_popup(event.x_root, event.y_root)
			finally:
				tree_right_click_menu.grab_release()

		self.tree.bind("<Button-3>",do_popup)

	def close(self):
		with AppEnv().gui_queue_lock:
			AppEnv().gui_control_queue.put_nowait("close")

	def _poll_request_queue(self):
		with AppEnv().gui_queue_lock :
			try :
				while True :
					elt = AppEnv().gui_control_queue.get(block=False, timeout=0.5)
					if elt == "refresh":
						self.refresh_tree_view()
					if elt == "close" :
						# Flush the control queue
						while not AppEnv().gui_control_queue.empty() :
							AppEnv().gui_control_queue.get_nowait()
						self.destroy()
			except Empty:
				pass
		self.after(100,self._poll_request_queue)

	def refresh_tree_view(self):
		full_tree = dict()
		roots = AppEnv().db.get_root_requirements()
		for elt in roots :
			full_tree.update(AppEnv().prj.get_hierarchy_tree(elt))
		self.tree.redisplay(AppEnv().db.get_root_requirements(), full_tree)

	def do_show_impact(self,elt):
		win = BopShowImpactWindow(elt, master=None)



