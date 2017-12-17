# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: hashdb_adapter.py
#     date: 2017-12-15
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
import multiprocessing
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class HashDBAdapter(object):
    # -------------------------------------------------------------------------
    # HashDBAdapter
    # -------------------------------------------------------------------------
    def __init__(self, conf):
        super(HashDBAdapter, self).__init__()

        self._conf = conf
        self._lock = multiprocessing.Lock()

        self.__mode = None
        self.__valid = False

    def _check_conf(self):
        raise NotImplementedError

    def _init_r(self):
        raise NotImplementedError

    def _init_w(self):
        raise NotImplementedError

    def _term_r(self):
        raise NotImplementedError

    def _term_w(self):
        raise NotImplementedError

    def merge(self, other):
        raise NotImplementedError

    def lookup(self, hexdigest):
        raise NotImplementedError

    def insert(self, hexdigest, path):
        raise NotImplementedError

    @trace()
    def init(self, mode):
        if mode not in ['r', 'w']:
            raise ValueError("mode must be one of ['r', 'w']")
        self.__mode = mode

        if not self._check_conf():
            self.__valid = False
            return

        if self.__mode == 'r':
            self.__valid = self._init_r()
        else:
            self.__valid = self._init_w()

    @trace()
    def term(self):
        if self.__mode == 'r':
            self._term_r()
        else:
            self._term_w()

    @trace()
    def is_valid(self):
        return self.__valid
