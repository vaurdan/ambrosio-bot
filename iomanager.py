import logging
import threading
import time
import importlib

from utils import list_unique
from queue import Queue, Empty
from skills import Skill

from inputs import *

logger = logging.getLogger(__name__)

class IOManager:

	input_queue = Queue()
	output_queues = {}

	skills_io = {}

	# List of Inputs
	inputs = {}

	outputs = {}

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

	def register_input( self, id, input ):
		logger.debug( "Registering %s Input (%s)" % ( id, input.name ) )
		self.inputs[id] = input
		return True

	def register_output( self, id, output ):
		logger.debug( "Registering %s Ouput (%s)" % ( id, output.name ) )
		self.outputs[id] = output
		return True

	def get_io_by_skill( self, skill_name ):
		from config import config

		if isinstance(skill_name, Skill):
			skill_name = skill_name.name

		skills = config['skills']
		for skill in skills:
			if(skill['skill'].lower() == skill_name.lower()):
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
		for input_id, input in self.inputs.iteritems():
			self.threads.append(input.start_fetcher())
		for output_id, output in self.outputs.iteritems():
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

		# Loop thru skills to find the available inputs
		for skill in skills:
			skill_name = skill['skill']
			self.skills_io[ skill_name ] = { 'inputs': [], 'outputs': [] }
			# If there are multiple inputs/outputs pairs
			if 'io' in skill:
				for io_pair in skill['io']: 
					# Check Inputs
					if isinstance(io_pair['input'],list):
						self.skills_io[ skill_name ]['inputs'].extend(io_pair['input'])
					else:
						self.skills_io[ skill_name ]['inputs'].append(io_pair['input'])
					# Check Outputs
					if isinstance(io_pair['output'],list):
						self.skills_io[ skill_name ]['outputs'].extend(io_pair['output'])
					else:
						self.skills_io[ skill_name ]['inputs'].append(io_pair['output'])

			else:
				# Check Inputs
				if isinstance(skill['input'],list):
					self.skills_io[ skill_name ]['inputs'].extend(skill['input'])
				else:
					self.skills_io[ skill_name ]['inputs'].append(skill['input'])
				# Check Outputs
				if isinstance(skill['output'],list):
					self.skills_io[ skill_name ]['outputs'].extend(skill['output'])
				else:
					self.skills_io[ skill_name ]['outputs'].append(skill['output'])

			# Make the list unique
			self.skills_io[ skill_name ]['inputs'] = list_unique(self.skills_io[ skill_name ]['inputs'])
			self.skills_io[ skill_name ]['outputs'] = list_unique(self.skills_io[ skill_name ]['outputs'])

		# Make inputs and outputs unique
		inputs = config['inputs']
		outputs = config['outputs']

		# Load Inputs
		logger.info( "Initializing Inputs" )
		for input in inputs: 
			input_id = input['id']
			input_class = input['input_class']
			args = input['args']
			try:
				module = importlib.import_module('inputs.' + input_class.lower())
				module_obj = getattr(module, input_class)
				# Create the input fetcher object
				input_module = module_obj( id=input_id, io_manager=self, args=args)
				if input_module.is_valid:
					self.register_input( input_id, input_module )
			except ImportError:
				logger.error( "Impossible to load Input %s: Module not found." % input_class )

		logger.info( "Initializing Outputs" )
		# Load outputs
		for output in outputs:
			output_id = output['id']
			output_class = output['output_class']
			args = output['args']

			# Create the queue
			self.output_queues[output_id] = Queue()

			# Load the outputs
			try:
				module = importlib.import_module('outputs.' + output_class.lower())
				module_obj = getattr(module, output_class)

				self.register_output( output_id, module_obj( id=output_id, io_manager=self, args=args ) )
			except ImportError:
				logger.error( "Impossible to load Output %s: Module not found." % output )
