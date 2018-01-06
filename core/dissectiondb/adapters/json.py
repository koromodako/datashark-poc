# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: json_adapter.py
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
from utils.json import json_dumps
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from dissectiondb.dissectiondb_adapter import DissectionDBAdapter
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for json db.
##
class JsonDB(DissectionDBAdapter):
    ##
    ## { item_description }
    ##
    JSON_BEGIN = '{"containers":['
    ##
    ## { item_description }
    ##
    JSON_END = ']}'
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(JsonDB, self).__init__(conf)
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
        return ConfigObj({"path": "path/to/hash/database/file.json"})
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _init_r(self):
        if not BinaryFile.exists(self._conf.path):
            return False

        self.bf = BinaryFile(self._conf.path, 'r')
        return self.bf.open()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _init_w(self):
        self.bf = BinaryFile(self._conf.path, 'w')

        if not self.bf.open():
            return False

        self.bf.write_text(self.JSON_BEGIN)
        self.bf.flush()
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _term_r(self):
        self.bf.close()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _term_w(self):
        self.bf.write_text(self.JSON_END)
        self.bf.flush()
        self.bf.close()
    ##
    ## @brief      { function_description }
    ##
    ## @param      container_dict  The container dictionary
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def insert(self, container_dict):
        data = json_dumps(container_dict)
        self._lock.acquire()
        # protect counter increment
        if self.cnt > 0:
            data = ',' + data
        self.cnt += 1
        # protect file writing
        self.bf.write_text(data)
        self.bf.flush()
        self._lock.release()
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
    return JsonDB(conf)
