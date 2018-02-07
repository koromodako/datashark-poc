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
    def __entries(self):
        data = b''
        for blk in self._reader.blocks():
            data += blk

            dirent = Ext4Dirent(self._dirent_vers, bytes=data)
            yield dirent

            while len(data) > dirent.st_size():
                data = data[dirent.st_size():]
                yield Ext4Dirent(self._dirent_vers, bytes=data)

        if self.slack_space is None:
            self.slack_space = data
    ##
    ## @brief      Yields entries as Ext4File subclasses instances
    ##
    def entries(self, dirent_only=True):
        for entry in self.__entries():
            if dirent_only:
                yield entry
                continue

            inode = entry.inode()

            if inode is None:
                continue

            ftype = inode.ftype()

            if ftype == Ext4FileType.DIRECTORY:
                yield Ext4Directory(entry.name(string=True),
                                    self._fs, self._bf, inode)
            elif ftype == Ext4FileType.SYMLINK:
                yield Ext4Symlink(entry.name(string=True),
                                  self._fs, self._bf, inode)
            elif ftype == Ext4FileType.REG_FILE:
                yield Ext4RegularFile(entry.name(string=True),
                                      self._fs, self._bf, inode)
            else:
                yield Ext4File(entry.name(string=True),
                               self._fs, self._bf, inode)
