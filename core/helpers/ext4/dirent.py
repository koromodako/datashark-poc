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
from utils.logging import get_logger
from helpers.ext4.constants import EXT4_NAME_LEN
from helpers.ext4.constants import Ext4FileType
from helpers.ext4.constants import Ext4DirentVersion
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_factory import StructFactory
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
    SimpleMember('file_type', 'B', fmtr=Ext4FileType),
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
## @brief      Class for dirent.
##
class Ext4Dirent(object):

    def __init__(self, version, bf, oft):
        super(Ext4Dirent, self).__init__()
        self.valid = False
        self.version = version
        if self.version == Ext4DirentVersion.V1:
            self._dirent = StructFactory.st_from_file(S_EXT4_DIR_ENTRY,
                                                      bf, oft)
        elif self.version == Ext4DirentVersion.V2:
            self._dirent = StructFactory.st_from_file(S_EXT4_DIR_ENTRY_2,
                                                      bf, oft)
        else:
            LGR.error("unknown ext4 dirent version.")
            return
