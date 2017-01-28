# -*- coding: utf-8 -*-
from skills import Skill

class GoodbyeWorld(Skill):
	
	regex="^Adeus Ambrósio(!|\.+)*$"

	def run(self, string):
		return "Adeus, até à proxima!"