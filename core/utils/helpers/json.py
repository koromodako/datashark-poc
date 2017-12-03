# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: json.py
#    date: 2017-11-18
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
import json
# =============================================================================
# GLOBAL
# =============================================================================
SEPARATORS = (',', ':')
# =============================================================================
# FUNCTIONS
# =============================================================================


def json_load(fp):
    # -------------------------------------------------------------------------
    # json_load
    # -------------------------------------------------------------------------
    return json.load(fp)


def json_loads(s):
    # -------------------------------------------------------------------------
    # json_loads
    # -------------------------------------------------------------------------
    return json.loads(s)


def json_dump(obj, fp):
    # -------------------------------------------------------------------------
    # json_dump
    # -------------------------------------------------------------------------
    json.dump(obj, fp, separators=SEPARATORS)


def json_dumps(obj):
    # -------------------------------------------------------------------------
    # json_dump
    # -------------------------------------------------------------------------
    return json.dumps(obj, separators=SEPARATORS)
