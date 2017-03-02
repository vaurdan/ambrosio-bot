# -*- coding: utf-8 -*-
from skills import Skill

class GoodbyeWorld(Skill):

	ignore_prefix = True

	def setup_rules(self):
		self.add_rule("Adeus Ambrósio(!|\.+)*$", self.say_bye, ignore_prefix=True)

	def say_bye(self, message):
		self.send_message( "Adeus, %s!" % str(message.user().name), message )

