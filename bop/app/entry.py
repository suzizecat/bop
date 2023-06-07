import argparse
import os

import cmd2.exceptions

from .interactive import Interactive
from .env import AppEnv
from bop.db import DB

class BopEntry:
	def __init__(self):
		self.parser = argparse.ArgumentParser(add_help=False)
		self.parser.add_argument("--db", type=str, default="project.db" )

		self.session = Interactive()

	def start_app(self, argv = None):
		args, remaining = self.parser.parse_known_args(argv)
		self.set_env_from_args(args)

		if "interactive" in remaining or len(remaining) == 0:
			self.session.update_prompt()
			self.session.cmdloop()
		else :
			self.session.settables["quiet"].set_value(True)
			self.run_sub_apps(remaining)

		AppEnv().db.save_db()

	def set_env_from_args(self,args):
		AppEnv().db = DB(args.db)
		AppEnv().db.read_db()

	def run_sub_apps(self,args_list):
		# Everything else shall have been setup beforehand, so no need to re-specify top level args.

		if len(args_list) == 0 :
			args_list = ["help"]
		command = " ".join(args_list)
		print("Running command ", command)
		try :
			self.session.onecmd(command)
		except cmd2.exceptions.Cmd2ArgparseError :
			# Ignore argument parsing error raised as messages should have been appropriately been displayed anyway.
			# Allows a proper management of the --help flags
			pass


