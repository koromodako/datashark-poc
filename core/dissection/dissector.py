#!/usr/bin/env <PROG>
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: dissector.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#       
#       http://www.iana.org/assignments/media-types/media-types.xhtml
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 paul.dautry
#   
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
from utils.helpers.logging import get_logger
#===============================================================================
# GLOBAL
#===============================================================================
lgr = get_logger(__name__)
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Dissector
#-------------------------------------------------------------------------------
class Dissector(object):
    DISSECTORS = {}
    MANDATORY_FUNCS = [
        'mimes',
        'dissect',
        'can_dissect'
    ]
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(Dissector, self).__init__()
    #---------------------------------------------------------------------------
    # dissectors
    #---------------------------------------------------------------------------
    @staticmethod
    def dissectors():
        return sorted(list(Dissector.DISSECTORS.keys()))
    #---------------------------------------------------------------------------
    # register_dissector
    #---------------------------------------------------------------------------
    @staticmethod
    def register_dissector(dissector):
        mod_attributes = dir(dissector)
        for f in Dissector.MANDATORY_FUNCS:
            if not f in mod_attributes:
                # TRACE
                return False
        for mime in dissector.mimes():
            if Dissector.DISSECTORS.get(mime, None) is None:
                Dissector.DISSECTORS[mime] = []
            Dissector.DISSECTORS[mime].append(dissector)
        return True
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def dissect(self, f):
        pass
#===============================================================================
# SCRIPT
#===============================================================================
