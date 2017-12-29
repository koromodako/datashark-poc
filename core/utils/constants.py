# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: constants.py
#     date: 2017-12-16
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
import sys
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
##
## { item_description }
##
PROG_NAME = 'datashark'
##
## { item_description }
##
VERS_MAJOR = 0
##
## { item_description }
##
VERS_MINOR = 0
##
## { item_description }
##
VERS_FIX = 0
##
## { item_description }
##
VERS_TAG = 'dev'
##
## { item_description }
##
LICENSE = """
Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `-w'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `-c' for details.
"""
##
## { item_description }
##
LICENSE_WARRANTY = """
15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""
##
## { item_description }
##
LICENSE_CONDITIONS = """
See LICENSE file for details.
"""
##
## { item_description }
##
PROG_VERSION = '{}.{}.{}{}'.format(VERS_MAJOR, VERS_MINOR, VERS_FIX, VERS_TAG)
##
## { item_description }
##
PYTHON_VERSION = sys.version_info
# =============================================================================
#  FUNCTIONS
# =============================================================================
def check_python_version(major, minor, micro):

    if PYTHON_VERSION.major < major:
        return False

    if PYTHON_VERSION.major == major:
        if PYTHON_VERSION.minor < minor:
            return False

        elif PYTHON_VERSION.minor == minor:
            if PYTHON_VERSION.micro < micro:
                return False

    return True

