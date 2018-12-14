# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: file.py
#     date: 2018-02-05
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
from utils.wrapper import lazy_getter
from utils.logging import get_logger
from utils.formatting import format_size
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
    def __init__(self, fs, bf, entry):
        super(Ext4File, self).__init__()
        self._fs = fs
        self._bf = bf
        self._entry = entry
        self._fname = entry.name(string=True)
        self._fs_blk_size = fs.block_size()
        self._slack_space = None
    ##
    ## @brief      Sets the slack space.
    ##
    ## @param      data  The data
    ##
    def _set_slack_space(self, data):
        cond = self._slack_space is None
        if cond:
            self._slack_space = data
        return cond
    ##
    ## @brief      { function_description }
    ##
    @lazy_getter('_inode')
    def inode(self):
        return self._entry.inode()
    ##
    ## @brief      { function_description }
    ##
    @lazy_getter('_reader')
    def reader(self):
        return Ext4InodeReader(self._fs, self._bf, self.inode())
    ##
    ## @brief      Returns the description using the following format
    ##             10228426 -rw-r--r-- 1 paul paul  1,4G janv.  7 15:33 partition.3.1c566bda.ds
    ##
    def description(self, human=False):
        return self._entry.description(self._fname, human)
    ##
    ## @brief      { function_description }
    ##
    def fname(self):
        return self._fname
    ##
    ## @brief      Returns file's slack space
    ##
    def slack_space(self):
        return self._slack_space
    ##
    ## @brief      Reads  `size` bytes of the file from offset `seek`
    ##
    ## @param      size  Number of bytes to read, if negative the whole data
    ##                   is read excluding slack space.
    ## @param      seek  The offset from which read operation should start
    ##
    def read(self, size=-1, seek=0):
        max_size = self.size()

        if seek < 0 or seek > (max_size-1):
            LGR.error("seek value cannot be smaller than zero or greater "
                      "than inode.size()-1.")
            return None

        if size == 0:
            LGR.warn("reading with size=0 is awkward.")
            return b''
        elif size < 0 or size > max_size:
            size = max_size - seek

        fst_blk_idx = seek // self._fs_blk_size
        lst_blk_idx = (seek + size - 1) // self._fs_blk_size

        data = b''
        for k in range(fst_blk_idx, lst_blk_idx+1):
            data += self.reader().block(k)

        rseek = seek - (fst_blk_idx * self._fs_blk_size)
        return data[rseek:rseek+size]
