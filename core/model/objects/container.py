#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: container.py
#    date: 2017-11-11
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
from os                     import stat
from magic                  import Magic
from hashlib                import sha256
from utils.helpers.logging  import get_logger
#===============================================================================
# GLOBAL
#===============================================================================
lgr = get_logger(__name__)
#===============================================================================
# FUNCTIONS
#===============================================================================
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Container
#-------------------------------------------------------------------------------
class Container(object):
    BLK_SZ = 4096
    #---------------------------------------------------------------------------
    # Container
    #---------------------------------------------------------------------------
    def __init__(self, path, magic_file=None):
        super(Container, self).__init__()
        self.path = path
        self.mime_text = Magic(magic_file=magic_file).from_file(path)
        self.mime_type = Magic(magic_file=magic_file, mime=True).from_file(path)
        self.sha256 = self.__hash()
        self.children = []
    #---------------------------------------------------------------------------
    # __hash
    #---------------------------------------------------------------------------
    def __hash(self):
        lgr.debug('Container.__hash()')
        if self.exists():
            h = sha256.new()
            sz = self.size()
            with open(self.path, 'rb') as f:
                while sz > 0:
                    h.update(f.read(Container.BLK_SZ))
                    sz -= Container.BLK_SZ
            return h.digest()
    #---------------------------------------------------------------------------
    # exists
    #---------------------------------------------------------------------------
    def exists(self):
        lgr.debug('Container.exists()')
        return os.path.isfile(self.path)
    #---------------------------------------------------------------------------
    # size
    #---------------------------------------------------------------------------
    def size(self):
        lgr.debug('Container.size()')
        return os.stat(self.path).st_size
