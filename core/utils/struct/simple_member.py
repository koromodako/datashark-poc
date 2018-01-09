# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: simple_member.py
#     date: 2017-12-19
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
# =============================================================================
#  IMPORTS
# =============================================================================
from struct import calcsize
from utils.logging import get_logger
from utils.converting import unpack_one
from utils.struct.member import Member
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief
##
class SimpleMember(Member):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      name   The name
    ## @param      fmt    The format
    ## @param      load   The load
    ## @param      valid  The valid
    ##
    def __init__(self, name, fmt, load=True, valid=False, formatter=None):
        self.fmt = fmt
        self.formatter = formatter
        super(SimpleMember, self).__init__(name, load, valid)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _validate(self):
        if not isinstance(self.fmt, str):
            LGR.error("SimpleMember's fmt must be a string.")
            return False

        if Member.RE_FMT.match(self.fmt) is None:
            LGR.error("SimpleMember's fmt must validate this regexp: "
                      "{} <{}>".format(Member.RE_FMT.pattern, self.fmt))
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _size(self):
        return calcsize(self.fmt)
    ##
    ## @brief      { function_description }
    ##
    ## @param      data  The data
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _read(self, data):
        return unpack_one(self.fmt, data)
