from .base_identified_record import BaseIdentifiedRecord


class Constraint(BaseIdentifiedRecord):
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

		return ret

	def __init__(self, code = None, name = None, descr = None):
		super().__init__(code,name,descr)

		self._products = list()
		self._requirements = list()

	def to_sql_dict(self):
		return {"id" : self.id,
				"code" :self.code,
				"name" :self.name,
				"descr":self.descr}

	def unbind_all(self):
		self.unbind_all_products()
		self.unbind_all_requirements()

	def bind_to_product(self, prod):
		if prod not in self._products :
			self._products.append(prod)
			prod.bind_to_constraint(self)

	def unbind_product(self,prod):
		if prod in self._products :
			self._products.remove(prod)
			prod.unbind_constraint(self)

	def unbind_all_products(self):
		while len(self._products) > 0 :
			prod = self._products.pop()
			prod.unbind_constraint(self)

	def bind_to_requirement(self, req):
		if req not in self._requirements :
			self._requirements.append(req)
			req.bind_to_constraint(self)

	def unbind_requirement(self, req):
		if req in self._requirements :
			self._requirements.remove(req)
			req.unbind_constraint(self)

	def unbind_all_requirements(self):
		while len(self._requirements) > 0 :
			req = self._requirements.pop()
			req.unbind_constraint(self)

	@property
	def impact_childs(self):
		return self._products