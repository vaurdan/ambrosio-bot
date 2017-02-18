# Ambrósio, the bot

Ambrósio is a smart bot to be used in any situation you need. You can create your own Telegram bot, your own Terminal bot, whatever you want. 

Ambrósio has a list of Skills that you can create. Each skill has multiple rules, which is a regular expression associated with a callback method.

It also features multiple inputs and outputs, like Telegram and Console, right now. 

## Installation

 * Clone this repository
 * Run `pip install -r requirements.php`
 * Copy `config/config.yaml.example` to `config/config.yaml` and make Ambrósio your own.  

## How to run?

It's quite easy. After configuring it, just call `python ambrosio.py` and Ambrosio will boot.

## Custom Skills

All the custom skills should be included as a module in `config/skills`. For example, if you want to create a Foo skill, you must have the `config/skills/foo/__init__.py`. You can check the example custom Skill in that file.

Also, when registering the skill in your `config.yaml` you need to include `custom: yes`, as you can see on the example config file. 

## Custom inputs
WIP

## Custom outputs
WIP

---

__This is still a WIP and it's really alpha and early release. I have made this bot for my personal use, so it might have a lot of bugs and nearly zero documentation. Sorry about that!__
