# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: struct_member.py
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
from utils.logging import get_logger
from utils.struct.member import Member
from utils.struct.factory import StructFactory
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
class StructMember(Member):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      name     The name
    ## @param      st_type  The st type
    ## @param      load     The load
    ## @param      valid    The valid
    ##
    def __init__(self, name, st_type, load=True, valid=False):
        self.st_type = st_type
        super(StructMember, self).__init__(name, load, valid)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _validate(self):
        if not StructFactory.st_exists(self.st_type):
            LGR.error("StructMember's struct_name must refer to an existant "
                      "structure registered in the StructFactory.")
            return False

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _size(self):
        return StructFactory.st_size(self.st_type)
    ##
    ## @brief      { function_description }
    ##
    ## @param      data  The data
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _read(self, data):

        return StructFactory.st_from_bytes(self.st_type, data)
