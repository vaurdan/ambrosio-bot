import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class InputFetcher:
	'Defines a InputFetcher that should go and fetch messages, and return InputMessages'

	def __init__(self, input_manager):
		self.name = self.__class__.__name__

		#logger.info( "Initializing %s" % self.name )
		self.input_manager = input_manager
		self.input_queue = self.input_manager.input_queue

		logger.info( "Initialized %s Input" % (self.name) )

	# Add input to the queue
	def add_input_message(self, input):
		self.input_queue.put( input )

	def fetch(self):
		raise NotImplementedError("Not implemented")

	def start_fetcher(self):
		logger.info("Starting %s Worker." % self.name)
		self.fetcher = InputFetcherWorker(self)
		self.fetcher.start()
		return self.fetcher
		

class InputFetcherWorker(threading.Thread):
	'Fetch and Distribute all the input'

	def __init__(self, input_fetcher):
		threading.Thread.__init__(self, name=input_fetcher.name + "Worker" )
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

	def set_content(string):
		self.content = string

	def get_content(self):
		return self.content

class InputProcesserWorker(threading.Thread):
	'Fetch and Distribute all the input to each registered Input object'

	def __init__(self, input_manager):
		threading.Thread.__init__(self, name="InputProcesserWorker")
		# A flag to notify the thread that it should finish up and exit
		self.kill_received = False

		# Save the bot reference
		self.input_manager = input_manager

	# Return an list of outputs
	def process_message( self, input ):
		# Get all the registered skills
		skills = self.input_manager.bot.skills
		# Loop thru the skills
		for level, skill_group in sorted(skills.iteritems()):
			for skill in skill_group:
				if skill.test(input.get_content()):
					logger.info( "Found a match on %s" % skill.name )
					continue;

	def run(self):
		while not self.kill_received:
			logger.debug("InputProcesserWorker is processing. It has %s messages" % self.input_manager.input_queue.qsize() )
			try:
				# Get an InputMessage
				input = self.input_manager.get_input()
				# Process the InputMessage (pass it through every skill)
				self.process_message(input)
				# Add result to the output queue
				#input_manager.add_output()
			except Empty:
				pass
