# -*- coding: utf-8 -*-
import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty

import models.user as UserModel

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

	def add_message( self, content, user_data ):
		# Create the Input Message
		message = InputMessage(self, content)
		message.set_user_data( user_data )
		# Store it in the queue
		self.add_input_message(message)

	def raw_user_data(self):
		raise NotImplementedError("Not implemented")

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
			except Exception as e:
				logger.exception( "%s Fetcher Exception: %s" % ( self.__class__.__name__, e.args[0] ) )


class InputMessage:
	'Abstract class defining a InputMessage, that is processed by the InputWorker'
	content = None 

	processed_message = None

	user_data = None

	def __init__(self, input, content=""):
		self.input = input
		self.set_content(content)
		self.did_ran = False

		self._is_direct = False
		self._user = None

	def user( self ):
		return self._user

	def set_as_direct(self):
		self._is_direct = True

	def is_direct(self):
		return self._is_direct

	def set_user_data( self, data ):
		if 'username' not in data:
			raise Exception('User data should have a username')

		self.user_data = data

	def get_user_data( self ):
		if self.user_data is None:
			raise Exception('Missing user data in the Message')
		return self.user_data


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

	def maybe_create_user(self):
		user_data = self.get_user_data()
		username = user_data['username']

		user_id = user_data['id']

		# Set default name if name is not set
		if 'name' not in user_data:
			user_data['name'] = user_data['username']

		# Setup the input in the userdata
		user_data['input'] = self.get_input_id()

		user_select = UserModel.find_by_id( user_id )

		# Try to get user by username
		if user_select is None:
			logger.info("User %s does not exist, creating..." % username)
			self._user = UserModel.User(**user_data)
			self._user.save()
		else:
			self._user = user_select

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
		# Try to create the user first
		try: 
			message.maybe_create_user()

			# Get all the registered skills
			skills = self.io_manager.bot.skills
			# Loop thru the skills
			for level, skill_group in sorted(skills.iteritems()):
				for skill in skill_group:
					# Make sure it only runs on the skill input
					should_run = False
					ios = self.io_manager.get_io_by_skill(skill)
					for io in ios:
						if io['input'] == message.input.id:
							should_run = True
							break;

					# Try to run the message
					if should_run and skill.run(message):
						message.did_ran = True
						logger.debug( "Found a match on %s" % skill.name )
						return

			# If I'm here, just send the default message
			if not message.did_ran:
				self.io_manager.bot.default_skill.run(message)

		except Exception as e:
			logger.exception( "Error in the %s message processing: %s" % ( message.get_input_id(), e.args[0]) )


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
