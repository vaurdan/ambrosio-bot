# -*- coding: utf-8 -*-
from skills import Skill

class GoodbyeWorld(Skill):

	regex="^Adeus Ambrósio(!|\.+)*$"

	def run(self, message):
		self.send_message( "Adeus, %s!" % str(message.user().name), message )
