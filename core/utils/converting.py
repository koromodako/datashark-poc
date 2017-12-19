# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: converting.py
#    date: 2017-11-19
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
import struct
from utils.logging import get_logger
from utils.wrapper import trace_func
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief   Converts a string to an integer
##
## @param   s   String representing an integer
##
## @return  integer corresponding to given string
##
@trace_func(__name__)
def str_to_int(s):
    if s.startswith('0x'):
        return int(s, 16)

    elif s.startswith('0o'):
        return int(s, 8)

    elif s.startswith('0b'):
        return int(s, 2)

    return int(s, 10)
##
## @brief      Unpacks one value from data
##
## @param      fmt   Format to use for unpacking
## @param      data  Data to unpack
##
## @return     Unpacked value
##
@trace_func(__name__)
def unpack_one(fmt, data):
    return struct.unpack(fmt, data)[0]
