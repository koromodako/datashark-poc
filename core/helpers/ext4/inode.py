# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: inode.py
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
from utils.struct.factory import StructFactory
from utils.struct.wrapper import StructWrapper
from helpers.ext4.constants import Ext4FileType
from helpers.ext4.constants import Ext4InodeMode
from helpers.ext4.constants import Ext4InodeFlag
from helpers.ext4.constants import Ext4InodeVersion
from utils.struct.union_member import UnionMember
from utils.struct.struct_member import StructMember
from utils.struct.simple_member import SimpleMember
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
    SimpleMember('i_blocks_lo', '<I'), # unit: FS block or 512
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
        StructMember('linux', S_OSD2_LINUX),
        StructMember('hurd', S_OSD2_HURD),
        StructMember('masix', S_OSD2_MASIX)
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
class Ext4Inode(StructWrapper):
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, number, bf, oft, version=Ext4InodeVersion.LINUX):
        super(Ext4Inode, self).__init__(S_EXT4_INODE, bf=bf, oft=oft)
        self.number = number
        self.version = version
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        todo("should check checksum here...", no_raise=True)
        return True
    ##
    ## @brief      Returns i_block's bytes
    ##
    def block(self):
        return self._s.i_block
    ##
    ## @brief      Returns hardlinks count
    ##
    def links_count(self):
        return self._s.i_links_count
    # -------------------------------------------------------------------------
    #  ENHANCED GETTERS
    # -------------------------------------------------------------------------
    ##
    ## @brief      Returns mode as a flag instance (including file type and
    #              permissions)
    ##
    @lazy_getter('_mode')
    def mode(self):
        mode = self._s.i_mode

        if self.version == Ext4InodeVersion.HURD:
            mode = lohi2int(mode, self._s.os2.hurd2.h_i_mode_high, 16)

        return Ext4InodeMode(mode)
    ##
    ## @brief      Returns file type
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
    ## @brief      Returns file permissions using POSIX syntax
    ##
    @lazy_getter('_permissions')
    def permissions(self):
        perm = ['-' for k in range(10)]

        ftype = self.ftype()

        if ftype == Ext4FileType.SYMLINK:
            perm[0] = 'l'
        elif ftype == Ext4FileType.DIRECTORY:
            perm[0] = 'd'

        mode = self.mode()

        perm[1] = "r" if is_flag_set(mode, Ext4InodeMode.S_IRUSR) else "-"
        perm[2] = "w" if is_flag_set(mode, Ext4InodeMode.S_IWUSR) else "-"
        perm[3] = "x" if is_flag_set(mode, Ext4InodeMode.S_IXUSR) else "-"
        perm[4] = "r" if is_flag_set(mode, Ext4InodeMode.S_IRGRP) else "-"
        perm[5] = "w" if is_flag_set(mode, Ext4InodeMode.S_IWGRP) else "-"
        perm[6] = "x" if is_flag_set(mode, Ext4InodeMode.S_IXGRP) else "-"
        perm[7] = "r" if is_flag_set(mode, Ext4InodeMode.S_IROTH) else "-"
        perm[8] = "w" if is_flag_set(mode, Ext4InodeMode.S_IWOTH) else "-"
        perm[9] = "x" if is_flag_set(mode, Ext4InodeMode.S_IXOTH) else "-"

        perm[3] = "s" if is_flag_set(mode, Ext4InodeMode.S_ISUID) else perm[3]
        perm[6] = "s" if is_flag_set(mode, Ext4InodeMode.S_ISGID) else perm[6]
        perm[9] = "t" if is_flag_set(mode, Ext4InodeMode.S_ISVTX) else perm[9]

        return ''.join(perm)
    ##
    ## @brief      Returns file user id
    ##
    @lazy_getter('_uid')
    def uid(self):
        uid = self._s.i_uid

        if self.version == Ext4InodeVersion.LINUX:
            uid = lohi2int(uid, self._s.osd2.linux.l_i_uid_high, 16)
        elif self.version == Ext4InodeVersion.HURD:
            uid = lohi2int(uid, self._s.osd2.hurd.h_i_uid_high, 16)

        return uid
    ##
    ## @brief      Returns file group id
    ##
    @lazy_getter('_gid')
    def gid(self):
        gid = self._s.i_gid

        if self.version == Ext4InodeVersion.LINUX:
            gid = lohi2int(gid, self._s.osd2.linux.l_i_gid_high, 16)
        elif self.version == Ext4InodeVersion.HURD:
            gid = lohi2int(gid, self._s.osd2.hurd.h_i_gid_high, 16)

        return gid
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_file_acl')
    def file_acl(self):
        acl = self._s.i_file_acl_lo

        if self.version == Ext4InodeVersion.LINUX:
            acl = lohi2int(acl, self._s.osd2.linux.l_i_file_acl_high)
        elif self.version == Ext4InodeVersion.MASIX:
            acl = lohi2int(acl, self._s.osd2.masix.m_i_file_acl_high)

        return acl
    ##
    ## @brief      Last status change time
    ##
    @lazy_getter('_ctime')
    def ctime(self):
        return timestamp2utc(self._s.i_ctime)
    ##
    ## @brief      Last access time
    ##
    @lazy_getter('_atime')
    def atime(self):
        return timestamp2utc(self._s.i_atime)
    ##
    ## @brief      Last modification time
    ##
    @lazy_getter('_mtime')
    def mtime(self):
        return timestamp2utc(self._s.i_mtime)
    ##
    ## @brief      Deletion time
    ##
    @lazy_getter('_dtime')
    def dtime(self):
        return timestamp2utc(self._s.i_dtime)
    ##
    ## @brief      Returns flags or check if a flag is set
    ##
    ## @param      has   Flag to check
    ##
    def flags(self, has=None):
        flags = Ext4InodeFlag(self._s.i_flags)

        if has is None:
            return flags

        return is_flag_set(flags, has)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_crtime')
    def crtime(self):
        return timestamp2utc(self._s.i_crtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_checksum')
    def checksum(self):
        checksum = self._s.i_checksum_hi

        if self.version == Ext4InodeVersion.LINUX:
            checksum = lohi2int(self._s.osd2.linux.l_i_checksum_lo, checksum, 16)

        return checksum
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_size')
    def size(self):
        return lohi2int(self._s.i_size_lo, self._s.i_size_high)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_blocks')
    def blocks(self):
        if self.version == Ext4InodeVersion.LINUX:
            if is_flag_set(self.flags(), Ext4InodeFlag.EXT4_HUGE_FILE_FL):
                blocks = self._s.i_blocks_lo
                blocks += self._s.osd2.linux.l_i_blocks_high
                blocks <<= 32
            else:
                blocks = lohi2int(self._s.i_blocks_lo,
                                  self._s.osd2.linux.l_i_blocks_high)
        else:
            blocks = self._s.i_blocks_lo

        return blocks
    ##
    ## @brief      Returns the description using the following format
    ##             10228426 -rw-r--r-- 1 paul paul  1,4G janv.  7 15:33 partition.3.1c566bda.ds
    ##
    def description(self, name, human=False):
        uid = self.uid()
        gid = self.gid()
        size = self.size()

        if human:
            uid = "({}:{})".format(uid, "root" if uid == 0 else "unknown")
            gid = "({}:{})".format(gid, "root" if gid == 0 else "unknown")
            size = format_size(size)

        return "{} {} {} {} {} {} {} {}".format(self.number,
                                                self.permissions(),
                                                self.links_count(),
                                                uid, gid, size,
                                                self.ctime(),
                                                self.atime(),
                                                self.mtime(),
                                                self.dtime(),
                                                name)
