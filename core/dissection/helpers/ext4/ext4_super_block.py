# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4_super_block.py
#     date: 2018-01-07
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
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.struct.array_member import ArrayMember
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_specif import StructSpecif
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_EXT4_SB = 'ext4_super_block'
StructFactory.st_register(StructSpecif(S_EXT4_SB, [
    SimpleMember('s_inodes_count', '<I'),           # Total inode count.
    SimpleMember('s_blocks_count_lo', '<I'),        # Total block count.
    SimpleMember('s_r_blocks_count_lo', '<I'),      # This number of blocks can only be allocated by the super-user.
    SimpleMember('s_free_blocks_count_lo', '<I'),   # Free block count.
    SimpleMember('s_free_inodes_count', '<I'),      # Free inode count.
    SimpleMember('s_first_data_block', '<I'),       # First data block. This must be at least 1 for 1k-block filesystems and is typically 0 for all other block sizes.
    SimpleMember('s_log_block_size', '<I'),         # Block size is 2 ^ (10 + s_log_block_size).
    SimpleMember('s_log_cluster_size', '<I'),       # Cluster size is (2 ^ s_log_cluster_size) blocks if bigalloc is enabled, zero otherwise.
    SimpleMember('s_blocks_per_group', '<I'),       # Blocks per group.
    SimpleMember('s_clusters_per_group', '<I'),     # Clusters per group, if bigalloc is enabled.
    SimpleMember('s_inodes_per_group', '<I'),       # Inodes per group.
    SimpleMember('s_mtime', '<I'),                  # Mount time, in seconds since the epoch.
    SimpleMember('s_wtime', '<I'),                  # Write time, in seconds since the epoch.
    SimpleMember('s_mnt_count', '<H'),              # Number of mounts since the last fsck.
    SimpleMember('s_max_mnt_count', '<H'),          # Number of mounts beyond which a fsck is needed.
    SimpleMember('s_magic', '<H'),                  # Magic signature, 0xEF53
    SimpleMember('s_state', '<H'),                  # File system state.
    SimpleMember('s_errors', '<H'),                 # Behaviour when detecting errors.
    SimpleMember('s_minor_rev_level', '<H'),        # Minor revision level.
    SimpleMember('s_lastcheck', '<I'),              # Time of last check, in seconds since the epoch.
    SimpleMember('s_checkinterval', '<I'),          # Maximum time between checks, in seconds.
    SimpleMember('s_creator_os', '<I'),             # OS
    SimpleMember('s_rev_level', '<I'),              # Revision level.
    SimpleMember('s_def_resuid', '<H'),             # Default uid for reserved blocks.
    SimpleMember('s_def_resgid', '<H'),             # Default gid for reserved blocks.
    SimpleMember('s_first_ino', '<I'),              # First non-reserved inode.
    SimpleMember('s_inode_size', '<H'),             # Size of inode structure, in bytes.
    SimpleMember('s_block_group_nr', '<H'),         # Block group # of this superblock.
    SimpleMember('s_feature_compat', '<I'),         # Compatible feature set flags. Kernel can still read/write this fs even if it doesn't understand a flag; fsck should not do that. Any of:
    SimpleMember('s_feature_incompat', '<I'),       # Incompatible feature set. If the kernel or fsck doesn't understand one of these bits, it should stop.
    SimpleMember('s_feature_ro_compat', '<I'),      # Readonly-compatible feature set. If the kernel doesn't understand one of these bits, it can still mount read-only.
    ByteArrayMember('s_uuid', 16),                  # 128-bit UUID for volume.
    ByteArrayMember('s_volume_name', 16),           # Volume label.
    ByteArrayMember('s_last_mounted', 64),          # Directory where filesystem was last mounted.
    SimpleMember('s_algorithm_usage_bitmap', '<I'), # For compression (Not used in e2fsprogs/Linux)
    SimpleMember('s_prealloc_blocks', '<B'),        # Number of blocks to try to preallocate for ... files? (Not used in e2fsprogs/Linux)
    SimpleMember('s_prealloc_dir_blocks', '<B'),    # Number of blocks to preallocate for directories. (Not used in e2fsprogs/Linux)
    SimpleMember('s_reserved_gdt_blocks', '<H'),    # Number of reserved GDT entries for future filesystem expansion.
    ByteArrayMember('s_journal_uuid', 16),          # UUID of journal superblock
    SimpleMember('s_journal_inum', '<I'),           # inode number of journal file.
    SimpleMember('s_journal_dev', '<I'),            # Device number of journal file, if the external journal feature flag is set.
    SimpleMember('s_last_orphan', '<I'),            # Start of list of orphaned inodes to delete.
    ArrayMember('s_hash_seed', SimpleMember('_', '<I'), 4), # HTREE hash seed.
    SimpleMember('s_def_hash_version', '<B'),       # Default hash algorithm to use for directory hashes.
    SimpleMember('s_jnl_backup_type', '<B'),        # If this value is 0 or EXT3_JNL_BACKUP_BLOCKS (1), then the s_jnl_blocks field contains a duplicate copy of the inode's i_block[] array and i_size.
    SimpleMember('s_desc_size', '<H'),              # Size of group descriptors, in bytes, if the 64bit incompat feature flag is set.
    SimpleMember('s_default_mount_opts', '<I'),     # Default mount options.
    SimpleMember('s_first_meta_bg', '<I'),          # First metablock block group, if the meta_bg feature is enabled.
    SimpleMember('s_mkfs_time', '<I'),              # When the filesystem was created, in seconds since the epoch.
    ArrayMember('s_jnl_blocks', SimpleMember('_', '<I'), 17), # Backup copy of the journal inode's i_block[] array in the first 15 elements and i_size_high and i_size in the 16th and 17th elements, respectively.
    SimpleMember('s_blocks_count_hi', '<I'),        # High 32-bits of the block count.
    SimpleMember('s_r_blocks_count_hi', '<I'),      # High 32-bits of the reserved block count.
    SimpleMember('s_free_blocks_count_hi', '<I'),   # High 32-bits of the free block count.
    SimpleMember('s_min_extra_isize', '<H'),        # All inodes have at least # bytes.
    SimpleMember('s_want_extra_isize', '<H'),       # New inodes should reserve # bytes.
    SimpleMember('s_flags', '<I'),                  # Miscellaneous flags.
    SimpleMember('s_raid_stride', '<H'),            # RAID stride. This is the number of logical blocks read from or written to the disk before moving to the next disk. This affects the placement of filesystem metadata, which will hopefully make RAID storage faster.
    SimpleMember('s_mmp_interval', '<H'),           # Number of seconds to wait in multi-mount prevention (MMP) checking. In theory, MMP is a mechanism to record in the superblock which host and device have mounted the filesystem, in order to prevent multiple mounts. This feature does not seem to be implemented...
    SimpleMember('s_mmp_block', '<Q'),              # Block # for multi-mount protection data.
    SimpleMember('s_raid_stripe_width', '<I'),      # RAID stripe width. This is the number of logical blocks read from or written to the disk before coming back to the current disk. This is used by the block allocator to try to reduce the number of read-modify-write operations in a RAID5/6.
    SimpleMember('s_log_groups_per_flex', '<B'),    # Size of a flexible block group is 2 ^ s_log_groups_per_flex.
    SimpleMember('s_checksum_type', '<B'),          # Metadata checksum algorithm type. The only valid value is 1 (crc32c).
    SimpleMember('s_reserved_pad', '<H', load=False),
    SimpleMember('s_kbytes_written', '<Q'),         # Number of KiB written to this filesystem over its lifetime.
    SimpleMember('s_snapshot_inum', '<I'),          # inode number of active snapshot. (Not used in e2fsprogs/Linux.)
    SimpleMember('s_snapshot_id', '<I'),            # Sequential ID of active snapshot. (Not used in e2fsprogs/Linux.)
    SimpleMember('s_snapshot_r_blocks_count', '<Q'),# Number of blocks reserved for active snapshot's future use. (Not used in e2fsprogs/Linux.)
    SimpleMember('s_snapshot_list', '<I'),          # inode number of the head of the on-disk snapshot list. (Not used in e2fsprogs/Linux.)
    SimpleMember('s_error_count', '<I'),            # Number of errors seen.
    SimpleMember('s_first_error_time', '<I'),       # First time an error happened, in seconds since the epoch.
    SimpleMember('s_first_error_ino', '<I'),        # inode involved in first error.
    SimpleMember('s_first_error_block', '<Q'),      # Number of block involved of first error.
    ByteArrayMember('s_first_error_func', 32),      # Name of function where the error happened.
    SimpleMember('s_first_error_line', '<I'),       # Line number where error happened.
    SimpleMember('s_last_error_time', '<I'),        # Time of most recent error, in seconds since the epoch.
    SimpleMember('s_last_error_ino', '<I'),         # inode involved in most recent error.
    SimpleMember('s_last_error_line', '<I'),        # Line number where most recent error happened.
    SimpleMember('s_last_error_block', '<Q'),       # Number of block involved in most recent error.
    ByteArrayMember('s_last_error_func', 32),       # Name of function where the most recent error happened.
    ByteArrayMember('s_mount_opts', 64),            # ASCIIZ string of mount options.
    SimpleMember('s_usr_quota_inum', '<I'),         # Inode number of user quota file.
    SimpleMember('s_grp_quota_inum', '<I'),         # Inode number of group quota file.
    SimpleMember('s_overhead_blocks', '<I'),        # Overhead blocks/clusters in fs. (Huh? This field is always zero, which means that the kernel calculates it dynamically.)
    ArrayMember('s_backup_bgs', SimpleMember('_', '<I') , 2),  # Block groups containing superblock backups (if sparse_super2)
    ArrayMember('s_encrypt_algos', SimpleMember('_', '<B'), 4),  # Encryption algorithms in use. There can be up to four algorithms in use at any time; valid algorithm codes are given below:
    ByteArrayMember('s_encrypt_pw_salt', 16),       # Salt for the string2key algorithm for encryption.
    SimpleMember('s_lpf_ino', '<I'),                # Inode number of lost+found
    SimpleMember('s_prj_quota_inum', '<I'),         # Inode that tracks project quotas.
    SimpleMember('s_checksum_seed', '<I'),          # Checksum seed used for metadata_csum calculations. This value is crc32c(~0, $orig_fs_uuid).
    ArrayMember('s_reserved', SimpleMember('_', '<I'), 98, load=False), # Padding to the end of the block.
    SimpleMember('s_checksum', '<I')                # Superblock checksum.
]))
# =============================================================================
#  CLASSES
# =============================================================================
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
##
## @brief      Class for extent 4 super block.
##
class Ext4SuperBlock(object):
    ##
    ## ext4 SuperBlock signature
    ##
    SIGN = 0xEF53
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf    { parameter_description }
    ##
    def __init__(self, bf):
        super(Ext4SuperBlock, self).__init__()
        self._sb = StructFactory.st_from_file(S_EXT4_SB, bf, 1024)
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return (self._sb.s_magic == self.SIGN)
