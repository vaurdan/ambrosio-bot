# -*- coding: utf-8 -*-
from inputs import InputFetcher, InputMessage
import os
import pwd

class Terminal(InputFetcher):
	
	def fetch(self):
		# Fetch the value from terminal
		value = raw_input('$: ')
		# Add the message with user data

		user_data = { 
			'username': pwd.getpwuid( os.getuid() )[ 0 ],
		}

		self.add_message(value, user_data)		

	def raw_user_data(self):
		return 
