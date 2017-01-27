#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot import Bot
import ConfigParser
import yaml
import logging
import sys

# Create config object
'''config = ConfigParser.ConfigParser()
config.optionxform = str
config.read('config.ini')'''

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(-1)

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
