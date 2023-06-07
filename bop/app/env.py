from bop.db import DB
class Singleton(type):
	__instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in Singleton.__instances:
			Singleton.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return Singleton.__instances[cls]


class AppEnv(metaclass=Singleton) :
	def __init__(self):
		self.db : DB = None