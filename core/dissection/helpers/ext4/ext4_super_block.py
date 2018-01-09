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
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.converting import lohi2int
from utils.converting import int2enum
from utils.converting import uuid_from_bytes
from utils.converting import utcfromtimestamp
from utils.struct.array_member import ArrayMember
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_specif import StructSpecif
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
from dissection.helpers.ext4.constants import Ext4State
from dissection.helpers.ext4.constants import Ext4Error
from dissection.helpers.ext4.constants import Ext4OS
from dissection.helpers.ext4.constants import Ext4Rev
from dissection.helpers.ext4.constants import Ext4Compat
from dissection.helpers.ext4.constants import Ext4Incompat
from dissection.helpers.ext4.constants import Ext4ReadOnlyCompat
from dissection.helpers.ext4.constants import Ext4HashAlgo
from dissection.helpers.ext4.constants import Ext4MountOpts
from dissection.helpers.ext4.constants import Ext4MiscFlag
from dissection.helpers.ext4.constants import Ext4EncryptAlgo
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_EXT4_SB = 'ext4_super_blk'
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
    SimpleMember('s_mtime', '<I', formatter=utcfromtimestamp),                  # Mount time, in seconds since the epoch.
    SimpleMember('s_wtime', '<I', formatter=utcfromtimestamp),                  # Write time, in seconds since the epoch.
    SimpleMember('s_mnt_count', '<H'),              # Number of mounts since the last fsck.
    SimpleMember('s_max_mnt_count', '<H'),          # Number of mounts beyond which a fsck is needed.
    ByteArrayMember('s_magic', 2),                  # Magic signature, 0xEF53
    SimpleMember('s_state', '<H'),                  # File system state.
    SimpleMember('s_errors', '<H'),                 # Behaviour when detecting errors.
    SimpleMember('s_minor_rev_level', '<H'),        # Minor revision level.
    SimpleMember('s_lastcheck', '<I', formatter=utcfromtimestamp),              # Time of last check, in seconds since the epoch.
    SimpleMember('s_checkinterval', '<I'),          # Maximum time between checks, in seconds.
    SimpleMember('s_creator_os', '<I'),             # OS
    SimpleMember('s_rev_level', '<I'),              # Revision level.
    SimpleMember('s_def_resuid', '<H'),             # Default uid for reserved blocks.
    SimpleMember('s_def_resgid', '<H'),             # Default gid for reserved blocks.
    #
    # These fields are for EXT4_DYNAMIC_REV superblocks only.
    #
    # Note: the difference between the compatible feature set and the
    #       incompatible feature set is that if there is a bit set in the
    #       incompatible feature set that the kernel doesn't know about, it
    #       should refuse to mount the filesystem.
    #
    # e2fsck's requirements are more strict; if it doesn't know about a feature
    # in either the compatible or incompatible feature set, it must abort and
    # not try to meddle with things it doesn't understand...
    #
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
    #
    # Performance hints. Directory preallocation should only happen if the
    # EXT4_FEATURE_COMPAT_DIR_PREALLOC flag is on.
    #
    SimpleMember('s_prealloc_blocks', '<B'),        # Number of blocks to try to preallocate for ... files? (Not used in e2fsprogs/Linux)
    SimpleMember('s_prealloc_dir_blocks', '<B'),    # Number of blocks to preallocate for directories. (Not used in e2fsprogs/Linux)
    SimpleMember('s_reserved_gdt_blocks', '<H'),    # Number of reserved GDT entries for future filesystem expansion.
    #
    # Journaling support valid if EXT4_FEATURE_COMPAT_HAS_JOURNAL set.
    #
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
    SimpleMember('s_mkfs_time', '<I', formatter=utcfromtimestamp),              # When the filesystem was created, in seconds since the epoch.
    ArrayMember('s_jnl_blocks', SimpleMember('_', '<I'), 17), # Backup copy of the journal inode's i_block[] array in the first 15 elements and i_size_high and i_size in the 16th and 17th elements, respectively.
    #
    # 64bit support valid if EXT4_FEATURE_COMPAT_64BIT
    #
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
    SimpleMember('s_first_error_time', '<I', formatter=utcfromtimestamp),       # First time an error happened, in seconds since the epoch.
    SimpleMember('s_first_error_ino', '<I'),        # inode involved in first error.
    SimpleMember('s_first_error_block', '<Q'),      # Number of block involved of first error.
    ByteArrayMember('s_first_error_func', 32),      # Name of function where the error happened.
    SimpleMember('s_first_error_line', '<I'),       # Line number where error happened.
    SimpleMember('s_last_error_time', '<I', formatter=utcfromtimestamp),        # Time of most recent error, in seconds since the epoch.
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
## @brief      Class for extent 4 super block.
##
class Ext4SuperBlock(object):
    ##
    ## ext4 SuperBlock signature
    ##
    SIGN = b'\x53\xef'
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
    @trace()
    def is_valid(self):
        return (self._sb.s_magic == self.SIGN)
    # -------------------------------------------------------------------------
    #  IMPROVED GETTERS
    # -------------------------------------------------------------------------
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_blocks_count')
    def blocks_count(self):
        return lohi2int(self._sb.s_blocks_count_lo,
                        self._sb.s_blocks_count_hi)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_r_blocks_count')
    def r_blocks_count(self):
        return lohi2int(self._sb.s_r_blocks_count_lo,
                        self._sb.s_r_blocks_count_hi)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_free_blocks_count')
    def free_blocks_count(self):
        return lohi2int(self._sb.s_free_blocks_count_lo,
                        self._sb.s_free_blocks_count_hi)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_mtime')
    def mtime(self):
        return utcfromtimestamp(self._sb.s_mtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_wtime')
    def wtime(self):
        return utcfromtimestamp(self._sb.s_wtime)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_state')
    def state(self):
        return int2enum(self._sb.s_state, Ext4State,
                        "unexpected value for ext4 revision level.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_errors')
    def errors(self):
        return int2enum(self._sb.s_errors, Ext4Error,
                        "unexpected value for ext4 errors.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_lastcheck')
    def lastcheck(self):
        return utcfromtimestamp(self._sb.s_lastcheck)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_creator_os')
    def creator_os(self):
        return int2enum(self._sb.s_creator_os, Ext4OS,
                        "unexpected value for ext4 creator OS.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_rev_level')
    def rev_level(self):
        return int2enum(self._sb.s_rev_level, Ext4Rev,
                        "unexpected value for ext4 revision level.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def feature_compat(self):
        return int2enum(self._sb.s_feature_compat, Ext4Compat,
                        "unexpected value for ext4 feature compat flag.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def feature_incompat(self):
        return int2enum(self._sb.s_feature_incompat, Ext4Incompat,
                        "unexpected value for ext4 feature incompat flag.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def feature_ro_compat(self):
        return int2enum(self._sb.s_feature_ro_compat, Ext4ReadOnlyCompat,
                        "unexpected value for ext4 feature ro incompat flag.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def uuid(self):
        return uuid_from_bytes(self._sb.s_uuid, le=True)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def def_hash_version(self):
        return int2enum(self._sb.s_def_hash_version, Ext4HashAlgo,
                        "unexpected value for ext4 default hash version.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def default_mount_opts(self):
        return int2enum(self._sb.s_default_mount_opts, Ext4MountOpts,
                        "unexpected value for ext4 default mount options.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def mkfs_time(self):
        return utcfromtimestamp(self._sb.s_mkfs_time)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def flags(self):
        return int2enum(self._sb.s_flags, Ext4MiscFlag,
                        "unexpected value for ext4 misc flags.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def first_error_time(self):
        return utcfromtimestamp(self._sb.s_first_error_time)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def last_error_time(self):
        return utcfromtimestamp(self._sb.s_last_error_time)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def encrypt_algos(self):
        algos = []
        for algo in self._sb.s_encrypt_algos:
            algo = int2enum(algo, Ext4EncryptAlgo,
                            "unexpected value for ext4 encryption algorithm.")
            algos.append(algo)
        return algos
