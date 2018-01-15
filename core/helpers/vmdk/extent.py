# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: extent.py
#     date: 2017-12-04
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
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for extent.
##
class Extent(object):
    ACCESS_KWDS = [
        'RW',
        'RDONLY',
        'NOACCESS'
    ]
    FLAT_TYPES = [
        'FLAT',
        'VMFS',
        'VMFSRDM',
        'VMFSRAW'
    ]
    TYPE_KWDS = FLAT_TYPES + [
        'SPARSE',
        'ZERO',
        'VMFSSPARSE'
    ]
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      line  The line
    ##
    def __init__(self, line):
        super(Extent, self).__init__()
        self.__valid = self.__parse(line)
    ##
    ## @brief      { function_description }
    ##
    ## @param      line  The line
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __parse(self, line):
        pts = line.split(' ')

        if len(pts) < 4:
            LGR.warn('invalid extent: {}'.format(line))
            return False

        self.access = pts[0]

        if self.access not in Extent.ACCESS_KWDS:
            LGR.warn('invalid extent access: {}'.format(self.access))
            return False

        self.size = int(pts[1])
        self.type = pts[2]

        if self.type not in Extent.TYPE_KWDS:
            LGR.warn('invalid extent type: {}'.format(self.type))
            return False

        self.filename = pts[3][1:-1]
        self.offset = None  # invalid offset

        if len(pts) == 5:
            self.offset = int(pts[4])

        return True
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self.__valid
    ##
    ## @brief      Determines if flat.
    ##
    ## @return     True if flat, False otherwise.
    ##
    @trace()
    def is_flat(self):
        return (self.type in Extent.FLAT_TYPES)
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        offset = '' if self.offset is None else self.offset

        return '{} {} {} {} {}'.format(self.access, self.size, self.type,
                                       self.filename, offset)
