# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: dissectiondatabase.py
#    date: 2017-11-28
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import utils.config as config
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_static
from utils.action_group import ActionGroup
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class DissectionDB(object):
    ADAPTERS = None
    # -------------------------------------------------------------------------
    # HashDB
    # -------------------------------------------------------------------------
    def __init__(self, name, conf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(HashDB, self).__init__()
        self.name = name
        self.conf = conf
        self.valid = False
        self.adapter = None
        if DissectionDB.ADAPTERS is None:
            pi = PluginImporter('dissectiondb.adapters',
                                __file__, 'adapters',
                                expected_funcs=set(['instance']))

            if not pi.load_plugins():
                LGR.warning("some adapters failed to be loaded.")

            DissectionDB.ADAPTERS = copy.deepcopy(pi.plugins)

    @trace()
    def init(self, mode):
        # ---------------------------------------------------------------------
        # init
        # ---------------------------------------------------------------------
        if not self.conf.has('adapter'):
            LGR.error("invalid configuration of dissectiondb adapter or "
                      "missing value.")
            return False

        adapter_mod = self.ADAPTERS.get(self.conf.adapter)
        if adapter_mod is None:
            LGR.error("failed to load adapter: <{}>".format(self.conf.adapter))
            return False

        self.adapter = adapter_mod.instance(self.conf)
        self.adapter.init(mode)
        if not self.adapter.is_valid():
            LGR.error("invalid adapter instance.")
            return False

        self.valid = True
        return True

    @trace()
    def term(self):
        # ---------------------------------------------------------------------
        # term
        # ---------------------------------------------------------------------
        if self.valid:
            self.adapter.term()
            self.adapter = None
            self.valid = False

    @trace()
    def persist(self, container):
        # ---------------------------------------------------------------------
        # insert
        # ---------------------------------------------------------------------
        if not self.valid:
            return False

        if not self.adapter.insert(container.to_dict()):
            return False

        return True

class DissectionDBActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # DissectionDBActionGroup
    # -------------------------------------------------------------------------
    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(DissectionDBActionGroup, self).__init__('dissectiondb', {
            'list': ActionGroup.action(DissectionDBActionGroup.list,
                                       "list of available database adapters.")
        })

    @staticmethod
    @trace_static('DissectionDBActionGroup')
    def list(keywords, args):
        # ---------------------------------------------------------------------
        # list
        # ---------------------------------------------------------------------
        conf = config.load_from_value('dissection_db')
        dissection_db = DissectionDB(None, None)
        adapters = sorted(DissectionDB.ADAPTERS.keys())

        text = "\nadapters:"

        if len(adapters) > 0:
            for adapter in adapters:
                text += "\n\t+ {}".format(adapter)
        else:
            text += "\n\tno adapter available."

        text += "\n"
        LGR.info(text)
