import typing as T

from tkinter import *
from tkinter import ttk

from bop.db.data import BaseIdentifiedHierarchicalRecord as BHRecord
from bop.db.data import BaseIdentifiedRecord as BRecord

from bop.app.env import AppEnv

class HierarchyTree(ttk.Treeview):
	def __init__(self, parent = None, show_type = False):
		super().__init__(parent)

		self._show_type = show_type

		self._displayed_elements = dict()

		cols = list()
		if self._show_type : cols.append("Type")
		cols.extend(["Name", "Description"])
		self['columns'] = tuple(cols)
		self.heading("#0",text="Code")
		for c in self['columns'] :
			self.heading(c,text=c)

	@staticmethod
	def _elt_id(elt : BRecord):
		return str(hash(elt))

	def _walker(self,pre_descend : T.Callable[[str],None] = None, post_descend : T.Callable[[str],None] = None, root = ""):
		def _visitor(item) :
			if pre_descend is not None :
				pre_descend(item)
			for i in self.get_children(item) :
				_visitor(i)
			if post_descend is not None :
				post_descend(item)

		_visitor(root)

	def delete(self,item):
		self._displayed_elements.pop(item)
		super().delete(item)

	def recurse_delete(self, item = ""):
		def delete_filter(item) :
			if item != "" :
				self.delete(item)
		self._walker(post_descend=delete_filter,root=item)

	def expand_all(self):
		self._walker(pre_descend=lambda x : self.item(x,open=TRUE))

	def collapse_all(self):
		self._walker(post_descend=lambda x : self.item(x,open=FALSE))

	def _tree_values(self, elt = BRecord ):
		values = list()
		if self._show_type : values.append(type(elt).__name__)
		values.append(elt.name if elt.name is not None else "")
		values.append(elt.descr if elt.descr is not None else "")

		return tuple(values)

	@property
	def selected_element(self) -> BRecord:
		return self._displayed_elements[self.focus()]

	def redisplay(self, roots : T.List[BRecord], tree : T.Dict[BRecord,T.List[BRecord]]):
		def insert_childs(parent : BRecord,elt : BRecord):
			elt_id = self._elt_id(elt)
			self._displayed_elements[elt_id] = elt
			self.insert(self._elt_id(parent) if parent is not None else "","end",elt_id, text=elt.code, values=self._tree_values(elt))
			for child in tree[elt]:
				insert_childs(elt,child)

		self.recurse_delete()
		for record in roots :
			insert_childs(None, record)

		self.expand_all()



