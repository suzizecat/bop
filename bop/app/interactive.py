import argparse
import cmd2
import typing as T
from cmd2 import CommandSet, with_argparser, with_category, with_default_category

# Required to register the apps
from .edit.commands import EditCommands
from .edit.interactive_requirement import AppRequirement
from .edit.interactive_products import AppProduct
from .edit.interactive_constraints import AppConstraint
from .edit.interactive_maturity import AppMaturity
from .analyze.app_analyze import AppAnalyze
# from .edit import AppProduct
# from .edit import AppConstraint

from bop.gui.window import BopMainWindow,BopMainWindowThread
from .env import AppEnv

from threading import Thread, Semaphore
from queue import Empty
from time import sleep


class Interactive(cmd2.Cmd):
	def __init__(self, *args, **kwargs):
		# gotta have this or neither the plugin or cmd2 will initialize
		super().__init__(*args, allow_cli_args=False, auto_load_commands=True,
						 persistent_history_file="~/.bop.history",persistent_history_length=100, **kwargs)
		self.prompt = "Bop>"

		self.intro = f"Welcome to the Build Objects Properly (BOP) tool.\n"
		self.gui_thread : BopMainWindowThread = None
		self.monitor_thread : BopMainWindowThread = None

		self.register_postloop_hook(self._ensure_gui_cleanup)
		self.register_precmd_hook(self._get_command_lock)
		self.register_cmdfinalization_hook(self._release_command_lock)

		self._cmd_lock = Semaphore()

	def _start_monitor_thread(self):
		def monitor():
			while True:
				sleep(0.1)
				with AppEnv().cmd_queue_lock :
					try :
						while True:
							elt = AppEnv().cmd_control_queue.get(block=False)
							if elt == "exit" :
								while not AppEnv().cmd_control_queue.empty() :
									AppEnv().cmd_control_queue.get_nowait()
								return
							print(elt)
							self.onecmd_plus_hooks(elt,add_to_history=False)
							print(self.prompt,end="")
					except Empty:
						pass

		if self.monitor_thread is None or not self.monitor_thread.is_alive() :
			self.monitor_thread = Thread(target=monitor)
			self.monitor_thread.start()

	def _get_command_lock(self, _ : cmd2.plugin.PrecommandData) -> cmd2.plugin.PrecommandData:
		self._cmd_lock.acquire()
		return _

	def _release_command_lock(self, _ : cmd2.plugin.CommandFinalizationData) -> cmd2.plugin.CommandFinalizationData:
		self._cmd_lock.release()
		return _

	def _ensure_gui_cleanup(self) -> None:
		if self.gui_thread is not None and self.gui_thread.is_alive():
			self.poutput("Cleanup the GUI")
			self.gui_thread.stop()
			self.gui_thread.join()

	# Add "aliases"
	do_exit = cmd2.Cmd.do_quit
	do_source = cmd2.Cmd.do__relative_run_script

	def do_gui(self,_):
		"""Start the GUI"""
		if self.gui_thread is not None and self.gui_thread.is_alive():
			self.poutput("Await for already opened window to be closed.")
			self.gui_thread.join()

		def gui_function() :
			root = BopMainWindow()
			root.mainloop()

		self.poutput("Starting BOP GUI.")
		self._start_monitor_thread()
		self.gui_thread = BopMainWindowThread()
		self.gui_thread.start()




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
