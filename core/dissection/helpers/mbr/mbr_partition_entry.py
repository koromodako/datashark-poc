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
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_specif import StructSpecif
from utils.struct.struct_factory import StructFactory
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_MBR_PART_ENTRY = 'MBRPartitionEntry'
StructFactory.st_register(StructSpecif(S_MBR_PART_ENTRY, [
    SimpleMember('status', '<B'),
    SimpleMember('first_chs', '<BH'),   # CHS addr of first sector
    SimpleMember('type', '<B'),
    SimpleMember('last_chs', '<BH'),    # CHS addr of last sector
    SimpleMember('first_lba', '<I'),    # index of first sector (in sectors)
    SimpleMember('size', '<I')          # count of sectors (in sectors)
]))
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for mbr partition entry.
##
class MBRPartitionEntry(object):
    SECTOR_SZ = 512
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self, bf, st_part):
        self.bf = bf
        self.st_part = st_part

    def block_count(self):
        pass

    def read_block(self, n):
        pass
