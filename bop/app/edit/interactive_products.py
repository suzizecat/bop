import cmd2
import os

from bop.app import AppEnv
from bop.db.data import Product


@cmd2.with_default_category("Products")
class AppProduct(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	addparser = cmd2.Cmd2ArgumentParser()

	addparser.add_argument("code", type=str, help="Product code to use")
	addparser.add_argument("-n", "--name", type=str, help="Human readable name")
	addparser.add_argument("-d", "--description", type=str, help="Long description")
	addparser.add_argument("-p", "--parent", type=str, default=None, help="Code of the parent")
	addparser.add_argument("-f", "--force", action="store_true",
							 help="Fail silently if the product already exists")

	@cmd2.as_subcommand_to("product","add",addparser, help="Add a product")
	def product_add(self,args):
		code = args.code
		if args.parent is not None:
			parent = AppEnv().db.get_product_by_code(args.parent)
			if code.strip() == "*":
				code = parent.generate_child_code()
		else:
			parent = None
			if code.strip() == "*":
				raise ValueError("Impossible to use the * placeholder without a proper parent")

		req = Product(code, args.name, args.description)
		AppEnv().db.add_product(req, ignore_duplicate=args.force)

		req.parent = parent

		self._cmd.pfeedback(f"Adding a product to {AppEnv().db.path} with the code {req.code} and the name {args.name}")

	_list_parser = cmd2.Cmd2ArgumentParser()
	_list_parser.add_argument("--output","-o", default=None, type=str, help="Output in script format")
	@cmd2.as_subcommand_to("product", "list", _list_parser, help="List all products")
	def product_list(self,args):
		self._print_str = ""
		self._output_str = ""

		base = AppEnv().db.get_root_products()

		self._cmd.poutput(f"Project : {AppEnv().db.path}")
		for prod in sorted(base, key=lambda x: x.code):
			self.print_level(prod)

		self._cmd.poutput(self._print_str)
		if args.output is not None:
			print(f"Dumping in {os.path.abspath(args.output)}")
			with open(args.output, "w") as f:
				f.write(self._output_str)

	def print_level(self, prod: Product, level=0):
		self._output_str += f'product add "{prod.code}" -f'
		if prod.name is not None: self._output_str += f' -n "{prod.name}"'
		if prod.parent is not None: self._output_str += f' -p "{prod.parent.code}"'
		if prod.descr is not None: self._output_str += f' -d "{prod.descr}"'
		self._output_str += "\n"

		descr = "" if prod.descr is None else prod.descr
		qual_name = f"{prod.code} : {prod.name}"
		self._print_str += f"{'':>{2 * level:d}s}- {qual_name:.<{50 - 2 * level:d}s} {descr}\n"

		for sreq in sorted(prod._children, key=lambda x: x.code):
			self.print_level(sreq, level + 1)


	_rm_parser = cmd2.Cmd2ArgumentParser()
	_rm_parser.add_argument("code",type=str, help="Product code to use")
	@cmd2.as_subcommand_to("product", "rm", _rm_parser, help="Remove a product")
	def product_rm(self,args):
		AppEnv().db.remove_product(args.code)
		self._cmd.pfeedback(f"Removing product from {AppEnv().db.name} with the code {args.code}")

	@cmd2.as_subcommand_to("product", "move", addparser, help="Edit a product")
	def product_move(self, args):
		prod = AppEnv().db.get_product_by_code(args.code)
		if args.new_code is not None:
			prod.code = args.new_code
		if args.name is not None:
			prod.name = args.name if args.name.strip() != "" else None
		if args.description is not None:
			prod.descr = args.description if args.description.strip() != "" else None
		if args.parent is not None:
			prod.parent = AppEnv().db.get_product_by_code(args.parent) if args.parent.strip() != "" else None

		self._cmd.pfeedback(f"Edition of the product of {AppEnv().db.name} with the code {args.code} and the name {args.name}")