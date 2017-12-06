# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: structure.py
#    date: 2017-11-18
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
# Additional information from python documentation:
#
#   | Character | Byte order             | Size     | Alignment |
#   |:---------:|:----------------------:|:--------:|:---------:|
#   | @         | native                 | native   | native    |
#   | =         | native                 | standard | none      |
#   | <         | little-endian          | standard | none      |
#   | >         | big-endian             | standard | none      |
#   | !         | network (= big-endian) | standard | none      |
#
#   | Format | C Type             | Python type       | Standard size |
#   |:------:|:-------------------|:------------------|:-------------:|
#   | x      | pad byte           | no value          |               |
#   | c      | char               | bytes of length 1 | 1             |
#   | b      | signed char        | integer           | 1             |
#   | B      | unsigned char      | integer           | 1             |
#   | ?      | _Bool              | bool              | 1             |
#   | h      | short              | integer           | 2             |
#   | H      | unsigned short     | integer           | 2             |
#   | i      | int                | integer           | 4             |
#   | I      | unsigned int       | integer           | 4             |
#   | l      | long               | integer           | 4             |
#   | L      | unsigned long      | integer           | 4             |
#   | q      | long long          | integer           | 8             |
#   | Q      | unsigned long long | integer           | 8             |
#   | n      | ssize_t            | integer           |               |
#   | N      | size_t             | integer           |               |
#   | f      | float              | float             | 4             |
#   | d      | double             | float             | 8             |
#   | s      | char[]             | bytes             |               |
#   | p      | char[]             | bytes             |               |
#   | P      | void *             | integer           |               |
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import re
import struct
from utils.logging import get_logger
from utils.converting import str_to_int
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
class Struct(object):
    # -------------------------------------------------------------------------
    # Struct class
    # -------------------------------------------------------------------------
    K_ST_TYPE = 'st_type'
    K_ST_SIZE = 'st_size'
    RESERVED = [
        K_ST_TYPE,
        K_ST_SIZE
    ]

    def __init__(self, st_type, st_size=-1):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Struct, self).__init__()
        setattr(self, Struct.K_ST_TYPE, st_type)
        setattr(self, Struct.K_ST_SIZE, st_size)

    def set_member(self, name, value):
        # ---------------------------------------------------------------------
        # set_member
        # ---------------------------------------------------------------------
        if hasattr(self, name):
            return False

        setattr(self, name, value)
        return True

    def set_size(self, st_size):
        # ---------------------------------------------------------------------
        # set_size
        # ---------------------------------------------------------------------
        setattr(self, Struct.K_ST_SIZE, st_size)

    def type(self):
        # ---------------------------------------------------------------------
        # name
        # ---------------------------------------------------------------------
        return getattr(self, Struct.K_ST_TYPE)

    def  size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        return getattr(self, Struct.K_ST_SIZE)

    def to_str(self):
        # ---------------------------------------------------------------------
        # to_str
        # ---------------------------------------------------------------------
        LGR.debug('Struct.to_str()')

        members = vars(self)
        st_type = members.pop(Struct.K_ST_TYPE)
        st_size = members.pop(Struct.K_ST_SIZE)
        s = "\n{}(size={}):".format(st_type, st_size)

        for key, value in members.items():

            if isinstance(value, Struct):
                s += value.to_str().replace("\n", "\n\t")
            else:
                s += "\n\t+ {}: {}".format(key, value)

        return s
