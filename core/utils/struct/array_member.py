# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: array_member.py
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
from utils.logging import get_logger
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
class ArrayMember(Member):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      name    The name
    ## @param      member  The member
    ## @param      length  The length
    ## @param      load    The load
    ## @param      valid   The valid
    ##
    def __init__(self, name, member, length, load=True, valid=False):
        self.member = member
        self.length = int(length)
        super(ArrayMember, self).__init__(name, load, valid)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _validate(self):
        if not isinstance(self.member, Member):
            LGR.error("ArrayMember's member must a subclass of Member.")
            return False

        if not self.member.valid:
            LGR.error("ArrayMember's member is invalid.")
            return False

        if self.length <= 0:
            LGR.error("ArrayMember's length must be in [1,+inf[.")
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _size(self):
        return self.member.size() * self.length
    ##
    ## @brief      { function_description }
    ##
    ## @param      data  The data
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _read(self, data):

        array = []
        msz = self.member.size()

        for i in range(self.length):
            array.append(self.member.read(data[i*msz:(i+1)*msz]))

        return array
