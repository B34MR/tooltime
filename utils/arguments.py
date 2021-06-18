#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter

# Custom usage / help menu.
class HelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ''
        return super(HelpFormatter, self).add_usage(
            usage, actions, groups, prefix)


def parse_args():
  ''' Define arguments '''
  
  # Custom help menu.
  custom_usage = """
  Usage: 
    python3 tooltime.py <configfile>
    
  Positional argument(s):
    [configfile]: Input from configuration file (defaults to './configs/internal.ini').
  """
  
  # Define parser
  parser = argparse.ArgumentParser(formatter_class=HelpFormatter, description='', usage=custom_usage, add_help=False)
  
  # Positional args.
  parser.add_argument('configfile', nargs="?", type=str, metavar='<configfile>', default='./configs/internal.ini', help="Input from configuration file (defaults to './configs/internal.ini')")
   
  # Initiate parser instance
  args = parser.parse_args()
  return args

def main():
  import arguments
  arguments.parse_args()

if __name__ == "__main__":
    main()