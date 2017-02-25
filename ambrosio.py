#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot import Bot
import logging

from config import config

# Create config object
'''config = ConfigParser.ConfigParser()
config.optionxform = str
config.read('config.ini')'''



# Enable logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [ %(name)s ] - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def main():

	print config

	bot = Bot(name=config['name'])

	# Run the bot thread
	bot.run()

if __name__ == '__main__':
    main()
