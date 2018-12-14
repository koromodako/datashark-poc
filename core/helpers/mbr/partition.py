# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: partition.py
#     date: 2018-01-07
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
from utils.wrapper import trace
from utils.logging import get_logger
from utils.constants import SECTOR_SZ
from utils.memory_map import MemoryMap
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for partition.
##
class Partition(MemoryMap):
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, bf, status, type, start, size):
        super(Partition, self).__init__(bf, start, size, SECTOR_SZ)
        self.status = status
        self.type = type
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    def __str__(self):
        return "Partition(status={},type={},start={},size={})".format(
            hex(self.status), hex(self.type), self.start, self.size)
