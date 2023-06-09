from queue import Queue
from threading import Semaphore


class Singleton(type):
	__instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in Singleton.__instances:
			Singleton.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return Singleton.__instances[cls]


class AppEnv(metaclass=Singleton):
	def __init__(self):
		from bop.db import DB
		from bop.db import Project

		self.db: DB = None
		self.prj: Project = None
		self.is_gui_up = False
		self.gui_queue_lock = Semaphore()
		self.cmd_queue_lock = Semaphore()
		self.gui_control_queue = Queue()
		self.cmd_control_queue = Queue()
		self.requirement_codes = list()
		self.product_codes = list()
		self.constraint_codes = list()
		self.maturity_codes = list()

	def refresh_caches(self):
		"""
		Force clear and refresh all caches.
		"""
		self.refresh_requirement_codes()
		self.refresh_product_codes()
		self.refresh_constraint_codes()
		self.refresh_maturity_codes()

	def refresh_requirement_codes(self):
		"""
		Clear the cache and refresh requirement codes.
		"""
		self.requirement_codes.clear()
		for req in self.db.requirement_codes:
			self.cache_requirement_codes(req)

	def cache_requirement_codes(self, code):
		self.requirement_codes.append(code)

	def uncache_requirement_codes(self, code):
		self.requirement_codes.remove(code)

	def refresh_product_codes(self):
		self.product_codes.clear()
		for req in self.db.product_codes:
			self.cache_product_codes(req)

	def cache_product_codes(self, code):
		self.product_codes.append(code)

	def uncache_product_codes(self, code):
		self.product_codes.remove(code)

	def refresh_constraint_codes(self):
		self.constraint_codes.clear()
		for req in self.db.constraint_codes:
			self.cache_constraint_codes(req)

	def cache_constraint_codes(self, code):
		self.constraint_codes.append(code)

	def uncache_constraint_codes(self, code):
		self.constraint_codes.remove(code)

	def refresh_maturity_codes(self):
		self.maturity_codes.clear()
		for mat in self.db.maturity_codes:
			self.cache_maturity_codes(mat)

	def cache_maturity_codes(self, code):
		self.maturity_codes.append(code)

	def uncache_maturity_codes(self, code):
		self.constraint_codes.remove(code)

	def gui_refresh(self):
		if self.is_gui_up:
			with self.gui_queue_lock:
				self.gui_control_queue.put_nowait("refresh")

