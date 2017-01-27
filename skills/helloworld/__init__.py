# -*- coding: utf-8 -*-
from skills import Skill

class HelloWorld(Skill):
	regex="^(olá|ola) Ambrósio(!|\.+)*$"

	def run(self, string):
		return "Olá Desconhecido!"
