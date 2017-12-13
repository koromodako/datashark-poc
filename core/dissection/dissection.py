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
from utils.config import config
from utils.config import module_config
from utils.config import section_config
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.wrapper import trace_static
from hashdb.hashdb import HashDB
from utils.workerpool import WorkerPool
from utils.action_group import ActionGroup
from container.container import Container
from utils.plugin_importer import PluginImporter
from dissectiondb.dissectiondb import DissectionDB
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================


@trace_func(LGR)
def dissect(container, dissectors):
    # -------------------------------------------------------------------------
    # dissect
    # -------------------------------------------------------------------------
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


@trace_func(LGR)
def carve(container, carvers):
    # -------------------------------------------------------------------------
    # dissect
    # -------------------------------------------------------------------------
    LGR.info('carving of <{}> begins...'.format(container.realname))
    containers = []
    #
    for carver in carvers:
        containers += carver.carve(container)
    #
    return containers


@trace_func(LGR)
def dissection_routine(container, whitelist, blacklist, dissectors, carvers):
    # -------------------------------------------------------------------------
    # dissection_routine
    # -------------------------------------------------------------------------
    iq = []
    oq = []

    # is container whitlisted ?
    if whitelist.contains(container):
        LGR.info("matching whitelisted container. skipping!")
        container.set_flag(Container.Flag.WHITELISTED)
        DissectionDB.persist_container(container)
        return (iq, oq)     # interrupt dissection process here

    # is container blacklisted ?
    if blacklist.contains(container):
        LGR.warn("matching blacklisted container. flagged!")
        container.set_flag(Container.Flag.BLACKLISTED)
        DissectionDB.persist_container(container)
        return (iq, oq)     # interrupt dissection process here

    # is dissection required ?
    if not container.has_flag(Container.Flag.DISSECTED):
        # dissect container and iterate over children
        for new_container in dissect(container, dissectors):
            new_container.set_parent(container)
            iq.append(new_container)
        # container dissection: OK => carving might be required
        container.set_flag(Container.Flag.DISSECTED)

    # is carving required ?
    if (container.has_flag(Container.Flag.CARVING_REQUIRED) and
       not container.has_flag(Container.Flag.CARVED)):
        # carve container and iterate over carving results
        for new_container in carve(container, carvers):
            new_container.set_parent(container)
            iq.append(new_container)
        # container carving: OK

    # finally persist container
    DissectionDB.persist_container(container)
    return (iq, oq)
# =============================================================================
# CLASSES
# =============================================================================


