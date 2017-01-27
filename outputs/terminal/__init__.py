# -*- coding: utf-8 -*-

from outputs import OutputDispatcher

class Terminal(OutputDispatcher):

	def handle(self, content):
		print "Ambrósio > " + content
