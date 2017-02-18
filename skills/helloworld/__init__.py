# -*- coding: utf-8 -*-
from skills import Skill

class HelloWorld(Skill):

	def setup_rules(self):
		self.add_rule("^(olá|ola) Ambrósio(!|\.+)*$", self.say_hello)

	def say_hello(self, message):
		self.send_message( "Olá %s!" % str(message.user().name), message )
		self.send_message( "Isto é um teste", message, reply=False)