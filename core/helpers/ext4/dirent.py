# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: dirent.py
#     date: 2018-01-15
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
from utils.struct.factory import StructFactory
from utils.struct.wrapper import StructWrapper
from helpers.ext4.constants import EXT4_NAME_LEN
from helpers.ext4.constants import Ext4DirentVersion
from helpers.ext4.constants import Ext4DirentFileType
from utils.struct.simple_member import SimpleMember
from utils.struct.byte_array_member import ByteArrayMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_EXT4_DIR_ENTRY = 'ext4_dir_entry'
StructFactory.st_register(S_EXT4_DIR_ENTRY, [
    # Number of the inode that this directory entry points to.
    SimpleMember('inode', '<I'),
    # Length of this directory entry.
    SimpleMember('rec_len', '<H'),
    # Length of the file name.
    SimpleMember('name_len', '<H'),
    # File name.
    ByteArrayMember('name', EXT4_NAME_LEN)
])
S_EXT4_DIR_ENTRY_2 = 'ext4_dir_entry_2'
StructFactory.st_register(S_EXT4_DIR_ENTRY_2, [
    # Number of the inode that this directory entry points to.
    SimpleMember('inode', '<I'),
    # Length of this directory entry.
    SimpleMember('rec_len', '<H'),
    # Length of the file name.
    SimpleMember('name_len', 'B'),
    # File type code, one of:
    SimpleMember('file_type', 'B', fmtr=Ext4DirentFileType),
    # File name.
    ByteArrayMember('name', EXT4_NAME_LEN)
])
S_EXT4_DIR_ENTRY_TAIL = 'ext4_dir_entry_tail'
StructFactory.st_register(S_EXT4_DIR_ENTRY_TAIL, [
    # Inode number, which must be zero.
    SimpleMember('det_reserved_zero1', '<I'),
    # Length of this directory entry, which must be 12.
    SimpleMember('det_rec_len', '<H'),
    # Length of the file name, which must be zero.
    SimpleMember('det_reserved_zero2', 'B'),
    # File type, which must be 0xDE.
    SimpleMember('det_reserved_ft', 'B'),
    # Directory leaf block checksum.
    SimpleMember('det_checksum', '<I')
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 directory entry.
##
class Ext4Dirent(StructWrapper):
        ##
        ## @brief      Constructs the object.
        ##
        ## @param      version  The version
        ## @param      bf       { parameter_description }
        ## @param      oft      The oft
        ##
        def __init__(self, fs, version, bytes, oft=0):
            self._fs = fs
            self.version = version
            if self.version == Ext4DirentVersion.V1:
                st_type = S_EXT4_DIR_ENTRY
            elif self.version == Ext4DirentVersion.V2:
                st_type = S_EXT4_DIR_ENTRY_2
            else:
                LGR.error("unknown ext4 dirent version.")
                return
            super(Ext4Dirent, self).__init__(st_type, bytes=bytes, oft=oft)
        ##
        ## @brief      { function_description }
        ##
        def inode_num(self):
            return self._s.inode
        ##
        ## @brief      { function_description }
        ##
        @lazy_getter('_inode')
        def inode(self):
            n = self.inode_num()

            if n <= 0:
                return None

            return self._fs.inode(n)
        ##
        ## @brief      { function_description }
        ##
        def rec_len(self):
            return self._s.rec_len
        ##
        ## @brief      { function_description }
        ##
        def name_len(self):
            return self._s.name_len
        ##
        ## @brief      { function_description }
        ##
        @lazy_getter('_file_type')
        def file_type(self):
            if self.version == Ext4DirentVersion.V2:
                return Ext4DirentFileType(self._s.file_type)

            LGR.warn("calling file_type on a V1 directory entry => None "
                     "returned.")
            return None
        ##
        ## @brief      { function_description }
        ##
        def name(self, string=False):
            if string:
                return self._s.name[:self.name_len()].decode()
            return self._s.name
        ##
        ## @brief      Determines if symlink.
        ##
        ## @return     True if symlink, False otherwise.
        ##
        @lazy_getter('_islink')
        def islink(self):
            if self.version == Ext4DirentVersion.V2:
                return (self.file_type() == Ext4DirentFileType.LNK)

            inode = self.inode()
            if inode is None:
                return False

            return self.inode().islink()
        ##
        ## @brief      Returns file type
        ##
        @lazy_getter('_isdir')
        def isdir(self):
            if self.version == Ext4DirentVersion.V2:
                return (self.file_type() == Ext4DirentFileType.DIR)

            inode = self.inode()
            if inode is None:
                return False

            return inode.isdir()
        ##
        ## @brief      { function_description }
        ##
        @lazy_getter('_isfile')
        def isfile(self):
            if self.version == Ext4DirentVersion.V2:
                return (self.file_type() == Ext4DirentFileType.REG)

            inode = self.inode()
            if inode is None:
                return False

            return inode.isfile()
        ##
        ## @brief      Determines if fifo.
        ##
        ## @return     True if fifo, False otherwise.
        ##
        @lazy_getter('_isfifo')
        def isfifo(self):
            if self.version == Ext4DirentVersion.V2:
                return (self.file_type() == Ext4DirentFileType.FIFO)

            inode = self.inode()
            if inode is None:
                return False

            return inode.isfifo()
        ##
        ## @brief      Determines if socket.
        ##
        ## @return     True if socket, False otherwise.
        ##
        @lazy_getter('_issock')
        def issock(self):
            if self.version == Ext4DirentVersion.V2:
                return (self.file_type() == Ext4DirentFileType.SOCK)

            inode = self.inode()
            if inode is None:
                return False

            return inode.issock()
        ##
        ## @brief      Determines if device.
        ##
        ## @return     True if device, False otherwise.
        ##
        @lazy_getter('_isdev')
        def isdev(self):
            if self.version == Ext4DirentVersion.V2:
                ftype = self.file_type()
                return (ftype == Ext4DirentFileType.BLK or
                        ftype == Ext4DirentFileType.CHR)

            inode = self.inode()
            if inode is None:
                return False

            return inode.isdev()
        ##
        ## @brief      Returns the description using the following format
        ##             10228426 -rw-r--r-- 1 paul paul  1,4G janv.  7 15:33 partition.3.1c566bda.ds
        ##
        def description(self, human=False):
            inode = self.inode()
            if inode is None:
                return "[empty dirent]"

            return inode.description(self.name(string=True), human)
