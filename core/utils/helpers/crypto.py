#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
import os
import hashlib
#===============================================================================
# GLOBALS
#===============================================================================
RD_BLK_SZ = 8192
#===============================================================================
# FUNCTIONS
#===============================================================================
def randbuf(sz):
    return os.urandom(sz)
#-------------------------------------------------------------------------------
# randstr
#-------------------------------------------------------------------------------
def randstr(sz):
    return randbuf(sz).hex()
#-------------------------------------------------------------------------------
# hashfile
#-------------------------------------------------------------------------------
def hashfile(hash_func, path):
    if os.path.isfile(path):
        h = hashlib.new(hash_func)
        sz = os.stat(path).st_size
        with open(path, 'rb') as f:
            while sz > 0:
                h.update(f.read(RD_BLK_SZ))
                sz -= RD_BLK_SZ
        return h.digest()
    return None
#-------------------------------------------------------------------------------
# hashbuf
#-------------------------------------------------------------------------------
def hashbuf(hash_func, buf):
    h = hashlib.new(hash_func)
    h.update(buf)
    return h.digest()