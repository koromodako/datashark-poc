# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: sqlite.py
#     date: 2018-01-02
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 koromodako
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
#  IMPORTS
# =============================================================================
import sqlite3
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_func
from utils.configobj import ConfigObj
from dissectiondb.dissectiondb_adapter import DissectionDBAdapter
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for json db.
##
class SQLiteDB(DissectionDBAdapter):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(SQLiteDB, self).__init__(conf)
        self.bf = None
        self.cnt = 0
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _check_conf(self):
        if self._conf is None:
            return False

        if not self._conf.has('path'):
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def expected_conf(self):
        return ConfigObj({"path": "path/to/dissection/database/file.db"})
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _init_r(self):
        try:
            uri = 'file:{}?mode=ro'.format(self._conf.path)
            self.conn = sqlite3.connect(uri, uri=True)
        except Exception as e:
            LGR.exception("failed to init sqlite3 database.")
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _init_w(self):
        try:
            uri = 'file:{}?mode=rwc'.format(self._conf.path)
            self.conn = sqlite3.connect(uri, uri=True)
        except Exception as e:
            LGR.exception("failed to init sqlite3 database.")
            return False

        c = self.conn.cursor()
        c.execute("DROP INDEX IF EXISTS container_parent_uuid")
        c.execute("DROP INDEX IF EXISTS container_uuid")
        c.execute("DROP TABLE IF EXISTS container")
        c.execute("CREATE TABLE container(uuid,parent_uuid,path,realname,hashed,mime_type,mime_text,flagged,whitelisted,blacklisted)")
        c.execute("CREATE INDEX container_uuid ON container(uuid)")
        c.execute("CREATE INDEX container_parent_uuid ON container(parent_uuid)")
        c.close()
        self.conn.commit()

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _term_r(self):
        self.conn.close()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _term_w(self):
        self.conn.close()
    ##
    ## @brief      { function_description }
    ##
    ## @param      container_dict  The container dictionary
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def insert(self, container_dict):
        self._lock.acquire()

        c = self.conn.cursor()
        c.execute("INSERT INTO container VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (container_dict.get('uuid'),
                   container_dict.get('parent_uuid'),
                   container_dict.get('path'),
                   container_dict.get('realname'),
                   container_dict.get('hashed'),
                   container_dict.get('mime', {}).get('type'),
                   container_dict.get('mime', {}).get('text'),
                   container_dict.get('flagged'),
                   container_dict.get('whitelisted'),
                   container_dict.get('blacklisted')))
        c.close()

        self.conn.commit()

        self._lock.release()
        return True
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      { function_description }
##
## @param      conf  The conf
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def instance(conf):
    return SQLiteDB(conf)
