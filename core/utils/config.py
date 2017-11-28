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
import os
import json
from tempfile                   import gettempdir
from argparse                   import ArgumentParser
from utils.helpers.configobj    import ConfigObj
#===============================================================================
# CONFIGURATION
#===============================================================================
ARGS = None # do not edit this value
CONFIG = None # do not edit this value
#
PROG_NAME = 'datashark'
#
VERS_MAJOR = 0
VERS_MINOR = 0
VERS_FIX = 0
VERS_TAG = 'dev'
PROG_VERSION = '{}.{}.{}{}'.format(VERS_MAJOR, VERS_MINOR, VERS_FIX, VERS_TAG)
#
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
    return '({})[{}]> '.format(PROG_NAME, lvl)
#-------------------------------------------------------------------------------
# get_arg_parser
#
#-------------------------------------------------------------------------------
def get_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='store_true', 
        help='Show program version.')
    parser.add_argument('--warranty', action='store_true', 
        help='Prints license warranty then exits.')
    parser.add_argument('--conditions', action='store_true', 
        help='Prints license conditions then exits.')
    parser.add_argument('--verbose', action='store_true', 
        help='Increase program verbosity.')
    parser.add_argument('-s', '--silent', action='store_true', 
        help='Do not output anything. A log will be produced anyway.')
    parser.add_argument('-d', '--debug', action='store_true', 
        help='Start in debug mode.')
    parser.add_argument('-c', '--config', nargs=1, 
        help='Specify a configuration file.')
    return parser
#-------------------------------------------------------------------------------
# print_license
#
#-------------------------------------------------------------------------------
def print_version():
    print(PROG_VERSION)
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
    conf_fname = '{}.conf'.format(PROG_NAME)
    conf_path = os.path.join(PROG_NAME, conf_fname)
    config_files = [
        conf_fname,
        os.path.expanduser('~/.config/{}'.format(conf_path)),
        '/etc/{}'.format(conf_path)
    ]
    #
    if 'config' in dir(ARGS):
        if ARGS.config is not None:
            config_files.insert(0, ARGS.config)
    #
    for config_file in config_files:
        if os.path.isfile(config_file):
            with open(config_file, 'r') as f:
                CONFIG = ConfigObj(json.load(f))
            return config_file
    #
    return None
#-------------------------------------------------------------------------------
# __progdir
#-------------------------------------------------------------------------------
def __progdir(dirname):
    path = os.path.join(gettempdir(), PROG_NAME, dirname)
    os.makedirs(path, exist_ok=True)
    return path
#-------------------------------------------------------------------------------
# logsdir
#   \brief returns application logs directory
#-------------------------------------------------------------------------------
def logsdir():
    return __progdir('logs')
#-------------------------------------------------------------------------------
# tmpdir
#   \brief returns application temporary files directory
#-------------------------------------------------------------------------------
def tmpdir():
    return __progdir('tmp')
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
            #LGR.debug('option value from command line arguments: {}={}'.format(
            #    option, val))
            return val
    # 2 - try configuration file option
    if CONFIG is not None:
        val = CONFIG.get(PROG_NAME, None)
        if val is not None:
            val = val.get(option, None)
        if val is not None:
            #LGR.debug('option value from configuration file: {}={}'.format(
            #    option, val))
            return val
    # 3 - try environment variable
    envar = '{}_{}'.format(PROG_NAME.upper(), option.upper())
    val = os.getenv(envar)
    if val is not None:
        #LGR.debug('option value from environment variable: {}={}'.format(
        #    envar, val))
        return val
    # 4 - finally return default argument
    #LGR.debug('default: {}={}'.format(option, default))
    return default
#-------------------------------------------------------------------------------
#  section_config
#-------------------------------------------------------------------------------
def section_config(section):
    return CONFIG.get(section)
#-------------------------------------------------------------------------------
# module_config
#   \brief 
#-------------------------------------------------------------------------------
def module_config(module, default=None):
    # check if CONFIG is set
    if CONFIG is None:
        return default
    #
    mods_conf = section_config('modules')
    if mods_conf is None:
        return default
    #
    mod_conf = mods_conf.get(module, None)
    if mod_conf is None:
        return default
    #
    return mod_conf