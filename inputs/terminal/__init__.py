# -*- coding: utf-8 -*-
from inputs import InputFetcher, InputMessage

class Terminal(InputFetcher):
	
	def fetch(self):
		# Fetch the value from terminal
		value = raw_input('$: ')
		# Create the Input Message
		message = InputMessage(self, value)
		# Store it in the queue
		self.add_input_message(message)
