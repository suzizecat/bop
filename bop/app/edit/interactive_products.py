import cmd2
import os

from bop.app import AppEnv
from bop.db.data import Product

import argparse

@cmd2.with_default_category("Products")
class AppProduct(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	_add_parser = cmd2.Cmd2ArgumentParser()

	_add_parser.add_argument("code", type=str, help="Product code to use")
	_add_parser.add_argument("-n", "--name", type=str, help="Human readable name")
	_add_parser.add_argument("-d", "--description", type=str, help="Long description")
	_add_parser.add_argument("-p", "--parent", type=str, choices=AppEnv().product_codes, help="Code of the parent")
	_add_parser.add_argument("-f", "--force", action="store_true",
							 help="Fail silently if the product already exists")

	@cmd2.as_subcommand_to("add","product",_add_parser, help="Add a product")
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

		prod = Product(code, args.name, args.description)
		AppEnv().db.add_product(prod, ignore_duplicate=args.force)

		prod.parent = parent
		AppEnv().cache_product_codes(prod.code)
		self._cmd.pfeedback(f"Adding a product to {AppEnv().db.path} with the code {prod.code} and the name {args.name}")

	_list_parser = cmd2.Cmd2ArgumentParser()
	_list_parser.add_argument("--output","-o", default=None, type=str, help="Output in script format")
	@cmd2.as_subcommand_to( "list", "product", _list_parser, help="List all products")
	def product_list(self,args):
		self._print_str = ""
		self._output_str = ""

		base = AppEnv().db.get_root_products()

		if not args.one_per_line :
			self._cmd.poutput(f"Project : {AppEnv().db.path}")
		for prod in sorted(base, key=lambda x: x.code):
			self.print_level(prod,simple = args.one_per_line)

		self._cmd.poutput(self._print_str)

		if args.output is not None:
			self._cmd.pfeedback(f"Dumping in {os.path.abspath(args.output)}")
			with open(args.output, "w") as f:
				f.write(self._output_str)

	def print_level(self, prod: Product, level=0, simple = False):
		self._output_str += f'add product "{prod.code}" -f'
		if prod.name is not None: self._output_str += f' -n "{prod.name}"'
		if prod.parent is not None: self._output_str += f' -p "{prod.parent.code}"'
		if prod.descr is not None: self._output_str += f' -d "{prod.descr}"'
		self._output_str += "\n"

		if simple :
			self._print_str += f"{prod.code}\n"
		else :
			descr = "" if prod.descr is None else prod.descr
			qual_name = f"{prod.code} : {prod.name}"

			self._print_str += f"{'':>{2 * level:d}s}- {qual_name:.<{50 - 2 * level:d}s} {descr}\n"
			for constr in sorted(prod.constraints, key=lambda x: x.code) :
				self._print_str += f"{'':>{2 * (level+1):d}s}- Bound to {constr.code}\n"

		for sprod in sorted(prod._children, key=lambda x: x.code):
			self.print_level(sprod, level + 1)


	_rm_parser = cmd2.Cmd2ArgumentParser()
	_rm_parser.add_argument("code",type=str, help="Product code to use", choices=AppEnv().product_codes)
	@cmd2.as_subcommand_to("remove","product",  _rm_parser, help="Remove a product")
	def product_rm(self,args):
		AppEnv().db.remove_product(args.code)
		AppEnv().uncache_product_codes(args.code)
		self._cmd.pfeedback(f"Removing product from {AppEnv().db.name} with the code {args.code}")

	_constr_parser = cmd2.Cmd2ArgumentParser()
	_constr_parser.add_argument("constr", type=str, help="Constraint code to use", choices=AppEnv().constraint_codes )

	# def _default_subcommand_stub(self, command : str, ns : argparse.Namespace):
	# 	handler = ns.cmd2_handler.get()
	# 	if handler is not None:
	# 		# Call whatever subcommand function was selected
	# 		handler(ns)
	# 	else:
	# 		# No subcommand was provided, so call help
	# 		self.poutput('This command does nothing without sub-parsers registered')
	# 		self.do_help(command)


	_bind_parser = cmd2.Cmd2ArgumentParser()
	_bind_parser.add_argument("prod",type=str, help="Product code to bind", choices=AppEnv().product_codes)
	_bind_subparser = _bind_parser.add_subparsers(title="action")
	@cmd2.as_subcommand_to( "bind","product", _bind_parser, help="Bind a product")
	def _bind_placeholder(self, args):
		pass

	_unbind_parser = cmd2.Cmd2ArgumentParser()
	_unbind_parser.add_argument("prod", type=str, help="Product code to unbind", choices=AppEnv().product_codes)
	_unbind_subparser = _unbind_parser.add_subparsers(title="action")
	@cmd2.as_subcommand_to("unbind","product",  _unbind_parser, help="Unbind a product")
	def _unbind_placeholder(self, args):
		pass

	@cmd2.as_subcommand_to("bind product", "to-constraint", _constr_parser, help="Bind a product")
	def product_constraint(self,args):
		prod = AppEnv().db.get_product_by_code(args.prod)
		prod.bind_to_constraint(AppEnv().db.get_constraint_by_code(args.constr))

	@cmd2.as_subcommand_to("unbind product", "to-constraint", _constr_parser, help="Unbind a product")
	def product_unconstraint(self,args):
		prod = AppEnv().db.get_product_by_code(args.prod)
		prod.unbind_constraint(AppEnv().db.get_constraint_by_code(args.constr))

	_update_parser = cmd2.Cmd2ArgumentParser()

	_update_parser.add_argument("code", type=str, help="Product code to use", choices=AppEnv().product_codes)
	_update_parser.add_argument("-n", "--name", type=str, default=None, help="Human readable name")
	_update_parser.add_argument("-d", "--description", type=str,default=None, help="Long description")
	_update_parser.add_argument("-p", "--parent", type=str,default=None, choices=AppEnv().product_codes, help="Code of the parent")
	_update_parser.add_argument("-c", "--new-code", type=str, default=None, help="New requirement code")

	@cmd2.as_subcommand_to("update", "product",  _update_parser, help="Edit a product")
	def product_move(self, args):
		prod = AppEnv().db.get_product_by_code(args.code)
		if args.new_code is not None:
			AppEnv().uncache_product_codes(prod.code)
			prod.code = args.new_code
			AppEnv().cache_product_codes(prod.code)
		if args.name is not None:
			prod.name = args.name if args.name.strip() != "" else None
		if args.description is not None:
			prod.descr = args.description if args.description.strip() != "" else None
		if args.parent is not None:
			prod.parent = AppEnv().db.get_product_by_code(args.parent) if args.parent.strip() != "" else None

		self._cmd.pfeedback(f"Edition of the product of {AppEnv().db.name} with the code {args.code} and the name {args.name}")
