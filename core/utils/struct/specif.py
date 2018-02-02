# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: specif.py
#     date: 2017-12-05
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
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
# =============================================================================
#  IMPORTS
# =============================================================================
import re
from utils.wrapper import trace
from utils.logging import get_logger
from utils.struct.member import Member
from utils.struct.struct import Struct
from utils.struct.simple_member import SimpleMember
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief
##
class StructSpecif(object):
    ##
    ## @brief
    ##
    RE_TYPE = re.compile(r'(\w+)')
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      st_type  The st type
    ## @param      members  The members
    ##
    def __init__(self, st_type, members):
        super(StructSpecif, self).__init__()
        self.st_type = st_type
        self.members = members
        self.formatters = {}
        self.valid = self.__validate()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __validate(self):
        if not isinstance(self.st_type, str):
            LGR.error("StructSpecif's st_type must be a string!")
            return False

        if self.RE_TYPE.match(self.st_type) is None:
            LGR.error("StructSpecif's st_type must validate regexp: "
                      "{}".format(self.RE_TYPE.pattern))
            return False

        if not isinstance(self.members, list) or len(self.members) == 0:
            LGR.error("StructSpecif's members must be a non-empty list!")
            return False

        names = []
        for member in self.members:
            if not isinstance(member, Member):
                LGR.error("at least one member of StructSpecif's members "
                          "is not a subclass of Member.")

            if not member.valid:
                LGR.error("at least one of StructSpecif's members is invalid.")
                return False

            if member.name in Struct.RESERVED:
                LGR.error("<{}> is part of Struct reserved keywords "
                          "<{}>".format(member.name, Struct.RESERVED))
                return False

            names.append(member.name)
            if isinstance(member, SimpleMember):
                if member.formatter is not None:
                    self.formatters[member.name] = member.formatter

        if len(names) != len(set(names)):
            LGR.error("at least two members of StructSpecif share the same "
                      "name.")
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def size(self):
        if not hasattr(self, '__size'):
            self.__size = sum([m.size() for m in self.members])

        return self.__size
