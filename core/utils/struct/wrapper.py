# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: wrapper.py
#     date: 2018-02-02
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 koromodako
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
from utils.struct.factory import StructFactory
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for structure wrapper.
##
class StructWrapper(object):

    def __init__(self, st_type, bytes=None, bf=None, oft=0):
        if bf is not None:
            self._s = StructFactory.st_from_file(st_type, bf, oft)
        elif bytes is not None:
            self._s = StructFactory.st_from_bytes(st_type, bytes, oft)
        else:
            LGR.error("bytes or bf must be specified.")
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def st_type(self):
        return self._s.st_type
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def st_size(self):
        return self._s.st_size
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def st_to_str(self):
        return self._s.to_str()
