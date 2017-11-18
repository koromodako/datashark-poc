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
from tempfile       import gettempdir
from argparse       import ArgumentParser
from configparser   import ConfigParser
#===============================================================================
# CONFIGURATION
#===============================================================================
ARGS = None # do not edit this value
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
#
#-------------------------------------------------------------------------------
def prog_prompt(lvl):
    return '({0})[{1}]> '.format(PROG_NAME, lvl)
#-------------------------------------------------------------------------------
# get_arg_parser
#
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
#
#-------------------------------------------------------------------------------
def print_license():
    print(LICENSE)
#-------------------------------------------------------------------------------
# print_license_warranty
#
#-------------------------------------------------------------------------------
def print_license_warranty():
    print(LICENSE_WARRANTY)
#-------------------------------------------------------------------------------
# print_license_conditions
#
#-------------------------------------------------------------------------------
def print_license_conditions():
    print(LICENSE_CONDITIONS)
#-------------------------------------------------------------------------------
# load_config
#
#-------------------------------------------------------------------------------
def load_config(args):
    global ARGS
    global CONFIG
    ARGS = args
    CONFIG = ConfigParser()
    config_files = [
        '{0}.ini'.format(PROG_NAME),
        os.path.expanduser('~/{0}.ini'.format(PROG_NAME)),
        '/etc/{progname}/{progname}.ini'.format(progname=PROG_NAME)
    ]
    if 'config' in dir(ARGS):
        if ARGS.config is not None:
            config_files.append(ARGS.config)
    CONFIG.read(config_files, encoding='utf-8')
#-------------------------------------------------------------------------------
# logsdir
#   \brief returns application logs directory
#-------------------------------------------------------------------------------
def logsdir():
    return os.path.join(gettempdir(), PROG_NAME, 'logs')
#-------------------------------------------------------------------------------
# config
#   \brief returns application configuration value
#-------------------------------------------------------------------------------
def config(option=None, default=None):
    # read option following priority order
    # 1 - try command line option
    if option in dir(ARGS):
        val = getattr(ARGS, option)
        if val is not None:
            #LGR.debug('option value from command line arguments: {0}={1}'.format(
            #    option, val))
            return val
    # 2 - try configuration file option
    val = CONFIG.get(PROG_NAME, option,fallback=None)
    if val is not None:
        #LGR.debug('option value from configuration file: {0}={1}'.format(
        #    option, val))
        return val
    # 3 - try environment variable
    envar = '{0}_{1}'.format(PROG_NAME.upper(), option.upper())
    val = os.getenv(envar)
    if val is not None:
        #LGR.debug('option value from environment variable: {0}={1}'.format(
        #    envar, val))
        return val
    # 4 - finally return default argument
    #LGR.debug('default: {0}={1}'.format(option, default))
    return default
#-------------------------------------------------------------------------------
# module_config
#   \brief 
#-------------------------------------------------------------------------------
def module_config(module, default=[]):
    #---------------------------------------------------------------------------
    # ModuleConfig
    #   \brief 
    #---------------------------------------------------------------------------
    class ModuleConfig:
        def has(self, member):
            return (member in dir(self))
    # create and fill config or return None
    conf = ModuleConfig()
    if CONFIG.has_section(module):
        for option, val in CONFIG.items(section):
            setattr(conf, option, val)
        return conf
    return None
