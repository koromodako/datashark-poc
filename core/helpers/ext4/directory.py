# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: dirent.py
#     date: 2018-01-15
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
from helpers.ext4.file import Ext4File
from helpers.ext4.dirent import Ext4Dirent
from helpers.ext4.symlink import Ext4Symlink
from helpers.ext4.regfile import Ext4RegularFile
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for dirent.
##
class Ext4Directory(Ext4File):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fs     The file system
    ## @param      bf     The binary file containing the entire partition
    ## @param      inode  The inode
    ##
    def __init__(self, fs, bf, inode):
        super(Ext4Directory, self).__init__(fs, bf, inode)
        if self._fs.filetype():
            self._dirent_vers = Ext4DirentVersion.V2
        else:
            self._dirent_vers = Ext4DirentVersion.V1
    ##
    ## @brief      Yields entries as Ext4Dirent
    ##
    @lazy_getter('_entries')
    def entries(self):
        entries = []
        data = b''
        for blk in self._reader.blocks():
            data += blk
            dirent = Ext4Dirent(self._dirent_vers, bytes=data)
            entries.append(dirent)
            while len(data) > dirent.st_size():
                data = data[dirent.st_size():]
                entries.append(Ext4Dirent(self._dirent_vers, bytes=data))

        self._slack_space = b''
        if len(data) > 0:
            self._slack_space = data
    ##
    ## @brief      Yields entries as Ext4File subclasses instances
    ##
    def files(self):
        for entry in self.entries():
            inode_num = entry.inode_num()

            if inode_num <= 0:
                continue

            inode = self._fs.inode(inode_num)
            ftype = inode.ftype()

            if ftype == Ext4FileType.DIRECTORY:
                yield Ext4Directory(self._fs, self._bf, inode)
            elif ftype == Ext4FileType.SYMLINK:
                yield Ext4Symlink(self._fs, self._bf, inode)
            elif ftype == Ext4FileType.REG_FILE:
                yield Ext4RegularFile(self._fs, self._bf, inode)
            else:
                yield Ext4File(self._fs, self._bf, inode)
