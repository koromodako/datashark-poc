# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import os
from importlib import import_module
from utils.config import config
from utils.config import module_config
from utils.config import section_config
from dissection.container import Container
from utils.helpers.logging import get_logger
from dissection.hashdatabase import HashDatabase
from utils.helpers.action_group import ActionGroup
from utils.threading.workerpool import WorkerPool
from dissection.dissectiondatabase import DissectionDatabase
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================


def dissect(container, dissectors):
    # -------------------------------------------------------------------------
    # dissect
    # -------------------------------------------------------------------------
    LGR.debug('dissect()')
    LGR.info('dissection of <{}> begins...'.format(container.realname))
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


def dissection_routine(container, whitelist, blacklist, dissectors):
    # -------------------------------------------------------------------------
    # dissection_routine
    # -------------------------------------------------------------------------
    LGR.debug('dissection_routine()')
    iq = []
    oq = []
    # foreach new container resulting of the dissection, add it to the
    # dissect queue
    for new_container in dissect(container, dissectors):

        new_container.set_parent(container)

        if whitelist.contains(container):
            LGR.info('matching whitelisted container. skipping!')
            new_container.whitelisted = True
            DissectionDatabase.persist_container(new_container)
            continue    # skip processing (whitelisted)

        elif blacklist.contains(container):
            LGR.warn('matching blacklisted container. flagged!')
            new_container.flagged = True
            new_container.blacklisted = True
            DissectionDatabase.persist_container(new_container)
            continue    # skip processing (blacklisted)

        else:
            iq.append(new_container)    # processing needed

    DissectionDatabase.persist_container(container)
    return (iq, oq)
# =============================================================================
# CLASSES
# =============================================================================


class Dissection(object):
    # -------------------------------------------------------------------------
    # Dissection
    # -------------------------------------------------------------------------
    MANDATORY_FUNCS = set([
        'mimes',
        'dissect',
        'can_dissect',
        'configure',
        'action_group'
    ])

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Dissection, self).__init__()
        self._dissectors = {}
        self.__whitelist = None
        self.__blacklist = None

    def __configure_dissector(self, dissector):
        # ---------------------------------------------------------------------
        # __register_dissector
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.__configure_dissector()')
        conf = module_config(dissector.name)
        return dissector.configure(conf)

    def __register_dissector(self, dissector):
        # ---------------------------------------------------------------------
        # __register_dissector
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.__register_dissector()')

        mod_funcs = set(dir(dissector))
        missing_funcs = mod_funcs.intersection(Dissection.MANDATORY_FUNCS)
        missing_funcs = list(missing_funcs.symmetric_difference(
            Dissection.MANDATORY_FUNCS))

        if len(missing_funcs) > 0:
            error = "failed to add:\n"
            error += "\t{}\n".format(dissector)
            error += "\t>>> details: missing mandatory functions"
            error += " ({}).".format(missing_funcs)
            LGR.error(error)
            return False

        for mime in dissector.mimes():
            if self._dissectors.get(mime, None) is None:
                self._dissectors[mime] = []
            self._dissectors[mime].append(dissector)

        return True

    def __import_dissector(self, import_path):
        # ---------------------------------------------------------------------
        # __import_dissector
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.__import_dissector(<{}>)'.format(import_path))

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

    def __init_dissection_db(self):
        # ---------------------------------------------------------------------
        # __init_dissection_db
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.__init_dissection_db()')
        return DissectionDatabase.init(section_config('dissectiondb'))

    def __term_dissection_db(self):
        # ---------------------------------------------------------------------
        # __term_dissection_db
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.__term_dissection_db()')
        DissectionDatabase.term()

    def load_dissectors(self):
        # ---------------------------------------------------------------------
        # load_dissectors
        # ---------------------------------------------------------------------
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
                            LGR.error('dissector import failure: see error '
                                      'above.')
                            exit(1)

        with_errors = ' (with errors).' if not ok else '.'
        LGR.info('dissectors loaded{}'.format(with_errors))
        return ok

    def load_hashdatabases(self):
        # ---------------------------------------------------------------------
        # load_hashdatabases
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.load_hashdatabases()')

        LGR.info('loading whitelist database...')
        self.__whitelist = HashDatabase('whitelist', config('whitelist'))

        LGR.info('loading blacklist database...')
        self.__blacklist = HashDatabase('blacklist', config('blacklist'))

    def dissectors(self):
        # ---------------------------------------------------------------------
        # dissectors
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.dissectors()')
        dissectors = []
        for mime in sorted(list(self._dissectors.keys())):
            mime_dissectors = []
            for dissector in self._dissectors[mime]:
                mime_dissectors.append(dissector.name)
            dissectors.append([mime, sorted(mime_dissectors)])
        return dissectors

    def dissect(self, path, num_threads=1):
        # ---------------------------------------------------------------------
        # dissect
        # ---------------------------------------------------------------------
        LGR.debug('Dissection.dissect()')

        LGR.info('starting dissection processes...')
        if not self.__init_dissection_db():
            return False

        container = Container(path, os.path.basename(path))

        kwargs = {
            'whitelist': self.__whitelist,
            'blacklist': self.__blacklist,
            'dissectors': self._dissectors
        }

        pool = WorkerPool(config('num_workers', default=1))
        pool.map(dissection_routine, kwargs, tasks=[container])

        LGR.info('dissection done.')
        self.__term_dissection_db()
        return True


class DissectionActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # DissectionActionGroup
    # -------------------------------------------------------------------------
    @staticmethod
    def dissectors(keywords, args):
        # ---------------------------------------------------------------------
        # dissectors
        # ---------------------------------------------------------------------
        LGR.debug('DissectionActionGroup.dissectors()')

        dissection = Dissection()
        dissection.load_dissectors()
        dissectors = dissection.dissectors()

        if len(dissectors) == 0:
            LGR.error('no dissector registered.')
            return

        LGR.info('dissectors:')
        for mime in dissectors:
            LGR.info('\t+ {}'.format(mime[0]))
            for dissector in mime[1]:
                LGR.info('\t\t+ {}'.format(dissector))

    @staticmethod
    def dissector(keywords, args):
        # ---------------------------------------------------------------------
        # dissector
        # ---------------------------------------------------------------------
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

    @staticmethod
    def dissect(keywords, args):
        # ---------------------------------------------------------------------
        # dissect
        # ---------------------------------------------------------------------
        LGR.debug('DissectionActionGroup.dissect()')
        dissection = Dissection()
        dissection.load_dissectors()
        dissection.load_hashdatabases()
        if len(args.files) == 0:
            LGR.error('give at least one file to dissect.')
            return

        for f in args.files:
            dissection.dissect(f)

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(DissectionActionGroup, self).__init__('dissection', {
            'list': ActionGroup.action(DissectionActionGroup.dissectors,
                                       "list dissectors."),
            'dissector': ActionGroup.action(DissectionActionGroup.dissector,
                                            "forward actions to given"
                                            "dissector."),
            'dissect': ActionGroup.action(DissectionActionGroup.dissect,
                                          "dissect given container.")
        })
