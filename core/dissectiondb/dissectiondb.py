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
from multiprocessing import Lock
from utils.logging import get_logger
from utils.wrapper import trace_static
from utils.action_group import ActionGroup
import dissectiondb.adapters.json_adapter as json_adapter
import dissectiondb.adapters.sqlite_adapter as sqlite_adapter
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class DissectionDB(object):
    # -------------------------------------------------------------------------
    # DissectionDB
    # -------------------------------------------------------------------------
    __ADAPTERS = {
        "json": json_adapter,
        "sqlite": sqlite_adapter
    }
    __DB_ADAPTER = None
    __VALID = False
    __LOCK = Lock()

    @staticmethod
    @trace_static(LGR, 'DissectionDB')
    def adapters():
        # ---------------------------------------------------------------------
        # adapters
        # ---------------------------------------------------------------------
        return list(DissectionDB.__ADAPTERS.keys())

    @staticmethod
    @trace_static(LGR, 'DissectionDB')
    def init(config):
        # ---------------------------------------------------------------------
        # init
        # ---------------------------------------------------------------------
        DissectionDB.__DB_ADAPTER = DissectionDB.__ADAPTERS.get(
            config.mode)
        DissectionDB.__VALID = DissectionDB.__DB_ADAPTER.init(
            config)

        if not DissectionDB.__VALID:
            LGR.error("database initialization failed.")
            DissectionDB.__DB_ADAPTER = None

        return DissectionDB.__VALID

    @staticmethod
    @trace_static(LGR, 'DissectionDB')
    def term():
        # ---------------------------------------------------------------------
        # term
        # ---------------------------------------------------------------------
        DissectionDB.__DB_ADAPTER.term()
        DissectionDB.__DB_ADAPTER = None
        DissectionDB.__VALID = False

    @staticmethod
    @trace_static(LGR, 'DissectionDB')
    def is_valid():
        # ---------------------------------------------------------------------
        # is_valid
        # ---------------------------------------------------------------------
        return DissectionDB.__VALID

    @staticmethod
    @trace_static(LGR, 'DissectionDB')
    def persist_container(container):
        # ---------------------------------------------------------------------
        # persist_container
        # ---------------------------------------------------------------------
        DissectionDB.__LOCK.acquire()
        status = DissectionDB.__DB_ADAPTER.persist(container)
        DissectionDB.__LOCK.release()
        return status


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
    @trace_static(LGR, 'DissectionDBActionGroup')
    def list(keywords, args):
        # ---------------------------------------------------------------------
        # list
        # ---------------------------------------------------------------------
        text = '\nAdaptaters:'
        for adapter in DissectionDB.adapters():
            text += '\n\t+ {}'.format(adapter)
        text += '\n'
        LGR.info(text)
