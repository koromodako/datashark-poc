# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: hashdb_adapter.py
#     date: 2017-12-15
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
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
from utils.wrapper import trace
from utils.logging import get_logger
from utils.db_adapter import DBAdapter
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Abstract representation of a hash database adapter
##
class HashDBAdapter(DBAdapter):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(HashDBAdapter, self).__init__(conf)
    ##
    ## @brief      Merges this database into the other
    ##
    ## @param      other  The other
    ##
    ## @return     { description_of_the_return_value }
    ##
    def merge_into(self, other):
        raise NotImplementedError
    ##
    ## @brief      Tries to retrieve an existing record having given hexdigest
    ##
    ## @param      hexdigest  The hexdigest
    ##
    ## @return     { description_of_the_return_value }
    ##
    def lookup(self, hexdigest):
        raise NotImplementedError
    ##
    ## @brief      Inserts a new hash tuple into the database
    ##
    ## @param      hexdigest  The hexdigest
    ## @param      path       The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def insert(self, hexdigest, path):
        raise NotImplementedError
