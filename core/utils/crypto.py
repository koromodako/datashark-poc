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
from Crypto import Hash
from utils.logging import get_logger
from utils.binary_file import BinaryFile
# =============================================================================
# GLOBALS
# =============================================================================
RD_BLK_SZ = 8192
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      { function_description }
##
## @param      hash_func  The hash function
##
## @return     { description_of_the_return_value }
##
def __new_hash(hash_func):
    hash_func = hash_func.lower()

    if hash_func == 'md2':
        return Hash.MD2.new()
    elif hash_func == 'md4':
        return Hash.MD4.new()
    elif hash_func == 'md5':
        return Hash.MD5.new()
    elif hash_func == 'ripemd':
        return Hash.RIPEMD.new()
    elif hash_func == 'sha':
        return Hash.SHA.new()
    elif hash_func == 'sha224':
        return Hash.SHA224.new()
    elif hash_func == 'sha256':
        return Hash.SHA256.new()
    elif hash_func == 'sha384':
        return Hash.SHA384.new()
    elif hash_func == 'sha512':
        return Hash.SHA512.new()

    return None
##
## @brief      { function_description }
##
## @param      sz    The size
##
## @return     { description_of_the_return_value }
##
def randbuf(sz):
    return os.urandom(sz)
##
## @brief      { function_description }
##
## @param      sz    The size
##
## @return     { description_of_the_return_value }
##
def randstr(sz):
    return randbuf(sz).hex()
##
## @brief      { function_description }
##
## @param      hash_func  The hash function
## @param      path       The path
##
## @return     { description_of_the_return_value }
##
def hashfile(hash_func, path):
    if not BinaryFile.exists(path):
        LGR.error("")
        return None

    h = __new_hash(hash_func)
    if h is None:
        LGR.error("")
        return None

    bf = BinaryFile(path, 'r')
    sz = bf.size()

    while sz > 0:
        h.update(bf.read(RD_BLK_SZ))
        sz -= RD_BLK_SZ

    bf.close()
    return h.digest()
##
## @brief      { function_description }
##
## @param      hash_func  The hash function
## @param      buf        The buffer
##
## @return     { description_of_the_return_value }
##
def hashbuf(hash_func, buf):
    h = __new_hash(hash_func)
    if h is None:
        LGR.error("")
        return None

    h.update(buf)
    return h.digest()
