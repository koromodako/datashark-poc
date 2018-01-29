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
from utils.logging import todo
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.comparing import is_flag_set
from utils.converting import lohi2int
from utils.converting import timestamp2utc
from helpers.ext4.tree import Ext4Tree
from helpers.ext4.block_map import Ext4BlockMap
from helpers.ext4.constants import Ext4FileType
from helpers.ext4.constants import Ext4InodeMode
from helpers.ext4.constants import Ext4InodeFlag
from utils.struct.union_member import UnionMember
from utils.struct.struct_member import StructMember
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
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
    SimpleMember('i_mode', '<H', fmtr=Ext4InodeMode),
    # Lower 16-bits of Owner UID.
    SimpleMember('i_uid', '<H'),
    # Lower 32-bits of size in bytes.
    SimpleMember('i_size_lo', '<I'),
    # Last access time, in seconds since the epoch. However, if the EA_INODE
    # inode flag is set, this inode stores an extended attribute value and this
    # field contains the checksum of the value.
    SimpleMember('i_atime', '<I', fmtr=timestamp2utc),
    # Last inode change time, in seconds since the epoch. However, if the
    # EA_INODE inode flag is set, this inode stores an extended attribute value
    # and this field contains the lower 32 bits of the attribute value's
    # reference count.
    SimpleMember('i_ctime', '<I', fmtr=timestamp2utc),
    # Last data modification time, in seconds since the epoch. However, if the
    # EA_INODE inode flag is set, this inode stores an extended attribute value
    # and this field contains the number of the inode that owns the extended
    # attribute.
    SimpleMember('i_mtime', '<I', fmtr=timestamp2utc),
    # Deletion Time, in seconds since the epoch.
    SimpleMember('i_dtime', '<I', fmtr=timestamp2utc),
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
    SimpleMember('i_flags', '<I', fmtr=Ext4InodeFlag),
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
    # Block map or extent tree. See the section "The Contents of inode.i_block".
    ByteArrayMember('i_block', 60),
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
    ]),
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
    SimpleMember('i_crtime', '<I', fmtr=timestamp2utc),
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
    def __init__(self, fs, bf, oft):
        super(Ext4Inode, self).__init__()
        self._fs = fs
        self._bf = bf
        self._inode = StructFactory.st_from_file(S_EXT4_INODE, bf, oft)
        self.valid = self._parse()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse(self):
        self._data = None
        self._tree = None
        self._block_map = None
        if is_flag_set(self.flags(), Ext4InodeFlag.EXT4_EXTENTS_FL):
            return self._parse_extents()
        elif is_flag_set(self.mode(), Ext4InodeMode.S_IFLNK) and self.size() < 60:
            return True

        return self._parse_block_map()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse_extents(self):
        self._tree = Ext4Tree(self._fs.block_size(),
                              self._bf,
                              self._inode.i_block)
        return self._tree.is_valid()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse_block_map(self):
        self._block_map = Ext4BlockMap(self._fs.block_size(),
                                       self._bf,
                                       self._inode.i_block)
        return self._block_map.is_valid()
    ##
    ## @brief      { function_description }
    ##
    ## @param      n     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _read(self, n=-1, oft=0):
        if self._tree is not None:
            return self._tree.read(n, oft)

        if self._block_map is not None:
            return self._block_map.read(n, oft)

        LGR.error("Neither extent tree nor block map was initialized.")
        return None
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _entries(self):
        todo(LGR, "implement entries listing for a directory.")
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return self.valid
    # -------------------------------------------------------------------------
    #  ENHANCED GETTERS
    # -------------------------------------------------------------------------
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_ftype')
    def ftype(self):
        mode = self.mode()
        if is_flag_set(mode, Ext4InodeMode.S_IFLNK):
            return Ext4FileType.SYMLINK

        elif is_flag_set(mode, Ext4InodeMode.S_IFIFO):
            return Ext4FileType.FIFO

        elif is_flag_set(mode, Ext4InodeMode.S_IFCHR):
            return Ext4FileType.CHR_DEV

        elif is_flag_set(mode, Ext4InodeMode.S_IFDIR):
            return Ext4FileType.DIRECTORY

        elif is_flag_set(mode, Ext4InodeMode.S_IFBLK):
            return Ext4FileType.BLK_DEV

        elif is_flag_set(mode, Ext4InodeMode.S_IFREG):
            return Ext4FileType.REG_FILE

        elif is_flag_set(mode, Ext4InodeMode.S_IFSOCK):
            return Ext4FileType.SOCKET

        return Ext4FileType.UNKNOWN
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_mode')
    def mode(self):
        return Ext4InodeMode(self._inode.i_mode)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_atime')
    def atime(self):
        return timestamp2utc(self._inode.i_atime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_ctime')
    def ctime(self):
        return timestamp2utc(self._inode.i_ctime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_mtime')
    def mtime(self):
        return timestamp2utc(self._inode.i_mtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_dtime')
    def dtime(self):
        return timestamp2utc(self._inode.i_dtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_flags')
    def flags(self):
        return Ext4InodeFlag(self._inode.i_flags)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_crtime')
    def crtime(self):
        return timestamp2utc(self._inode.i_crtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_checksum')
    def checksum(self):
        return lohi2int(self._inode.osd2.linux2.l_i_checksum_lo,
                        self._inode.i_checksum_hi, sz=16)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_size')
    def size(self):
        return lohi2int(self._inode.i_size_lo, self._inode.i_size_high)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_blocks')
    def blocks(self):
        if is_flag_set(self.flags(), Ext4InodeFlag.EXT4_HUGE_FILE_FL):
            blocks = self._inode.i_blocks_lo
            blocks += self._inode.osd2.linux2.l_i_blocks_high
            blocks <<= 32
        else:
            blocks = lohi2int(self._inode.i_blocks_lo,
                              self._inode.osd2.linux2.l_i_blocks_high)
        return blocks
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_file_acl')
    def file_acl(self):
        return lohi2int(self._inode.i_file_acl_lo,
                        self._inode.osd2.linux2.l_i_file_acl_high)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_target')
    def target(self):
        if self.ftype() != Ext4FileType.SYMLINK:
            LGR.error("cannot call 'target()' for a non-symlink file.")
            return None

        if self.size() < 60:
            return self._inode.i_block

        return self._read()
    ##
    ## @brief      { function_description }
    ##
    ## @param      n     { parameter_description }
    ## @param      oft   The oft
    ##
    ## @return     { description_of_the_return_value }
    ##
    def read(self, n=-1, oft=0):
        if self.ftype() != Ext4FileType.REG_FILE:
            LGR.error("cannot call 'read()' on a non-regular file.")
            return None

        sz = self.size()
        if n < 0 or n > sz:
            n = sz

        if is_flag_set(self.flags(), Ext4InodeFlag.EXT4_INLINE_DATA_FL):
            data = self._inode.i_block[oft:n]

            if n > 60:
                data += self._read(n-60)

            return data

        return self._read(n, oft)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def entries(self):
        if self.ftype() != Ext4FileType.DIRECTORY:
            LGR.error("cannot call 'entries()' on a non-directory file.")
            return None

        return self._entries()

