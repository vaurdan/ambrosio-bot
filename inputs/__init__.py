import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class InputFetcher:
	'Defines a InputFetcher that should go and fetch messages, and return InputMessages'

	def __init__(self, io_manager):
		self.name = self.__class__.__name__

		#logger.info( "Initializing %s" % self.name )
		self.io_manager = io_manager
		self.input_queue = self.io_manager.input_queue

		logger.info( "Initialized %s Input" % (self.name) )

	# Add input to the queue
	def add_input_message(self, input):
		self.input_queue.put( input )

	def fetch(self):
		raise NotImplementedError("Not implemented")

	def start_fetcher(self):
		logger.info("Starting %s Input Fetcher Worker." % self.name)
		self.fetcher = InputFetcherWorker(self)
		self.fetcher.start()
		return self.fetcher


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

	def __init__(self, input, content=""):
		self.input = input
		self.content = content

	def set_content(self,string):
		self.content = string

	def get_content(self):
		return self.content

	def get_input_name(self):
		return self.input.name 

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
					output_content = skill.run(message.get_content())
					# Store the output in the correct queue
					try:
						# O add output tem que ser para todos os outputs
						ios = self.io_manager.get_io_by_skill(skill.name) # todo: optimizar para nao correr sempre
						for io in ios:
							# If is a list, loop thru the list of outputs
							if isinstance(io['output'],list) and message.get_input_name() in io['input']:
								# Ok, got the correct input, loop the output and process it
								for output in io['output']:
									self.io_manager.add_output( output, output_content )
							elif message.get_input_name() == io['input']:
								self.io_manager.add_output( io['output'], output_content )

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
