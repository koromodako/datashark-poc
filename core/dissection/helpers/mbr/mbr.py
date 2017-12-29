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
from utils.converting import unpack_one
from utils.struct.array_member import ArrayMember
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_specif import StructSpecif
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_MBR_PART_ENTRY = 'MBRPartitionEntry'
StructFactory.st_register(StructSpecif(S_MBR_PART_ENTRY, [
    SimpleMember('status', '<B'),
    SimpleMember('first_chs', '<BH'),
    SimpleMember('type', '<B'),
    SimpleMember('last_chs', '<BH'),
    SimpleMember('first_lba', '<I'),
    SimpleMember('size', '<I')
]))
S_GENERIC_MBR = 'GenericMBR'
StructFactory.st_register(StructSpecif(S_GENERIC_MBR, [
    ByteArrayMember('bootcode', 446),
    ArrayMember('primary_part_tab', StructMember('_', S_MBR_PART_ENTRY), 4),
    ByteArrayMember('signature', 2)
]))
# =============================================================================
#  CLASSES
# =============================================================================


class MBR(object):
    MBR_SIGN = b'\x55\xaa'
    # -------------------------------------------------------------------------
    # MBR
    # -------------------------------------------------------------------------
    def __init__(self, bf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(MBR, self).__init__()
        self.mbr = StructFactory.st_from_file(S_GENERIC_MBR, self.bf)

    def is_valid(self):
        return self.mbr.signature == self.MBR_SIGN
