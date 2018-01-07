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
from dissection.helpers.mbr.partition import Partition
from dissection.helpers.mbr.mbr_partition_entry import S_MBR_PART_ENTRY
from dissection.helpers.mbr.mbr_partition_entry import MBRPartitionEntry
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_GENERIC_MBR = 'MBR_o_EBR'
StructFactory.st_register(StructSpecif(S_GENERIC_MBR, [
    ByteArrayMember('bootcode', 446),
    ArrayMember('primary_part_tab', StructMember('_', S_MBR_PART_ENTRY), 4),
    ByteArrayMember('signature', 2)
]))
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for mbr or ebr.
##
class MBR(object):
    ##
    ## { item_description }
    ##
    MBR_SIGN = b'\x55\xaa'
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf    Binary file to read MBR/EBR from
    ## @param      oft   Absolute offset of this MBR/EBR (in bytes)
    ##
    def __init__(self, bf, oft=0, first_ebr=None):
        super(MBR, self).__init__()
        self._bf = bf
        self._mbr = StructFactory.st_from_file(S_GENERIC_MBR, bf, oft)
        self._next = None
        self._lba_oft = oft // SECTOR_SZ
        self._first_ebr = first_ebr
        self._part_entries = []
        self._parse()
    ##
    ## @brief      { item_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def _parse(self):
        for st_part in self._mbr.primary_part_tab:
            if st_part.type != 0:
                self._part_entries.append(MBRPartitionEntry(self._bf, st_part))

        if len(self._part_entries) == 2:
            second_part = self._part_entries[1]

            if second_part.is_extended():
                abs_lba_oft = second_part.start

                if self._first_ebr is None:
                    self._first_ebr = second_part.start
                else:
                    abs_lba_oft += self._first_ebr

                mbr = MBR(self._bf, abs_lba_oft * SECTOR_SZ, self._first_ebr)

                if mbr.is_valid():
                    self._next = mbr
                else:
                    LGR.warn("invalid EBR in linked list.")
                    LGR.warn(mbr.to_str())
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self._mbr.signature == self.MBR_SIGN
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_parts')
    def partitions(self, recursive=True):
        parts = []

        for part in self._part_entries:

            if part.is_extended():
                continue

            start = self._lba_oft + part.start
            parts.append(Partition(self._bf, part.status, part.type, start, part.size))

        if recursive and self._next is not None:
            parts += self._next.partitions()

        return sorted(parts, key=lambda x: x.start)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_allocated')
    def allocated(self):
        allocated = [ MemoryMap(self._bf, self._lba_oft, 1, SECTOR_SZ) ]

        allocated += self.partitions(recursive=False)

        if self._next is not None:
            allocated += self._next.allocated()

        return sorted(allocated, key=lambda x: x.start)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_unallocated')
    def unallocated(self):
        unallocated = []
        sector_cnt = self._bf.size() // SECTOR_SZ
        index = 0

        for mm in self.allocated():

            if index < mm.start:
                size = mm.start - index
                unallocated.append(MemoryMap(self._bf, index, size, SECTOR_SZ))
                index += size

            index += mm.size

        if index < sector_cnt-1:
            unallocated.append(MemoryMap(self._bf, index,
                                         sector_cnt - index, SECTOR_SZ))

        return sorted(unallocated, key=lambda x: x.start)
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        mbr = self
        text = ""
        while mbr is not None:
            text += mbr._mbr.to_str()
            mbr = mbr._next

        return text
