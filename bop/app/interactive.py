import argparse
import cmd2
from cmd2 import CommandSet, with_argparser, with_category, with_default_category

# Required to register the apps
from .edit import AppRequirement
from .edit import AppProduct
from .edit import AppConstraint

from bop.gui.window import BopMainWindow
from .env import AppEnv

class Interactive(cmd2.Cmd):
	def __init__(self, *args, **kwargs):
		# gotta have this or neither the plugin or cmd2 will initialize
		super().__init__(*args, allow_cli_args=False, auto_load_commands=True,
						 persistent_history_file="~/.bop.history",persistent_history_length=100, **kwargs)
		self.prompt = "Bop>"

		self.intro = f"Welcome to the Build Objects Properly (BOP) tool.\n"

	base_parser = cmd2.Cmd2ArgumentParser()
	base_subparsers = base_parser.add_subparsers(title='action', help='available actions')

	@with_argparser(base_parser)
	def do_requirement(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("requirement",ns)

	prod_parser = cmd2.Cmd2ArgumentParser()
	prod_subparser = prod_parser.add_subparsers(title='action', help='available actions')

	@with_argparser(prod_parser)
	def do_product(self, ns: argparse.Namespace):
		"""Manage products."""
		self._default_subcommand_stub("product",ns)


	constr_parser = cmd2.Cmd2ArgumentParser()
	constr_subparser = constr_parser.add_subparsers(title='action', help='available actions')

	@with_argparser(constr_parser)
	def do_constraint(self, ns: argparse.Namespace):
		"""Manage products."""
		self._default_subcommand_stub("constraint",ns)


	def do_gui(self,_):
		"""Start the GUI"""
		root = BopMainWindow()
		self.poutput("Starting BOP GUI.")
		root.mainloop()

	def update_prompt(self):
		self.prompt = f"Bop {AppEnv().db.name}> "
		self.intro = f"Welcome to the Build Objects Properly (BOP) tool.\n" \
					 f"Database is {AppEnv().db.name}"

	def _default_subcommand_stub(self, command : str, ns : argparse.Namespace):
		handler = ns.cmd2_handler.get()
		if handler is not None:
			# Call whatever subcommand function was selected
			handler(ns)
		else:
			# No subcommand was provided, so call help
			self.poutput('This command does nothing without sub-parsers registered')
			self.do_help(command)