import typing as T

from tkinter import *
from tkinter import ttk

from bop.db.data.base_identified_record import BaseIdentifiedRecord as BIRecord
from bop.app.env import AppEnv


class IdentifiedRecordEdit(Frame):
	def __init__(self, master = None, curr_element : BIRecord = None, elt_type = None):
		super().__init__(master)

		self._curr_elt : BIRecord = curr_element

		self.elt_id = IntVar(self)
		self.elt_code = StringVar(self)
		self.elt_name = StringVar(self)
		self.elt_descr = StringVar(self)

		self._generated_elt_type = type(curr_element) if elt_type is None else elt_type

		self._setup()

	def destroy(self) -> None:
		# Purge variables to avoid thread errors on destroying tkinter.
		del self.elt_id
		del self.elt_code
		del self.elt_name
		del self.elt_descr
		super().destroy()

	@property
	def element(self):
		return self._curr_elt

	@element.setter
	def element(self,elt : BIRecord):
		self._curr_elt = elt
		self.update()

	def _setup(self):
		Label(self,text="ID:").grid(column=0,row=0)
		Label(self,text="Code:").grid(column=0,row=1)
		Label(self,text="Name:").grid(column=0,row=2)
		Label(self,text="Description:").grid(column=0,row=3)

		Label(self,textvariable=self.elt_id).grid(column=1,row=0)
		Entry(self,textvariable=self.elt_code).grid(column=1,row=1)
		Entry(self,textvariable=self.elt_name).grid(column=1,row=2)
		Entry(self,textvariable=self.elt_descr).grid(column=1,row=3)

	def clear(self):
		self._curr_elt = None
		self.elt_id.set(0)
		self.elt_code.set("")
		self.elt_name.set("")
		self.elt_descr.set("")

	def save(self):
		if self._curr_elt is None :
			self._curr_elt = self._generated_elt_type()

		self._curr_elt.code = self.elt_code.get()
		self._curr_elt.name = self.elt_name.get()
		self._curr_elt.descr = self.elt_descr.get()

	def refresh(self):
		self.elt_id.set(self._curr_elt.id)
		self.elt_code.set(self._curr_elt.code)
		self.elt_name.set(self._curr_elt.name)
		self.elt_descr.set(self._curr_elt.descr)



