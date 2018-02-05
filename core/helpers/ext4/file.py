# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: file.py
#     date: 2018-02-05
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
from helpers.ext4.inode_reader import Ext4InodeReader
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 file.
##
class Ext4File(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      inode  The inode
    ##
    def __init__(self, fs, bf, inode):
        super(Ext4File, self).__init__()
        self._fs = fs
        self._fs_blk_size = fs.block_size()
        self._bf = bf
        self._inode = inode
        self._reader = Ext4InodeReader(fs, bf, inode)
    ##
    ## @brief      { function_description }
    ##
    ## @param      size  The size
    ## @param      seek  The seek
    ##
    ## @return     { description_of_the_return_value }
    ##
    def read(self, size=-1, seek=0):
        if seek < 0:
            LGR.error("seek value cannot be smaller than zero.")
            return None

        if size == 0:
            LGR.warn("reading with size=0 is awkward.")
            return b''

        fst_blk_idx = seek // self._fs_blk_size
        lst_blk_idx = (seek + size - 1) // self._fs_blk_size

        data = b''
        for k in range(fst_blk_idx, lst_blk_idx+1):
            data += self._reader.block(k)

        rseek = seek - (fst_blk_idx * self._fs_blk_size)
        return data[rseek:rseek+size]

