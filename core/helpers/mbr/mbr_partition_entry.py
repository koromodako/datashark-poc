# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: mbr_partition_entry.py
#     date: 2018-01-04
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
from utils.constants import SECTOR_SZ
from utils.memory_map import MemoryMap
from utils.struct.factory import StructFactory
from utils.struct.simple_member import SimpleMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_MBR_PART_ENTRY = 'MBRPartitionEntry'
StructFactory.st_register(S_MBR_PART_ENTRY, [
    SimpleMember('status', '<B'),
    SimpleMember('first_chs', '<BH'),   # CHS addr of first sector
    SimpleMember('type', '<B'),
    SimpleMember('last_chs', '<BH'),    # CHS addr of last sector
    SimpleMember('first_lba', '<I'),    # index of first sector (in sectors)
    SimpleMember('size', '<I')          # count of sectors (in sectors)
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for mbr partition entry.
##
class MBRPartitionEntry(MemoryMap):
    ##
    ## { item_description }
    ##
    EXTD_PART_TYPES = {
        0x05: 'CHS',
        0x0F: 'LBA',
        0xC5: 'CHS (secured)',
        0x85: 'CHS (hidden)',
        0x15: 'CHS (hidden)',
        0x1F: 'LBA (hidden)',
        0x91: 'CHS (hidden)',
        0x9B: 'LBA (hidden)',
        0x5E: '(access-restricted)',
        0x5F: '(access-restricted)',
        0xCF: 'LBA (secured)',
        0XD5: 'CHS (secured)'
    }
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, bf, st_part):
        super(MBRPartitionEntry, self).__init__(bf,
                                                st_part.first_lba,
                                                st_part.size,
                                                SECTOR_SZ)
        self.status = st_part.status
        self.type = st_part.type
    ##
    ## @brief      Determines if null.
    ##
    ## @return     True if null, False otherwise.
    ##
    def is_null(self):
        return (self.start == 0 and self.size == 0)
    ##
    ## @brief      Determines if extended.
    ##
    ## @return     True if extended, False otherwise.
    ##
    def is_extended(self):
        return (self.type in list(self.EXTD_PART_TYPES.keys()))
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    def __str__(self):
        return "MBRPartitionEntry(status={},type={},start={},size={})".format(
            self.status, self.type, self.start, self.size)
