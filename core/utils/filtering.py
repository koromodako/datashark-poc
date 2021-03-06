# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: filtering.py
#    date: 2017-11-18
#  author: koromodako
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 koromodako
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
from fnmatch import fnmatch
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for fs entry filter.
##
class FSEntryFilter(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      include  The include
    ## @param      exclude  The exclude
    ##
    def __init__(self, include=[], exclude=[]):
        self.sep = ','

        if isinstance(include, str):
            if len(include) == 0:
                include = []
            else:
                include = include.split(self.sep)

        if isinstance(exclude, str):
            if len(exclude) == 0:
                exclude = []
            else:
                exclude = exclude.split(self.sep)

        self.include = include
        self.exclude = exclude
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def keep(self, path):
        # check if files matches an inclusion pattern
        for pattern in self.include:
            if fnmatch(path, pattern):
                return True
        # check if files matches an exclusion pattern
        for pattern in self.exclude:
            if fnmatch(path, pattern):
                return False
        # default behavior is if include empty return true for files not
        # matched
        return (len(self.include) == 0)