class Dissection(object):
    # -------------------------------------------------------------------------
    # Dissection
    # -------------------------------------------------------------------------
    DISSECTOR_EXPECTED_FUNCS = set([
        'mimes',
        'dissect',
        'configure',
        'can_dissect',
        'action_group'
    ])
    CARVER_EXPECTED_FUNCS = set([
        'carve',
        'configure',
        'action_group'
    ])

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Dissection, self).__init__()
        self._dissectors = {}
        self._carvers = []
        self.__whitelist = None
        self.__blacklist = None

    @trace(LGR)
    def __init_dissection_db(self):
        # ---------------------------------------------------------------------
        # __init_dissection_db
        # ---------------------------------------------------------------------
        return DissectionDB.init(section_config('dissectiondb'))

    @trace(LGR)
    def __term_dissection_db(self):
        # ---------------------------------------------------------------------
        # __term_dissection_db
        # ---------------------------------------------------------------------
        DissectionDB.term()

    @trace(LGR)
    def load_dissectors(self):
        # ---------------------------------------------------------------------
        # load_dissectors
        # ---------------------------------------------------------------------
        LGR.info("loading dissectors...")

        script_absdir = os.path.dirname(__file__)
        search_root = os.path.join(script_absdir, 'dissectors')

        import_root = ['dissection', 'dissectors']

        pi = PluginImporter(import_root, search_root,
                            expected_funcs=Dissection.DISSECTOR_EXPECTED_FUNCS)

        if not pi.load_plugins():
            LGR.warn("some dissectors have failed while being loaded.")

        for dissector in pi.plugins.values():

            conf = module_config(dissector.name)
            if not dissector.configure(conf):
                LGR.warning("failed to configure dissector, see errors above.")
                return False

            for mime in dissector.mimes():
                if self._dissectors.get(mime, None) is None:
                    self._dissectors[mime] = [dissector]
                else:
                    self._dissectors[mime].append(dissector)

            LGR.info("dissector <{}> import successful.".format(dissector.name))

        return True

    @trace(LGR)
    def load_carvers(self):
        # ---------------------------------------------------------------------
        # load_carvers
        # ---------------------------------------------------------------------
        LGR.info("loading carvers...")

        script_absdir = os.path.dirname(__file__)
        search_root = os.path.join(script_absdir, 'carvers')

        import_root = ['dissection', 'carvers']

        pi = PluginImporter(import_root, search_root,
                            expected_funcs=Dissection.CARVER_EXPECTED_FUNCS)

        if not pi.load_plugins():
            LGR.warn("some carvers have failed while being loaded.")

        for carver in pi.plugins.values():

            conf = module_config(carver.name)
            if not carver.configure(conf):
                LGR.warning("failed to configure dissector, see errors above.")
                return False

            self._carvers.append(carver)
            LGR.info("carver <{}> import successful.".format(carver.name))

        return True

    @trace(LGR)
    def load_hashdatabases(self):
        # ---------------------------------------------------------------------
        # load_hashdatabases
        # ---------------------------------------------------------------------
        LGR.info("loading whitelist database...")
        self.__whitelist = HashDB('whitelist', config('whitelist'))

        LGR.info("loading blacklist database...")
        self.__blacklist = HashDB('blacklist', config('blacklist'))

    @trace(LGR)
    def dissectors(self):
        # ---------------------------------------------------------------------
        # dissectors
        # ---------------------------------------------------------------------
        dissectors = []
        for mime in sorted(list(self._dissectors.keys())):
            mime_dissectors = []
            for dissector in self._dissectors[mime]:
                mime_dissectors.append(dissector.name)
            dissectors.append([mime, sorted(mime_dissectors)])
        return dissectors

    @trace(LGR)
    def carvers(self):
        # ---------------------------------------------------------------------
        # carvers
        # ---------------------------------------------------------------------
        return [carver.name for carver in self._carvers]

    @trace(LGR)
    def dissect(self, path, num_threads=1):
        # ---------------------------------------------------------------------
        # dissect
        # ---------------------------------------------------------------------
        LGR.info('starting dissection processes...')
        if not self.__init_dissection_db():
            return False

        container = Container(path, os.path.basename(path))

        kwargs = {
            'whitelist': self.__whitelist,
            'blacklist': self.__blacklist,
            'dissectors': self._dissectors,
            'carvers': self._carvers
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
    @trace_static(LGR, 'DissectionActionGroup')
    def dissectors(keywords, args):
        # ---------------------------------------------------------------------
        # dissectors
        # ---------------------------------------------------------------------
        dissection = Dissection()
        dissection.load_dissectors()
        dissectors = dissection.dissectors()

        if len(dissectors) == 0:
            LGR.error("no dissector registered.")
            return

        LGR.info('dissectors:')
        for mime in dissectors:
            LGR.info('\t+ {}'.format(mime[0]))
            for dissector in mime[1]:
                LGR.info('\t\t+ {}'.format(dissector))

    @staticmethod
    @trace_static(LGR, 'DissectionActionGroup')
    def carvers(keywords, args):
        # ---------------------------------------------------------------------
        # carvers
        # ---------------------------------------------------------------------
        dissection = Dissection()
        dissection.load_carvers()
        carvers = dissection.carvers()

        if len(carvers) == 0:
            LGR.error("no carver registered.")
            return

        LGR.info('carvers:')
        for carver in carvers:
            LGR.info('\t+ {}'.format(carver))

    @staticmethod
    @trace_static(LGR, 'DissectionActionGroup')
    def dissector(keywords, args):
        # ---------------------------------------------------------------------
        # dissector
        # ---------------------------------------------------------------------
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
            LGR.error("missing keyword.")

    @staticmethod
    @trace_static(LGR, 'DissectionActionGroup')
    def carver(keywords, args):
        # ---------------------------------------------------------------------
        # carver
        # ---------------------------------------------------------------------
        # check args
        if len(keywords) > 0:
            # create a dissection and load dissectors
            dissection = Dissection()
            dissection.load_carvers()
            # create action group mapping
            actions = {}
            for dissectors in dissection._carvers:
                for carver in carvers:
                    act_grp = carver.action_group()
                    actions[act_grp.name] = act_grp
            # create action group to perform action
            ActionGroup('carver', actions).perform_action(keywords, args)
        else:
            LGR.error("missing keyword.")

    @staticmethod
    @trace_static(LGR, 'DissectionActionGroup')
    def dissect(keywords, args):
        # ---------------------------------------------------------------------
        # dissect
        # ---------------------------------------------------------------------
        LGR.debug('DissectionActionGroup.dissect()')
        dissection = Dissection()
        dissection.load_carvers()
        dissection.load_dissectors()
        dissection.load_hashdatabases()
        if len(args.files) == 0:
            LGR.error("give at least one file to dissect.")
            return

        for f in args.files:
            dissection.dissect(f)

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(DissectionActionGroup, self).__init__('dissection', {
            'dissectors': ActionGroup.action(DissectionActionGroup.dissectors,
                                             "list dissectors."),
            'dissector': ActionGroup.action(DissectionActionGroup.dissector,
                                            "forward actions to given "
                                            "dissector."),
            'carvers': ActionGroup.action(DissectionActionGroup.carvers,
                                          "list carvers."),
            'carver': ActionGroup.action(DissectionActionGroup.carver,
                                         "forward actions to given "
                                         "carver."),
            'dissect': ActionGroup.action(DissectionActionGroup.dissect,
                                          "dissect given container.")
        })
