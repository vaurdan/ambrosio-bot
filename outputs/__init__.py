import logging
import threading

from queue import Empty

logger = logging.getLogger(__name__)

class OutputDispatcher:

	def __init__(self, id, io_manager, args=[]):
		self.name = self.__class__.__name__
		self.args = []
		self.id = id

		#logger.info( "Initializing %s" % self.name )
		self.io_manager = io_manager

		logger.info( "Initialized %s (%s) Output" % (self.id, self.name) )

	def handle(self, content):
		raise NotImplementedError("Not implemented")

	def start_handler(self):
		logger.info("Starting %s Output Handler Worker." % self.name)
		self.handler = OutputDispatcherWorker(self)
		self.handler.start()
		return self.handler

class OutputDispatcherWorker(threading.Thread):
	'Fetch and Distribute all the input'

	def __init__(self, output_dispatcher):
		threading.Thread.__init__(self, name=output_dispatcher.name + "OutputWorker" )
		# A flag to notify the thread that it should finish up and exit
		self.kill_received = False

		# Save the fetcher reference
		self.output_dispatcher = output_dispatcher
		self.io_manager = output_dispatcher.io_manager

	def run(self):
		while not self.kill_received:
			try:
				# Get output from the Queue
				logger.debug("Trying to get output from queue %s" % self.output_dispatcher.id)
				output = self.io_manager.get_output(self.output_dispatcher.id)
				# Handle the output
				self.output_dispatcher.handle( output )
			except NotImplementedError:
				logger.error( "%s has no Output handler implemented." % self.__class__.__name__)
			except Empty:
				logger.debug( "The queue for %s is empty" % self.output_dispatcher.id)

