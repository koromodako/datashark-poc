# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: member.py
#     date: 2017-12-19
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 koromodako
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
# =============================================================================
#  IMPORTS
# =============================================================================
import re
from utils.logging import get_logger
from utils.wrapper import lazy_getter
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Abstract class inherited by all structure specification members
##
class Member(object):
    ##
    ##  @brief Regular expression to verify type string
    ##
    RE_TYPE = re.compile(r'([a-zA-Z_]\w*)')
    ##
    ##  @brief Regular expression to verify format string
    ##
    RE_FMT = re.compile(r'([@=<>!]?[0-9xcbB?hHiIlLqQnNfdspP]+)')
    ##
    ## @brief      Constructor
    ##
    ## @param  name
    ## @param  load
    ## @param  valid
    ##
    def __init__(self, name, load=True, valid=False):
        super(Member, self).__init__()
        self.name = name
        self.load = load
        self.valid = valid
        if not valid:
            self.valid = (self._validate() and self.__validate())
    ##
    ## @brief      Checks member's validity
    ##
    ## @return     True if member is valid else False
    ##
    def __validate(self):
        if not isinstance(self.name, str):
            LGR.error("Member's name must be a string.")
            return False

        if self.RE_TYPE.match(self.name) is None:
            LGR.error("Member's name must validate this regexp: "
                      "{} <{}>".format(self.RE_TYPE.pattern, self.name))
            return False

        if not isinstance(self.load, bool):
            LGR.error("Member's load property must be a boolean value: "
                      "{} <{}>".format(self.name, self.load))
            return False

        return True
    ##
    ## @brief      Member's size
    ##
    ## @return     Size of member in bytes of raw data
    ##
    @lazy_getter('__size')
    def size(self):
        return self._size()
    ##
    ## @brief      Creates a member value from raw bytes
    ##
    ## @param      data  Raw data (bytes or bytearray)
    ##
    ## @return     Value according to member type
    ##
    def read(self, data):
        if not self.load:
            return None

        return self._read(data)
    ##
    ## @brief      Virtual method to be implemented by subclasses. Must return
    ##             a boolean value indicating if subclass instance is valid or
    ##             not.
    ##
    def _validate(self):
        raise NotImplementedError
    ##
    ## @brief      Virtual method to be implemented by subclasses. Must return
    ##             the size of raw bytes needed to build a value
    ##
    def _size(self):
        raise NotImplementedError
    ##
    ## @brief      Virtual method to be implemented by subclasses. Must return
    ##             the value according to the member subclass type.
    ##
    def _read(self, data):
        raise NotImplementedError
