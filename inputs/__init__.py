# -*- coding: utf-8 -*-
import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class InputFetcher:
	'Defines a InputFetcher that should go and fetch messages, and return InputMessages'

	def __init__(self, id, io_manager, args=[]):
		self.name = self.__class__.__name__

		#logger.info( "Initializing %s" % self.name )
		self.io_manager = io_manager
		self.input_queue = self.io_manager.input_queue
		self.args = args
		self.id = id
		self.is_valid = True

		try:
			self.boot()
		except Exception as e:
			self.is_valid = False
			logger.error("Error initializing %s Input Fetcher Worker: %s " % ( self.name, e.args[0] ) ) 
			return 

		logger.info( "Initialized %s (%s) Input" % (self.id, self.name) )

	def boot(self):
		return True

	# Add input to the queue
	def add_input_message(self, input):
		self.input_queue.put( input )

	def fetch(self):
		raise NotImplementedError("Not implemented")

	def start_fetcher(self):
		if not self.is_valid:
			return
		logger.info("Starting %s Input Fetcher Worker." % self.name)
		self.fetcher = InputFetcherWorker(self)
		self.fetcher.start()
		return self.fetcher

	def get_arg(self, key, default=None):
		try:
			return self.args[key]
		except Exception:
			if default is not None:
				return default
			raise Exception("Missing mandatory '%s' in %s config." % (key,self.id))
			


class InputFetcherWorker(threading.Thread):
	'Fetch and Distribute all the input'

	def __init__(self, input_fetcher):
		threading.Thread.__init__(self, name=input_fetcher.name + "InputWorker" )
		# A flag to notify the thread that it should finish up and exit
		self.kill_received = False

		# Save the fetcher reference
		self.input_fetcher = input_fetcher

	def run(self):
		while not self.kill_received:
			try:
				self.input_fetcher.fetch()
			except NotImplementedError:
				logger.error( "%s has no Fetcher implemented." % self.__class__.__name__)
				return


class InputMessage:
	'Abstract class defining a InputMessage, that is processed by the InputWorker'
	content = None

	processed_message = None

	def __init__(self, input, content=""):
		self.input = input
		self.set_content(content)

	def set_content(self,string):
		# Normalize the string to UTF8
		if isinstance(string, unicode):
			string.encode('utf8')

		self.content = string

	def get_content(self):
		if isinstance(self.content, unicode):
			return self.content.encode('utf8')
		return self.content

	def get_input_id(self):
		return self.input.id 

	def get_output_message(self):
		return self.processed_message

	def set_output_message(self, string):
		self.processed_message = string

class InputProcesserWorker(threading.Thread):
	'Fetch and Distribute all the input to each registered Input object'

	def __init__(self, io_manager):
		threading.Thread.__init__(self, name="InputProcesserWorker")
		# A flag to notify the thread that it should finish up and exit
		self.kill_received = False

		# Save the bot reference
		self.io_manager = io_manager

	# Return an list of outputs
	def process_message( self, message ):

		# Get all the registered skills
		skills = self.io_manager.bot.skills
		# Loop thru the skills
		for level, skill_group in sorted(skills.iteritems()):
			for skill in skill_group:
				if skill.test(message.get_content()):
					logger.info( "Found a match on %s" % skill.name )
					# Process the message
					message.set_output_message( skill.run(message.get_content()) )
					# Store the output in the correct queue
					try:
						# O add output tem que ser para todos os outputs
						ios = self.io_manager.get_io_by_skill(skill.name) # todo: optimizar para nao correr sempre
						for io in ios:
							# If is a list, loop thru the list of outputs
							if isinstance(io['output'],list) and message.get_input_id() in io['input']:
								# Ok, got the correct input, loop the output and process it
								for output in io['output']:
									self.io_manager.add_output( output, message )
							elif message.get_input_id() == io['input']:
								self.io_manager.add_output( io['output'], message )
					except KeyError as e:
						logger.error("Couldn't send to %s output. Queue not found. Maybe the module doesn't exist?" % e.args[0])


	def run(self):
		while not self.kill_received:
			logger.debug("InputProcesserWorker is processing. It has %s messages" % self.io_manager.input_queue.qsize() )
			try:
				# Get an InputMessage
				input = self.io_manager.get_input()
				# Process the InputMessage (pass it through every skill)
				skills = self.process_message(input)
			except Empty:
				pass
