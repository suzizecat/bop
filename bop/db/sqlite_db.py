import sqlite3
import os
import typing as T

from bop.db.data import Requirement
from bop.db.data import Product
from bop.db.data import Constraint


class DB:
	def __init__(self, path = ":memory:"):
		self.path = path
		self._db = sqlite3.connect(self.path)
		self._db.execute("PRAGMA FOREIGN_KEYS=ON;")

		self._cur : sqlite3.Cursor = self._db.cursor()

		"""Requirements by SQL id"""
		self._requirements : T.Dict[int,Requirement] = dict()

		"""Products by SQL id"""
		self._products: T.Dict[int, Product] = dict()

		"""Constraints by SQL id"""
		self._constraints: T.Dict[int, Constraint] = dict()

		self.create()

	def __del__(self):
		self._db.close()

	def __enter__(self):
		return self._cur

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None :
			self._db.commit()
		else :
			self._db.rollback()

	@property
	def name(self):
		return os.path.basename(self.path)

	def create(self):
		script_path = os.path.dirname(__file__) + "/create.sql"
		with self as sql:
			with open(script_path, "r") as script:
				sql.executescript(script.read())

	def read_db(self):
		self.read_requirements()
		self.read_products()
		self.read_constraints()

		self.read_product_constraints_bindings()

	def save_db(self):
		self.save_requirements()
		self.save_products()
		self.save_constraints()

		self.save_product_constraints_bindings()

	def read_requirements(self):
		self.clear_requirements()
		self.populate_requirements()
		self.resolve_requirements()
		self.validate_requirements()

	def read_products(self):
		self.clear_products()
		self.populate_products()
		self.resolve_products()
		self.validate_products()

	def read_constraints(self):
		self.clear_constraints()
		self.populate_constraints()
		self.validate_constraints()

	def add_element(self,elt, ignore_duplicate = False):
		if isinstance(elt,Requirement) :
			self.add_requirement(elt,ignore_duplicate)
		elif isinstance(elt,Product) :
			self.add_product(elt, ignore_duplicate)
		elif isinstance(elt, Constraint) :
			self.add_constraint(elt, ignore_duplicate)
		else :
			TypeError(f"Invalid element type {type(elt).__name__}")

	### Requirements

	def clear_requirements(self):
		self._requirements.clear()

	def validate_requirements(self):
		for req in self._requirements.values() :
			req.validate()

	def populate_requirements(self):
		with self as sql:
			results = sql.execute("SELECT * FROM t_requirement")
			for row in results:
				self.add_requirement(Requirement.from_sql_row(row))

	def resolve_requirements(self):
		for req in self._requirements.values() :
			if not req.resolved :
				req.parent = self._requirements[req._parent_id]

	def add_requirement(self,req : Requirement, ignore_duplicate = False):
		if req.id in self._requirements :
			raise KeyError(f"Cannot override requirement with same ID {req.id}")
		else :
			if req.id is None :
				with self as sql :
					res = sql.execute("SELECT id FROM t_requirement WHERE code = ?", (req.code,)).fetchone()
					if res is not None :
						if ignore_duplicate :
							return
						else :
							raise KeyError(f"The code {req.code} already exists in the database")

					result = sql.execute("INSERT INTO t_requirement(code, name, descr, parent) VALUES (:code, :name, :descr, :parent)",
						req.to_sql_dict())
					req._id = result.lastrowid
					for child in req._children :
						child._parent_id = req.id
			self._requirements[req.id] = req

	def remove_requirement(self,req : T.Union[Requirement,str,int]):
		if isinstance(req,str):
			req = self.get_requirement_by_code(req)
			self.remove_requirement(req.id)
		elif isinstance(req,Requirement) :
			if req.id is not None :
				self.remove_requirement(req.id)
			else :
				self.remove_requirement(req.code)
		elif isinstance(req,int) :
			req = self._requirements[req]
			with self as sql :
				sql.execute("DELETE FROM t_requirement WHERE id=?",(req.id,))
				req.detatch_from_parent()
				self._requirements.pop(req.id)
		else :
			raise KeyError(f"Trying to remove an invalid requirement {req!r} not found.")


	def save_requirements(self):
		to_update = list()

		for req in self._requirements.values() :
				to_update.append(req.to_sql_dict())

		with self as sql :
			sql.executemany("UPDATE t_requirement SET code=:code, name=:name, descr=:descr, parent=:parent WHERE id=:id",to_update)

		self.validate_requirements()

	def get_requirement_by_code(self,code) -> Requirement:
		for req in self._requirements.values() :
			if req.code == code :
				return req
		raise KeyError(f"No requirement found with code {code}")

	def get_root_requirements(self) -> T.List[Requirement]:
		ret = list()
		for req in self._requirements.values() :
			if req.parent_id is None :
				ret.append(req)
		return ret

	### Products

	def clear_products(self):
		self._products.clear()

	def validate_products(self):
		for req in self._products.values() :
			req.validate()

	def populate_products(self):
		with self as sql:
			results = sql.execute("SELECT * FROM t_product")
			for row in results:
				self.add_product(Product.from_sql_row(row))

	def resolve_products(self):
		for req in self._products.values() :
			if not req.resolved :
				req.parent = self._products[req._parent_id]

	def add_product(self, prod : Product, ignore_duplicate = False):
		if prod.id in self._products :
			raise KeyError(f"Cannot override product with same ID {prod.id}")
		else :
			if prod.id is None :
				with self as sql :
					res = sql.execute("SELECT id FROM t_product WHERE code = ?", (prod.code,)).fetchone()
					if res is not None :
						if ignore_duplicate :
							return
						else :
							raise KeyError(f"The code {prod.code} already exists in the database")

					result = sql.execute("INSERT INTO t_product(code, name, descr, parent) VALUES (:code, :name, :descr, :parent)",
										 prod.to_sql_dict())
					prod._id = result.lastrowid
					for child in prod._children :
						child._parent_id = prod.id
			self._products[prod.id] = prod

	def remove_product(self, prod : T.Union[Product, str, int]):
		if isinstance(prod, str):
			prod = self.get_product_by_code(prod)
			self.remove_product(prod.id)
		elif isinstance(prod, Product) :
			if prod.id is not None :
				self.remove_product(prod.id)
			else :
				self.remove_product(prod.code)
		elif isinstance(prod, int) :
			prod = self._products[prod]
			with self as sql :
				sql.execute("DELETE FROM t_product WHERE id=?", (prod.id,))
				prod.detatch_from_parent()
				self._products.pop(prod.id)
		else :
			raise TypeError(f"Try to remove an invalid element")

	def save_products(self):
		to_update = list()

		for req in self._products.values() :
				to_update.append(req.to_sql_dict())

		with self as sql :
			sql.executemany("UPDATE t_product SET code=:code, name=:name, descr=:descr, parent=:parent WHERE id=:id",to_update)

		self.validate_products()

	def get_product_by_code(self, code) -> Product:
			for prod in self._products.values():
				if prod.code == code:
					return prod
			raise KeyError(f"No product found with code {code}")

	def get_root_products(self) -> T.List[Product]:
			ret = list()
			for prod in self._products.values():
				if prod.parent_id is None:
					ret.append(prod)
			return ret

	### Constraints

	def clear_constraints(self):
		self._constraints.clear()

	def validate_constraints(self):
		for req in self._constraints.values() :
			req.validate()

	def populate_constraints(self):
		with self as sql:
			results = sql.execute("SELECT * FROM t_constraint")
			for row in results:
				self.add_constraint(Constraint.from_sql_row(row))

	def add_constraint(self, constr : Constraint, ignore_duplicate = False):
		if constr.id in self._constraints :
			raise KeyError(f"Cannot override constraint with same ID {constr.id}")
		else :
			if constr.id is None :
				with self as sql :
					result = sql.execute("INSERT INTO t_constraint(code, name, descr) VALUES (:code, :name, :descr)",
										 constr.to_sql_dict())
					constr._id = result.lastrowid
			self._constraints[constr.id] = constr

	def save_constraints(self):
		to_update = list()

		for req in self._constraints.values() :
				to_update.append(req.to_sql_dict())

		with self as sql :
			sql.executemany("UPDATE t_constraint SET code=:code, name=:name, descr=:descr WHERE id=:id",to_update)

		self.validate_constraints()

	def read_product_constraints_bindings(self):
		with self as sql:
			results = sql.execute("SELECT * FROM t_cstr_prod")
			for row in results:
				self._products[row[1]].add_constraint(self._constraints[row[2]])

	def save_product_constraints_bindings(self):
		to_create = list()
		for prod in self._products.values():
			to_create.extend(prod.to_sql_constr_bind_dict())

		with self as sql :
			# Empty table and fill again
			sql.execute("DELETE FROM t_cstr_prod")
			sql.executemany("INSERT INTO t_cstr_prod(id_prod, id_cstr) VALUES (:id_prod, :id_cstr)", to_create)


if __name__ == "__main__" :
	if os.path.exists("test.db") :
		db = DB("test.db")
		print("Read existing DB")
		db.read_db()
	else :
		db = DB("test.db")
		db.create()

		r1 = Requirement("REQ-100")
		r2 = Requirement("REQ-200")
		r11 = Requirement("REQ-110")

		r1.add_child(r11)

		db.add_requirement(r1)
		db.add_requirement(r2)
		db.add_requirement(r11)

		p1 = Product("PROD-100")
		p2 = Product("PROD-200")
		p21 = Product("PROD-210")

		db.add_product(p1)
		db.add_product(p2)
		db.add_product(p21)

		c1 = Constraint("CSTR-1")
		c2 = Constraint("CSTR-2")

		db.add_constraint(c1)
		db.add_constraint(c2)

		p1.add_constraint(c1)
		p1.add_constraint(c2)
		p21.add_constraint(c1)

		db.save_db()

	print("Done")