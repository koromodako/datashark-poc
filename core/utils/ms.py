# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: ms.py
#    date: 2017-11-12
#  author: koromodako
# purpose:
#    Microsoft Windows helpers
# license:
#    Utils
#    Copyright (C) 2017  Paul Dautry
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# =============================================================================
import os
from utils.exceptions import MSWindowsSpecificFeatureException
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      { function_description }
##
## @param      no_raise  No raise
##
## @return     { description_of_the_return_value }
##
def assert_ms_windows(no_raise=False):
    if os.name != 'nt':
        if no_raise:
            return False

        raise MSWindowsSpecificFeatureException

    return True
