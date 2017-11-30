#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#-------------------------------------------------------------------------------
import os
import logging
import logging.handlers
from termcolor          import colored
from utils.config       import PROG_NAME
from utils.helpers.ms   import assert_ms_windows
#===============================================================================
# CONFIGURATION
#===============================================================================
FMT = '(%(asctime)s)[%(levelname)s]{%(process)d:%(module)s} - %(message)s'
CONSOLE_FMT = '[%(levelname)s]{%(process)d:%(module)s} - %(message)s'
COLORED = True
if assert_ms_windows(no_raise=True):
    COLORED = False
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# ColoredFormatter
#-------------------------------------------------------------------------------
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super(ColoredFormatter, self).__init__(fmt, datefmt, style)
    #---------------------------------------------------------------------------
    # format
    #---------------------------------------------------------------------------
    def format(self, record):
        os = super(ColoredFormatter, self).format(record)
        if COLORED:
            os = colored(os, ColoredFormatter.COLORS[record.levelname])
        return os
#-------------------------------------------------------------------------------
# LoggingModule
#-------------------------------------------------------------------------------
class LoggingModule(object):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
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
    #---------------------------------------------------------------------------
    # __configure_verbose_hdlr
    #---------------------------------------------------------------------------
    def __configure_verbose_hdlr(self):
        if self.verbose:
            self.rootlgr.debug('adding verbose handler.')
            self.rootlgr.addHandler(self.verbose_hdlr)
        else:
            self.rootlgr.debug('removing verbose handler.')
            self.rootlgr.removeHandler(self.verbose_hdlr)
    #---------------------------------------------------------------------------
    # __configure_debug_hdlr
    #---------------------------------------------------------------------------
    def __configure_debug_hdlr(self):
        if self.debug:
            self.rootlgr.debug('adding debug handler.')
            self.rootlgr.addHandler(self.debug_hdlr)
        else:
            self.rootlgr.debug('removing debug handler.')
            self.rootlgr.removeHandler(self.debug_hdlr)
    #---------------------------------------------------------------------------
    # __configure_console_hdlr
    #---------------------------------------------------------------------------
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
    #---------------------------------------------------------------------------
    # init
    #---------------------------------------------------------------------------
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
        self.console_hdlr = logging.StreamHandler()
        self.console_hdlr.setFormatter(self.cfmtr)
        self.__configure_console_hdlr()
    #---------------------------------------------------------------------------
    # configure
    #---------------------------------------------------------------------------
    def configure(self, silent, verbose, debug):
        self.silent = silent
        self.verbose = verbose
        self.debug = debug
        # reconfigure handlers
        self.__configure_debug_hdlr()
        self.__configure_verbose_hdlr()
        self.__configure_console_hdlr()
#===============================================================================
# GLOBALS
#===============================================================================
LOGGING = None
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# init
#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
# reconfigure_loggers
#-------------------------------------------------------------------------------
def reconfigure(silent, verbose, debug):
    LOGGING.configure(silent, verbose, debug)
#-------------------------------------------------------------------------------
# get_logger
#-------------------------------------------------------------------------------
def get_logger(name):
    lgr_name = '.'.join([PROG_NAME, name])
    return logging.getLogger(lgr_name)
#-------------------------------------------------------------------------------
# todo
#-------------------------------------------------------------------------------
def todo(lgr, task='', no_raise=False):
    msg = 'not implemented. TODO: {}'.format(task)
    if no_raise:
        lgr.warning(msg)
    else:
        lgr.error(msg)
        raise NotImplementedError