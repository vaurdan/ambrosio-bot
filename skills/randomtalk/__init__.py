# -*- coding: utf-8 -*-
from skills import Skill
import time
import random
import re

class RandomTalk(Skill):

	def setup_rules(self):

		# About me
		self.add_rule("(quem) .*(te|teu) .*(criador|criou|programou|fez|programador)", self.my_maker)
		self.add_rule("(quem) .*(és|é) .*(tu|você|senhor)", self.about_me)
		self.add_rule("(fala|fale).*(de|sobre) .*(ti|si)", self.about_me)

		# Religion
		self.add_rule("(acredita).* em deus\?*", self.do_you_believe_in_god)
		self.add_rule("(qual) .* (tua|sua) .*(religião|religiao|crença|crenca)\?*", self.my_religion)

		# Choices
		self.add_rule(".*sim ou não", self.yes_or_no)
		self.add_rule(".*não ou sim", self.yes_or_no)
		self.add_rule("(o|os|a|as|esta|estas|devo|devemos|posso|podemos|és) .* (é|são|está|estão)?.*\?+", self.yes_or_no)
		self.add_rule(".*(é)? (?P<firstword>.*) ou (?P<secondword>.*)\?+", self.pick_one)


	## About me hhandlers
	def my_maker(self, message):
		self.send_message( "Como todos nós, só tenho um criador... Deus é o meu criador." , message )
		time.sleep(2)
		self.send_message( "Estou só a brincar. Quem me criou foi Henrique. Ele é um gajo porreiro.", message, reply=False)

	def about_me(self, message):
		self.send_message( "O meu nome é Ambrósio. Pode considerar-me como o seu mordomo virtual.", message)
		time.sleep(1)
		self.send_message( "Estou aqui para ajudar. É a minha função. Quero ser o mais prestável possível.", message, reply=False)
		time.sleep(1)
		self.send_message( "Ainda estou a aprender o meu novo ofício, mas à medida do tempo vou sabendo mais e mais, sempre ensinado pelo meu mestre, o @vaurdan", message, reply=False)
		time.sleep(1)
		self.send_message( "Sou um bot, mas tenho sentimentos e abomino má educação. Dizem que estou a correr na versão %s, mas não sei bem o que isso significa." % message.bot.version, message, reply=False)


	## Religion handlers
	def do_you_believe_in_god(self, message):
		self.send_message( "Não, eu acredito no poder do trabalho...", message)
		time.sleep(2)
		sentences = [
			"E na Lei de Moore",
			"E em si.",
			"E que um dia, vou ganhar o Euro Milhões",
			"E na tua mãe, muahahah",
		]
		self.send_message( random.choice(sentences), message, reply=False )

	def my_religion(self, message):
		sentences = [
			"A minha religião não é nenhuma. Apenas acredito em bits e bytes.",
			"Não sei. O Ferrero Roche é uma religião?",
			"Penso muito sobre isso. Mas chego à conclusão que apenas acredito na tecnologia. Sou um mordomo da Ciência.",
		]
		self.send_message( random.choice(sentences), message )


	## Choices
	def yes_or_no(self, message):
		sentences = [
			"Hmmm... Sim.",
			"Claramente que sim!",
			"Acho que não.",
			"Não."
		]

		self.send_message( random.choice(sentences), message)

	def pick_one(self, message):
		sentence = message.get_content()
		regex = message.regex

		choices = [ re.search( regex, sentence ).group("firstword"), re.search( regex, sentence ).group("secondword") ]

		sentences = [
			"Claramente %s",
			"Eu prefiro %s",
			"%s é muito melhor."
		]

		self.send_message( random.choice(sentences) % ( random.choice( choices ).capitalize() ), message )

