import typing as T

from tkinter import *
from tkinter import ttk

from bop.db.data import BaseIdentifiedHierarchicalRecord as BHRecord
from bop.db.data import BaseIdentifiedRecord as BRecord

class HierarchyTree(ttk.Treeview):
	def __init__(self, parent = None):
		super().__init__(parent)

		self['columns'] = ("Name", "Description")

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

	def recurse_delete(self, item = ""):
		def delete_filter(item) :
			if item != "" :
				self.delete(item)
		self._walker(post_descend=delete_filter,root=item)

	def expand_all(self):
		self._walker(pre_descend=lambda x : self.item(x,open=TRUE))

	def collapse_all(self):
		self._walker(post_descend=lambda x : self.item(x,open=FALSE))

	def redisplay(self, roots : T.List[BRecord], tree : T.Dict[BRecord,T.List[BRecord]]):
		def insert_childs(parent : BRecord,elt : BRecord):
			self.insert(self._elt_id(parent) if parent is not None else "","end",self._elt_id(elt), text=elt.code, values=(elt.name, elt.descr if elt.descr is not None else ""))
			for child in tree[elt]:
				insert_childs(elt,child)

		self.recurse_delete()
		for record in roots :
			insert_childs(None, record)

		self.expand_all()


