import cmd2
import os

from bop.app import AppEnv
from bop.db.data import Maturity


@cmd2.with_default_category("Maturity levels")
class AppMaturity(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	_addparser = cmd2.Cmd2ArgumentParser()

	_addparser.add_argument("code", type=str, help="Name for the maturity level")
	_addparser.add_argument("-f","--force", action="store_true", help="Silently fail if duplicate exists")
	_addparser.add_argument("level",type=int, help="Maturity integer level. Higher is more mature")

	@cmd2.as_subcommand_to("add", "maturity",_addparser, help="Add a maturity level")
	def maturity_add(self,args):
		mat = Maturity(args.code,  args.level)

		AppEnv().db.add_maturity(mat, ignore_duplicate=args.force)
		AppEnv().cache_maturity_codes(mat.code)

		self._cmd.pfeedback(f"Adding a maturity level to {AppEnv().db.path} with the code {mat.code} and the value {mat.level}")

	_list_parser = cmd2.Cmd2ArgumentParser()
	_list_parser.add_argument("--output","-o", default=None, type=str, help="Output in script format")
	@cmd2.as_subcommand_to("list", "maturity",  _list_parser, help="List all ergistered maturity levels")
	def maturity_list(self,args):
		self._print_str = ""
		self._output_str = ""

		base = AppEnv().db._maturity.values()

		if not args.one_per_line :
			self._cmd.poutput(f"Project : {AppEnv().db.path}")
		for mat_level in sorted(base, key=lambda x: x.level):
				self.print_level(mat_level)

		self._cmd.poutput(self._print_str)

		if args.output is not None:
			self._cmd.pfeedback(f"Dumping in {os.path.abspath(args.output)}")
			with open(args.output, "w") as f:
				f.write(self._output_str)

	def print_level(self, elt: Maturity, level=0):
		self._output_str += f'add maturity "{elt.code}" "{elt.level}"'
		self._output_str += "\n"

		self._print_str += f"{elt.level:4d} : {elt.code}\n"


	# for sreq in sorted(constraint._children, key=lambda x: x.code):
	# 	self.print_level(sreq, level + 1)

	_rm_parser = cmd2.Cmd2ArgumentParser()
	_rm_parser.add_argument("code",type=str, help="Maturity code to handle", choices=AppEnv().maturity_codes)
	@cmd2.as_subcommand_to("remove", "maturity", _rm_parser, help="Remove a maturity level")
	def maturity_rm(self,args):
		AppEnv().db.remove_constraint(args.code)
		AppEnv().uncache_constraint_codes(args.code)
		self._cmd.pfeedback(f"Removing constraint from {AppEnv().db.name} with the code {args.code}")

	_update_parser = cmd2.Cmd2ArgumentParser()

	_update_parser.add_argument("code", type=str, help="Maturity code to use", choices=AppEnv().maturity_codes)
	_update_parser.add_argument("-c", "--new-code", type=str, default=None, help="New maturity code")
	_update_parser.add_argument("-l", "--level", type=int, default=None, help="New maturity level value")
	@cmd2.as_subcommand_to("update", "maturity", _update_parser, help="Edit a maturity level")
	def maturity_move(self, args):
		mat = AppEnv().db.get_maturity_by_code(args.code)
		if args.new_code is not None:
			AppEnv().uncache_maturity_codes(mat.code)
			mat.code = args.new_code
			AppEnv().cache_maturity_codes(mat.code)
		if args.level is not None:
			mat.level = args.level

		self._cmd.pfeedback(f"Edition of the maturity level of {AppEnv().db.name} with the code {args.code} ")