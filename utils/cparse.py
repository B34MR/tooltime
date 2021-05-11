#!/usr/bin/env python3

from configparser import ConfigParser, ExtendedInterpolation


# Confile filepath. 
configfile = './configs/internal.ini'
# Read config file.
config = ConfigParser(allow_no_value=True, delimiters=':')
config.optionxform = str
config.read(configfile)