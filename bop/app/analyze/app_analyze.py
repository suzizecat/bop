import cmd2
import os

from bop.app import AppEnv
from bop.db.data.base_identified_record import BaseIdentifiedRecord
from bop.app.utils import provide_base_subcommand_parser

@cmd2.with_default_category("Analyze")
class AppAnalyze(cmd2.CommandSet):
	def __init__(self):
		super().__init__()

		self._print_str = ""
		self._output_str = ""

	@cmd2.as_subcommand_to("analyze", "impact", provide_base_subcommand_parser(), help="Add a constraint")
	def _analyze_impact_placeholder(self,_):
		pass

	_parser_analyze_impact_req = cmd2.Cmd2ArgumentParser()
	_parser_analyze_impact_req.add_argument("code", type=str, help="Item code to use", choices=AppEnv().requirement_codes)
	@cmd2.as_subcommand_to("analyze impact", "of-requirement", _parser_analyze_impact_req, help="Analyze impact of a requirement")
	def analyze_requirement_impact(self, args):
		def print_impact_level(self, elt : BaseIdentifiedRecord, level = 0) :
			space = "  "*level
			elt_type = type(elt).__name__

			if elt.impact_childs is not None and len(elt.impact_childs) > 0 :
				self._print_str += f"{space}- {elt_type} {elt.code} will impact:\n"
				for s_elt in elt.impact_childs :
					print_impact_level(self,s_elt,level + 1)

			else :
				self._print_str += f"{space}- {elt_type} {elt.code}\n"

		self._print_str = ""
		elt = AppEnv().db.get_requirement_by_code(args.code)
		print_impact_level(self,elt)

		self._cmd.poutput(f"Requirement change impact report for {elt.code}:")
		self._cmd.poutput(self._print_str)



