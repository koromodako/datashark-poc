# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: converting.py
#    date: 2017-11-19
#  author: paul.dautry
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 paul.dautry
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
# no import for now
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
# no global or config. for now
# =============================================================================
# FUNCTIONS
# =============================================================================


def str_to_int(s):
    # -------------------------------------------------------------------------
    # str_to_int
    # -------------------------------------------------------------------------
    if s.startswith('0x'):
        return int(s, 16)
    elif s.startswith('0o'):
        return int(s, 8)
    elif s.startswith('0b'):
        return int(s, 2)
    # fallback on base 10
    return int(s)