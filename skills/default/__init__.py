# -*- coding: utf-8 -*-
from skills import Skill
import random

class Default(Skill):

	ignore_prefix = False

	sorry_messages = [
		'Lamento, senhor. Não o consigo ajudar.',
		'Acho que não o entendi, senhor.',
		'Ainda não tive formação suficiente, senhor. Talvez mais tarde.',
		'Gostaria de o ajudar, mas não consigo.'
	]

	def setup_rules(self):
		self.add_rule(".*", self.say_sorry)

	def say_sorry(self, message):
		message_str = random.choice( self.sorry_messages )
		self.send_message( message_str , message )

	def send_message(self, text_message, original_message, reply=True, args = {}):
		args['is_default'] = True
		Skill.send_message(self, text_message, original_message, reply, args)