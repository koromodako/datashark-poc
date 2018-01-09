# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4.py
#     date: 2018-01-07
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
from enum import IntEnum
from utils.wrapper import trace
from utils.logging import get_logger
from dissection.helpers.ext4.ext4_super_block import Ext4SuperBlock
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Enum for extent 4 block size.
##
class Ext4BlockSize(IntEnum):
    KB1 = 1
    KB2 = 2
    KB4 = 4
    KB64 = 64
##
## @brief      Class for extent 4 fs.
##
class Ext4FS(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      self    The object
    ## @param      bf      { parameter_description }
    ## @param      blk_sz  The block size
    ##
    def __init__(self, bf, blk_sz=Ext4BlockSize.KB4):
        self._bf = bf
        self.blk_sz = blk_sz * 1024
        self.blk_gp_sz = 8 * blk_sz
        self.sb = Ext4SuperBlock(self._bf)
        self._parse_gds()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse_gds(self):
        self.gds = []
        #raise NotImplementedError
    ##
    ## @brief      Determines if valid.
    ##
    ## @param      self  The object
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return self.sb.is_valid()
