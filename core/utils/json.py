# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: json.py
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
import json
# =============================================================================
# GLOBAL
# =============================================================================
SEPARATORS = (',', ':')
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      { function_description }
##
## @param      fp    { parameter_description }
##
## @return     { description_of_the_return_value }
##
def json_load(fp):
    return json.load(fp)
##
## @brief      { function_description }
##
## @param      s     { parameter_description }
##
## @return     { description_of_the_return_value }
##
def json_loads(s):
    return json.loads(s)
##
## @brief      { function_description }
##
## @param      fp    { parameter_description }
##
## @return     { description_of_the_return_value }
##
def json_dump(obj, fp):
    json.dump(obj, fp, separators=SEPARATORS)
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
def json_dumps(obj, indent=None):
    return json.dumps(obj, separators=SEPARATORS, indent=indent)
