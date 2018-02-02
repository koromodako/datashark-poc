# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: index_node.py
#     date: 2018-02-01
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
from utils.constants import TAB
from utils.converting import lohi2int
from utils.struct.factory import StructFactory
from utils.struct.wrapper import StructWrapper
from utils.struct.simple_member import SimpleMember
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_TREE_IDX = 'ext4_extent_idx'
StructFactory.st_register(S_TREE_IDX, [
    # This index node covers file blocks from 'block' onward.
    SimpleMember('ei_block', '<I'), # unit: FS block
    # Lower 32-bits of the block number of the extent node that is the next
    # level lower in the tree. The tree node pointed to can be either
    # another internal node or a leaf node, described below.
    SimpleMember('ei_leaf_lo', '<I'), # unit: FS block
    # Upper 16-bits of the previous field.
    SimpleMember('ei_leaf_hi', '<H'), # unit: FS block
    SimpleMember('ei_unused', '<H', load=False)
])
# =============================================================================
#  CLASSES
# =============================================================================

class Ext4IndexNode(StructWrapper):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bytes  The bytes
    ## @param      oft    The oft
    ##
    def __init__(self, bytes, oft, depth):
        super(Ext4IndexNode, self).__init__(S_TREE_IDX, bytes=bytes, oft=oft)
        self.depth = depth
        self.children = []

    def set_children(self, children):
        if not isinstance(children, list):
            LGR.critical("programatical error: children must be a list.")
            return False

        self.children = children
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def first_block_idx(self):
        return self._s.ei_block
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @lazy_getter('_leaf_block')
    def leaf_block_idx(self):
        return lohi2int(self._s.ei_leaf_lo, self._s.ei_leaf_hi)
    ##
    ## @brief      { function_description }
    ##
    ## @param      blk_idx  The file block index
    ##
    ## @return     { description_of_the_return_value }
    ##
    def block_idx(self, blk_idx):
        # prune search tree first
        if blk_idx < self.first_block_idx():
            return None

        # search within children list
        for child in self.children:
            idx = child.block(blk_idx)

            if idx is None:
                continue

            return idx

        # file index not found within children list
        return None
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        indent = self.depth * TAB
        for child in self.children:
            print(child.st_to_str().replace('\n', '\n{}'.format(indent)))
