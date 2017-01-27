import logging
import threading

from queue import Empty

logger = logging.getLogger(__name__)

class OutputHandler:

	def __init__(self, io_manager):
		self.name = self.__class__.__name__

		#logger.info( "Initializing %s" % self.name )
		self.io_manager = io_manager

		logger.info( "Initialized %s Input" % (self.name) )

	def handle(self, content):
		raise NotImplementedError("Not implemented")

	def start_handler(self):
		logger.info("Starting %s Output Handler Worker." % self.name)
		self.handler = OutputHandlerWorker(self)
		self.handler.start()
		return self.handler

class OutputHandlerWorker(threading.Thread):
	'Fetch and Distribute all the input'

	def __init__(self, output_handler):
		threading.Thread.__init__(self, name=output_handler.name + "OutputWorker" )
		# A flag to notify the thread that it should finish up and exit
		self.kill_received = False

		# Save the fetcher reference
		self.output_handler = output_handler
		self.io_manager = output_handler.io_manager

	def run(self):
		while not self.kill_received:
			try:
				# Get output from the Queue
				logger.debug("Trying to get output from queue %s" % self.output_handler.name)
				output = self.io_manager.get_output(self.output_handler.name)
				# Handle the output
				self.output_handler.handle( output )
			except NotImplementedError:
				logger.error( "%s has no Output handler implemented." % self.__class__.__name__)
			except Empty:
				logger.debug( "The queue for %s is empty" % self.output_handler.name)

