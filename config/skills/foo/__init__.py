# -*- coding: utf-8 -*-
from skills import Skill

'''
This is an example Custom Skill.
Rules should be registered in setup_rules.
Each rule callback will receive the message object.
'''
class Foo(Skill):

	def setup_rules(self):
		self.add_rule("^Foo$", self.say_bye)

	def say_bye(self, message):
		self.send_message( "Bar, %s" % str(message.user().name), message )

