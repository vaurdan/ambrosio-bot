# -*- coding: utf-8 -*-
from skills import Skill

class HelloWorld(Skill):

	ignore_prefix = True

	def setup_rules(self):
		self.add_rule("(olá|ola) Ambrósio(!|\.+)*$", self.say_hello, ignore_prefix=True)

	def say_hello(self, message):
		self.send_message( "Olá %s!" % str(message.user().name), message )
		self.send_message( "Isto é um teste", message, reply=False)