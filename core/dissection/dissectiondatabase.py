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
from utils.action_group import ActionGroup
import dissection.database_adapters.json_adapter as json_adapter
import dissection.database_adapters.sqlite_adapter as sqlite_adapter
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class DissectionDatabase(object):
    # -------------------------------------------------------------------------
    # DissectionDatabase
    # -------------------------------------------------------------------------
    __ADAPTERS = {
        "json": json_adapter,
        "sqlite": sqlite_adapter
    }
    __DB_ADAPTER = None
    __VALID = False
    __LOCK = Lock()

    @staticmethod
    def adapters():
        # ---------------------------------------------------------------------
        # adapters
        # ---------------------------------------------------------------------
        LGR.debug('DissectionDatabase.adpaters()')
        return list(DissectionDatabase.__ADAPTERS.keys())

    @staticmethod
    def init(config):
        # ---------------------------------------------------------------------
        # init
        # ---------------------------------------------------------------------
        LGR.debug('DissectionDatabase.init()')
        DissectionDatabase.__DB_ADAPTER = DissectionDatabase.__ADAPTERS.get(
            config.mode)
        DissectionDatabase.__VALID = DissectionDatabase.__DB_ADAPTER.init(
            config)

        if not DissectionDatabase.__VALID:
            LGR.error('database initialization failed.')
            DissectionDatabase.__DB_ADAPTER = None

        return DissectionDatabase.__VALID

    @staticmethod
    def term():
        # ---------------------------------------------------------------------
        # term
        # ---------------------------------------------------------------------
        LGR.debug('DissectionDatabase.term()')
        DissectionDatabase.__DB_ADAPTER.term()
        DissectionDatabase.__DB_ADAPTER = None
        DissectionDatabase.__VALID = False

    @staticmethod
    def is_valid():
        # ---------------------------------------------------------------------
        # is_valid
        # ---------------------------------------------------------------------
        LGR.debug('DissectionDatabase.is_valid()')
        return DissectionDatabase.__VALID

    @staticmethod
    def persist_container(container):
        # ---------------------------------------------------------------------
        # persist_container
        # ---------------------------------------------------------------------
        LGR.debug('DissectionDatabase.persist_container()')
        DissectionDatabase.__LOCK.acquire()
        status = DissectionDatabase.__DB_ADAPTER.persist(container)
        DissectionDatabase.__LOCK.release()
        return status


class DissectionDatabaseActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # DissectionDatabaseActionGroup
    # -------------------------------------------------------------------------
    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(DissectionDatabaseActionGroup, self).__init__('dissectiondb', {
            'list': ActionGroup.action(DissectionDatabaseActionGroup.list,
                                       "list of available database adapters.")
        })

    @staticmethod
    def list(keywords, args):
        # ---------------------------------------------------------------------
        # list
        # ---------------------------------------------------------------------
        text = '\nAdaptaters:'
        for adapter in DissectionDatabase.adapters():
            text += '\n\t+ {}'.format(adapter)
        text += '\n'
        LGR.info(text)
