# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4.py
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
from math import ceil
from utils.wrapper import trace
from utils.wrapper import lazy_getter
from utils.logging import get_logger
from utils.comparing import is_flag_set
from helpers.ext4.inode import Ext4Inode
from helpers.ext4.constants import Ext4Incompat
from helpers.ext4.constants import Ext4ROCompat
from helpers.ext4.constants import Ext4BlockSize
from helpers.ext4.superblock import Ext4SuperBlock
from helpers.ext4.fs_explorer import Ext4FSExplorer
from helpers.ext4.inode_reader import Ext4InodeReader
from helpers.ext4.bg_descriptor import Ext4BlkGrpDesc
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
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
        self.blk_sz = blk_sz
        self.sb = Ext4SuperBlock(self._bf, 1024)
        self._parse_gds()
    ##
    ## @brief      Return size in bytes of a "FS block"
    ##
    ## @return     int, power of 2
    ##
    @lazy_getter('_block_size')
    def block_size(self):
        return self.blk_sz * 1024
    ##
    ## @brief      Does FS support "huge files"
    ##
    @lazy_getter('_huge_file')
    def huge_file(self):
        return self.sb.feature_ro_compat(Ext4ROCompat.RO_COMPAT_HUGE_FIL)
    ##
    ## @brief      Does FS support "inline data"
    ##
    @lazy_getter('_inline_data')
    def inline_data(self):
        return self.sb.feature_incompat(Ext4Incompat.INCOMPAT_INLINE_DATA)
    ##
    ## @brief      Does FS use extents
    ##
    @lazy_getter('_use_extents')
    def use_extents(self):
        return self.sb.feature_incompat(Ext4Incompat.INCOMPAT_EXTENTS)
    ##
    ## @brief      Does FS support 64bit structures
    ##
    @lazy_getter('_use_64b')
    def use_64b(self):
        return self.sb.feature_incompat(Ext4Incompat.INCOMPAT_64BIT)
    ##
    ## @brief      Does FS support "inline data"
    ##
    @lazy_getter('_filetype')
    def filetype(self):
        return self.sb.feature_incompat(Ext4Incompat.INCOMPAT_FILETYPE)
    ##
    ## @brief      Parses the block group descriptor table
    ##
    @trace()
    def _parse_gds(self):
        self.bgds = []

        bgd_sz = 32
        if self.use_64b():
            bgd_sz = self.sb.desc_size()

        bg_count = ceil(self.sb.blocks_count() / self.sb.blocks_per_group())

        oft = self.block_size()
        for i in range(0, bg_count):
            bgd = Ext4BlkGrpDesc(bgd_sz, self._bf, oft)
            self.bgds.append(bgd)
            oft += bgd_sz
    ##
    ## @brief      Yields all inodes
    ##
    ## @note       Should be used as an iterator, i.e.
    ##             ```
    ##             fs = Ext4FS(...)
    ##             for inode in fs.inodes():
    ##                 perform_op_on(inode)
    ##             ```
    ##
    @trace()
    def inodes(self):
        n = 1
        for bgd in self.bgds:
            oft = bgd.inode_table() * self.block_size()

            for inode in range(0, self.sb.inodes_per_group()):
                yield Ext4Inode(n, self._bf, oft)
                oft += self.sb.inode_size()
                n += 1
    ##
    ## @brief      Returns a specific inode identified by its index (starting
    ##             from 1)
    ##
    ## @param      n     Index of inode. WARNING: starts with 1 !
    ##
    @trace()
    def inode(self, n):
        if n < 1 or n > self.sb.inodes_count():
            raise ValueError("inode index out-of-bounds: index starts at 1 "
                             "and stops at {} (n={}).".format(
                                self.sb.inodes_count(), n))

        bgd_idx = (n - 1) // self.sb.inodes_per_group()
        inode_bg_idx = (n - 1) % self.sb.inodes_per_group()

        bgd = self.bgds[bgd_idx]

        oft = bgd.inode_table() * self.block_size()
        oft += inode_bg_idx * self.sb.inode_size()

        return Ext4Inode(n, self._bf, oft)
    ##
    ## @brief      Yields data blocks associated with given inode
    ##
    ## @param      inode    Inode to be used
    ##
    @trace()
    def inode_blocks(self, inode):
        reader = Ext4InodeReader(self, self._bf, inode)
        for blk_id, blk in reader.blocks():
            yield (blk_id, blk)
    ##
    ## @brief      Returns a single data block based on given inode and block
    ##             index
    ##
    ## @param      inode           The inode
    ## @param      blk_idx  The file block index
    ##
    @trace()
    def inode_block(self, inode, blk_idx):
        reader = Ext4InodeReader(self, self._bf, inode)
        return reader.block(blk_idx)
    ##
    ## @brief      { function_description }
    ##
    @trace()
    def explorer(self):
        return Ext4FSExplorer(self, self._bf)
    ##
    ## @brief      Determines if valid.
    ##
    ## @param      self  The object
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self.sb.is_valid()
