# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: constants.py
#     date: 2018-01-08
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
import enum
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for block group flag.
##
class Ext4BGDFlag(enum.Flag):
    ##
    ## Inode table and bitmap are not initialized.
    ##
    EXT4_BG_INODE_UNINIT = 0x1
    ##
    ## Block bitmap is not initialized.
    ##
    EXT4_BG_BLOCK_UNINIT = 0x2
    ##
    ## Inode table is zeroed.
    ##
    EXT4_BG_INODE_ZEROED = 0x4
##
## @brief      Class for extent 4 state.
##
class Ext4State(enum.Flag):
    CLEANLY_UNMOUNTED = 0x0001
    ERRORS_DETECTED = 0x0002
    ORPHANS_BEING_RECOVERED = 0x0004
##
## @brief      Class for extent 4 error.
##
class Ext4Error(enum.Enum):
    CONTINUE = 1
    REMOUNT_RO = 2
    PANIC = 3
##
## @brief      Class for extent 4 os.
##
class Ext4OS(enum.Enum):
    LINUX = 0
    HURD = 1
    MASIX = 2
    FREEBSD = 3
    LITES = 4
##
## @brief      Class for extent 4 reverse.
##
class Ext4Rev(enum.Enum):
    ORIGINAL_FORMAT = 0
    V2_DYN_INODE_SZ = 1
##
## @brief      Flag for extent 4 compatible SB field.
##
class Ext4Compat(enum.Flag):
    ##
    ## Directory preallocation
    ##
    COMPAT_DIR_PREALLOC = 0x1
    ##
    ## "imagic inodes". Not clear from the code what this does.
    ##
    COMPAT_IMAGIC_INODES = 0x2
    ##
    ## Has a journal.
    ##
    COMPAT_HAS_JOURNAL = 0x4
    ##
    ## Supports extended attributes.
    ##
    COMPAT_EXT_ATTR = 0x8
    ##
    ## Has reserved GDT blocks for filesystem expansion.
    ##
    COMPAT_RESIZE_INODE = 0x10
    ##
    ## Has directory indices.
    ##
    COMPAT_DIR_INDEX = 0x20
    ##
    ## "Lazy BG". Not in Linux kernel, seems to have been for uninitialized
    ## block groups?
    ##
    COMPAT_LAZY_BG = 0x40
    ##
    ## "Exclude inode". Not used.
    ##
    COMPAT_EXCLUDE_INODE = 0x80
    ##
    ## "Exclude bitmap". Seems to be used to indicate the presence of
    ## snapshot-related exclude bitmaps? Not defined in kernel or used in
    ## e2fsprogs.
    ##
    COMPAT_EXCLUDE_BITMAP = 0x100
    ##
    ## Sparse Super Block, v2. If this flag is set, the SB field s_backup_bgs
    ## points to the two block groups that contain backup superblocks.
    ##
    COMPAT_SPARSE_SUPER2 = 0x200
##
## @brief      Flag for extent 4 incompat SB field.
##
class Ext4Incompat(enum.Flag):
    ##
    ## Compression.
    ##
    INCOMPAT_COMPRESSION = 0x1
    ##
    ## Directory entries record the file type. See ext4_dir_entry_2 below.
    ##
    INCOMPAT_FILETYPE = 0x2
    ##
    ## Filesystem needs recovery.
    ##
    INCOMPAT_RECOVER = 0x4
    ##
    ## Filesystem has a separate journal device.
    ##
    INCOMPAT_JOURNAL_DEV = 0x8
    ##
    ## Meta block groups.
    ##
    INCOMPAT_META_BG = 0x10
    ##
    ## Files in this filesystem use extents.
    ##
    INCOMPAT_EXTENTS = 0x40
    ##
    ## Enable a filesystem size of 2^64 blocks.
    ##
    INCOMPAT_64BIT = 0x80
    ##
    ## Multiple mount protection. Not implemented.
    ##
    INCOMPAT_MMP = 0x100
    ##
    ## Flexible block groups.
    ##
    INCOMPAT_FLEX_BG = 0x200
    ##
    ## Inodes can be used to store large extended attribute values.
    ##
    INCOMPAT_EA_INODE = 0x400
    ##
    ## Data in directory entry. (Not implemented?)
    ##
    INCOMPAT_DIRDATA = 0x1000
    ##
    ## Metadata checksum seed is stored in the superblock. This feature enables
    ## the administrator to change the UUID of a metadata_csum filesystem while
    ## the filesystem is mounted; without it, the checksum definition requires
    ## all metadata blocks to be rewritten.
    ##
    INCOMPAT_CSUM_SEED = 0x2000
    ##
    ## Large directory >2GB or 3-level htree. Prior to this feature,
    ## directories could not be larger than 4GiB and could not have an htree
    ## more than 2 levels deep. If this feature is enabled, directories can be
    ## larger than 4GiB and have a maximum htree depth of 3.
    ##
    INCOMPAT_LARGEDIR = 0x4000
    ##
    ## Data in inode.
    ##
    INCOMPAT_INLINE_DATA = 0x8000
    ##
    ## Encrypted inodes are present on the filesystem.
    ##
    INCOMPAT_ENCRYPT = 0x10000
