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
import os.path
import utils.config as config
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
##
## @brief      { function_description }
##
## @param      container   The container
## @param      dissectors  The dissectors
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def dissect(container, dissectors):
    LGR.info("dissection of <{}> begins...".format(container.realname))
    containers = []

    dissection_mods = dissectors.get(container.mime_type, None)
    if dissection_mods is None:
        LGR.warn("cannot find dissector for: {} => flagged.".format(
            container.mime_type))
        container.set_flag(Container.Flag.FLAGGED)
        return []

    for dissector in dissection_mods:
        if dissector.can_dissect(container):
            containers += dissector.dissect(container)

    return containers
##
## @brief      { function_description }
##
## @param      container  The container
## @param      carvers    The carvers
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def carve(container, carvers):
    LGR.info("carving of <{}> begins...".format(container.realname))
    containers = []

    for carver in carvers:
        containers += carver.carve(container)

    return containers
##
## @brief      { function_description }
##
## @param      container      The container
## @param      whitelist_db   The whitelist database
## @param      blacklist_db   The blacklist database
## @param      dissection_db  The dissection database
## @param      dissectors     The dissectors
## @param      carvers        The carvers
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def dissection_routine(container,
                       whitelist_db,
                       blacklist_db,
                       dissection_db,
                       dissectors,
                       carvers):
    iq = []
    oq = []
    # is the container whitelisted ?
    if whitelist_db.contains(container):
        LGR.info("whitelisted container => skipping!")
        container.set_flag(Container.Flag.WHITELISTED)
        dissection_db.persist(container)
        return (iq, oq)     # interrupt dissection process here
    # is the container blacklisted ?
    if blacklist_db.contains(container):
        LGR.warn("blacklisted container => flagged!")
        container.set_flag(Container.Flag.BLACKLISTED)
        dissection_db.persist(container)
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
    dissection_db.persist(container)
    return (iq, oq)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for dissection.
##
class Dissection(object):
    ##
    ## { item_description }
    ##
    DISSECTOR_EXPECTED_FUNCS = set([
        'mimes',
        'dissect',
        'configure',
        'can_dissect',
        'action_group'
    ])
    ##
    ## { item_description }
    ##
    CARVER_EXPECTED_FUNCS = set([
        'carve',
        'configure',
        'action_group'
    ])
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(Dissection, self).__init__()
        self.conf = config.load_from_value('dissection_config')
        LGR.debug("dissection configuration:\n{}".format(self.conf))
        self._dissectors = {}
        self._carvers = []
        self.__whitelist = None
        self.__blacklist = None
    ##
    ## @brief      Loads dissectors.
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def load_dissectors(self):
        noerr = True
        LGR.info("loading dissectors...")

        pi = PluginImporter('dissection.dissectors',
                            __file__, 'dissectors',
                            expected_funcs=Dissection.DISSECTOR_EXPECTED_FUNCS)

        if not pi.load_plugins():
            LGR.warn("some dissectors have failed while being loaded.")

        conf = self.conf.get('dissectors')

        for dissector in pi.plugins.values():

            dissector_conf = conf.get(dissector.name)
            LGR.debug("{} dissector configuration:\n{}".format(dissector.name,
                                                               dissector_conf))
            if dissector_conf is None:
                LGR.warn("dissector configuration is empty.")

            if not dissector.configure(dissector_conf):
                LGR.warn("failed to configure dissector, see errors above.")
                noerr = False

            for mime in dissector.mimes():
                if self._dissectors.get(mime, None) is None:
                    self._dissectors[mime] = [dissector]
                else:
                    self._dissectors[mime].append(dissector)

            LGR.info("dissector <{}> import successful.".format(dissector.name))

        return noerr
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def dissectors(self):
        dissectors = []

        for mime in sorted(list(self._dissectors.keys())):
            mime_dissectors = []

            for dissector in self._dissectors[mime]:
                mime_dissectors.append(dissector.name)

            dissectors.append([mime, sorted(mime_dissectors)])

        return dissectors
    ##
    ## @brief      Loads carvers.
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def load_carvers(self):
        noerr = True
        LGR.info("loading carvers...")

        pi = PluginImporter('dissection.carvers',
                            __file__, 'carvers',
                            expected_funcs=Dissection.CARVER_EXPECTED_FUNCS)

        conf = self.conf.get('carvers')

        if not pi.load_plugins():
            LGR.warn("some carvers have failed while being loaded.")

        for carver in pi.plugins.values():

            carver_conf = conf.get(carver.name)
            LGR.debug("{} carver configuration:\n{}".format(carver.name,
                                                            carver_conf))
            if carver_conf is None:
                LGR.warn("carver configuration is empty.")

            if not carver.configure(carver_conf):
                LGR.warn("failed to configure dissector, see errors above.")
                noerr = False

            self._carvers.append(carver)
            LGR.info("carver <{}> import successful.".format(carver.name))

        return noerr
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def carvers(self):
        return [carver.name for carver in self._carvers]
    ##
    ## @brief      { function_description }
    ##
    ## @param      path         The path
    ## @param      num_threads  The number threads
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def dissect(self, path, num_threads=1):
        LGR.info("starting dissection processes...")

        LGR.info("preparing dissection database...")
        dissection_db = DissectionDB(self.conf)
        if not dissection_db.init('w'):
            LGR.error("failed to init dissection db.")
            return False

        LGR.info("preparing whitelist database...")
        whitelist_conf = config.load_from_value('whitelist_config')
        whitelist_db = HashDB(whitelist_conf)
        if not whitelist_db.init('r'):
            LGR.warn("failed to init whitelist db.")

        LGR.info("preparing blacklist database...")
        blacklist_conf = config.load_from_value('blacklist_config')
        blacklist_db = HashDB(blacklist_conf)
        if not blacklist_db.init('r'):
            LGR.warn("failed to init blacklist db.")

        LGR.info("preparing first container...")
        container = Container(path, os.path.basename(path))

        kwargs = {
            'carvers': self._carvers,
            'dissectors': self._dissectors,
            'whitelist_db': whitelist_db,
            'blacklist_db': blacklist_db,
            'dissection_db': dissection_db
        }

        LGR.info("starting recursive processing of containers...")
        pool = WorkerPool(config.value('num_workers', 1))
        pool.map(dissection_routine, kwargs, tasks=[container])

        LGR.info("closing databases...")
        whitelist_db.term()
        blacklist_db.term()
        dissection_db.term()
        LGR.info("dissection done.")

        return True
