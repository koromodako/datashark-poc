#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: dissection.py
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
from dissection.container       import Container
from utils.helpers.logging      import get_logger
from dissection.hashdatabase    import HashDatabase
from utils.helpers.action_group import ActionGroup
from utils.threading.workerpool import WorkerPool
#===============================================================================
# GLOBAL
#===============================================================================
LGR = get_logger(__name__)
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# dissect
#-------------------------------------------------------------------------------
def dissect(container, dissectors):
    containers = []
    #
    dissection_mods = dissectors.get(container.mime_type, None)
    if dissection_mods is None:
        LGR.warn('cannot find dissector for: {}'.format(container.mime_type))
        container.flagged = True
        return []
    #
    for dissector in dissection_mods:
        if dissector.can_dissect(container):
            containers += dissector.dissect(container)
    #
    return containers
#-------------------------------------------------------------------------------
# dissection_routine
#-------------------------------------------------------------------------------
def dissection_routine(container, whitelist, blacklist, dissectors):
        iq = []
        oq = []
        # foreach new container resulting of the dissection, add it to the 
        # dissect queue
        for new_container in dissect(container, dissectors):
            #
            container.add_child(new_container)
            #    
            if whitelist.contains(container):
                LGR.info('matching whitelisted container. skipping!')
                new_container.whitelisted = True 
                continue # skip processing (whitelisted)
            elif blacklist.contains(container):
                LGR.warn('matching blacklisted container. flagged!')
                new_container.flagged = True
                new_container.blacklisted = True
                continue # skip processing (blacklisted)
            else:
                iq.append(new_container) # processing needed
        # return lists
        return (iq, oq)
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Dissection
#-------------------------------------------------------------------------------
class Dissection(object):
    MANDATORY_FUNCS = set([
        'mimes',
        'dissect',
        'can_dissect',
        'configure',
        'action_group'
    ])
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(Dissection, self).__init__()
        self._dissectors = {}
        self.__whitelist = None
        self.__blacklist = None
    #---------------------------------------------------------------------------
    # __register_dissector
    #---------------------------------------------------------------------------
    def __configure_dissector(self, dissector):
        LGR.debug('Dissection.__configure_dissector()')
        conf = module_config(dissector.name)
        return dissector.configure(conf)
    #---------------------------------------------------------------------------
    # __register_dissector
    #---------------------------------------------------------------------------
    def __register_dissector(self, dissector):
        LGR.debug('Dissection.__register_dissector()')
        mod_funcs = set(dir(dissector))
        missing_funcs = mod_funcs.intersection(Dissection.MANDATORY_FUNCS)
        missing_funcs = list(missing_funcs.symmetric_difference(Dissection.MANDATORY_FUNCS))
        if len(missing_funcs) > 0:
            LGR.error("""failed to add:
    {}
    >>> details: missing mandatory functions ({}).""".format(dissector, missing_funcs))
            return False
        for mime in dissector.mimes():
            if self._dissectors.get(mime, None) is None:
                self._dissectors[mime] = []
            self._dissectors[mime].append(dissector)
        return True
    #---------------------------------------------------------------------------
    # __import_dissector
    #---------------------------------------------------------------------------
    def __import_dissector(self, import_path):
        LGR.debug('importing: {}'.format(import_path))
        try:
            dissector = import_module(import_path)
            dissector.name = import_path.split('.')[-1]
        except Exception as e:
            LGR.exception('failed to import: {}'.format(import_path))
            return False
        if not self.__register_dissector(dissector):
            LGR.warning('failed to load dissector, see errors above.')
            return False
        if not self.__configure_dissector(dissector):
            LGR.warning('failed to configure dissector, see errors above.')
            return False
        LGR.info('<{}> imported successfully.'.format(import_path))
        return True
    #---------------------------------------------------------------------------
    # load_dissectors
    #---------------------------------------------------------------------------
    def load_dissectors(self):
        LGR.debug('Dissection.load_dissectors()')
        LGR.info('loading dissectors...')
        ok = True
        script_path = os.path.dirname(__file__)
        search_path = os.path.join(script_path, 'dissectors')
        LGR.debug('dissectors search_path: {}'.format(search_path))
        for root, dirs, files in os.walk(search_path):
            rel_root = root.replace(search_path, '')[1:]
            for f in files:
                if f.endswith('.py'):
                    rel_import_path = search_path.split(os.sep)[-2:]
                    rel_import_path += rel_root.split(os.sep)
                    rel_import_path.append(f[:-3])
                    import_path = '.'.join(rel_import_path)
                    if not self.__import_dissector(import_path):
                        ok = False
                        if not config('skip_failing_import', False):
                            LGR.error('dissector import failure: see error above.')
                            exit(1)
        LGR.info('dissectors loaded{}'.format(' (with errors).' if not ok else '.'))
        return ok
    #---------------------------------------------------------------------------
    # load_hashdatabases
    #---------------------------------------------------------------------------
    def load_hashdatabases(self):
        LGR.debug('Dissection.load_hashdatabases()')
        LGR.info('loading whitelist database...')
        self.__whitelist = HashDatabase('whitelist', config('whitelist'))
        LGR.info('loading blacklist database...')
        self.__blacklist = HashDatabase('blacklist', config('blacklist'))
    #---------------------------------------------------------------------------
    # dissectors
    #---------------------------------------------------------------------------
    def dissectors(self):
        LGR.debug('Dissection.dissectors()')
        dissectors = []
        for mime in sorted(list(self._dissectors.keys())):
            mime_dissectors = []
            for dissector in self._dissectors[mime]:
                mime_dissectors.append(dissector.name)
            dissectors.append([mime, sorted(mime_dissectors)])
        return dissectors
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    def dissect(self, path, num_threads=1):
        LGR.debug('Dissection.dissect()')
        LGR.info('starting dissection processes...')
        container = Container(path, os.path.basename(path))
        kwargs = {
            'whitelist': self.__whitelist,
            'blacklist': self.__blacklist,
            'dissectors': self._dissectors 
        }
        pool = WorkerPool(config('num_workers', default=1))
        pool.map(dissection_routine, kwargs, tasks=[container])
        LGR.info('dissection done.')
        return container
