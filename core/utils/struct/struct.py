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
from copy import copy
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
    PK_FORMATTERS = '__formatters'
    RESERVED = [
        # attributes
        PK_FORMATTERS,
        K_ST_TYPE,
        K_ST_SIZE,
        # methods
        '__kv_to_str',
        'set_member',
        'set_size',
        'to_str'
    ]
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      st_type  The st type
    ## @param      st_size  The st size
    ##
    def __init__(self, st_type, st_size=-1, formatters={}):
        super(Struct, self).__init__()
        setattr(self, Struct.K_ST_TYPE, st_type)
        setattr(self, Struct.K_ST_SIZE, st_size)
        setattr(self, Struct.PK_FORMATTERS, formatters)
    ##
    ##
    ## @brief      { function_description }
    ##
    ## @param      key    The key
    ## @param      value  The value
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __kv_to_str(self, key, value):
        tab = ' ' * 4
        if isinstance(value, Struct):
            s = value.to_str().replace("\n", "\n{}".format(tab))

        elif isinstance(value, list):
            s = "\n{}+ {}:".format(tab, key)

            k = 0
            for elem in value:
                s += self.__kv_to_str(str(k), elem).replace("\n", "\n{}".format(tab))
                k += 1

        else:
            if isinstance(value, bytes) or isinstance(value, bytearray):
                s = "\n{}+ {}:".format(tab, key)

                for line in hexdump_lines(value):
                    s += "\n{}{}{}".format(tab, tab, line)
            else:
                fmtr = getattr(self, Struct.PK_FORMATTERS, {}).get(key)

                if fmtr is None:
                    s = "\n{}+ {}: {}".format(tab, key, value)
                else:
                    try:
                        formatted = fmtr(value)
                    except Exception as e:
                        LGR.exception("failsafe: call to formatter failed.")
                        formatted = 'invalid'

                    s = "\n{}+ {}: {} ({})".format(tab, key, value, formatted)

        return s
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
        members = copy(vars(self))
        members.pop(Struct.PK_FORMATTERS)
        st_type = members.pop(Struct.K_ST_TYPE)
        st_size = members.pop(Struct.K_ST_SIZE)
        s = "\n{}(size={}):".format(st_type, st_size)

        for key, value in members.items():
            s += self.__kv_to_str(key, value)

        return s
