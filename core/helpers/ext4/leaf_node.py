# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: leaf_node.py
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
S_TREE_LEAF = 'ext4_extent_leaf'
StructFactory.st_register(S_TREE_LEAF, [
    # First file block number that this extent covers.
    SimpleMember('ee_block', '<I'), # unit: FS block
    # Number of blocks covered by extent. If the value of this field
    # is <= 32768, the extent is initialized. If the value of the field
    # is > 32768, the extent is uninitialized and the actual extent length
    # is ee_len - 32768. Therefore, the maximum length of a initialized extent
    # is 32768 blocks, and the maximum length of an uninitialized extent
    # is 32767.
    SimpleMember('ee_len', '<H'), # unit: FS block
    # Upper 16-bits of the block number to which this extent points.
    SimpleMember('ee_start_hi', '<H'), # unit: FS block
    # Lower 32-bits of the block number to which this extent points.
    SimpleMember('ee_start_lo', '<I') # unit: FS block
])
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 leaf node.
##
class Ext4LeafNode(StructWrapper):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      bytes  The bytes
    ## @param      oft    The oft
    ##
    def __init__(self, bytes, oft, depth):
        super(Ext4LeafNode, self).__init__(S_TREE_LEAF, bytes=bytes, oft=oft)
        self.depth = depth
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_initialized')
    def initialized(self):
        return (self._s.ee_len <= 32768)  # 2**(16-1)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def first_block_idx(self):
        return self._s.ee_block
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_block_count')
    def block_count(self):
        if self.initialized():
            return self._s.ee_len
        return self._s.ee_len - 32768
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    @lazy_getter('_start_idx')
    def start_idx(self):
        return lohi2int(self._s.ee_start_lo, self._s.ee_start_hi)
    ##
    ## @brief      { function_description }
    ##
    ## @param      file_block_index  The file block index
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def block_idx(self, file_block_index):
        # prune search tree first
        fst_blk_idx = self.first_block_idx()
        lst_blk_idx = fst_blk_idx + self.block_count() - 1
        if (file_block_index < fst_blk_idx or file_block_index > lst_blk_idx):
            return None

        return self.start_idx() + file_block_index - fst_blk_idx
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        indent = self.depth * TAB
        return self.st_to_str().replace('\n', '\n{}'.format(indent))

