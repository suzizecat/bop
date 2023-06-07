import argparse
import cmd2
from cmd2 import CommandSet, with_argparser, with_category, with_default_category

# Required to register the apps
from .edit.requirements import AppRequirement
from .edit.products import AppProduct

from bop.gui.window import BopMainWindow
from .env import AppEnv

class Interactive(cmd2.Cmd):
	def __init__(self, *args, **kwargs):
		# gotta have this or neither the plugin or cmd2 will initialize
		super().__init__(*args, allow_cli_args=False, auto_load_commands=True,
						 persistent_history_file="~/.bop.history",persistent_history_length=100, **kwargs)
		self.prompt = "Bop>"



	base_parser = cmd2.Cmd2ArgumentParser()
	base_subparsers = base_parser.add_subparsers(title='action', help='available actions')

	@with_argparser(base_parser)
	def do_requirement(self, ns: argparse.Namespace):
		"""Manage requirements."""
		handler = ns.cmd2_handler.get()
		if handler is not None:
			# Call whatever subcommand function was selected
			handler(ns)
		else:
			# No subcommand was provided, so call help
			self.poutput('This command does nothing without sub-parsers registered')
			self.do_help('requirement')

	prod_parser = cmd2.Cmd2ArgumentParser()
	prod_subparser = prod_parser.add_subparsers(title='action', help='available actions')

	@with_argparser(prod_parser)
	def do_product(self, ns: argparse.Namespace):
		"""Manage products."""
		handler = ns.cmd2_handler.get()
		if handler is not None:
			# Call whatever subcommand function was selected
			handler(ns)
		else:
			# No subcommand was provided, so call help
			self.poutput('This command does nothing without sub-parsers registered')
			self.do_help('product')

	def do_gui(self,_):
		"""Start the GUI"""
		root = BopMainWindow()
		self.poutput("Starting BOP GUI.")
		root.mainloop()

	def update_prompt(self):
		self.prompt = f"Bop {AppEnv().db.name}> "