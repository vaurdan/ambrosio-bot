# -*- coding: utf-8 -*-

from outputs import OutputHandler

class Terminal(OutputHandler):

	def handle(self, content):
		print "Ambrósio > " + content
