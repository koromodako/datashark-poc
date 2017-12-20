# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: dissectiondb_adapter.py
#     date: 2017-12-16
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
## @brief      Abstract representation of a dissection db adapter plugin
##
class DissectionDBAdapter(DBAdapter):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(DissectionDBAdapter, self).__init__(conf)
    ##
    ## @brief      Checks if a container UUID is already used within the
    ##             database
    ##
    ## @param      container_uuid  The container uuid
    ##
    ## @return     { description_of_the_return_value }
    ##
    def exists(self, container_uuid):
        raise NotImplementedError
    ##
    ## @brief      Inserts a new container into the database
    ##
    ## @param      container_dict  The container dictionary
    ##
    ## @return     { description_of_the_return_value }
    ##
    def insert(self, container_dict):
        raise NotImplementedError
