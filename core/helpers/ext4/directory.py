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
from helpers.ext4.constants import Ext4DirentVersion
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
    ## @param      entry  The directory entry
    ##
    def __init__(self, fs, bf, entry):
        super(Ext4Directory, self).__init__(fs, bf, entry)
        if self._fs.filetype():
            self._dirent_version = Ext4DirentVersion.V2
        else:
            self._dirent_version = Ext4DirentVersion.V1
    ##
    ## @brief      Yields entries as Ext4Dirent
    ##
    ## @param      fs            The file system
    ## @param      inode_reader  The inode reader
    ## @param      extra         The extra
    ##
    @staticmethod
    def parse_entries(fs, inode_reader, extra):
        version = Ext4DirentVersion.V2 if fs.filetype() else Ext4DirentVersion.V1

        data = b''
        for blk_idx, blk in inode_reader.blocks():
            data += blk

            dirent = Ext4Dirent(fs, version, bytes=data)
            yield dirent

            while True:
                data = data[dirent.rec_len():]

                if len(data) < dirent.st_size():
                    break

                dirent = Ext4Dirent(fs, version, bytes=data)
                yield dirent

        extra['slack_space'] = data
    ##
    ## @brief      Yields entries as Ext4Dirent
    ##
    def __entries(self):
        extra = {}
        for dirent in self.parse_entries(self._fs, self._reader, extra):
            yield dirent

        self.set_slack_space(extra['slack_space'])
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

            if inode.islink():
                yield Ext4Symlink(self._fs, self._bf, entry)
            elif inode.isdir():
                yield Ext4Directory(self._fs, self._bf, entry)
            elif inode.isfile():
                yield Ext4RegularFile(self._fs, self._bf, entry)
            else:
                yield Ext4File(self._fs, self._bf, entry)
