# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: dissectiondatabase.py
#    date: 2017-11-28
#  author: koromodako
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 koromodako
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
import utils.config as config
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_static
from utils.action_group import ActionGroup
from utils.plugin_importer import PluginImporter
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for dissection db.
##
class DissectionDB(object):
    ##
    ## { item_description }
    ##
    ADAPTERS = None
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(DissectionDB, self).__init__()
        self.conf = conf
        LGR.debug("configuration:\n{}".format(self.conf))
        self.valid = False
        self.adapter = None
        if DissectionDB.ADAPTERS is None:
            pi = PluginImporter('dissectiondb.adapters',
                                __file__, 'adapters',
                                expected_funcs=set(['instance']))

            if not pi.load_plugins():
                LGR.warn("some adapters failed to be loaded.")

            DissectionDB.ADAPTERS = pi.plugins
    ##
    ## @brief      { function_description }
    ##
    ## @param      mode  The mode
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def init(self, mode):
        if self.conf is None:
            LGR.error("invalid dissection database configuration.")
            return False

        if not self.conf.has('adapter'):
            LGR.error("dissection database configuration must have 'adapter' "
                      "key.")
            return False

        if not self.conf.has('adapters'):
            LGR.error("dissection database configuration must have 'adapters' "
                      "key.")
            return False

        adapter_mod = self.ADAPTERS.get(self.conf.adapter)
        if adapter_mod is None:
            LGR.error("failed to load adapter: <{}>".format(self.conf.adapter))
            return False

        adapter_conf = self.conf.adapters.get(self.conf.adapter)
        LGR.debug("configuration:\n{}".format(adapter_conf))
        if adapter_conf is None:
            LGR.error("expected configuration:\n{}".format(
                self.adapter.expected_conf()))

        self.adapter = adapter_mod.instance(adapter_conf)
        self.adapter.init(mode)
        if not self.adapter.is_valid():
            LGR.error("invalid adapter instance.")
            return False

        self.valid = True
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def term(self):
        if self.valid:
            self.adapter.term()
            self.adapter = None
            self.valid = False
    ##
    ## @brief      { function_description }
    ##
    ## @param      container  The container
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def persist(self, container):
        if not self.valid:
            return False

        container_dict = container.to_dict()
        LGR.debug("container_dict:\n{}".format(container_dict))

        if not self.adapter.insert(container_dict):
            return False

        return True
##
## @brief      Class for dissection db action group.
##
class DissectionDBActionGroup(ActionGroup):
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('DissectionDBActionGroup')
    def adapters(keywords, args):
        conf = config.load_from_value('dissection_db')
        dissection_db = DissectionDB(None)
        adapters = sorted(DissectionDB.ADAPTERS.keys())

        text = "\nadapters:"

        if len(adapters) > 0:
            for adapter in adapters:
                text += "\n\t+ {}".format(adapter)
        else:
            text += "\n\tno adapter available."

        text += "\n"
        print(text)
        return True
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(DissectionDBActionGroup, self).__init__('dissectiondb', {
            'adapters': ActionGroup.action(DissectionDBActionGroup.adapters,
                                           "list of available database "
                                           "adapters.")
        })

