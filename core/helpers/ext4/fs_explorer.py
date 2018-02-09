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
# -------------------------------------------------------------------------
#  SPECIFIC INODES
# -------------------------------------------------------------------------
#   0  Doesn't exist; there is no inode 0.
#   1   List of defective blocks.
#   2   Root directory.
#   3   User quota.
#   4   Group quota.
#   5   Boot loader.
#   6   Undelete directory.
#   7   Reserved group descriptors inode. ("resize inode")
#   8   Journal inode.
#   9   The "exclude" inode, for snapshots(?)
#   10  Replica inode, used for some non-upstream feature?
#   11  Traditional first non-reserved inode. Usually this is the lost+found
#       directory. See s_first_ino in the superblock.
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
from helpers.ext4.inode_reader import Ext4InodeReader
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
ROOT = '/'
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
    ## @brief      Returns a generator which yields root entries
    ##
    def _root_entries_generator(self):
        inode_reader = Ext4InodeReader(self._fs, self._bf, self._fs.inode(2))
        return Ext4Directory.parse_entries(self._fs, inode_reader, {})
    ##
    ## @brief      { function_description }
    ##
    ## @param      parent  The parent
    ## @param      name    The name
    ##
    def _find_dirent(self, parent_dirent, name):
        if parent_dirent is None:
            entries_generator = self._root_entries_generator()
        else:
            d = Ext4Directory(self._fs, self._bf, parent_dirent)
            entries_generator = d.entries()

        for dirent in entries_generator:
            if dirent.isdir():
                dirent_name = dirent.name(string=True)
                if fnmatch(dirent_name, name):
                    return dirent

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

        dirent = None
        parts = p.parts
        while len(parts) > 0:
            part = parts[0]

            dirent = self._find_dirent(dirent, part)
            if dirent is None:
                LGR.warn("file not found: {}".format(path))
                return None

            parts = parts[1:]

        return Ext4Directory(self._fs, self._bf, dirent)
    ##
    ## @brief      { function_description }
    ##
    ## @param      self               The object
    ## @param      entries_generator  The entries generator
    ##
    def _sort_entries(self, entries_generator):
        dirs, nondirs = [], []

        for entry in entries_generator:
            if entry.isdir():
                dirs.append(entry)
            else:
                nondirs.append(entry)

        return (dirs, nondirs)
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

        dirs, nondirs = self._sort_entries(topd.entries(path, dirent_only))

        if topdown:
            yield str(root), dirs, nondirs

        for cdir in dirs:

            if cdir.islink():
                if not followlinks:
                    continue

                cdir = cdir.resolve()

                if cdir is None:
                    LGR.warn("failed to resolve symlink to directory.")
                    continue

            for x in self._walk(root, cdir, dirent_only, topdown, followlinks):
                yield x

        if not topdown:
            yield str(root), dirs, nondirs
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    def scandir(self, path=ROOT, dirent_only=True):
        if path == ROOT:
            for entry in self._root_entries_generator():
                yield entry
        else:
            topd = self._find_top(path)

            if topd is None:
                return None

            for entry in topd.entries(dirent_only):
                yield entry
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    def walk(self, path=ROOT, dirent_only=True, topdown=True, followlinks=False):
        if path == ROOT:
            dirs, nondirs = self._sort_entries(self._root_entries_generator())
            yield (ROOT, dirs, nondirs)
        else:
            topd = self._find_top(path)

            if topd is None:
                return (None, None, None)

            return self._walk(Path(path), topd, dirent_only, topdown, followlinks)
