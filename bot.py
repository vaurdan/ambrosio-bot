# -*- coding: utf-8 -*-

import time
import importlib
import logging
import re
import traceback
from unidecode import unidecode

from collections import defaultdict

from iomanager import IOManager
from skills.default import Default

logger = logging.getLogger(__name__)

class Bot:
	"""
	Creates a new bot instance
	"""
	
	# Bot name
	name = "Mr. Nobody"

	version = "2.0"

	# List of Skills
	skills = defaultdict(list)

	io_manager = None

	threads = []


	def __init__(self, name):
		self.name = name

		self.regex_name = '^(' + re.escape(name) + "|" + re.escape(unidecode(name)) + "),? ?"

		logger.info( "%s is initializing. Running version %s" % (name, self.version) )

		# Create input manager
		self.io_manager = IOManager(self)

		# 1st. Setup Inputs
		self.io_manager.setup()

		# 2nd. Setup Skills
		self.setup_skills()

		# 3rd. Setup default skill
		self.default_skill = Default(self)

	def start(self):

		# Start input manager worker
		self.io_manager.start()
	
	def shutdown(self):
		logger.info( "Shutting down %s threads " % len( self.threads ) )

		# Shutdown all the bot instantiated threads
		for t in self.threads:
			t.kill_received = True
			t.join()
			#self.threads.remove(t)
			self.threads = [thread for thread in self.threads if thread is not t]
			logger.info( "Killed %s " % t)

		# Shutdown the input manager
		self.io_manager.shutdown()

	def run(self):

		self.start()

		# Check if threads are running
		while True:
			try:
				time.sleep(60)
			except KeyboardInterrupt:
				logger.info( "Ctrl-c received! Shutting down..." )
				self.shutdown()
				return

	def setup_skills(self):
		from ambrosio import config

		# Fetch skills from config
		skills = config['skills']

		logger.info( "Initializing Skills" )

		for skill in skills:

			level = skill['level'] if 'level' in skill else 0
			name = skill['skill']
			is_custom = skill['custom'] if 'custom' in skill else False

			try:
				if is_custom:
					module = importlib.import_module('config.skills.' + name.lower())
				else:
					module = importlib.import_module('skills.' + name.lower())

				module_obj = getattr(module, name)

				self.register_skill( module_obj(self), level )
			except ImportError as e:
				logger.error( "Impossible to load skill %s: Module not found (%s)" % (name, e.args[0] ) )
			except Exception:
				logger.error( "Error loading skill. " + str( traceback.format_exc() ) )


	def register_skill( self, skill, level = 0 ):
		logger.debug( "Registering Skill %s in level %s" % ( skill.name, level ) )
		self.skills[ level ].append( skill )
		return True
