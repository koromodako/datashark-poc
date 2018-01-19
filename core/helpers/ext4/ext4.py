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
from math import ceil
from enum import IntEnum
from utils.wrapper import trace
from utils.logging import get_logger
from utils.comparing import is_flag_set
from helpers.ext4.tree import Ext4TreeNode
from helpers.ext4.constants import Ext4Incompat
from helpers.ext4.super_block import Ext4SuperBlock
from helpers.ext4.inode_table_entry import Ext4Inode
from helpers.ext4.block_group_descriptor import Ext4BlkGrpDesc
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
        self.blk_grp_sz = 8 * blk_sz
        self.sb = Ext4SuperBlock(self._bf, 1024)
        self._parse_gds()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse_gds(self):
        self.bgds = []

        bgd_sz = 32
        if is_flag_set(self.sb.feature_incompat(), Ext4Incompat.INCOMPAT_64BIT):
            bgd_sz = self.sb._sb.s_desc_size

        bg_count = ceil(self.sb.blocks_count() / self.sb._sb.s_blocks_per_group)

        oft = self.blk_sz
        for i in range(0, bg_count):
            bgd = Ext4BlkGrpDesc(bgd_sz, self._bf, oft)
            self.bgds.append(bgd)
            oft += bgd_sz
    ##
    ## @brief      { item_description }
    ##
    ## @note       Should be used as an iterator, i.e.
    ##             ```
    ##             fs = Ext4FS(...)
    ##             for inode in fs.inodes():
    ##                 perform_op_on(inode)
    ##             ```
    ##
    ## @return     { description_of_the_return_value }
    ##
    def inodes(self):
        for bgd in self.bgds:
            oft = bgd.inode_table() * self.blk_sz

            for inode in range(0, self.sb._sb.s_inodes_per_group):
                inode = Ext4Inode(self._bf, oft)
                yield inode
                oft += self.sb._sb.s_inode_size
    ##
    ## @brief      Determines if valid.
    ##
    ## @param      self  The object
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return self.sb.is_valid()
