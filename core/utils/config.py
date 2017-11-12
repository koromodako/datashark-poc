#-------------------------------------------------------------------------------
#    file: config.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#    Utils program configuration
# license:
#    Utils
#    Copyright (C) 2017  Paul Dautry
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
# IMPORTS
#===============================================================================
import os.path
from argparse       import ArgumentParser
from configparser   import ConfigParser
#===============================================================================
# CONFIGURATION
#===============================================================================
CONFIG = None # do not edit this value
PROG_NAME = 'datashark'
LICENSE = """
Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `--warranty'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `--conditions' for details.
"""
LICENSE_WARRANTY = """
15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""
LICENSE_CONDITIONS = """
See LICENSE file for details.
"""
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# prog_prompt
#-------------------------------------------------------------------------------
def prog_prompt(lvl):
    return '({0})[{1}]> '.format(PROG_NAME, lvl)
#-------------------------------------------------------------------------------
# get_arg_parser
#-------------------------------------------------------------------------------
def get_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', 
        help='Make output more verbose.')
    parser.add_argument('-s', '--silent', action='store_true', 
        help='Do not output anything. A log will be produced anyway.')
    parser.add_argument('-d', '--debug', action='store_true', 
        help='Start in debug mode.')
    parser.add_argument('--warranty', action='store_true', 
        help='Prints license warranty then exits.')
    parser.add_argument('--conditions', action='store_true', 
        help='Prints license conditions then exits.')
    parser.add_argument('-c', '--config', nargs=1, 
        help='Specify a configuration file.')
    return parser
#-------------------------------------------------------------------------------
# print_license
#-------------------------------------------------------------------------------
def print_license():
    print(LICENSE)
#-------------------------------------------------------------------------------
# print_license_warranty
#-------------------------------------------------------------------------------
def print_license_warranty():
    print(LICENSE_WARRANTY)
#-------------------------------------------------------------------------------
# print_license_conditions
#-------------------------------------------------------------------------------
def print_license_conditions():
    print(LICENSE_CONDITIONS)
#-------------------------------------------------------------------------------
# load_config
#-------------------------------------------------------------------------------
def load_config(configfile=None):
    global CONFIG
    if configfile is None:
        configfile = ''
    CONFIG = ConfigParser()
    CONFIG.read([
        '/etc/datashark.conf', 
        os.path.expanduser('~/datashark.conf'),
        configfile
    ])
#-------------------------------------------------------------------------------
# config
#-------------------------------------------------------------------------------
def config(key, section=None, default=None):
    # try environment variables first
    env_key = key.upper()
    if section is not None:
        env_key = '_'.join([section.upper(), env_key])
    val = os.getenv(env_key)
    if val is not None:
        return val
    # try config file and finally fallback
    return CONFIG.get(section, key, fallback=default)
