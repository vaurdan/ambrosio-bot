# -*- coding: utf-8 -*-
from skills import Skill

class TalkOnTelegram(Skill):
	regex="^\/talk (.*)"

	def run(self, string):
		return string.replace('/talk ', '')
