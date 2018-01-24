# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: logging.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#    Utils logging functions
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# =============================================================================
import os
import sys
import logging
import logging.handlers
from termcolor import colored
from utils.ms import assert_ms_windows
from utils.constants import PROG_NAME
# =============================================================================
# CONFIGURATION
# =============================================================================
FMT = '(%(asctime)s)[%(levelname)s]{%(process)d:%(name)s} - %(message)s'
CONSOLE_FMT = '[%(levelname)s]{%(process)d:%(name)s} - %(message)s'
COLORED = True
if assert_ms_windows(no_raise=True):
    COLORED = False
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for colored formatter.
##
class ColoredFormatter(logging.Formatter):
    ##
    ## { item_description }
    ##
    COLORS = {
        'DEBUG': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fmt      The format
    ## @param      datefmt  The datefmt
    ## @param      style    The style
    ##
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super(ColoredFormatter, self).__init__(fmt, datefmt, style)
    ##
    ## @brief      { function_description }
    ##
    ## @param      record  The record
    ##
    ## @return     { description_of_the_return_value }
    ##
    def format(self, record):
        os = super(ColoredFormatter, self).format(record)
        if COLORED:
            os = colored(os, ColoredFormatter.COLORS[record.levelname])
        return os
##
## @brief      Class for logging module.
##
class LoggingModule(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      logsdir  The logsdir
    ##
    def __init__(self, logsdir):
        self.logsdir = logsdir
        self.silent = True
        self.verbose = False
        self.debug = True
        # root logger init
        self.rootlgr = logging.getLogger(PROG_NAME)
        self.rootlgr.setLevel(logging.DEBUG)
        # formatters init
        self.fmtr = logging.Formatter(fmt=FMT)
        self.cfmtr = ColoredFormatter(fmt=CONSOLE_FMT)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __configure_verbose_hdlr(self):
        if self.verbose:
            self.rootlgr.debug('adding verbose handler.')
            self.rootlgr.addHandler(self.verbose_hdlr)
        else:
            self.rootlgr.debug('removing verbose handler.')
            self.rootlgr.removeHandler(self.verbose_hdlr)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __configure_debug_hdlr(self):
        if self.debug:
            self.rootlgr.debug('adding debug handler.')
            self.rootlgr.addHandler(self.debug_hdlr)
        else:
            self.rootlgr.debug('removing debug handler.')
            self.rootlgr.removeHandler(self.debug_hdlr)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __configure_console_hdlr(self):
        # set level depending on 'debug' value
        lvl = logging.INFO
        if self.debug:
            lvl = logging.DEBUG
        self.console_hdlr.setLevel(lvl)
        # enable/disable handler depending on 'silent' value
        if not self.silent:
            self.rootlgr.debug('adding console handler.')
            self.rootlgr.addHandler(self.console_hdlr)
        else:
            self.rootlgr.debug('removing console handler.')
            self.rootlgr.removeHandler(self.console_hdlr)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def init(self):
        # instanciate and configure error hdlr
        error_hdlr = logging.handlers.RotatingFileHandler(
            os.path.join(self.logsdir, '{}.error.log'.format(PROG_NAME)),
            maxBytes=10*1024*1024, backupCount=5)
        error_hdlr.setFormatter(self.fmtr)
        error_hdlr.setLevel(logging.ERROR)
        self.rootlgr.addHandler(error_hdlr)
        # instanciate and configure verbose hdlr
        self.verbose_hdlr = logging.handlers.RotatingFileHandler(
            os.path.join(self.logsdir, '{}.debug.log'.format(PROG_NAME)),
            maxBytes=10*1024*1024, backupCount=5)
        self.verbose_hdlr.setFormatter(self.fmtr)
        self.verbose_hdlr.setLevel(logging.INFO)
        self.__configure_verbose_hdlr()
        # add debug log if required
        self.debug_hdlr = logging.handlers.RotatingFileHandler(
            os.path.join(self.logsdir, '{}.log'.format(PROG_NAME)),
            maxBytes=10*1024*1024, backupCount=5)
        self.debug_hdlr.setFormatter(self.fmtr)
        self.debug_hdlr.setLevel(logging.DEBUG)
        self.__configure_debug_hdlr()
        # create
        self.console_hdlr = logging.StreamHandler(stream=sys.stderr)
        self.console_hdlr.setFormatter(self.cfmtr)
        self.__configure_console_hdlr()
    ##
    ## @brief      { function_description }
    ##
    ## @param      silent   The silent
    ## @param      verbose  The verbose
    ## @param      debug    The debug
    ##
    ## @return     { description_of_the_return_value }
    ##
    def configure(self, silent, verbose, debug):
        self.silent = silent
        self.verbose = verbose
        self.debug = debug
        # reconfigure handlers
        self.__configure_debug_hdlr()
        self.__configure_verbose_hdlr()
        self.__configure_console_hdlr()


# =============================================================================
# GLOBALS
# =============================================================================
LOGGING = None
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      { function_description }
##
## @param      logsdir  The logsdir
##
## @return     { description_of_the_return_value }
##
def init(logsdir):
    global LOGGING

    if LOGGING is None:
        LOGGING = LoggingModule(logsdir)

        try:
            LOGGING.init()
            return True
        except Exception as e:
            print(e)

    return False
##
## @brief      { function_description }
##
## @param      silent   The silent
## @param      verbose  The verbose
## @param      debug    The debug
##
## @return     { description_of_the_return_value }
##
def reconfigure(silent, verbose, debug):
    LOGGING.configure(silent, verbose, debug)
##
## @brief      Gets the logger.
##
## @param      name  The name
##
## @return     The logger.
##
def get_logger(name):
    lgr_name = '.'.join([PROG_NAME, name])
    return logging.getLogger(lgr_name)
##
## @brief      { function_description }
##
## @param      lgr       The lgr
## @param      task      The task
## @param      no_raise  No raise
##
## @return     { description_of_the_return_value }
##
def todo(lgr, task="", no_raise=False):
    msg = 'not implemented [contribute! :)]. TODO: {}'.format(task)

    if not no_raise:
        lgr.error(msg)
        raise NotImplementedError

    lgr.warning(msg)

