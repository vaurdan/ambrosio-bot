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


	def handle_text(self, message):
		# Check if the message came from telegram
		if hasattr(message.input_message, 'update'):
			telegram_message = message.input_message.message

			if message.is_reply:
				telegram_message.reply_text( message.get_content() )
			else:
				chat_id = telegram_message.chat.id
				self.telegram_bot.sendMessage( chat_id=chat_id, text=message.get_content() )
			return
		
		self.telegram_bot.sendMessage( chat_id=self.default_chat, text=message.get_content() )

	def handle_image(self, message):
		# Get the caption
		caption = message.get_caption() if message.has_caption() else False

		# Check if the message came from telegram
		if hasattr(message.input_message, 'update'):
			telegram_message = message.input_message.message

			if message.is_reply:
				telegram_message.reply_photo( message.get_content(), caption=caption )
			else:
				chat_id = telegram_message.chat.id
				self.telegram_bot.send_photo( chat_id=chat_id, photo=message.get_content(), caption=caption )
		else:
			self.telegram_bot.send_photo( chat_id=self.default_chat, photo=message.get_content(), caption=caption )