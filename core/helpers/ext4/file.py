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
    def __init__(self, fname, fs, bf, inode):
        super(Ext4File, self).__init__()
        if not isinstance(type, Ext4FileType):
            LGR.error("Ext4File type argument must be a instance of "
                      "Ext4FileType.")
        self._fname = fname
        self._fs = fs
        self._fs_blk_size = fs.block_size()
        self._bf = bf
        self._inode = inode
        self._reader = Ext4InodeReader(fs, bf, inode)
    ##
    ## @brief      { function_description }
    ##
    def ftype(self):
        return self._inode.ftype()
    ##
    ## @brief      Returns the description using the following format
    ##             10228426 -rw-r--r-- 1 paul paul  1,4G janv.  7 15:33 partition.3.1c566bda.ds
    ##
    def description(self, human=False):
        uid = self._inode.uid()
        gid = self._inode.gid()
        size = self._inode.size()

        if human:
            uid = "{} ({})".format(uid, "root" if uid == 0 else "unknown")
            gid = "{} ({})".format(gid, "root" if gid == 0 else "unknown")
            size = format_size(size)

        return "{} {} {} {} {} {} {} {}".format(self._inode.number,
                                                self._inode.permissions(),
                                                self._inode.links_count(),
                                                uid, gid, size,
                                                self._inode.ctime(),
                                                self._inode.atime(),
                                                self._inode.mtime(),
                                                self._inode.dtime(),
                                                self._fname)
    ##
    ## @brief      { function_description }
    ##
    ## @param      size  The size
    ## @param      seek  The seek
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
            data += self._reader.block(k)

        rseek = seek - (fst_blk_idx * self._fs_blk_size)
        return data[rseek:rseek+size]
