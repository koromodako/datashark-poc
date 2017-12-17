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
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from dissectiondb.dissectiondb_adapter import DissectionDBAdapter
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class JsonDB(DissectionDBAdapter):
    # -------------------------------------------------------------------------
    # JsonDB
    # -------------------------------------------------------------------------
    JSON_BEGIN = '{"containers":['
    JSON_END = ']}'

    def __init__(self, conf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(JsonDB, self).__init__()
        self.conf = conf
        self.bf = None

    @trace()
    def _check_conf(self):
        # ---------------------------------------------------------------------
        # _check_conf
        # ---------------------------------------------------------------------
        if self.conf.get('path') is None:
            return False

        return True

    @trace()
    def _init_r(self):
        # ---------------------------------------------------------------------
        # _init_r
        # ---------------------------------------------------------------------
        if not BinaryFile.exists(self.conf.path):
            return False

        self.bf = BinaryFile(self.conf.path, 'r')

    @trace()
    def _init_w(self):
        # ---------------------------------------------------------------------
        # _init_w
        # ---------------------------------------------------------------------
        self.bf = BinaryFile(self.conf.path, 'w')
        self.bf.write(self.JSON_BEGIN)

    @trace()
    def _term_r(self):
        # ---------------------------------------------------------------------
        # _term_r
        # ---------------------------------------------------------------------
        self.bf.close()

    @trace()
    def _term_w(self):
        # ---------------------------------------------------------------------
        # _term_w
        # ---------------------------------------------------------------------
        self.bf.write(self.JSON_END)
        self.bf.close()

    @trace()
    def insert(self, container_dict):
        # ---------------------------------------------------------------------
        # insert
        # ---------------------------------------------------------------------
        self.bf.write_text(json_dumps(container_dict))

# =============================================================================
# FUNCTIONS
# =============================================================================

@trace_func(__name__)
def instance(conf):
    return JsonDB(conf)
