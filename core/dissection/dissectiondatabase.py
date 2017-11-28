#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
from multiprocessing                                import Lock
from utils.helpers.logging                          import get_logger
from utils.helpers.action_group                     import ActionGroup
import dissection.database_adapters.json_adapter    as json_adapter
import dissection.database_adapters.sqlite_adapter  as sqlite_adapter
#===============================================================================
# GLOBAL
#===============================================================================
LGR = get_logger(__name__)
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# DissectionDatabase
#-------------------------------------------------------------------------------
class DissectionDatabase(object):
    __ADAPTERS = {
        "json": json_adapter,
        "sqlite": sqlite_adapter
    }
    __DB_ADAPTER = None
    __VALID = False
    __LOCK = Lock()
    #---------------------------------------------------------------------------
    # adapters
    #---------------------------------------------------------------------------
    @staticmethod
    def adapters():
        LGR.debug('DissectionDatabase.adpaters()')
        return list(DissectionDatabase.__ADAPTERS.keys())
    #---------------------------------------------------------------------------
    # init
    #---------------------------------------------------------------------------
    @staticmethod
    def init(config):
        LGR.debug('DissectionDatabase.init()')
        DissectionDatabase.__DB_ADAPTER = DissectionDatabase.__ADAPTERS.get(config.mode)
        DissectionDatabase.__VALID = DissectionDatabase.__DB_ADAPTER.init(config)
        if not DissectionDatabase.__VALID:
            LGR.error('database initialization failed.')
            DissectionDatabase.__DB_ADAPTER = None
        return DissectionDatabase.__VALID
    #---------------------------------------------------------------------------
    # term
    #---------------------------------------------------------------------------
    @staticmethod
    def term():
        LGR.debug('DissectionDatabase.term()')
        DissectionDatabase.__DB_ADAPTER.term()
        DissectionDatabase.__DB_ADAPTER = None
        DissectionDatabase.__VALID = False
    #---------------------------------------------------------------------------
    # is_valid
    #---------------------------------------------------------------------------
    @staticmethod
    def is_valid():
        LGR.debug('DissectionDatabase.is_valid()')
        return DissectionDatabase.__VALID
    #---------------------------------------------------------------------------
    # persist_container
    #---------------------------------------------------------------------------
    @staticmethod
    def persist_container(container):
        LGR.debug('DissectionDatabase.persist_container()')
        DissectionDatabase.__LOCK.acquire()
        status = DissectionDatabase.__DB_ADAPTER.persist(container)
        DissectionDatabase.__LOCK.release()
        return status
#-------------------------------------------------------------------------------
# DissectionDatabaseActionGroup
#-------------------------------------------------------------------------------
class DissectionDatabaseActionGroup(ActionGroup):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(DissectionDatabaseActionGroup, self).__init__('dissectiondb', {
            'list': ActionGroup.action(DissectionDatabaseActionGroup.list, 
                "list of available database adapters.")
        })
    #---------------------------------------------------------------------------
    # list
    #---------------------------------------------------------------------------
    @staticmethod
    def list(keywords, args):
        text = '\nAdaptaters:'
        for adapter in DissectionDatabase.adapters():
            text += '\n\t+ {}'.format(adapter)
        text += '\n'
        LGR.info(text)