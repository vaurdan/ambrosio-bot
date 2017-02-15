# -*- coding: utf-8 -*-

from outputs import OutputDispatcher

class Terminal(OutputDispatcher):

	def handle_text(self, message):
		print "Ambrósio > " + message.get_content()
