import typing as T


class BaseIdentifiedRecord:
	def __init__(self, code : T.Optional[str] = None , name : T.Optional[str] = None, descr : T.Optional[str] = None ):
		self._id: T.Union[int, None] = None
		self._code = code
		self._name = name
		self._descr = descr

		self._updated = True


	def validate(self):
		self._updated = False

	def invalidate(self):
		self._updated = True

	@property
	def id(self) -> int:
		return self._id

	@property
	def code(self) -> str :
		return self._code

	@code.setter
	def code(self, new) -> None:
		if new != self._code :
			self.invalidate()
			self._code = new

	@property
	def name(self) -> str :
		return self._name

	@name.setter
	def name(self, new) -> None:
		if new != self._name :
			self.invalidate()
			self._name = new

	@property
	def descr(self) -> str :
		return self._descr

	@descr.setter
	def descr(self, new) -> None:
		if new != self._descr :
			self.invalidate()
			self._descr = new


#
		# self._code : T.Union[str,None] = code
		# self._name : T.Union[str,None] = name
		# self._descr : T.Union[str,None] = descr


class BaseIdentifiedHierarchicalRecord(BaseIdentifiedRecord):
	def __init__(self, code : T.Optional[str] = None , name : T.Optional[str] = None, descr : T.Optional[str] = None ):
		super().__init__(code,name,descr)

		self._parent_id : T.Union[int,None] = None
		self._parent : T.Union[BaseIdentifiedHierarchicalRecord, None] = None
		self._children : T.List[BaseIdentifiedHierarchicalRecord] = list()

		self.invalidate()

	@property
	def resolved(self):
		return (self._parent_id is None and self._parent is None) \
			   or (self._parent is not None and self._parent.id == self._parent_id)

	@property
	def parent(self) -> "BaseIdentifiedHierarchicalRecord":
		return self._parent

	@parent.setter
	def parent(self, new) -> None:
		if new is None or isinstance(new,int) :
			if new is not None and new == self._id :
				raise ValueError(f"Impossible to self-affect as a parent.")
			if new != self._parent_id :
				self.detatch_from_parent()
				self._parent_id = new
				self._parent = None
		elif isinstance(new,type(self)) :
			if new is self :
				raise ValueError(f"Impossible to self-affect as a parent.")
			if new.lookup_in_parents(self,new) :
				raise ValueError(f"Setting {new.code} as parent of {self.code} would produce a loop.")
			if self._parent is not new :
				self.detatch_from_parent()
				new.add_child(self)
		else:
			raise TypeError(f"Invalid parent type '{type(new)!s}'")

	def lookup_in_parents(self,elt : "BaseIdentifiedHierarchicalRecord", start = None) :
		if self.parent is None or self.parent is start:
			return False
		elif self.parent is elt :
			return True
		else :
			return self.parent.lookup_in_parents(elt, start)

	@property
	def parent_id(self) -> T.Union[None, int]:
		return self._parent_id

	def add_child(self, child : "BaseIdentifiedHierarchicalRecord"):
		if child not in self._children :
			self.invalidate()
			self._children.append(child)

			if child.parent is not self :
				child._parent = self
				child._parent_id = self.id
				child.invalidate()

	def remove_child(self, child : "BaseIdentifiedHierarchicalRecord"):
		if child in self._children :
			self.invalidate()
			self._children.remove(child)

			child.detatch_from_parent()

	def detatch_from_parent(self):
		if self._parent is not None and self._parent_id is not None:
			self.invalidate()
			old_parent = self._parent
			self._parent = None
			self._parent_id = None

			old_parent.remove_child(self)

	def generate_child_code(self) -> str:
		new_code = ""
		new_code_base = self.code
		new_code_base += "." if new_code_base[-1].isdigit() else "-"
		code_number = len(self._children)

		valid = False
		while not valid:
			new_code = new_code_base + str(code_number)
			for child in self._children:
				if child.code == new_code:
					code_number += 1
					break
			else:
				valid = True
		return new_code