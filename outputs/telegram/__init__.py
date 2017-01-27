# -*- coding: utf-8 -*-

from outputs import OutputDispatcher
import telegram
import logging

logger = logging.getLogger(__name__)

class Telegram(OutputDispatcher):

	def __init__(self, io_manager):
		from ambrosio import config 
		OutputDispatcher.__init__(self,io_manager)
		logger.info("Initializing Telegram API")
		self.bot = telegram.Bot( config['telegram_api'] )
		self.chat_id = config['telegram_default_channel']


	def handle(self, content):
		self.bot.sendMessage( chat_id=self.chat_id, text=content )
		

