import typing as T

from .base_identified_record import BaseIdentifiedHierarchicalRecord
from .constraint import Constraint
from .maturity_code import Maturity

class Requirement(BaseIdentifiedHierarchicalRecord):
	@classmethod
	def from_sql_row(cls, row):
		"""
		Map the table structure to the requirement internal fields.
		:return: An initialized field
		"""
		ret = cls()
		ret._id = row[0]
		ret.code = row[1]
		ret.name = row[2]
		ret.descr = row[3]
		ret._parent_id = row[4]
		# ret.maturity = row[5]

		return ret

	def __init__(self, code = None, name = None, descr = None):
		super().__init__(code,name,descr)

		self.constraints : T.List[Constraint] = list()
		self.maturity : Maturity = None

	def to_sql_dict(self):
		return {"id" : self.id,
				"code" :self.code,
				"name" :self.name,
				"descr":self.descr,
				"parent" : self._parent_id,
				"maturity" : self.maturity._id if self.maturity is not None else None }

	def to_sql_constr_bind_dict(self):
		ret = list()
		for c in self.constraints :
			ret.append({"id_cstr" : c.id, "id_req" : self.id})

		return ret

	def bind_to_constraint(self,constr : Constraint):
		if constr not in self.constraints :
			self.constraints.append(constr)
			constr.bind_to_requirement(self)

	def unbind_constraint(self,constr : Constraint):
		if constr in self.constraints :
			self.constraints.remove(constr)
			constr.unbind_requirement(self)

	def set_maturity(self,mat : Maturity):
		if self.maturity is not mat :
			self.maturity = mat
			self.invalidate()

	def unset_maturity(self,mat : Maturity = None):
		if mat is None or self.maturity is mat :
			self.set_maturity(None)

	@property
	def impact_childs(self) -> T.Union[None, T.List["BaseIdentifiedRecord"]]:
		return self.constraints

	@property
	def mat_level(self):
		return None if self.maturity is None else int(self.maturity)

