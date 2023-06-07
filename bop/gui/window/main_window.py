from tkinter import *
from tkinter import ttk


class BopMainWindow(Tk) :
	def __init__(self):
		super().__init__()

		self.geometry("800x600")
		self.title("BOP")
		self.setup()

	

	def setup(self):
		ttk.Button(self,text="Test").grid()
