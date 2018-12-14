# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: tree.py
#     date: 2018-01-15
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
from utils.logging import todo
from utils.logging import get_logger
from helpers.ext4.constants import Ext4NodeType
from helpers.ext4.leaf_node import Ext4LeafNode
from helpers.ext4.index_node import Ext4IndexNode
from helpers.ext4.node_header import Ext4NodeHeader
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 tree.
##
class Ext4Tree(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fs     The file system
    ## @param      bf     { parameter_description }
    ## @param      inode  The inode
    ##
    def __init__(self, fs, bf, inode):
        super(Ext4Tree, self).__init__()
        self._bf = bf
        self._inode = inode
        self._fs_blk_sz = fs.block_size()
        (self._valid, self._root) = self._parse(self._inode.block())
    ##
    ## @brief      Parses ext4 extent tree (recursive)
    ##
    def _parse(self, bytes, depth=0):
        entries = []
        hdr = Ext4NodeHeader(bytes)

        if not hdr.is_valid():
            LGR.error("invalid node header.")
            return (False, None)

        oft = hdr.st_size()
        for k in range(hdr.entries()):
            if hdr.type() == Ext4NodeType.INDEX:
                entry = Ext4IndexNode(bytes, oft, depth)

                nbytes = self._bf.read(self._fs_blk_sz,
                                       self._fs_blk_sz * entry.leaf_block_idx())

                (valid, children) = self._parse(nbytes, depth+1)

                if not valid:
                    LGR.error("invalid sub-tree.")
                    return (False, None)

                entry.set_children(children)
            else:
                entry = Ext4LeafNode(bytes, oft, depth)

            entries.append(entry)
            oft += entry.st_size()
        # sort entries based on first block index
        entries = sorted(entries, key=lambda x: x.first_block_idx())

        return (True, entries)
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self._valid
    ##
    ## @brief      Yields partition block indexes where files data is located
    ##
    @trace()
    def file_blocks(self):
        f_blk_cnt = self._inode.size() // self._fs_blk_sz
        for f_blk_idx in range(0, f_blk_cnt):
            yield self.file_block(f_blk_idx)
    ##
    ## @brief      Translates a file block index to a partition block index
    ##
    ## @param      f_blk_idx    Given file block index to be translated
    ##
    @trace()
    def file_block(self, f_blk_idx):
        for entry in self._root:
            blk_idx = entry.block_idx(f_blk_idx)

            if blk_idx is None:
                continue

            return blk_idx

        LGR.warn("block index out-of-bounds => None returned.")
        return None
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    def to_str(self):
        text = ""
        for child in self._root:
            text += child.to_str()
        return text

