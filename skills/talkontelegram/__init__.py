# -*- coding: utf-8 -*-
from skills import Skill

class TalkOnTelegram(Skill):

	def setup_rules(self):
		self.add_rule("^\/talk (.*)", self.talk)

	def talk(self, message):
		string = message.get_content()
		self.send_message( string.replace('/talk ', ''), message, reply=False)

