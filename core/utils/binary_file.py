# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: binary_file.py
#     date: 2017-12-03
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
import os
import io
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_static
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
BF_READ='r'
BF_WRIT='w'
# =============================================================================
#  CLASSES
# =============================================================================


class BinaryFile(object):
    # -------------------------------------------------------------------------
    # BinaryFile
    # \param fpath: file path
    # \param mode: can be 'r' or 'w'
    # -------------------------------------------------------------------------
    @staticmethod
    @trace_static('BinaryFile')
    def exists(path):
        # ---------------------------------------------------------------------
        # exists
        # ---------------------------------------------------------------------
        return os.path.isfile(path)

    def __init__(self, fpath, mode):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        self.path = fpath
        self.dirname = os.path.dirname(fpath)
        self.basename = os.path.basename(fpath)
        self.abspath = os.path.abspath(fpath)
        if mode not in [BF_READ, BF_WRIT]:
            self.valid = False
        else:
            self.fp = open(fpath, mode+'b')
            self.valid = True

    # @trace()
    def stat(self):
        # ---------------------------------------------------------------------
        # stat
        # ---------------------------------------------------------------------
        return os.stat(self.abspath)

    # @trace()
    def size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        return self.stat().st_size

    # @trace()
    def seek(self, offset, whence=io.SEEK_SET):
        # ---------------------------------------------------------------------
        # seek
        # ---------------------------------------------------------------------
        return self.fp.seek(offset, whence)

    # @trace()
    def read_text(self, n=-1, encoding='utf-8'):
        # ---------------------------------------------------------------------
        # read_text
        # ---------------------------------------------------------------------
        return self.read(n).decode(encoding)

    # @trace()
    def read(self, n=-1):
        # ---------------------------------------------------------------------
        # read
        # ---------------------------------------------------------------------
        return self.fp.read(n)

    # @trace()
    def readinto(self, b):
        # ---------------------------------------------------------------------
        # readinto
        # ---------------------------------------------------------------------
        return self.fp.readinto(b)

    # @trace()
    def write_text(self, text, encoding='utf-8'):
        # ---------------------------------------------------------------------
        # write_text
        # ---------------------------------------------------------------------
        return self.fp.write(text.encode('utf-8'))

    # @trace()
    def write(self, data):
        # ---------------------------------------------------------------------
        # write
        # ---------------------------------------------------------------------
        return self.fp.write(data)

    # @trace()
    def flush(self):
        # ---------------------------------------------------------------------
        # flush
        # ---------------------------------------------------------------------
        self.fp.flush()

    # @trace()
    def close(self):
        # ---------------------------------------------------------------------
        # close
        # ---------------------------------------------------------------------
        self.valid = False
        self.fp.close()
