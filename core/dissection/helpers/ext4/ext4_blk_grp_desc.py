# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4_blk_grp_desc.py
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
from enum import Flag
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.converting import lohi2int
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_member import StructMember
from utils.struct.struct_factory import StructFactory
from dissection.helpers.ext4.constants import Ext4BGDFlag
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_EXT4_32B_BGD = 'ext4_32b_blk_grp_desc'
StructFactory.st_register(S_EXT4_BGD, [
    SimpleMember('bg_block_bitmap_lo', '<I'),       # Lower 32-bits of location of block bitmap.
    SimpleMember('bg_inode_bitmap_lo', '<I'),       # Lower 32-bits of location of inode bitmap.
    SimpleMember('bg_inode_table_lo', '<I'),        # Lower 32-bits of location of inode table.
    SimpleMember('bg_free_blocks_count_lo', '<H'),  # Lower 16-bits of free block count.
    SimpleMember('bg_free_inodes_count_lo', '<H'),  # Lower 16-bits of free inode count.
    SimpleMember('bg_used_dirs_count_lo', '<H'),    # Lower 16-bits of directory count.
    SimpleMember('bg_flags', '<H', fmtr=Ext4BGDFlag),   # Block group flags.
    SimpleMember('bg_exclude_bitmap_lo', '<I'),     # Lower 32-bits of location of snapshot exclusion bitmap.
    SimpleMember('bg_block_bitmap_csum_lo', '<H'),  # Lower 16-bits of the block bitmap checksum.
    SimpleMember('bg_inode_bitmap_csum_lo', '<H'),  # Lower 16-bits of the inode bitmap checksum.
    SimpleMember('bg_itable_unused_lo', '<H'),      # Lower 16-bits of unused inode count. If set, we needn't scan past the (sb.s_inodes_per_group - gdt.bg_itable_unused)th entry in the inode table for this group.
    SimpleMember('bg_checksum', '<H'),              # Group descriptor checksum; crc16(sb_uuid+group+desc) if the RO_COMPAT_GDT_CSUM feature is set, or crc32c(sb_uuid+group_desc) & 0xFFFF if the RO_COMPAT_METADATA_CSUM feature is set.
])
S_EXT4_64B_BGD = 'ext4_64b_blk_grp_desc'
StructFactory.st_register(S_EXT4_64B_BGD, [
    StructMember('bg_32b', S_EXT4_32B_BGD),
    # These fields only exist if the 64bit feature is enabled and sb.s_desc_size > 32.
    SimpleMember('bg_block_bitmap_hi', '<I'),       # Upper 32-bits of location of block bitmap.
    SimpleMember('bg_inode_bitmap_hi', '<I'),       # Upper 32-bits of location of inodes bitmap.
    SimpleMember('bg_inode_table_hi', '<I'),        # Upper 32-bits of location of inodes table.
    SimpleMember('bg_free_blocks_count_hi', '<H'),  # Upper 16-bits of free block count.
    SimpleMember('bg_free_inodes_count_hi', '<H'),  # Upper 16-bits of free inode count.
    SimpleMember('bg_used_dirs_count_hi', '<H'),    # Upper 16-bits of directory count.
    SimpleMember('bg_itable_unused_hi', '<H'),      # Upper 16-bits of unused inode count.
    SimpleMember('bg_exclude_bitmap_hi', '<I'),     # Upper 32-bits of location of snapshot exclusion bitmap.
    SimpleMember('bg_block_bitmap_csum_hi', '<H'),  # Upper 16-bits of the block bitmap checksum.
    SimpleMember('bg_inode_bitmap_csum_hi', '<H'),  # Upper 16-bits of the inode bitmap checksum.
    SimpleMember('bg_reserved', '<I', load=False)   # Padding to 64 bytes.
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 block group description.
##
class Ext4BlkGrpDesc(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf    { parameter_description }
    ## @param      oft   The oft
    ##
    def __init__(self, bg_size, bf, oft):
        super(Ext4BlkGrpDesc, self).__init__()
        self.size = bg_size
        if self.size <= 32:
            self._bgd = StructFactory.st_from_file(S_EXT4_32B_BGD, bf, oft)
        else:
            self._bgd = StructFactory.st_from_file(S_EXT4_64B_BGD, bf, oft)
    # -------------------------------------------------------------------------
    #  ENHANCED GETTERS
    # -------------------------------------------------------------------------
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def block_bitmap(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_block_bitmap_lo,
                            self._bgd.bg_block_bitmap_hi)
        return self.bg_block_bitmap_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def inode_bitmap(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_inode_bitmap_lo,
                            self._bgd.bg_inode_bitmap_hi)
        return self.bg_inode_bitmap_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def inode_table(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_inode_table_lo,
                            self._bgd.bg_inode_table_hi)
        return self.bg_inode_table_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def free_blocks_count(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_free_blocks_count_lo,
                            self._bgd.bg_free_blocks_count_hi)
        return self.bg_free_blocks_count_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def free_inodes_count(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_free_inodes_count_lo,
                            self._bgd.bg_free_inodes_count_hi)
        return self.bg_free_inodes_count_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def used_dirs_count(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_used_dirs_count_lo,
                            self._bgd.bg_used_dirs_count_hi)
        return self.bg_used_dirs_count_lo

    def flags(self):
        return Ext4BGDFlag(self._bgd.bg_flags)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def itable_unused(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_itable_unused_lo,
                            self._bgd.bg_itable_unused_hi)
        return self.bg_itable_unused_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def exclude_bitmap(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_exclude_bitmap_lo,
                            self._bgd.bg_exclude_bitmap_hi)
        return self.bg_exclude_bitmap_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def block_bitmap_csum(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_block_bitmap_csum_lo,
                            self._bgd.bg_block_bitmap_csum_hi)
        return self.bg_block_bitmap_csum_lo
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def inode_bitmap_csum(self):
        if self.size > 32:
            return lohi2int(self._bgd.bg_inode_bitmap_csum_lo,
                            self._bgd.bg_inode_bitmap_csum_hi)
        return self.bg_inode_bitmap_csum_lo
