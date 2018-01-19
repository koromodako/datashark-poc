# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: htree_dir.py
#     date: 2018-01-16
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
from helpers.ext4.constants import Ext4FileType
from helpers.ext4.constants import Ext4HashAlgo
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_member import StructMember
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_EXT4_DOT_ENTRY = 'ext4_dot_entry'
StructFactory.st_register(S_EXT4_DOT_ENTRY, [
    # . => inode number of this directory.
    # .. => inode number of parent directory.
    SimpleMember('inode', '<I'),
    # . => Length of this record, 12.
    # .. => block_size - 12. The record length is long enough to cover all
    #       htree data.
    SimpleMember('rec_len', '<H'),
    # . => Length of the name, 1.
    # .. => Length of the name, 2.
    SimpleMember('name_len', 'B'),
    # . => File type of this entry, 0x2 (directory) (if the feature flag is set).
    # .. => idem
    SimpleMember('file_type', 'B', fmtr=Ext4FileType),
    # . => ".\0\0\0"
    # .. => "..\0\0"
    ByteArrayMember('name', 4)
])
S_EXT4_DX_ENTRY = 'ext4_dx_entry'
StructFactory.st_register(S_EXT4_DX_ENTRY, [
    # Hash code.
    SimpleMember('hash', '<I'),
    # Block number (within the directory file, not filesystem blocks) of the
    # next node in the htree.
    SimpleMember('block', '<I')
])
S_EXT4_DX_ROOT = 'ext4_dx_root'
StructFactory.st_register(S_EXT4_DX_ROOT, [
    StructMember('dot', S_EXT4_DOT_ENTRY),
    StructMember('dotdot', S_EXT4_DOT_ENTRY),
    # Zero.
    SimpleMember('reserved_zero', '<I')
    # Hash version.
    SimpleMember('hash_version', 'B', fmtr=Ext4HashAlgo),
    # Length of the tree information, 0x8.
    SimpleMember('info_length', 'B'),
    # Depth of the htree. Cannot be larger than 3 if the INCOMPAT_LARGEDIR
    # feature is set; cannot be larger than 2 otherwise.
    SimpleMember('indirect_levels', 'B'),
    SimpleMember('unused_flags', 'B'),
    # Maximum number of dx_entries that can follow this header, plus 1 for the
    # header itself.
    SimpleMember('limit', '<H'),
    # Actual number of dx_entries that follow this header, plus 1 for the
    # header itself.
    SimpleMember('count', '<H'),
    # The block number (within the directory file) that goes with hash=0.
    SimpleMember('block', '<I'),
    # As many 8-byte struct dx_entry as fits in the rest of the data block.
    # struct dx_entry     entries[0] (retrieved in Python Class)
])
S_EXT4_DX_NODE = 'ext4_dx_node'
StructFactory.st_register(S_EXT4_DX_NODE, [
    # Zero, to make it look like this entry is not in use.
    SimpleMember('inode', '<I'),
    # The size of the block, in order to hide all of the dx_node data.
    SimpleMember('rec_len', '<H'),
    # Zero. There is no name for this "unused" directory entry.
    SimpleMember('name_len', 'B'),
    # Zero. There is no file type for this "unused" directory entry.
    SimpleMember('file_type', 'B'),
    # Maximum number of dx_entries that can follow this header, plus 1 for the
    # header itself.
    SimpleMember('limit', '<H'),
    # Actual number of dx_entries that follow this header, plus 1 for the
    # header itself.
    SimpleMember('count', '<H'),
    # The block number (within the directory file) that goes with the lowest
    # hash value of this block. This value is stored in the parent block.
    SimpleMember('block', '<I'),
    # As many 8-byte struct dx_entry as fits in the rest of the data block.
    # struct dx_entry     entries[0] (retrieved in Python Class)
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 h tree dir.
##
class Ext4HTreeDir(object):
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(Ext4HTreeDir, self).__init__()

