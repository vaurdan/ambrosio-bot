# -*- coding: utf-8 -*-
import logging
import threading

from queue import Empty

logger = logging.getLogger(__name__)

class OutputDispatcher:

	def __init__(self, id, io_manager, args=[]):
		self.name = self.__class__.__name__
		self.args = args
		self.id = id

		#logger.info( "Initializing %s" % self.name )
		self.io_manager = io_manager

		logger.info( "Initialized %s (%s) Output" % (self.id, self.name) )

	def handle(self, output_message):
		if isinstance( output_message, TextMessage ):
			self.handle_text(output_message)
		elif isinstance( output_message, ImageMessage ):
			self.handle_image(output_message)
		else:
			# By default, handle the OutputMessage as a text
			self.handle_text(output_message)

	def handle_text(self, message):
		raise NotImplementedError("Not implemented")

	def handle_image(self, message):
		raise NotImplementedError("Not implemented")

	def start_handler(self):
		logger.info("Starting %s Output Handler Worker." % self.name)
		self.handler = OutputDispatcherWorker(self)
		self.handler.start()
		return self.handler

	def get_arg(self, key, default=None):
		try:
			return self.args[key]
		except Exception:
			if default is not None:
				return default
			raise Exception("Missing mandatory '%s' in %s config." % (key,self.id))

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

## OUTPUT MESSAGES

class OutputMessage:

	content = ""

	input_message = None

	is_reply = True

	def __init__(self, content, input_message, reply=True):
		self.content = content
		self.input_message = input_message
		self.is_reply = reply

	def get_input_id(self):
		return self.input_message.get_input_id()

	def get_content(self):
		return self.content

class TextMessage(OutputMessage):
	pass

class ImageMessage(OutputMessage):
	
	def __init__(self, image_path, input_message, reply=True, caption=None):
		OutputMessage.__init__(self, image_path, input_message, reply)
		self.caption = caption

	def has_caption(self):
		return self.caption is not None

	def get_caption(self):
		return self.caption
