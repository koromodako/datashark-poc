# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: crypto.py
#    date: 2017-11-28
#  author: paul.dautry
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 paul.dautry
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import os
import hashlib
from utils.helpers.binary_file import BinaryFile
# =============================================================================
# GLOBALS
# =============================================================================
RD_BLK_SZ = 8192
# =============================================================================
# FUNCTIONS
# =============================================================================


def randbuf(sz):
    # -------------------------------------------------------------------------
    # randbuf
    # -------------------------------------------------------------------------
    return os.urandom(sz)


def randstr(sz):
    # -------------------------------------------------------------------------
    # randstr
    # -------------------------------------------------------------------------
    return randbuf(sz).hex()


def hashfile(hash_func, path):
    # -------------------------------------------------------------------------
    # hashfile
    # -------------------------------------------------------------------------
    if BinaryFile.exists(path):
        h = hashlib.new(hash_func)
        bf = BinaryFile(path, 'r')
        sz = bf.size()
        while sz > 0:
            h.update(bf.read(RD_BLK_SZ))
            sz -= RD_BLK_SZ
        return h.digest()
    return None


def hashbuf(hash_func, buf):
    # -------------------------------------------------------------------------
    # hashbuf
    # -------------------------------------------------------------------------
    h = hashlib.new(hash_func)
    h.update(buf)
    return h.digest()
