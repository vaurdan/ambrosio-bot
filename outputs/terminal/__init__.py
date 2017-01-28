# -*- coding: utf-8 -*-

from outputs import OutputDispatcher

class Terminal(OutputDispatcher):

	def handle(self, message):
		print "Ambrósio > " + message.get_output_message()
