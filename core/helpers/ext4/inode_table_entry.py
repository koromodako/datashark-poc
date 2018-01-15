# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: inode_table_entry.py
#     date: 2018-01-12
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
from utils.wrapper import lazy_getter
from utils.struct.union_member import UnionMember
from utils.struct.struct_member import StructMember
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_factory import StructFactory
from helpers.ext4.constants import Ext4InodeMode
from helpers.ext4.constants import Ext4InodeFlag
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_OSD2_LINUX = 's_osd2_linux'
StructFactory.st_register(S_OSD2_LINUX, [
    # Upper 16-bits of the block count. Please see the note attached to
    # i_blocks_lo.
    SimpleMember('l_i_blocks_high', '<H'),
    # Upper 16-bits of the extended attribute block (historically, the file
    # ACL location). See the Extended Attributes section below.
    SimpleMember('l_i_file_acl_high', '<H'),
    # Upper 16-bits of the Owner UID.
    SimpleMember('l_i_uid_high', '<H'),
    # Upper 16-bits of the GID.
    SimpleMember('l_i_gid_high', '<H'),
    # Lower 16-bits of the inode checksum.
    SimpleMember('l_i_checksum_lo', '<H'),
    # Unused.
    SimpleMember('l_i_reserved', '<H')
])
S_OSD2_HURD = 's_osd2_hurd'
StructFactory.st_register(S_OSD2_HURD, [
    # ??
    SimpleMember('h_i_reserved1', '<H'),
    # Upper 16-bits of the file mode.
    SimpleMember('h_i_mode_high', '<H'),
    # Upper 16-bits of the Owner UID.
    SimpleMember('h_i_uid_high', '<H'),
    # Upper 16-bits of the GID.
    SimpleMember('h_i_gid_high', '<H'),
    # Author code?
    SimpleMember('h_i_author', '<I')
])
S_OSD2_MASIX = 's_osd2_masix'
StructFactory.st_register(S_OSD2_MASIX, [
    # ??
    SimpleMember('h_i_reserved1', '<H'),
    # Upper 16-bits of the extended attribute block (historically, the file
    # ACL location).
    SimpleMember('m_i_file_acl_high', '<H'),
    # ??
    SimpleMember('m_i_reserved2', '<II', load=False)
])
S_EXT4_INODE = 'ext4_inode'
StructFactory.st_register(S_EXT4_INODE, [
    # File mode.
    SimpleMember('i_mode', '<H'),
    # Lower 16-bits of Owner UID.
    SimpleMember('i_uid', '<H'),
    # Lower 32-bits of size in bytes.
    SimpleMember('i_size_lo', '<I'),
    # Last access time, in seconds since the epoch. However, if the EA_INODE
    # inode flag is set, this inode stores an extended attribute value and this
    # field contains the checksum of the value.
    SimpleMember('i_atime', '<I'),
    # Last inode change time, in seconds since the epoch. However, if the
    # EA_INODE inode flag is set, this inode stores an extended attribute value
    # and this field contains the lower 32 bits of the attribute value's
    # reference count.
    SimpleMember('i_ctime', '<I'),
    # Last data modification time, in seconds since the epoch. However, if the
    # EA_INODE inode flag is set, this inode stores an extended attribute value
    # and this field contains the number of the inode that owns the extended
    # attribute.
    SimpleMember('i_mtime', '<I'),
    # Deletion Time, in seconds since the epoch.
    SimpleMember('i_dtime', '<I'),
    # Lower 16-bits of GID.
    SimpleMember('i_gid', '<H'),
    # Hard link count. Normally, ext4 does not permit an inode to have more
    # than 65,000 hard links. This applies to files as well as directories,
    # which means that there cannot be more than 64,998 subdirectories in a
    # directory (each subdirectory's '..' entry counts as a hard link, as does
    # the '.' entry in the directory itself). With the DIR_NLINK feature
    # enabled, ext4 supports more than 64,998 subdirectories by setting this
    # field to 1 to indicate that the number of hard links is not known.
    SimpleMember('i_links_count', '<H'),
    # Lower 32-bits of "block" count. If the huge_file feature flag is not set
    # on the filesystem, the file consumes i_blocks_lo 512-byte blocks on disk.
    # If huge_file is set and EXT4_HUGE_FILE_FL is NOT set in inode.i_flags,
    # then the file consumes i_blocks_lo + (i_blocks_hi << 32) 512-byte blocks
    # on disk. If huge_file is set and EXT4_HUGE_FILE_FL IS set in
    # inode.i_flags, then this file consumes (i_blocks_lo + i_blocks_hi << 32)
    # filesystem blocks on disk.
    SimpleMember('i_blocks_lo', '<I'),
    # Inode flags.
    SimpleMember('i_flags', '<I'),
    UnionMember('osd1', [
        # Inode version. However, if the EA_INODE inode flag is set, this inode
        # stores an extended attribute value and this field contains the upper
        # 32 bits of the attribute value's reference count.
        SimpleMember('l_i_version', '<I'),
        # ??
        SimpleMember('h_i_translator', '<I'),
        # ??
        SimpleMember('m_i_reserved', '<I')
    ]),
0x28    60 bytes    i_block[EXT4_N_BLOCKS=15]   Block map or extent tree. See the section "The Contents of inode.i_block".
    # File version (for NFS).
    SimpleMember('i_generation', '<I'),
    # Lower 32-bits of extended attribute block. ACLs are of course one of
    # many possible extended attributes; I think the name of this field is a
    # result of the first use of extended attributes being for ACLs.
    SimpleMember('i_file_acl_lo', '<I'),
    # Upper 32-bits of file/directory size.
    # In ext2/3 this field was named i_dir_acl,though it was usually set to
    # zero and never used.
    SimpleMember('i_size_high', '<I'),
    # (Obsolete) fragment address.
    SimpleMember('i_obso_faddr', '<I'),
    UnionMember('osd2', [
        StructMember('linux2', S_OSD2_LINUX),
        StructMember('hurd2', S_OSD2_HURD),
        StructMember('masix2', S_OSD2_MASIX)
    ])
    # Size of this inode - 128. Alternately, the size of the extended inode
    # fields beyond the original ext2 inode, including this field.
    SimpleMember('i_extra_isize', '<H'),
    # Upper 16-bits of the inode checksum.
    SimpleMember('i_checksum_hi', '<H'),
    # Extra change time bits. This provides sub-second precision. See Inode
    # Timestamps section.
    SimpleMember('i_ctime_extra', '<I'),
    # Extra modification time bits. This provides sub-second precision.
    SimpleMember('i_mtime_extra', '<I'),
    # Extra access time bits. This provides sub-second precision.
    SimpleMember('i_atime_extra', '<I'),
    # File creation time, in seconds since the epoch.
    SimpleMember('i_crtime', '<I'),
    # Extra file creation time bits. This provides sub-second precision.
    SimpleMember('i_crtime_extra', '<I'),
    # Upper 32-bits for version number.
    SimpleMember('i_version_hi', '<I'),
    # Project ID.
    SimpleMember('i_projid', '<I')
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 inode.
##
class Ext4Inode(object):
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, bf, oft):
        super(Ext4Inode, self).__init__()
        self._inode = StructFactory.st_from_file(S_EXT4_INODE, bf, oft)
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return True
