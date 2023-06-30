
class Maturity():
	@classmethod
	def from_sql_row(cls, row):
		"""
		Map the table structure to the requirement internal fields.
		:return: An initialized field
		"""
		ret = cls()
		ret._id = row[0]
		ret.level = int(row[1])
		ret.code = row[2]

		return ret

	def __init__(self, code = None, level = None):
		self._id = None
		self.level = int(level) if level is not None else None
		self.code = code

	def to_sql_dict(self):
		return {"level" : self.level,
				"code" :self.code,
				"id":self._id}

	def __index__(self):
		return self.level

	def __str__(self):
		return self.code
