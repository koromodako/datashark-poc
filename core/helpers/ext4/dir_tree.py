# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: dir_tree.py
#     date: 2018-02-02
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
from pathlib import Path
from fnmatch import fnmatch
from utils.logging import todo
from utils.logging import get_logger
from helpers.ext4.dirent import Ext4Dirent
from helpers.ext4.constants import Ext4DirentVersion
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 dir tree.
##
class Ext4DirTree(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fs    The file system
    ##
    def __init__(self, fs):
        super(Ext4DirTree, self).__init__()
        self._fs = fs
        if self._fs.filetype():
            self._dirent_vers = Ext4DirentVersion.V2
        else:
            self._dirent_vers = Ext4DirentVersion.V1
    ##
    ## @brief      { function_description }
    ##
    ## @param      inode  The inode
    ##
    def _parse_entries(self, inode):
        todo("implement directory parsing...")
    ##
    ## @brief      { function_description }
    ##
    ## @param      parent  The parent
    ## @param      name    The name
    ##
    def _find_inode(self, parent_inode, name):
        if parent_inode is None:
            return self.root_dir_inode()

        for entry in self._parse_entries(parent_inode):
            todo("implement entry selection based on name...")
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    def _find_root(self, path):
        p = Path(path)
        if not p.is_absolute():
            return None

        inode = None
        parts = p.parts
        while len(parts) > 0:
            part = parts[0]
            inode = self._find_inode(inode, part)
            if inode is None:
                return False
            parts = parts[1:]

        return inode

    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def walk(self, path='/'):
        inode = self._find_root(path)
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def scandir(self, path='/'):
        inode = self._find_root(path)
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def listdir(self, path='/'):
        inode = self._find_root(path)
    # -------------------------------------------------------------------------
    #  SPECIFIC INODES
    # -------------------------------------------------------------------------
    #   0  Doesn't exist; there is no inode 0.
    #   1   List of defective blocks.
    def defective_blocks_inode(self):
        return self._fs.inode(1)
    #   2   Root directory.
    def root_dir_inode(self):
        return self._fs.inode(2)
    #   3   User quota.
    def user_quota_inode(self):
        return self._fs.inode(3)
    #   4   Group quota.
    def group_quota_inode(self):
        return self._fs.inode(4)
    #   5   Boot loader.
    def boot_loader_inode(self):
        return self._fs.inodes(5)
    #   6   Undelete directory.
    def undelete_dir_inode(self):
        return self._fs.inode(6)
    #   7   Reserved group descriptors inode. ("resize inode")
    def reserved_group_desc_inode(self):
        return self._fs.inode(7)
    #   8   Journal inode.
    def journal_inode(self):
        return self._fs.inode(8)
    #   9   The "exclude" inode, for snapshots(?)
    def exclude_inode(self):
        return self._fs.inode(9)
    #   10  Replica inode, used for some non-upstream feature?
    def replica_inode(self):
        return self._fs.inode(10)
    #   11  Traditional first non-reserved inode. Usually this is the lost+found directory. See s_first_ino in the superblock.
    def lost_found_inode(self):
        return self._fs.inode(11)
