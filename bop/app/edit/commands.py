import argparse
import cmd2
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from bop.app import AppEnv
# Required to register the apps
# from .edit import AppRequirement
# from .edit import AppProduct
# from .edit import AppConstraint


def _base_subcommand_parser():
	ret = cmd2.Cmd2ArgumentParser()
	ret.add_subparsers(title='action', help='available actions')

	return ret


class BaseBopCommandSet(CommandSet) :
	def __init__(self):
		super().__init__()

	def _default_subcommand_stub(self, command : str, ns : argparse.Namespace):
		handler = ns.cmd2_handler.get()
		if handler is not None:
			# Call whatever subcommand function was selected
			handler(ns)
		else:
			# No subcommand was provided, so call help
			self._cmd.poutput('This command does nothing without sub-parsers registered')
			self._cmd.do_help(command)



@with_default_category("Database edition")
class EditCommands(BaseBopCommandSet) :
	def __init__(self):
		super().__init__()

	@with_argparser(_base_subcommand_parser())
	def do_add(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("add",ns)

	@with_argparser(_base_subcommand_parser())
	def do_update(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("update",ns)

	@with_argparser(_base_subcommand_parser())
	def do_remove(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("remove", ns)

	@with_argparser(_base_subcommand_parser())
	def do_bind(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("bind", ns)

	@with_argparser(_base_subcommand_parser())
	def do_unbind(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("unbind", ns)

	@with_argparser(_base_subcommand_parser())
	def do_list(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("list", ns)

@with_default_category("Database Analysis")
class AnalyzeCommands(BaseBopCommandSet) :
	def __init__(self):
		super().__init__()

	@with_argparser(_base_subcommand_parser())
	def do_analyze(self, ns: argparse.Namespace):
		"""Manage requirements."""
		self._default_subcommand_stub("analyze",ns)