import logging
import re

from outputs import TextMessage, ImageMessage

logger = logging.getLogger(__name__)

class Skill:

	regex = ".*"

	ignore_case = True

	def __init__(self, bot, args={}):
		self.name = self.__class__.__name__
		self.bot = bot
		self.io_manager = bot.io_manager
		self.io = self.io_manager.get_io_by_skill(self.name)
		self.args = {}
		#self.outputs = bot.get_outputs_by_skill(self.name)
		
		logger.info( "Initializing Skill %s with IO=%s" % (self.name, self.io) )
	
	def get_regex(self):
		flag = 0

		if self.ignore_case:
			flag |= re.IGNORECASE

		flag |= re.LOCALE
		flag |= re.UNICODE

		return re.compile( self.regex, flag)

	def test(self, string):
		'Returns true if the regex matches'
		return self.get_regex().match(string) is not None

	def run(self, message):
		'Runs the algoritmh for a given string'
		return "Not Implemented"

	def add_output(self, output_message):
		# Store the output in the correct queue
		try:
			# O add output tem que ser para todos os outputs
			for io in self.io:
				# If is a list, loop thru the list of outputs
				if isinstance(io['output'],list) and output_message.get_input_id() in io['input']:
					# Ok, got the correct input, loop the output and process it
					for output in io['output']:
						self.io_manager.add_output( output, output_message )
				elif output_message.get_input_id() == io['input']:
					self.io_manager.add_output( io['output'], output_message )
		except KeyError as e:
			logger.error("Couldn't send to %s output. Queue not found. Maybe the module doesn't exist?" % e.args[0])

	def send_message(self, text_message, original_message, reply=True, args = {}):
		# setup the args
		args['reply'] = reply

		message = TextMessage( text_message, original_message, **args )
		self.add_output(message)
	
	def send_text(self, text_message, original_message, reply=True,  args = {}):
		self.send_message(text_message, original_message, reply, **args)

	def send_image(self, image_message, original_message, reply=True,  args = {}):

		# setup the args
		args['reply'] = reply
		
		message = ImageMessage( image_message, original_message, **args )
		self.add_output(message)
	