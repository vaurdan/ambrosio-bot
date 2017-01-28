# -*- coding: utf-8 -*-

from outputs import OutputDispatcher
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

class Telegram(OutputDispatcher):

	def __init__(self, id, io_manager, args=[]):

		OutputDispatcher.__init__(self,id,io_manager,args)

		self.api_key = self.get_arg('api_key')

		# Initialize the telegram api
		logger.info("Initializing the Telegram API")
		
		self.telegram_bot = Bot( self.api_key )
		self.default_chat = self.get_arg('default_chat')


	def handle(self, message):
		# Check if the message came from telegram
		if hasattr(message, 'update'):
			telegram_message = message.message
			telegram_message.reply_text( message.get_output_message() )
			return
		
		self.telegram_bot.sendMessage( chat_id=self.default_chat, text=message.get_output_message() )
		

