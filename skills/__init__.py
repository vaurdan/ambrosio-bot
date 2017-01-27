import logging
import re

logger = logging.getLogger(__name__)

class Skill:

	regex = ".*"

	ignore_case = True

	def __init__(self, bot):
		self.name = self.__class__.__name__
		self.bot = bot
		self.inputs = bot.get_inputs_by_skill(self.name)
		self.outputs = bot.get_outputs_by_skill(self.name)
		
		logger.info( "Initializing Skill %s with Inputs=%s and Outputs=%s" % (self.name, self.inputs, self.outputs) )
	
	def get_regex(self):
		flag = 0

		if self.ignore_case:
			flag |= re.IGNORECASE

		return re.compile( self.regex, flag)

	def test(self, string):
		'Returns true if the regex matches'
		return self.get_regex().match(string) is not None