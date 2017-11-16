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
import os
from importlib                  import import_module
from utils.config               import config
from utils.config               import module_config
from utils.helpers.logging      import get_logger
from model.objects.container    import Container
from utils.threading.workerpool import WorkerPool
#===============================================================================
# GLOBAL
#===============================================================================
LGR = get_logger(__name__)
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Dissector
#-------------------------------------------------------------------------------
class Dissector(object):
    MANDATORY_FUNCS = set([
        'mimes',
        'dissect',
        'can_dissect',
        'configure'
    ])
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(Dissector, self).__init__()
        self.__dissectors = {}
    #---------------------------------------------------------------------------
    # __register_dissector
    #---------------------------------------------------------------------------
    def __configure_dissector(self, dissector):
        LGR.debug('Dissector.__configure_dissector()')
        conf = module_config(dissector.name)
        return dissector.configure(conf)
    #---------------------------------------------------------------------------
    # __register_dissector
    #---------------------------------------------------------------------------
    def __register_dissector(self, dissector):
        LGR.debug('Dissector.__register_dissector()')
        mod_funcs = set(dir(dissector))
        missing_funcs = mod_funcs.intersection(Dissector.MANDATORY_FUNCS)
        missing_funcs = list(missing_funcs.symmetric_difference(Dissector.MANDATORY_FUNCS))
        if len(missing_funcs) > 0:
            LGR.error("""failed to add:
    {0}
    >>> details: missing mandatory functions ({1}).""".format(dissector, missing_funcs))
            return False
        for mime in dissector.mimes():
            if self.__dissectors.get(mime, None) is None:
                self.__dissectors[mime] = []
            self.__dissectors[mime].append(dissector)
        return True
    #---------------------------------------------------------------------------
    # __import_dissector
    #---------------------------------------------------------------------------
    def __import_dissector(self, import_path):
        LGR.debug('importing: {0}'.format(import_path))
        try:
            dissector = import_module(import_path)
            dissector.name = import_path.split('.')[-1]
        except Exception as e:
            LGR.error('failed to import: {0}'.format(import_path))
            LGR.error('error: {0}'.format(e))
            return False
        if not self.__register_dissector(dissector):
            LGR.warning('failed to load dissector, see errors above.')
            return False
        if not self.__configure_dissector(dissector):
            LGR.warning('failed to configure dissector, see errors above.')
            return False
        return True
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def load_dissectors(self):
        LGR.debug('Dissector.load_dissectors()')
        LGR.info('loading dissectors...')
        ok = True
        script_path = os.path.dirname(__file__)
        search_path = os.path.join(script_path, 'dissectors')
        rel_import_path = search_path.split(os.sep)[-2:]
        LGR.debug('dissectors search_path: {0}'.format(search_path))
        for root, dirs, files in os.walk(search_path):
            rel_root = root.replace(search_path, '')[1:]
            for f in files:
                if f.endswith('.py'):
                    rel_import_path += rel_root.split(os.sep)
                    rel_import_path.append(f[:-3])
                    import_path = '.'.join(rel_import_path)
                    if not self.__import_dissector(import_path):
                        ok = False
        LGR.info('dissectors loaded{0}'.format(' (with errors).' if not ok else '.'))
        return ok
    #---------------------------------------------------------------------------
    # dissectors
    #---------------------------------------------------------------------------
    def dissectors(self):
        LGR.debug('Dissector.dissectors()')
        dissectors = []
        for mime in sorted(list(self.__dissectors.keys())):
            mime_dissectors = []
            for dissector in self.__dissectors[mime]:
                mime_dissectors.append(dissector.name)
            dissectors.append([mime, sorted(mime_dissectors)])
        return dissectors
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def dissect(self, path, num_threads=1):
        LGR.debug('Dissector.dissect()')
        container = Container(path)
        pool = WorkerPool(config('num_workers'), self.__dissectors)
        pool.process([container]) # will hang until container has been fully processed.