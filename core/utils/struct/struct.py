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
# =============================================================================
# IMPORTS
# =============================================================================
import re
import struct
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_static
from utils.converting import str_to_int
from utils.formatting import hexdump_lines
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for structure.
##
class Struct(object):
    K_ST_TYPE = 'st_type'
    K_ST_SIZE = 'st_size'
    RESERVED = [
        # attributes
        K_ST_TYPE,
        K_ST_SIZE,
        # methods
        'set_member',
        'set_size',
        '__kv_to_str',
        'to_str'
    ]
    ##
    ## @brief      { function_description }
    ##
    ## @param      key    The key
    ## @param      value  The value
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('Struct')
    def __kv_to_str(key, value):
        if isinstance(value, Struct):
            s = value.to_str().replace("\n", "\n\t")

        elif isinstance(value, list):
            s = "\n\t+ {}:".format(key)

            for elem in value:
                s += Struct.__kv_to_str('_', elem).replace("\n", "\n\t")

        else:
            if isinstance(value, bytes) or isinstance(value, bytearray):
                s = "\n\t+ {}:".format(key)
                for line in hexdump_lines(value):
                    s += "\n\t\t{}".format(line)
            else:
                s = "\n\t+ {}: {}".format(key, value)

        return s
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      st_type  The st type
    ## @param      st_size  The st size
    ##
    def __init__(self, st_type, st_size=-1):
        super(Struct, self).__init__()
        setattr(self, Struct.K_ST_TYPE, st_type)
        setattr(self, Struct.K_ST_SIZE, st_size)
    ##
    ## @brief      Sets the member.
    ##
    ## @param      name   The name
    ## @param      value  The value
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def set_member(self, name, value):
        if hasattr(self, name):
            LGR.error('member <{}> already exists.'.format(name))
            return False

        setattr(self, name, value)
        return True
    ##
    ## @brief      Sets the size.
    ##
    ## @param      st_size  The st size
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def set_size(self, st_size):
        setattr(self, Struct.K_ST_SIZE, st_size)
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        members = vars(self)
        st_type = members.pop(Struct.K_ST_TYPE)
        st_size = members.pop(Struct.K_ST_SIZE)
        s = "\n{}(size={}):".format(st_type, st_size)

        for key, value in members.items():
            s += self.__kv_to_str(key, value)

        return s
