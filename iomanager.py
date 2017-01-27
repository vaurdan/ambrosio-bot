import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty

from inputs import *

logger = logging.getLogger(__name__)

class IOManager:

	input_queue = Queue()
	output_queues = {}

	skills_io = {}

	# List of Inputs
	inputs = []

	outputs = []

	threads = []

	def __init__(self, bot):
		logger.info( "Initializing the Input/Output Manager")
		self.bot = bot

	# Add input to the queue
	def add_input(self, input):
		self.input_queue.put( input )

	# Add output to the Queue
	def add_output(self, output, message):
		logger.debug("Adding output to queue %s. Message: %s" % (output, message) )
		self.output_queues[output].put(message)

	def get_input_fetcher_by_name( name ):
		for input in self.input:
			if input.name == name: return input
		return False

	# Get an input and block if no input is available
	def get_input(self):
		return self.input_queue.get(True, 3)

	# Get an output and block if no output is available
	def get_output(self,output):
		return self.output_queues[output].get(True, 3)

	def register_input( self, input ):
		logger.debug( "Registering %s Input", input.name)
		self.inputs.append( input )
		return True

	def register_output( self, input ):
		logger.debug( "Registering %s Output", input.name)
		self.outputs.append( input )
		return True

	def get_io_by_skill( self, skill_name ):
		from ambrosio import config

		skills = config['skills']
		for skill in skills:
			if(skill['skill'] == skill_name):
				# If it's already a properly formated dict, return it
				if 'io' in skill:
					return skill['io']

				return [{ 'input': skill['input'], 'output': skill['output']}]

	def start(self):
		# Start the Input Processer Worker
		logger.info( "Creating InputProcesserWorker." )
		self.input_worker = InputProcesserWorker(self)
		self.input_worker.start()
		self.threads.append(self.input_worker)
		# Start each InputFetcher workers
		for input in self.inputs:
			self.threads.append(input.start_fetcher())
		for output in self.outputs:
			self.threads.append(output.start_handler())


	def shutdown(self):
		logger.info( "Stopping Input Manager. Shutting down %s threads " % len( self.threads ) )
		for t in self.threads:
			t.kill_received = True
			t.join()
			self.threads = [thread for thread in self.threads if thread is not t]
			logger.info( "Killed %s " % t)

	def setup(self):
		from ambrosio import config

		# Fetch skills from config
		skills = config['skills']
		# Initialize the empty inputs list
		inputs = []
		outputs = []

		logger.info( "Initializing Inputs" )
		# Loop thru skills to find the available inputs
		for skill in skills:
			skill_name = skill['skill']
			self.skills_io[ skill_name ] = { 'inputs': [], 'outputs': [] }
			# If there are multiple inputs/outputs pairs
			if 'io' in skill:
				for io_pair in skill['io']: 
					# Check Inputs
					if isinstance(io_pair['input'],list):
						inputs.extend(io_pair['input'])
						self.skills_io[ skill_name ]['inputs'].extend(io_pair['input'])
					else:
						inputs.append(io_pair['input'])
						self.skills_io[ skill_name ]['inputs'].append(io_pair['input'])
					# Check Outputs
					if isinstance(io_pair['output'],list):
						outputs.extend(io_pair['output'])
						self.skills_io[ skill_name ]['outputs'].extend(io_pair['output'])
					else:
						outputs.append(io_pair['output'])
						self.skills_io[ skill_name ]['inputs'].append(io_pair['output'])

			else:
				# Check Inputs
				if isinstance(skill['input'],list):
					inputs.extend(skill['input'])
					self.skills_io[ skill_name ]['inputs'].extend(skill['input'])
				else:
					inputs.append(skill['input'])
					self.skills_io[ skill_name ]['inputs'].append(skill['input'])
				# Check Outputs
				if isinstance(skill['output'],list):
					outputs.extend(skill['output'])
					self.skills_io[ skill_name ]['outputs'].extend(skill['output'])
				else:
					outputs.append(skill['output'])
					self.skills_io[ skill_name ]['outputs'].append(skill['output'])

			# Make the list unique
			self.skills_io[ skill_name ]['inputs'] = list_unique(self.skills_io[ skill_name ]['inputs'])
			self.skills_io[ skill_name ]['outputs'] = list_unique(self.skills_io[ skill_name ]['outputs'])

		# Make inputs and outputs unique
		inputs = list_unique(inputs)
		outputs = list_unique(outputs)

		# Load Inputs
		for input in inputs: 
			try:
				module = importlib.import_module('inputs.' + input.lower())
				module_obj = getattr(module, input)

				self.register_input( module_obj(self) )
			except ImportError:
				logger.error( "Impossible to load Input %s: Module not found." % input )

		# Load outputs
		for output in outputs:
			# Create the queue
			self.output_queues[output] = Queue()
			# Load the outputs
			try:
				module = importlib.import_module('outputs.' + output.lower())
				module_obj = getattr(module, output)

				self.register_output( module_obj(self) )
			except ImportError:
				logger.error( "Impossible to load Output %s: Module not found." % output )
