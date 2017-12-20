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
from Crypto.Hash import HMAC
from Crypto.Hash import MD2
from Crypto.Hash import MD4
from Crypto.Hash import MD5
from Crypto.Hash import RIPEMD
from Crypto.Hash import SHA
from Crypto.Hash import SHA224
from Crypto.Hash import SHA256
from Crypto.Hash import SHA384
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from utils.logging import get_logger
from utils.binary_file import BinaryFile
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
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
def __new_hash(hash_func, key=None, digestmod=None):
    if hash_func is None:
        return None

    hash_func = hash_func.lower()

    if hash_func == 'hmac':
        if key is None:
            LGR.error("key must be specified for hmac")
            return None
        return HMAC.new(key, digestmod=__new_hash(digestmod))
    elif hash_func == 'md2':
        return MD2.new()
    elif hash_func == 'md4':
        return MD4.new()
    elif hash_func == 'md5':
        return MD5.new()
    elif hash_func == 'ripemd':
        return RIPEMD.new()
    elif hash_func == 'sha':
        return SHA.new()
    elif hash_func == 'sha224':
        return SHA224.new()
    elif hash_func == 'sha256':
        return SHA256.new()
    elif hash_func == 'sha384':
        return SHA384.new()
    elif hash_func == 'sha512':
        return SHA512.new()

    LGR.warn("unknown hash_func value: <{}>".format(hash_func))
    return None
##
## @brief      { function_description }
##
## @param      sz    The size
##
## @return     { description_of_the_return_value }
##
def randbuf(sz):
    return get_random_bytes(sz)
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
def hashfile(hash_func, path, key=None, digestmod=None):
    if not BinaryFile.exists(path):
        LGR.error("file must exists to be hashed.")
        return None

    h = __new_hash(hash_func, key, digestmod)
    if h is None:
        LGR.error("invalid hash object returned.")
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
def hashbuf(hash_func, buf, key=None, digestmod=None):
    h = __new_hash(hash_func)
    if h is None:
        LGR.error("invalid hash object returned.")
        return None

    h.update(buf)
    return h.digest()
