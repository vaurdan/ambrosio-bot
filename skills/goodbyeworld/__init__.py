# -*- coding: utf-8 -*-
from skills import Skill, Rule

class GoodbyeWorld(Skill):

	def setup_rules(self):
		self.add_rule("^Adeus Ambrósio(!|\.+)*$", self.say_bye)

	def say_bye(self, message):
		self.send_message( "Adeus, %s!" % str(message.user().name), message )

