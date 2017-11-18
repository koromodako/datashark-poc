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
import os
from magic                  import Magic
from hashlib                import sha256
from utils.helpers.logging  import get_logger
#===============================================================================
# GLOBAL
#===============================================================================
LGR = get_logger(__name__)
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
        # container file path
        self.path = path
        # file information
        self.sha256 = self.__hash()
        (self.mime_text, self.mime_type) = self.__mimes(magic_file)
        # properties
        self.flagged = False
        self.whitelisted = False
        self.blacklisted = False
        # container hierarchy
        self.__parent = None
        self.__children = []
        # unexpected dissection results will fill this list of errors
        self.__errors = []
    #---------------------------------------------------------------------------
    # __hash
    #---------------------------------------------------------------------------
    def __hash(self):
        LGR.debug('Container.__hash()')
        if self.exists():
            h = sha256()
            sz = self.size()
            with open(self.path, 'rb') as f:
                while sz > 0:
                    h.update(f.read(Container.BLK_SZ))
                    sz -= Container.BLK_SZ
            return h.digest().hex()
    #---------------------------------------------------------------------------
    # __mimes
    #---------------------------------------------------------------------------
    def __mimes(self, magic_file):
        LGR.debug('Container.__mimes()')
        return (Magic(magic_file=magic_file).from_file(self.path), 
                Magic(magic_file=magic_file, mime=True).from_file(self.path))
    #---------------------------------------------------------------------------
    # exists
    #---------------------------------------------------------------------------
    def exists(self):
        LGR.debug('Container.exists()')
        return os.path.isfile(self.path)
    #---------------------------------------------------------------------------
    # size
    #---------------------------------------------------------------------------
    def size(self):
        LGR.debug('Container.size()')
        return os.stat(self.path).st_size
    #---------------------------------------------------------------------------
    # virtual_path
    #---------------------------------------------------------------------------
    def virtual_path(self):
        LGR.debug('Container.virtual_path()')
        path = []
        parent = self.__parent
        while parent is not None:
            path.insert(0, parent.namesubsection)
            parent = parent.__parent
        return os.path.join(path)
    #---------------------------------------------------------------------------
    # add_child
    #---------------------------------------------------------------------------
    def add_child(container):
        LGR.debug('Container.add_child()')
        container.__parent = self
        self.__children.append(container)