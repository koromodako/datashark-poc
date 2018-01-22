# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: tree.py
#     date: 2018-01-15
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
from utils.logging import todo
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.converting import lohi2int
from utils.struct.simple_member import SimpleMember
from utils.struct.struct_factory import StructFactory
from utils.struct.byte_array_member import ByteArrayMember
from helpers.ext4.constants import Ext4TreeNodeType
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
S_TREE_IDX = 'ext4_extent_idx'
StructFactory.st_register(S_TREE_IDX, [
    # This index node covers file blocks from 'block' onward.
    SimpleMember('ei_block', '<I'),
    # Lower 32-bits of the block number of the extent node that is the next
    # level lower in the tree. The tree node pointed to can be either
    # another internal node or a leaf node, described below.
    SimpleMember('ei_leaf_lo', '<I'),
    # Upper 16-bits of the previous field.
    SimpleMember('ei_leaf_hi', '<H'),
    SimpleMember('ei_unused', '<H', load=False)
])
S_TREE_LEAF = 'ext4_extent_leaf'
StructFactory.st_register(S_TREE_LEAF, [
    # First file block number that this extent covers.
    SimpleMember('ee_block', '<I'),
    # Number of blocks covered by extent. If the value of this field
    # is <= 32768, the extent is initialized. If the value of the field
    # is > 32768, the extent is uninitialized and the actual extent length
    # is ee_len - 32768. Therefore, the maximum length of a initialized extent
    # is 32768 blocks, and the maximum length of an uninitialized extent
    # is 32767.
    SimpleMember('ee_len', '<H'),
    # Upper 16-bits of the block number to which this extent points.
    SimpleMember('ee_start_hi', '<H'),
    # Lower 32-bits of the block number to which this extent points.
    SimpleMember('ee_start_lo', '<I')
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
class Ext4TreeNode(object):
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
        super(Ext4TreeNode, self).__init__()
        self._hdr = StructFactory.st_from_bytes(S_TREE_HEADER, bytes, oft)
        self.type = None

        body = []
        if self._hdr.eh_magic == self.SIGN:
            oft += self._hdr.st_size

            if self._hdr.eh_depth > 0:
                self.type = Ext4TreeNodeType.INDEX
            elif self._hdr.eh_depth == 0:
                self.type = Ext4TreeNodeType.LEAF

            for i in range(0, self._hdr.eh_entries):
                if self.type == Ext4TreeNodeType.INDEX:
                    e = StructFactory.st_from_bytes(S_TREE_IDX, bytes, oft)
                else:
                    e = StructFactory.st_from_bytes(S_TREE_LEAF, bytes, oft)

                body.append(e)
                oft += e.st_size

        self._body = body
        self.children = []
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    def to_str(self):
        hdr_str = self._hdr.to_str(indent=2)
        body_str = "".join([ n.to_str(indent=2) for n in self._body ])
        return """
extent_tree_node:
    + type: {}
    + header: {}
    + body: [{}
    ]
""".format(self.type, hdr_str, body_str)
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return (self._hdr.eh_magic == self.SIGN and self._body is not None)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def leaf(self):
        if self.type == Ext4TreeNodeType.INDEX:
            return lohi2int(self._body.ei_leaf_lo, self._body.ei_leaf_hi)
        raise ValueError("cannot call leaf() method on a non-INDEX extent "
                         "node.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def start(self):
        if self.type == Ext4TreeNodeType.LEAF:
            return lohi2int(self._body.ee_start_lo, self._body.ee_start_hi)
        raise ValueError("cannot call start() method on a non-INDEX extent "
                         "node.")
##
## @brief      Class for extent 4 tree.
##
class Ext4Tree(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bf     { parameter_description }
    ## @param      bytes  The bytes
    ##
    def __init__(self, bf, bytes):
        super(Ext4Tree, self).__init__()
        self._bf = bf
        self._root = Ext4TreeNode(bytes)
        self._parse(self._root)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _parse(self, node):
        children = []

        if node.type == Ext4TreeNodeType.INDEX:
            todo(LGR, "implement extent tree index parsing...")

        node.children = children
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return self._root.is_valid()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def blocks(self):
        todo(LGR, "implement all block retrieval (/!\ as a generator /!\)...")
    ##
    ## @brief      { function_description }
    ##
    ## @param      n     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def block(self, n):
        todo(LGR, "implement single block retrieval...")
    ##
    ## @brief      { function_description }
    ##
    ## @param      n     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def read(self, n=-1, oft=0):
        todo(LGR, "implement read() ...")
