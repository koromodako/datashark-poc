# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: memory_map.py
#     date: 2018-01-05
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 paul.dautry
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
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for memory map.
##
class MemoryMap(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf     Binary file
    ## @param      start  The start
    ## @param      size   The size
    ## @param      unit   The unit
    ##
    def __init__(self, bf, start, size, unit=1):
        super(MemoryMap, self).__init__()
        self._bf = bf
        self.start = start
        self.size = size
        self.unit = unit
    ##
    ## @brief      Reads one.
    ##
    ## @param      idx   The index
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def read_one(self, idx):
        if idx >= self.size:
            LGR.warn("reading after end of map => None returned.")
            return None

        self._bf.seek((self.start + idx) * self.unit)
        return self._bf.read(self.unit)
    ##
    ## @brief      Reads all.
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def read_all(self):
        self._bf.seek(self.start * self.unit)
        return self._bf.read(self.size * self.unit)

