# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: json_adapter.py
#    date: 2017-11-28
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
from utils.json import json_dumps
from utils.logging import todo
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_func
from dissection.workspace import workspace
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
JSON_FILE = None
BEGIN = '{"containers":['
END = ']}'
# =============================================================================
# CLASSES
# =============================================================================


class JsonFile(object):
    # -------------------------------------------------------------------------
    # JsonFile
    # -------------------------------------------------------------------------
    def __init__(self, name):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(JsonFile, self).__init__()
        self.name = name
        self.__sz = 0
        self.__bf = None

    @trace(LGR)
    def open(self):
        # ---------------------------------------------------------------------
        # open
        # ---------------------------------------------------------------------
        self.__sz = 0
        self.__bf = workspace().datfile(self.name, 'json')

    @trace(LGR)
    def close(self):
        # ---------------------------------------------------------------------
        # close
        # ---------------------------------------------------------------------
        self.__sz = 0
        self.__bf.close()
        self.__bf = None

    @trace(LGR)
    def write(self, data):
        # ---------------------------------------------------------------------
        # write
        # ---------------------------------------------------------------------
        self.__sz += len(data)
        self.__bf.write_text(data)

    @trace(LGR)
    def seek(self, offset):
        # ---------------------------------------------------------------------
        # seek
        # ---------------------------------------------------------------------
        self.__bf.seek(offset)

    @trace(LGR)
    def size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        return self.__sz
# =============================================================================
# FUNCTIONS
# =============================================================================

@trace_func(LGR)
def init(config):
    # -------------------------------------------------------------------------
    # init
    # -------------------------------------------------------------------------
    global JSON_FILE

    JSON_FILE = JsonFile(config.get('filename', 'db'))
    JSON_FILE.open()
    JSON_FILE.write(BEGIN)

    return True

@trace_func(LGR)
def term():
    # -------------------------------------------------------------------------
    # term
    # -------------------------------------------------------------------------
    sz = JSON_FILE.size()

    if sz > len(BEGIN):
        JSON_FILE.seek(sz - 2)

    JSON_FILE.write(END)
    JSON_FILE.close()

@trace_func(LGR)
def persist(container):
    # -------------------------------------------------------------------------
    # persist
    # -------------------------------------------------------------------------
    json = json_dumps(container.to_dict())
    json += ','
    JSON_FILE.write(json)
