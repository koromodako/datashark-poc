# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: inode_reader.py
#     date: 2018-01-29
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
from utils.wrapper import lazy_getter
from utils.logging import get_logger
from helpers.ext4.tree import Ext4Tree
from helpers.ext4.block_map import Ext4BlockMap
from helpers.ext4.constants import Ext4FileType
from helpers.ext4.constants import Ext4InodeFlag
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 inode reader.
##
class Ext4InodeReader(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      inode  The inode
    ##
    def __init__(self, fs, bf, inode):
        self._bf = bf
        self._fs_blk_sz = fs.block_size()
        self._fs_inline_data = fs.inline_data()
        self._fs_use_extents = fs.use_extents()
        self._i_type = inode.ftype()
        self._i_size = inode.size()
        self._i_block = inode.block()
        self._i_inline = inode.flags(Ext4InodeFlag.EXT4_INLINE_DATA_FL)
        self._tree = Ext4Tree(fs, bf, inode)
        self._bmap = Ext4BlockMap(fs, bf, inode)
    ##
    ## @brief      Returns an iblock tuple
    ##
    def _iblock(self):
        return ("iblock", self._iblock)
    ##
    ## @brief      Returns a standard block tuple
    ##
    ## @param      f_blk_idx  The file block index
    ## @param      blk_idx    The block index
    ##
    def _block(self, f_blk_idx, blk_idx):
        data = self._bf.read(self._fs_blk_sz,
                             self._fs_blk_sz * blk_idx)
        name = "block n°(file={},part={})".format(f_blk_idx, blk_idx)
        return (name, data)
    ##
    ## @brief      Returns an abort tuple
    ##
    def _abort_block(self):
        return (None, None)
    ##
    ## @brief      Yields blocks of data mapped by the inode.
    ##
    @trace()
    def blocks(self):
        if self._i_type == Ext4FileType.SYMLINK and self._i_size < 60:
            yield self._iblock()

        elif self._fs_inline_data and self._i_inline:
            yield self._iblock()

        elif self._fs_use_extents:
            if not self._tree.is_valid():
                LGR.error("invalid extent tree.")
                return (None, None)

            k = 0
            for blk_idx in self._tree.file_blocks():
                yield self._block(k, blk_idx)
                k += 1

        else:
            k = 0
            for blk_idx in self._bmap.file_blocks():
                yield self._block(k, blk_idx)
                k += 1
    ##
    ## @brief      Returns a single block of data using given file block
    ##             index.
    ##
    ## @param      blk_idx  The file block index
    ##
    @trace()
    def block(self, f_blk_idx):
        if self._i_type == Ext4FileType.SYMLINK and self._i_size < 60:

            if f_blk_idx > 0:
                LGR.warn("block index is out-of-bounds. (inline symlink)")
                return (None, None)

            return self._iblock()

        elif self._fs_inline_data and self._i_inline:

            if f_blk_idx > 0:
                LGR.warn("block index is out-of-bounds. (inline data)")
                return (None, None)

            return self._iblock()

        elif self._fs_use_extents:
            if not self._tree.is_valid():
                LGR.error("invalid extent tree.")
                return (None, None)

            # translate file block index to partition block index
            blk_idx = self._tree.file_block(f_blk_idx)

            if blk_idx is None:
                LGR.error("file block index out-of-bounds.")
                return (None, None)

            return self._block(f_blk_idx, blk_idx)

        else:
            # translate file block index to partition block index
            blk_idx = self._bmap.file_block(f_blk_idx)

            if blk_idx is None:
                LGR.error("file block index out-of-bounds.")
                return (None, None)

            return self._block(f_blk_idx, blk_idx)
