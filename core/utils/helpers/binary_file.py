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
from utils.helpers.logging import get_logger
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
    def exists(path):
        # ---------------------------------------------------------------------
        # exists
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.exists()')
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

    def stat(self):
        # ---------------------------------------------------------------------
        # stat
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.stat()')
        return os.stat(self.abspath)

    def size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.size()')
        return self.stat().st_size

    def seek(self, offset, whence=io.SEEK_SET):
        # ---------------------------------------------------------------------
        # seek
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.seek()')
        return self.fp.seek(offset, whence)

    def read_text(self, n=-1, encoding='utf-8'):
        # ---------------------------------------------------------------------
        # read_text
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.read_text()')
        return self.read(n).decode(encoding)

    def read(self, n=-1):
        # ---------------------------------------------------------------------
        # read
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.read()')
        return self.fp.read(n)

    def readinto(self, b):
        # ---------------------------------------------------------------------
        # readinto
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.readinto()')
        return self.fp.readinto(b)

    def write_text(self, text, encoding='utf-8'):
        # ---------------------------------------------------------------------
        # write_text
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.write_text()')
        return self.fp.write(text.encode('utf-8'))

    def write(self, data):
        # ---------------------------------------------------------------------
        # write
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.write()')
        return self.fp.write(data)

    def close(self):
        # ---------------------------------------------------------------------
        # close
        # ---------------------------------------------------------------------
        LGR.debug('BinaryFile.close()')
        self.valid = False
        self.fp.close()