##
## @brief      Class for dissection action group.
##
class DissectionActionGroup(ActionGroup):
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionActionGroup')
    def dissectors(keywords, args):
        dissection = Dissection()
        dissection.load_dissectors()
        dissectors = dissection.dissectors()

        if len(dissectors) == 0:
            LGR.warn("no dissector registered.")
            return True

        print("dissectors:")
        for mime in dissectors:
            print("\t+ {}".format(mime[0]))
            for dissector in mime[1]:
                print("\t\t+ {}".format(dissector))

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionActionGroup')
    def carvers(keywords, args):
        dissection = Dissection()
        dissection.load_carvers()
        carvers = dissection.carvers()

        if len(carvers) == 0:
            LGR.warn("no carver registered.")
            return True

        print("carvers:")
        for carver in carvers:
            print("\t+ {}".format(carver))

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionActionGroup')
    def dissector(keywords, args):
        # check args
        if len(keywords) == 0:
            LGR.error("missing keyword.")
            return False

        dissection = Dissection()
        dissection.load_dissectors()

        actions = {}
        for dissectors in dissection._dissectors.values():
            for dissector in dissectors:
                act_grp = dissector.action_group()
                actions[act_grp.name] = act_grp

        return ActionGroup('dissector', actions).perform_action(keywords, args)
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionActionGroup')
    def carver(keywords, args):
        # check args
        if len(keywords) == 0:
            LGR.error("missing keyword.")
            return False

        dissection = Dissection()
        dissection.load_carvers()

        actions = {}
        for dissectors in dissection._carvers:
            for carver in carvers:
                act_grp = carver.action_group()
                actions[act_grp.name] = act_grp

        return ActionGroup('carver', actions).perform_action(keywords, args)
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionActionGroup')
    def dissect(keywords, args):
        dissection = Dissection()
        dissection.load_carvers()
        dissection.load_dissectors()
        if len(args.files) == 0:
            LGR.error("give at least one file to dissect.")
            return False

        for f in args.files:
            if not dissection.dissect(f):
                return False

        return True
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
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
