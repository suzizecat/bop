import argparse
import cmd2

def provide_base_subcommand_parser():
	ret = cmd2.Cmd2ArgumentParser()
	ret.add_subparsers(title='action', help='available actions')

	return ret