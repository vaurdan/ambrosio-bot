# -*- coding: utf-8 -*-
from skills import Skill

class HelloWorld(Skill):
	regex="^(olá|ola) Ambrósio(!|\.+)*$"

	def run(self, message):
		self.send_message( "Olá %s!" % str(message.user().name), message, )
		self.send_message( "Isto é um teste", message, reply=False)

