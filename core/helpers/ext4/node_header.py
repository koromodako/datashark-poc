# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: tree_node_header.py
#     date: 2018-02-01
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 koromodako
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
from utils.struct.factory import StructFactory
from utils.struct.wrapper import StructWrapper
from helpers.ext4.constants import Ext4NodeType
from utils.struct.simple_member import SimpleMember
from utils.struct.byte_array_member import ByteArrayMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_TREE_HEADER = 'ext4_extent_header'
StructFactory.st_register(S_TREE_HEADER, [
    # Magic number, 0xF30A.
    ByteArrayMember('eh_magic', 2),
    # Number of valid entries following the header.
    SimpleMember('eh_entries', '<H'),
    # Maximum number of entries that could follow the header.
    SimpleMember('eh_max', '<H'),
    # Depth of this extent node in the extent tree. 0 = this extent node points
    # to data blocks; otherwise, this extent node points to other extent nodes.
    # The extent tree can be at most 5 levels deep: a logical block number can
    # be at most 2^32, and the smallest n that satisfies
    # 4*(((blocksize - 12)/12)^n) >= 2^32 is 5.
    SimpleMember('eh_depth', '<H'),
    # Generation of the tree. (Used by Lustre, but not standard ext4).
    SimpleMember('eh_generation', '<I')
])
S_TREE_TAIL = 'ext4_extent_tail'
StructFactory.st_register(S_TREE_TAIL, [
    # Checksum of the extent block, crc32c(uuid+inum+igeneration+extentblock)
    SimpleMember('eb_checksum', '<I')
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 tree node.
##
class Ext4NodeHeader(StructWrapper):
    ##
    ## { item_description }
    ##
    SIGN = b'\x0a\xf3'
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf    { parameter_description }
    ## @param      oft   The oft
    ##
    def __init__(self, bytes, oft=0):
        super(Ext4NodeHeader, self).__init__(S_TREE_HEADER,
                                             bytes=bytes, oft=oft)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_valid')
    def is_valid(self):
        return self._s.eh_magic == self.SIGN
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_type')
    def type(self):
        if self._s.eh_depth > 0:
            return Ext4NodeType.INDEX
        return Ext4NodeType.LEAF
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def entries(self):
        return self._s.eh_entries
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def max_entries(self):
        return self._s.eh_max
