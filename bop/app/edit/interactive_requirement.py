import cmd2

from bop.app import AppEnv
from bop.db.data import Requirement


@cmd2.with_default_category("Requirements")
class AppRequirement(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	addparser = cmd2.Cmd2ArgumentParser()

	addparser.add_argument("code", type=str, help="Requirement code to use")
	addparser.add_argument("-n", "--name", type=str, help="Human readable name")
	addparser.add_argument("-d", "--description", type=str, help="Long description")
	addparser.add_argument("-p", "--parent", type=str, default=None, help="Code of the parent")
	addparser.add_argument("-f", "--force", action="store_true",
							 help="Fail silently if the requirement already exists")

	@cmd2.as_subcommand_to("requirement","add",addparser, help="Add a requirement")
	def requirement_add(self,args):
		code = args.code
		if args.parent is not None:
			parent = AppEnv().db.get_requirement_by_code(args.parent)
			if code.strip() == "*":
				code = parent.generate_child_code()
		else:
			parent = None
			if code.strip() == "*":
				raise ValueError("Impossible to use the * placeholder without a proper parent")

		req = Requirement(code, args.name, args.description)
		AppEnv().db.add_requirement(req, ignore_duplicate=args.force)

		req.parent = parent

		self._cmd.pfeedback(f"Adding a requirement to {AppEnv().db.path} with the code {req.code} and the name {args.name}")

	_list_parser = cmd2.Cmd2ArgumentParser()
	_list_parser.add_argument("--output","-o", default=None, type=str, help="Output in script format")
	@cmd2.as_subcommand_to("requirement", "list", _list_parser, help="List all requirement")
	def requirement_list(self,args):
		self._print_str = ""
		self._output_str = ""

		base = AppEnv().db.get_root_requirements()

		self._cmd.poutput(f"Project : {AppEnv().db.path}")
		for req in sorted(base,key=lambda x : x.code) :
			self.print_level(req)

		self._cmd.poutput(self._print_str)
		if args.output is not None :
			print(f"Dumping in {os.path.abspath(args.output)}")
			with open(args.output,"w") as f :
				f.write(self._output_str)

	_rm_parser = cmd2.Cmd2ArgumentParser()
	_rm_parser.add_argument("code",type=str, help="Requirement code to use")
	@cmd2.as_subcommand_to("requirement", "rm", _rm_parser, help="Remove a requirement")
	def requirement_rm(self,args):
		AppEnv().db.remove_requirement(args.code)
		self._cmd.pfeedback(f"Removing requirement from {AppEnv().db.name} with the code {args.code}")

	@cmd2.as_subcommand_to("requirement", "move", addparser, help="Edit a requirement")
	def requirement_move(self, args):
		req = AppEnv().db.get_requirement_by_code(args.code)
		if args.new_code is not None:
			req.code = args.new_code
		if args.name is not None:
			req.name = args.name if args.name.strip() != "" else None
		if args.description is not None:
			req.descr = args.description if args.description.strip() != "" else None
		if args.parent is not None:
			req.parent = AppEnv().db.get_requirement_by_code(args.parent) if args.parent.strip() != "" else None

		self._cmd.pfeedback(f"I'm editing the requirement of {AppEnv().db.name} with the code {args.code} and the name {args.name}")

	def print_level(self,req : Requirement, level = 0):
		self._output_str += f'requirement add "{req.code}" -f'
		if req.name is not None : self._output_str += f' -n "{req.name}"'
		if req.parent is not None : self._output_str += f' -p "{req.parent.code}"'
		if req.descr is not None : self._output_str += f' -d "{req.descr}"'
		self._output_str += "\n"

		descr = "" if req.descr is None else req.descr
		qual_name = f"{req.code} : {req.name}"
		self._print_str += f"{'':>{2*level:d}s}- {qual_name:.<{50-2*level:d}s} {descr}\n"

		for sreq in sorted(req._children,key= lambda x : x.code) :
			self.print_level(sreq,level + 1)