#-------------------------------------------------------------------------------
# DissectionActionGroup
#-------------------------------------------------------------------------------
class DissectionActionGroup(ActionGroup):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(DissectionActionGroup, self).__init__('dissection', {
            'dissectors': ActionGroup.action(DissectionActionGroup.dissectors, 
                'list dissectors.'),
            'dissector': ActionGroup.action(DissectionActionGroup.dissector, 
                'forward actions to given dissector.'),
            'dissect': ActionGroup.action(DissectionActionGroup.dissect, 
                'dissect given container.')
        })
    #---------------------------------------------------------------------------
    # dissectors
    #---------------------------------------------------------------------------
    @staticmethod
    def dissectors(keywords, args):
        LGR.debug('DissectionActionGroup.dissectors()')
        dissection = Dissection()
        dissection.load_dissectors()
        dissectors = dissection.dissectors()
        LGR.info('dissectors:')
        if len(dissectors) > 0:
            for mime in dissectors:
                LGR.info('\t+ {}'.format(mime[0]))
                for dissector in mime[1]:
                    LGR.info('\t\t+ {}'.format(dissector))
        else:
            LGR.error('no dissector registered.')
    #---------------------------------------------------------------------------
    # dissector
    #---------------------------------------------------------------------------
    @staticmethod
    def dissector(keywords, args):
        LGR.debug('DissectionActionGroup.dissector()')
        # check args
        if len(keywords) > 0:
            # create a dissection and load dissectors
            dissection = Dissection()
            dissection.load_dissectors()
            # create action group mapping
            actions = {}
            for dissectors in dissection._dissectors.values():
                for dissector in dissectors:
                    act_grp = dissector.action_group()
                    actions[act_grp.name] = act_grp
            # create action group to perform action
            ActionGroup('dissector', actions).perform_action(keywords, args)
        else:
            LGR.error('missing keyword.')
    #---------------------------------------------------------------------------
    # dissect
    #---------------------------------------------------------------------------
    @staticmethod
    def dissect(keywords, args):
        LGR.debug('DissectionActionGroup.dissect()')
        dissection = Dissection()
        dissection.load_dissectors()
        dissection.load_hashdatabases()
        if len(args.files) > 0:
            for f in args.files:
                dissection.dissect(f)
        else:
            LGR.error('give at least one file to dissect.')