#!/usr/bin/env <PROG>
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: lifo.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#   
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
# no import
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# LIFO
#-------------------------------------------------------------------------------
class LIFO(object):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, elements=[]):
        super(LIFO, self).__init__()
        self.__elements = elements
    #---------------------------------------------------------------------------
    # push
    #---------------------------------------------------------------------------
    def push(elements):
        if not isinstance(elements, list):
            elements = [ elements ]
        self.__elements += elements
    #---------------------------------------------------------------------------
    # pop
    #---------------------------------------------------------------------------
    def pop():
        e = self.__elements[-1]
        self.__elements = self.elements[:-1]
        return e