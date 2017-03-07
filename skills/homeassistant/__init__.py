# -*- coding: utf-8 -*-
from skills import Skill
import logging
import utils
from requests import get
import re
import random

from skills.homeassistant.remote import RemoteHA, TooManyEntities

logger = logging.getLogger(__name__)


class HomeAssistant(Skill):

	def __init__(self, bot):
		Skill.__init__(self, bot)

		self.api_url = self.get_arg( 'url') + "/api/"
		self.password = self.get_arg( 'password', None )

		self.remoteapi = RemoteHA(self.api_url, self.password)

		logger.info("Testing HomeAssistant connection. Please hold.")
		if self.remoteapi.test_connection():
			logger.info("HomeAssistant connection to %s is O.K." % self.api_url )
		else:
			raise Exception("HomeAssistant cannot connect to %s... Please check your config file." % self.api_url)

	def setup_rules(self):
		self.add_rule("lig(a|ue)r? (?P<article>a|as|o|os)?", self.turn_entity, privileged=True )
		self.add_rule("deslig(a|ue)r? (?P<article>a|as|o|os)?", self.turn_entity, privileged=True )

		self.add_rule("(?P<article>a|as|o|os) +(?P<prefixed_name>(.*(luz(es)?|iluminação).* (da|na|do|no)? ?)?(?P<entity>(\w|\s)*)) *(?P<is_word>est(á|a)|est(ã|a)o) (des)?ligad(o|a|os|as)\?*", self.check_status, privileged=True)

		self.add_rule("deixei *(?P<article>a|as|o|os) +(?P<prefixed_name>(.*(luz(es)?|iluminação).* (da|na|do|no) ?)?(?P<entity>(\w|\s)*)) *(des)?ligad(o|a|os|as)\?*", self.did_i_forgot, privileged=True)
		self.add_rule("(esqueci(-me)? +de )?((des)?ligar|desliguei) (?P<article>a|as|o|os) (?P<prefixed_name>(.*(luz(es)?|iluminação).* (da|na|do|no) ?)?(?P<entity>(\w|\s)*))\?*", self.did_i_forgot, privileged=True)

	def turn_entity(self, message):

		# Test if it's a light
		light_regex = message.regex.pattern + " ?(?P<prefixed_name>(.*(luz(es)?|iluminação).* (da|na|do|no)? ?)?(?P<entity>(\w|\s)*))"
		regex = re.search( re.compile(light_regex, re.IGNORECASE), message.get_content() )

		entity_name = regex.group("entity")
		article = regex.group("article")
		prefixed_name = regex.group("prefixed_name")

		if prefixed_name is None:
			name_to_print = str(article) + " " + str(entity_name)
		else:
			name_to_print = str(article) + " " + str(prefixed_name)

		try:
			entity = self.remoteapi.get_entity_id(entity_name)

			if entity is None:
				self.send_message("Lamento senhor. Não tenho conhecimento sobre %s." % name_to_print, message)
				return

			message_text = message.get_content().lower()

			if 'deslig' in message_text:
				self.send_message("É para já senhor, vou desligar %s." % name_to_print, message)
				self.remoteapi.switch(entity, 'off')
			elif 'lig' in message_text:
				self.send_message("É para já senhor, vou ligar %s." % name_to_print, message)
				self.remoteapi.switch(entity, 'on')

		except TooManyEntities as e:
			self.send_message( "Existem várias entidades com esse nome. Poderá ser um pouco mais específico?" , message )
			logger.error("Found multiple entities: %s" % e.entities )

	def check_status(self, message):

		regex = re.search( re.compile( message.regex.pattern, re.IGNORECASE ), message.get_content())

		entity_name = regex.group("entity")
		try:
			entity = self.remoteapi.get_entity(entity_name)
		except TooManyEntities as e:
			self.send_message("Existem várias entidades com esse nome. Poderá ser um pouco mais específico?", message)
			logger.error("Found multiple entities: %s" % e.entities)
			return

		article = regex.group("article")
		prefixed_name = regex.group("prefixed_name")

		if prefixed_name is None:
			name_to_print = str(article) + " " + str(entity_name.strip())
		else:
			name_to_print = str(article) + " " + str(prefixed_name.strip())

		if entity['state'] == "on":
			sentences = [
				"Pelo que vejo, %(name)s %(is_word)s %(turned_on_word)s.",
				"%(name)s %(is_word)s %(turned_on_word)s.",
				"Posso confirmar que %(name)s %(is_word)s %(turned_on_word)s."
			]
			turned_on_word = "ligad" + str(regex.group('article')).lower()
			is_word = regex.group('is_word').lower()

			self.send_message( utils.upperfirst( random.choice( sentences ) % { 'name': utils.lowerfirst(name_to_print), 'turned_on_word': turned_on_word, 'is_word': is_word} ), message)
		elif entity['state'] == "off":
			sentences = [
				"Pelo que vejo, %(name)s %(is_word)s %(turned_on_word)s.",
				"%(name)s %(is_word)s %(turned_on_word)s.",
				"Posso confirmar que %(name)s %(is_word)s %(turned_on_word)s."
			]
			turned_on_word = "desligad" + str(regex.group('article')).lower()
			is_word = regex.group('is_word').lower()

			self.send_message( utils.upperfirst( random.choice( sentences ) % { 'name': utils.lowerfirst(name_to_print), 'turned_on_word': turned_on_word, 'is_word': is_word} ), message)


	def did_i_forgot(self,message):
		regex = re.search( re.compile( message.regex.pattern, re.IGNORECASE ), message.get_content())

		entity_name = regex.group("entity")
		try:
			entity = self.remoteapi.get_entity(entity_name)
		except TooManyEntities as e:
			self.send_message("Existem várias entidades com esse nome. Poderá ser um pouco mais específico?", message)
			logger.error("Found multiple entities: %s" % e.entities)
			return

		if entity['state'] == "on":
			sentences = [
				"Sim, senhor. Está %(turned_on_word)s.",
				"Está %(turned_on_word)s.",
			]
			turned_on_word = "ligad" + str(regex.group('article')).lower()
			self.send_message( utils.upperfirst( random.choice( sentences ) % { 'turned_on_word': turned_on_word }), message)

		elif entity['state'] == "off":
			sentences = [
				"Não se preocupe, que está %(turned_on_word)s..",
				"Não, senhor.",
				"Está %(turned_on_word)s."
			]
			turned_on_word = "desligad" + str(regex.group('article')).lower()

			self.send_message( utils.upperfirst( random.choice( sentences ) % { 'turned_on_word': turned_on_word }), message)



