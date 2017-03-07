# -*- coding: utf-8 -*-
import logging
import re

from outputs import TextMessage, ImageMessage
from config import config

logger = logging.getLogger(__name__)

class Skill:

	ignore_case = True

	def __init__(self, bot):
		self.name = self.__class__.__name__
		self.bot = bot
		self.io_manager = bot.io_manager
		self.io = self.io_manager.get_io_by_skill(self.name)
		self.args = self.setup_args()
		self.rules = {}
		#self.outputs = bot.get_outputs_by_skill(self.name)
		
		logger.info( "Initializing Skill %s with IO=%s" % (self.name, self.io) )
		self.setup_rules()

	def setup_rules(self):
		logger.warning("%s has no rules. Please implement the setup_rules method." % self.name)
		return False

	def add_rule( self, regex, callback, privileged = False, ignore_prefix = False ):
		args = {
			'privileged': privileged,
			'ignore_prefix': ignore_prefix,
		}
		logger.info("[ %s ] Registering rule %s" % (self.name, regex) )
		self.rules[ regex ] = ( callback, args )
		return True

	def setup_args(self):

		skills = config['skills']
		for skill in skills:
			if skill['skill'].lower() == self.name.lower():
				return skill['args'] if 'args' in skill else None

	def get_arg(self, key, default=None):
		try:
			return self.args[key]
		except Exception:
			if default is not None:
				return default
			raise Exception("Missing mandatory '%s' in %s config." % (key,self.__class__.__name__))

	def compile_regex(self, regex):
		flag = 0

		if self.ignore_case:
			flag |= re.IGNORECASE

		flag |= re.LOCALE
		flag |= re.UNICODE

		return re.compile( regex, flag)

	def run(self, message):
		"""
		Runs the algorithm for a given string

		:param message:
		:return:
		"""
		content_string = message.get_content()

		if config['ignore_utf8'] == 'yes' or config['ignore_utf8'] == True:
			content_string = content_string # todo: unidecode this

		for rule, rule_config in self.rules.iteritems():
			callback, rule_args = rule_config
			if config['ignore_utf8'] == 'yes' or config['ignore_utf8'] == True:
				rule = rule # todo: unidecode this

			# Append the prefix if it's set
			if not message.is_direct() and not rule_args['ignore_prefix']:
				rule = self.bot.regex_name.encode('utf-8') + rule
			else:
				rule = "(" + str(self.bot.regex_name.encode('utf-8')) + ")?" + rule

			regex = self.compile_regex( rule )

			if regex.match(content_string) is not None:
				message.regex = regex
				self._run_callback( callback, rule_args, message )
				message.did_run = True
				return True
		return False

	def _run_callback(self, callback, args, message):
		# Make sure user has permissions to run the skill
		if args['privileged'] and not self.check_permission(message):
			return

		callback(message)

	def check_permission(self, message, output=True):
		if message.user().is_privileged():
			return True

		if output:
			self.send_message( "Lamento senhor. Não tenho permissão para o ajudar...", message )

		return False

	def add_output(self, output_message):
		# Store the output in the correct queue
		try:
			# If it's default, simply add the output to the symmetrical output
			if output_message.is_default:
				self.io_manager.add_output( output_message.get_input_id(), output_message)
				return

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
		"""
		Alias of Skill.send_message

		:param text_message:
		:param original_message:
		:param reply:
		:param args:
		:return:
		"""
		self.send_message(text_message, original_message, reply, **args)

	def send_image(self, image_message, original_message, reply=True,  args = {}):

		# setup the args
		args['reply'] = reply

		message = ImageMessage( image_message, original_message, **args )
		self.add_output(message)