##
## @brief      Flag for extent 4 read only compatible SB field.
##
class Ext4ReadOnlyCompat(enum.Flag):
    ##
    ## Sparse superblocks.
    ##
    RO_COMPAT_SPARSE_SUPER = 0x1
    ##
    ## This filesystem has been used to store a file greater than 2GiB.
    ##
    RO_COMPAT_LARGE_FILE = 0x2
    ##
    ## Not used in kernel or e2fsprogs.
    ##
    RO_COMPAT_BTREE_DIR = 0x4
    ##
    ## This filesystem has files whose sizes are represented in units of
    ## logical blocks, not 512-byte sectors. This implies a very large file
    ## indeed!)
    ##
    RO_COMPAT_HUGE_FIL = 0x8
    ##
    ## Group descriptors have checksums. In addition to detecting corruption,
    ## this is useful for lazy formatting with uninitialized groups.
    ##
    RO_COMPAT_GDT_CSUM = 0x10
    ##
    ## Indicates that the old ext3 32,000 subdirectory limit no longer applies.
    ## A directory's i_links_count will be set to 1 if it is incremented past
    ## 64,999.
    ##
    RO_COMPAT_DIR_NLINK = 0x20
    ##
    ## Indicates that large inodes exist on this filesystem.
    ##
    RO_COMPAT_EXTRA_ISIZE = 0x40
    ##
    ## This filesystem has a snapshot.
    ##
    RO_COMPAT_HAS_SNAPSHOT = 0x80
    ##
    ## Quota.
    ##
    RO_COMPAT_QUOTA = 0x100
    ##
    ## This filesystem supports "bigalloc", which means that file extents are
    ## tracked in units of clusters (of blocks) instead of blocks.
    ##
    RO_COMPAT_BIGALLOC = 0x200
    ##
    ## This filesystem supports metadata checksumming; implies
    ## RO_COMPAT_GDT_CSUM, though GDT_CSUM must not be set..
    ##
    RO_COMPAT_METADATA_CSUM = 0x400
    ##
    ## Filesystem supports replicas. This feature is neither in the kernel nor
    ## e2fsprogs.
    ##
    RO_COMPAT_REPLICA = 0x800
    ##
    ## Read-only filesystem image; the kernel will not mount this image
    ## read-write and most tools will refuse to write to the image..
    ##
    RO_COMPAT_READONLY = 0x1000
    ##
    ## Filesystem tracks project quotas.
    ##
    RO_COMPAT_PROJECT = 0x2000
##
## @brief      Class for extent 4 hash algorithm.
##
class Ext4HashAlgo(enum.Enum):
    LEGACY = 0
    HALF_MD4 = 1
    TEA = 2
    LEGACY_UNSIGNED = 3
    HALF_MD4_UNSIGNED = 4
    TEA_UNSIGNED = 5
##
## @brief      Flag for extent 4 mount options.
##
class Ext4MountOpts(enum.Flag):
    ##
    ## Print debugging info upon (re)mount.
    ##
    EXT4_DEFM_DEBUG = 0x0001
    ##
    ## New files take the gid of the containing directory (instead of the fsgid
    ## of the current process).
    ##
    EXT4_DEFM_BSDGROUPS = 0x0002
    ##
    ## Support userspace-provided extended attributes.
    ##
    EXT4_DEFM_XATTR_USER = 0x0004
    ##
    ## Support POSIX access control lists (ACLs).
    ##
    EXT4_DEFM_ACL = 0x0008
    ##
    ## Do not support 32-bit UIDs.
    ##
    EXT4_DEFM_UID16 = 0x0010
    ##
    ## All data and metadata are commited to the journal.
    ##
    EXT4_DEFM_JMODE_DATA = 0x0020
    ##
    ## All data are flushed to the disk before metadata are committed to the
    ## journal.
    ##
    EXT4_DEFM_JMODE_ORDERED = 0x0040
    ##
    ## Data ordering is not preserved; data may be written after the metadata
    ## has been written.
    ##
    EXT4_DEFM_JMODE_WBACK = 0x0060
    ##
    ## Disable write flushes.
    ##
    EXT4_DEFM_NOBARRIER = 0x0100
    ##
    ## Track which blocks in a filesystem are metadata and therefore should
    ## not be used as data blocks. This option will be enabled by default on
    ## 3.18, hopefully.
    ##
    EXT4_DEFM_BLOCK_VALIDITY = 0x0200
    ##
    ## Enable DISCARD support, where the storage device is told about blocks
    ## becoming unused.
    ##
    EXT4_DEFM_DISCARD = 0x0400
    ##
    ## Disable delayed allocation.
    ##
    EXT4_DEFM_NODELALLOC = 0x0800
##
## @brief      Class for extent 4 misc flag.
##
class Ext4MiscFlag(enum.Flag):
    ##
    ## Signed directory hash in use.
    ##
    EXT4_MISC_SIGNED_DIR_HASH = 0x0001
    ##
    ## Unsigned directory hash in use.
    ##
    EXT4_MISC_UNSIGNED_DIR_HASH = 0x0002
    ##
    ## To test development code.
    ##
    EXT4_MISC_DEV_TEST = 0x0004
##
## @brief      Class for extent 4 encrypt algorithm.
##
class Ext4EncryptAlgo(enum.Enum):
    ##
    ## Invalid algorithm.
    ##
    ENCRYPTION_MODE_INVALID = 0
    ##
    ## 256-bit AES in XTS mode.
    ##
    ENCRYPTION_MODE_AES_256_XTS = 1
    ##
    ## 256-bit AES in GCM mode.
    ##
    ENCRYPTION_MODE_AES_256_GCM = 2
    ##
    ## 256-bit AES in CBC mode.
    ##
    ENCRYPTION_MODE_AES_256_CBC = 3
