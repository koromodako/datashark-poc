# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vdi_disk.py
#     date: 2017-12-29
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
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
from struct import calcsize
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.constants import SECTOR_SZ
from utils.converting import unpack_one
from utils.memory_map import MemoryMap
from utils.struct.array_member import ArrayMember
from utils.struct.struct_member import StructMember
from utils.struct.struct_specif import StructSpecif
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
from dissection.helpers.mbr.mbr_partition_entry import S_MBR_PART_ENTRY
from dissection.helpers.mbr.mbr_partition_entry import MBRPartitionEntry
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_GENERIC_MBR = 'GenericMBR'
StructFactory.st_register(StructSpecif(S_GENERIC_MBR, [
    ByteArrayMember('bootcode', 446),
    ArrayMember('primary_part_tab', StructMember('_', S_MBR_PART_ENTRY), 4),
    ByteArrayMember('signature', 2)
]))
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for mbr.
##
class MBR(object):
    ##
    ## { item_description }
    ##
    MBR_SIGN = b'\x55\xaa'
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf    { parameter_description }
    ##
    def __init__(self, bf):
        super(MBR, self).__init__()
        self.bf = bf
        self.mbr = StructFactory.st_from_file(S_GENERIC_MBR, bf)
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self.mbr.signature == self.MBR_SIGN
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_parts')
    def partitions(self):
        parts = []

        for st_part in self.mbr.primary_part_tab:
            if st_part.type != 0:
                parts.append(MBRPartitionEntry(self.bf, st_part))

        return sorted(parts, key=lambda x: x.start)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_unallocated')
    def unallocated(self):
        unallocated = []
        total_sz = self.bf.size() // SECTOR_SZ
        current_idx = 1 # first sector contains MBR

        for part in self.partitions():

            if part.start > current_idx:
                unalloc_sz = part.start - current_idx
                mm = MemoryMap(self.bf, current_idx, unalloc_sz, SECTOR_SZ)
                unallocated.append(mm)
                current_idx += unalloc_sz

            current_idx += part.size

        return unallocated
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def drive_mapping(self):
        mapping = self.partitions() + self.unallocated()
        return sorted(mapping, key=lambda x: x.start)
