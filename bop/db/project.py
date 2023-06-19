import typing as T

from .sqlite_db import DB
from .data import *

class Project:
	"""
	This class provides high-level functions related to an open project
	"""
	def __init__(self, db : DB):
		self.db = db

	@staticmethod
	def _report_from_tree(root :BaseIdentifiedRecord, tree : T.Dict[BaseIdentifiedRecord, T.List[BaseIdentifiedRecord]]):
		def _line(elt : BaseIdentifiedRecord, level) :
			space = "  "* level
			identifier = f"{space}- {type(elt).__name__} {elt.code} : {elt.name}"
			return f"{identifier:.<50s} {elt.descr}\n"

		def _tree(root : BaseIdentifiedRecord, level = 0) :
			ret = ""
			ret += _line(root,level)
			for elt in tree[root] :
				ret += _tree(elt,level+1)
			return ret

		return _tree(root)

	def report_hierarchy(self, roots : T.Union[BaseIdentifiedHierarchicalRecord,T.Iterable[BaseIdentifiedHierarchicalRecord]], same_elements = False):
		def _gen_report(root : BaseIdentifiedHierarchicalRecord) :
			tree = self.get_hierarchy_tree(root)
			return self._report_from_tree(root,tree)

		if isinstance(roots,BaseIdentifiedHierarchicalRecord) :
			return _gen_report(roots)
		else :
			ret = ""
			for root in roots :
				ret += _gen_report(root)
			return ret

	def report_impact(self, roots : T.Union[BaseIdentifiedHierarchicalRecord,T.Iterable[BaseIdentifiedHierarchicalRecord]], same_elements = False):
		def _gen_report(root : BaseIdentifiedHierarchicalRecord) :
			tree = self.get_impact_tree(root)
			return self._report_from_tree(root,tree)

		if isinstance(roots,BaseIdentifiedHierarchicalRecord) :
			return _gen_report(roots)
		else :
			ret = ""
			for root in roots :
				ret += _gen_report(root)
			return ret

	def get_hierarchy_tree(self, root : BaseIdentifiedHierarchicalRecord) -> T.Dict[BaseIdentifiedRecord, T.List[BaseIdentifiedRecord]]:
		ret = {root:root.children}

		for child in root.children :
			ret.update(self.get_hierarchy_tree(child))

		return ret

	def get_impact_tree(self,root : BaseIdentifiedRecord) -> T.Dict[BaseIdentifiedRecord, T.List[BaseIdentifiedRecord]]:
		ret = {root:list()}

		if root.impact_childs is None :
			return ret
		else :
			ret[root] = root.impact_childs

		for elt in root.impact_childs :
			ret.update(self.get_impact_tree(elt))

		return ret
