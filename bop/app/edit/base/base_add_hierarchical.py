import argparse
from bop.app import AppEnv
from bop.db.data.base_identified_record import BaseIdentifiedHierarchicalRecord


class BaseAddHierarchical:
	def __init__(self, argparser : argparse.ArgumentParser, element_type = BaseIdentifiedHierarchicalRecord ):
		self.parser = argparser
		self.element_type = element_type

		self.parser.set_defaults(func=self.run_from_args)

		self.parser.add_argument("code",type=str, help="Code to use")
		self.parser.add_argument("-n", "--name", type=str, help="Human readable name")
		self.parser.add_argument("-d", "--description", type=str, help="Long description")
		self.parser.add_argument("-p", "--parent", type=str,default = None, help="Code of the parent")
		self.parser.add_argument("-f", "--force", action="store_true", help="Fail silently if the element already exists")

	def run_from_args(self,args):
		code = args.code
		if args.parent is not None :
			parent = AppEnv().db.get_requirement_by_code(args.parent)
			if code.strip() == "*" :
				code = parent.generate_child_code()
		else :
			parent = None
			if code.strip() == "*":
				raise ValueError("Impossible to use the * placeholder without a proper parent")

		req = self.element_type(code, args.name, args.description)
		AppEnv().db.add_requirement(req,ignore_duplicate=args.force)

		req.parent = parent

		print(f"I'm adding a requirement to {AppEnv().db.path} with the code {req.code} and the name {args.name}")


