# -*- coding: utf-8 -*-

import yaml
import sys

with open("config/config.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(-1)