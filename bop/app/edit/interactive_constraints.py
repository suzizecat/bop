import cmd2
import os

from bop.app import AppEnv
from bop.db.data import Constraint


@cmd2.with_default_category("Constraints")
class AppConstraint(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	addparser = cmd2.Cmd2ArgumentParser()

	addparser.add_argument("code", type=str, help="Product code to use")
	addparser.add_argument("-n", "--name", type=str, help="Human readable name")
	addparser.add_argument("-d", "--description", type=str, help="Long description")
	addparser.add_argument("-f", "--force", action="store_true",
							 help="Fail silently if the product already exists")

	@cmd2.as_subcommand_to("add", "constraint",addparser, help="Add a constraint")
	def constraint_add(self,args):
		code = args.code
		constr = Constraint(code, args.name, args.description)
		AppEnv().db.add_constraint(constr, ignore_duplicate=args.force)
		AppEnv().cache_constraint_codes(constr.code)
		self._cmd.pfeedback(f"Adding a constraint to {AppEnv().db.path} with the code {constr.code} and the name {args.name}")

	_list_parser = cmd2.Cmd2ArgumentParser()
	_list_parser.add_argument("--output","-o", default=None, type=str, help="Output in script format")
	@cmd2.as_subcommand_to("list", "constraint",  _list_parser, help="List all products")
	def constraint_list(self,args):
		self._print_str = ""
		self._output_str = ""

		base = AppEnv().db._constraints.values()

		self._cmd.poutput(f"Project : {AppEnv().db.path}")
		for constraint in sorted(base, key=lambda x: x.code):
			self.print_level(constraint)

		self._cmd.poutput(self._print_str)
		if args.output is not None:
			print(f"Dumping in {os.path.abspath(args.output)}")
			with open(args.output, "w") as f:
				f.write(self._output_str)

	def print_level(self, constraint: Constraint, level=0):
		self._output_str += f'add constraint "{constraint.code}" -f'
		if constraint.name is not None: self._output_str += f' -n "{constraint.name}"'
		if constraint.descr is not None: self._output_str += f' -d "{constraint.descr}"'
		self._output_str += "\n"

		descr = "" if constraint.descr is None else constraint.descr
		qual_name = f"{constraint.code} : {constraint.name}"
		self._print_str += f"{'':>{2 * level:d}s}- {qual_name:.<{50 - 2 * level:d}s} {descr}\n"

		for req in constraint._requirements:
			self._output_str += f'bind constraint "{constraint.code}" to-requirement "{req.code}"\n'
			self._print_str += f"{'':>{2 * (level + 1):d}s}- Bound to requirement {req.code}\n"

		for prod in constraint._products :
			self._output_str += f'bind product "{prod.code}" to-constraint "{constraint.code}"\n'
			self._print_str += f"{'':>{2 * (level+1):d}s}- Impact product {prod.code}\n"


		# for sreq in sorted(constraint._children, key=lambda x: x.code):
		# 	self.print_level(sreq, level + 1)

	_rm_parser = cmd2.Cmd2ArgumentParser()
	_rm_parser.add_argument("code",type=str, help="Product code to use", choices=AppEnv().constraint_codes)
	@cmd2.as_subcommand_to("remove", "constraint", _rm_parser, help="Remove a constraint")
	def constraint_rm(self,args):
		AppEnv().db.remove_constraint(args.code)
		AppEnv().uncache_constraint_codes(args.code)
		self._cmd.pfeedback(f"Removing constraint from {AppEnv().db.name} with the code {args.code}")

	_updateparser = cmd2.Cmd2ArgumentParser()

	_updateparser.add_argument("code", type=str, help="Product code to use",choices=AppEnv().constraint_codes)
	_updateparser.add_argument("-n", "--name", type=str, help="Human readable name")
	_updateparser.add_argument("-d", "--description", type=str, help="Long description")
	_updateparser.add_argument("-f", "--force", action="store_true",
							 help="Fail silently if the product already exists")
	@cmd2.as_subcommand_to("update", "constraint", _updateparser, help="Edit a product")
	def constraint_move(self, args):
		constr = AppEnv().db.get_constraint_by_code(args.code)
		if args.new_code is not None:
			AppEnv().uncache_constraint_codes(constr.code)
			constr.code = args.new_code
			AppEnv().cache_constraint_codes(constr.code)
		if args.name is not None:
			constr.name = args.name if args.name.strip() != "" else None
		if args.description is not None:
			constr.descr = args.description if args.description.strip() != "" else None

		self._cmd.pfeedback(f"Edition of the constraint of {AppEnv().db.name} with the code {args.code} and the name {args.name}")


	_bind_parser = cmd2.Cmd2ArgumentParser()
	_bind_parser.add_argument("constraint",type=str, help="Constraint code to bind", choices=AppEnv().constraint_codes)
	_bind_subparser = _bind_parser.add_subparsers(title="action")
	@cmd2.as_subcommand_to( "bind","constraint", _bind_parser, help="Bind a constraint")
	def _bind_placeholder(self, args):
		pass

	_unbind_parser = cmd2.Cmd2ArgumentParser()
	_unbind_parser.add_argument("constraint", type=str, help="Constraint code to unbind", choices=AppEnv().constraint_codes)
	_unbind_subparser = _unbind_parser.add_subparsers(title="action")
	@cmd2.as_subcommand_to("unbind","constraint",  _unbind_parser, help="Unbind a constraint")
	def _unbind_placeholder(self, args):
		pass

	_requirement_parser = cmd2.Cmd2ArgumentParser()
	_requirement_parser.add_argument("requirement", type=str, help="Requirement code to use", choices=AppEnv().requirement_codes)

	@cmd2.as_subcommand_to("bind constraint", "to-requirement", _requirement_parser, help="Bind a constraint")
	def constraint_bind_to_req(self,args):
		req = AppEnv().db.get_requirement_by_code(args.requirement)
		req.bind_to_constraint(AppEnv().db.get_constraint_by_code(args.constraint))

	@cmd2.as_subcommand_to("unbind constraint", "to-requirement", _requirement_parser, help="Unbind a constraint")
	def constraint_unbind_to_req(self,args):
		req = AppEnv().db.get_requirement_by_code(args.requirement)
		req.unbind_constraint(AppEnv().db.get_constraint_by_code(args.constraint))