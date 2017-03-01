# -*- coding: utf-8 -*-
from inputs import InputFetcher, InputMessage
from time import sleep
import logging

from telegram import Bot
from telegram.utils.request import Request
from telegram.error import Unauthorized, InvalidToken, RetryAfter, TelegramError

logger = logging.getLogger(__name__)
'''
Warning: Part of this code was pulled from the Updater class of PythonTelegramBot, released under GPL-3.0
'''
class Telegram(InputFetcher):

	def boot(self):
		self.api_key = self.get_arg('api_key')

		# Initialize the telegram api
		logger.info("Initializing the Telegram Bot")
		self.poll_interval = self.get_arg('poll_interval', 0.0)
		self.timeout = self.get_arg('timeout', 10)
		self.max_retries = self.get_arg('max_retries', 0)
		self.clean = self.get_arg('clean', False)
		self.read_latency = self.get_arg('read_latency', 2.)
		request = Request(con_pool_size=10)

		self.telegram_bot = Bot( self.api_key, request=request )

		self.last_update_id = 0

	def fetch(self):
		cur_interval = self.poll_interval

		self._bootstrap(self.max_retries, clean=self.clean)

		try:
			updates = self.telegram_bot.getUpdates(
				self.last_update_id, timeout=self.timeout, read_latency=self.read_latency)
		except RetryAfter as e:
			logger.info(str(e))
			cur_interval = 0.5 + e.retry_after
		except TelegramError as te:
			logger.error("Error while getting Updates: {0}".format(te))

			# Put the error into the update queue and let the Dispatcher
			# broadcast it
			#self.update_queue.put(te)
			print te

			cur_interval = self._increase_poll_interval(cur_interval)
		else:
			if updates:
				for update in updates:
					if not hasattr( update.message, 'text' ):
						logger.info( "Received Telegram message without a text. Ignoring..." )
						continue;
					# Create the message object
					message = InputMessage(self, update.message.text)
					message.update = update
					message.message = update.message
					message.set_user_data({
						'username': update.message.from_user.username,
						'name': update.message.from_user.first_name + " " + update.message.from_user.last_name,
						'id': update.message.from_user.id, # TODO: Pode haver conflito de ID's?
					})

					# Check if it is a direct message or a channel message
					chat_id = update.message.chat_id
					if chat_id > 0:
						message.set_as_direct()

					# Add it to the queue
					logger.debug("Received Message on Telegram: %s" % update.message.text)
					self.add_input_message(message)

				self.last_update_id = updates[-1].update_id + 1

			cur_interval = self.poll_interval

		sleep(cur_interval)

	def _clean_updates(self):
		self.logger.debug('Cleaning updates from Telegram server')
		updates = self.telegram_bot.getUpdates()
		while updates:
			updates = self.telegram_bot.getUpdates(updates[-1].update_id + 1)

	def _bootstrap(self, max_retries, clean):
		retries = 0
		while 1:

			try:
				if clean:
					self._clean_updates()
					sleep(1)
			except (Unauthorized, InvalidToken):
				raise
			except TelegramError:
				msg = 'error in bootstrap phase; try={0} max_retries={1}'.format(retries,
																				 max_retries)
				if max_retries < 0 or retries < max_retries:
					logger.warning(msg)
					retries += 1
				else:
					logger.exception(msg)
					raise
			else:
				break
			sleep(1)

	@staticmethod
	def _increase_poll_interval(current_interval):
		# increase waiting times on subsequent errors up to 30secs
		if current_interval == 0:
			current_interval = 1
		elif current_interval < 30:
			current_interval += current_interval / 2
		elif current_interval > 30:
			current_interval = 30
		return current_interval

