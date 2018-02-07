# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: fs_explorer.py
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
from helpers.ext4.symlink import Ext4Symlink
from helpers.ext4.regfile import Ext4RegularFile
from helpers.ext4.directory import Ext4Directory
from helpers.ext4.constants import Ext4FileType
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent 4 fs explorer.
##
class Ext4FSExplorer(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fs    The file system
    ## @param      bf    { parameter_description }
    ##
    def __init__(self, fs, bf):
        super(Ext4FSExplorer, self).__init__()
        self._fs = fs
        self._bf = bf
    ##
    ## @brief      { function_description }
    ##
    ## @param      parent  The parent
    ## @param      name    The name
    ##
    def _find_inode(self, parent_inode, name):
        if parent_inode is None:
            return self.root_dir_inode()

        d = Ext4Directory(self._fs, self._bf, parent_inode)

        for entry in d.entries():
            if dirent.ftype() == Ext4FileType.DIRECTORY:
                dirent_name = dirent.name(string=True)
                if fnmatch(dirent_name, name):
                    return dirent.inode()

        return None
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    def _find_top(self, path):
        p = Path(path)
        if not p.is_absolute():
            LGR.error("path must be absolute!")
            return None

        inode = None
        parts = p.parts
        while len(parts) > 0:
            part = parts[0]

            inode = self._find_inode(inode, part)
            if inode is None:
                LGR.warn("file not found!")
                return None

            parts = parts[1:]

        return inode
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def scandir(self, path='/', dirent_only=True):
        top = self._find_top(path)

        if top is None:
            return None

        for entry in top.entries(dirent_only):
            yield entry
    ##
    ## @brief      { function_description }
    ##
    ## @param      topd         The topd
    ## @param      dirent_only  The dirent only
    ## @param      topdown      The topdown
    ## @param      followlinks  The followlinks
    ##
    def _walk(self, path, topd, dirent_only, topdown, followlinks):
        root = path.joinpath(topd.fname())
        dirs, nondirs = [], []

        for entry in topd.entries(path, dirent_only):
            if entry.ftype() == Ext4FileType.DIRECTORY:
                dirs.append(entry)
            else:
                nondirs.append(entry)

        if topdown:
            yield str(root), dirs, nondirs

        for d in dirs:

            if followlinks and d.is_symlink():
                d = d.resolve()

            for x in self._walk(root, d, dirent_only, topdown, followlinks):
                yield x

        if not topdown:
            yield str(root), dirs, nondirs
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    def walk(self, path='/', dirent_only=True, topdown=True, followlinks=False):

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
