#!/usr/bin/env python3
# -!- encoding:utf8 -!-
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
#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------
FMT = '(%(asctime)s){%(name)s}[%(levelname)s] - %(message)s'
STREAM_FMT = '[%(levelname)s] - %(message)s'
DEBUG = False
VERBOSE = False
COLORED = True
LOGS_DIR = 'logs'
if assert_ms_windows(no_raise=True):
    COLORED = False
#-------------------------------------------------------------------------------
# CLASSES
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
# FUNCTIONS
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# configure_logging
#-------------------------------------------------------------------------------
def configure_logging(silent, verbose, debug):
    error_log = os.path.join(LOGS_DIR, 'datashark.error.log')
    debug_log = os.path.join(LOGS_DIR, 'datashark.debug.log')
    verbose_log = os.path.join(LOGS_DIR, 'datashark.log')
    os.makedirs(LOGS_DIR, exist_ok=True)
    lgr = logging.getLogger(PROG_NAME)
    lgr.setLevel(logging.DEBUG)
    fmtr = logging.Formatter(fmt=FMT)
    # add error log
    rfh = logging.handlers.RotatingFileHandler(error_log, 
        maxBytes=10*1024*1024, backupCount=5)
    rfh.setLevel(logging.ERROR)
    rfh.setFormatter(fmtr)
    lgr.addHandler(rfh)
    # add verbose log if required
    if verbose:
        rfh = logging.handlers.RotatingFileHandler(verbose_log, 
            maxBytes=10*1024*1024, backupCount=5)
        rfh.setLevel(logging.INFO)
        rfh.setFormatter(fmtr)
        lgr.addHandler(rfh)
    # add debug log if required
    if debug:
        rfh = logging.handlers.RotatingFileHandler(debug_log, 
            maxBytes=10*1024*1024, backupCount=5)
        rfh.setLevel(logging.DEBUG)
        rfh.setFormatter(fmtr)
        lgr.addHandler(rfh)
    if not silent:
        sh = logging.StreamHandler()
        lvl = logging.ERROR
        if verbose:
            lvl = logging.INFO
        if debug:
            lvl = logging.DEBUG
        sh.setLevel(lvl)
        sh.setFormatter(ColoredFormatter(fmt=STREAM_FMT))
        lgr.addHandler(sh)
#-------------------------------------------------------------------------------
# get_logger
#-------------------------------------------------------------------------------
def get_logger(name):
    lgr_name = '.'.join([PROG_NAME, name])
    return logging.getLogger(lgr_name)
