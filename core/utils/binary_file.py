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
from utils.memory_map import MemoryMap
from utils.formatting import hexdump
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for binary file.
##
class BinaryFile(object):
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('BinaryFile')
    def exists(path):
        return os.path.isfile(path)
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      fpath  File's path
    ## @param      mode   Open mode ('r' or 'w')
    ##
    def __init__(self, fpath, mode):
        self.fp = None
        self.path = fpath
        self.mode = mode
        self.dirname = os.path.dirname(fpath)
        self.basename = os.path.basename(fpath)
        self.abspath = os.path.abspath(fpath)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __enter__(self):
        self.open()
        return self
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    def is_valid(self):
        return (self.fp is not None)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def open(self):
        if self.fp is not None:
            LGR.warn("binary file is already opened.")
            return False

        try:
            self.fp = open(self.path, self.mode+'b')
        except Exception as e:
            LGR.exception("binary file open operation failed.")
            self.fp = None
            return False

        return True
    ##
    ## @brief      Releases underlying file handle
    ##
    def close(self):
        if self.fp is None:
            LGR.warn("binary file is already closed.")
            return False

        self.fp.close()
        self.fp = None
        return True
    ##
    ## @brief      Returns file's stat structure
    ##
    ## @return     stat structure
    ##
    def stat(self):
        return os.stat(self.abspath)
    ##
    ## @brief      Returns file size.
    ##
    ## @return     Number of bytes in file.
    ##
    def size(self):
        return self.stat().st_size
    ##
    ## @brief      Places cursor at given offset in file using whence
    ##
    ## @param      offset  The offset
    ## @param      whence  The whence
    ##
    ## @return     { description_of_the_return_value }
    ##
    def seek(self, offset, whence=io.SEEK_SET):
        return self.fp.seek(offset, whence)
    ##
    ## @brief      Reads n bytes from file as text using encoding.
    ##
    ## @param      n         Number of bytes to read
    ## @param      encoding  Encoding to use for decoding read bytes
    ##
    ## @return     str
    ##
    def read_text(self, size=-1, seek=None, encoding='utf-8'):
        return self.read(n, seek).decode(encoding)
    ##
    ## @brief      Reads n bytes from file.
    ##
    ## @param      n     Number of bytes to read
    ##
    ## @return     bytes
    ##
    def read(self, size=-1, seek=None):
        if isinstance(seek, int):
            self.seek(seek)
        return self.fp.read(size)
    ##
    ## @brief      Reads bytes N bytes into given buffer, N being buffer size.
    ##
    ## @param      b     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def readinto(self, b):
        return self.fp.readinto(b)
    ##
    ## @brief      Writes bytes to file as text using encoding.
    ##
    ## @param      text      The text
    ## @param      encoding  The encoding
    ##
    ## @return     { description_of_the_return_value }
    ##
    def write_text(self, text, encoding='utf-8'):
        return self.fp.write(text.encode('utf-8'))
    ##
    ## @brief      Writes bytes to file.
    ##
    ## @param      data  The data
    ##
    ## @return     { description_of_the_return_value }
    ##
    def write(self, data):
        return self.fp.write(data)
    ##
    ## @brief      Flushes underlying file buffer
    ##
    def flush(self):
        self.fp.flush()
    ##
    ## @brief      { function_description }
    ##
    ## @param      start  The start
    ## @param      size   The size
    ## @param      unit   The unit
    ##
    ## @return     { description_of_the_return_value }
    ##
    def mmap(self, start, size, unit=1):
        return MemoryMap(self, start, size, unit)
    ##
    ## @brief      { function_description }
    ##
    ## @param      start  The start
    ## @param      size   The size
    ##
    ## @return     { description_of_the_return_value }
    ##
    def dump(self, size=-1, seek=None):
        return hexdump(self.read(size, seek))
