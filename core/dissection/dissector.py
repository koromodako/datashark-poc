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
from time                       import sleep
from utils.helpers.lifo         import LIFO
from utils.helpers.logging      import get_logger
from model.objects.container    import Container
from utils.threading.workerpool import WorkerPool
## import dissectors below
import dissection.dissectors.application.octet_stream_dissector as octet_stream_dissector
## import dissectors before
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
        self.__dissectors = {}
    #---------------------------------------------------------------------------
    # __register_dissector
    #---------------------------------------------------------------------------
    def __register_dissector(self, dissector):
        lgr.debug('Dissector.__register_dissector()')
        mod_attributes = dir(dissector)
        for f in Dissector.MANDATORY_FUNCS:
            if not f in mod_attributes:
                lgr.error('failed to add <{0}>: missing mandatory functions.'.format(
                    dissector))
                return False
        for mime in dissector.mimes():
            if self.__dissectors.get(mime, None) is None:
                self.__dissectors[mime] = []
            self.__dissectors[mime].append(dissector)
        return True
    #---------------------------------------------------------------------------
    # dissectors
    #---------------------------------------------------------------------------
    def dissectors(self):
        lgr.debug('Dissector.dissectors()')
        return sorted(list(self.__dissectors.keys()))
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def dissect(self, path):
        lgr.debug('Dissector.dissect()')
        container = Container(path)
        pending = LIFO([ container ])
        pool = WorkerPool(4)
        while len(pending) > 0:
            # take next container
            next_container = pending.pop()
            # select dissectors for 
            for dissector in self.__dissectors[next_container.mime_type]:
                # take worker results
                for r in pool.results():
                    # add new containers to pending LIFO
                    pending.push(r)
                while not pool.exec_task(func=run_dissector, args=(dissector, next_container)):
                    sleep(1)


    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def load_dissectors(self):
        lgr.debug('Dissector.load_dissectors()')
        ## add dissectors below
        self.__register_dissector(octet_stream_dissector)
        ## add dissectors before