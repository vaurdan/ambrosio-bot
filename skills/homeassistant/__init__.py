# -*- coding: utf-8 -*-
from skills import Skill
import logging
from requests import get

from skills.homeassistant.remote import RemoteHA

logger = logging.getLogger(__name__)


class HomeAssistant(Skill):

	def __init__(self, bot):
		Skill.__init__(self, bot)

		self.api_url = self.get_arg( 'url') + "/api/"
		self.password = self.get_arg( 'password', None )

		self.remoteapi = RemoteHA(self.api_url, self.password)

		if self.remoteapi.test_connection():
			logger.info("HomeAssistant connection to %s is O.K." % self.api_url )
		else:
			raise Exception("HomeAssistant cannot connect to %s... Please check your config file." % self.api_url)

	def setup_rules(self):
		self.add_rule("lig(a|e)r? (a|as|o|os)", self.turn_on_entity, privileged=True )
		self.add_rule("deslig(a|e)r? (a|as|o|os)", self.turn_off_entity, privileged=True )

	def turn_on_entity(self, message):
		self.send_message( "A ligar...", message )

	def turn_off_entity(self, message):
		self.send_message("A desligar...", message)

