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
import hashlib
from magic                      import Magic
from utils.config               import tmpdir
from utils.config               import config
from utils.helpers.logging      import get_logger
from utils.helpers.action_group import ActionGroup
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
    BLK_SZ = 8192
    #---------------------------------------------------------------------------
    # Container
    #---------------------------------------------------------------------------
    def __init__(self, path, realname, magic_file=None):
        super(Container, self).__init__()
        # container file path
        self.path = path
        self.realname = realname
        self.tmpd = self.__tmpd()
        # file information
        self.hashed = ''
        if not config('skip_hash', False):
            self.hashed = Container.hash(path)
        (self.mime_text, self.mime_type) = Container.mimes(magic_file, path)
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
    # __tmpd
    #---------------------------------------------------------------------------
    def __tmpd(self):
        md5 = hashlib.new('md5')
        md5.update(self.path.encode('utf-8'))
        tmpd = 'ds-{}-{}'.format(md5.digest().hex(), os.urandom(4).hex())
        path = os.path.join(tmpdir(), tmpd)
        os.makedirs(path, exist_ok=True)
        return path
    #---------------------------------------------------------------------------
    # exists
    #---------------------------------------------------------------------------
    @staticmethod
    def exists(path):
        LGR.debug('Container.exists()')
        return os.path.isfile(path)
    #---------------------------------------------------------------------------
    # size
    #---------------------------------------------------------------------------
    @staticmethod
    def size(path):
        LGR.debug('Container.size()')
        return os.stat(path).st_size
    #---------------------------------------------------------------------------
    # hash
    #---------------------------------------------------------------------------
    @staticmethod
    def hash(path):
        LGR.debug('Container.hash()')
        if Container.exists(path):
            hash_f = config('hash_func', 'sha256')
            h = hashlib.new(hash_f)
            sz = Container.size(path)
            with open(path, 'rb') as f:
                LGR.info('computing <{}> {}... please wait...'.format(
                    path, hash_f))
                while sz > 0:
                    h.update(f.read(Container.BLK_SZ))
                    sz -= Container.BLK_SZ
            return h.digest().hex()
        return None
    #---------------------------------------------------------------------------
    # __mimes
    #---------------------------------------------------------------------------
    @staticmethod
    def mimes(magic_file, path):
        LGR.debug('Container.mimes()')
        return (Magic(magic_file=magic_file).from_file(path), 
                Magic(magic_file=magic_file, mime=True).from_file(path))
    #---------------------------------------------------------------------------
    # wdir
    #---------------------------------------------------------------------------
    def wdir(self):
        LGR.debug('Container.wdir()')
        return os.path.dirname(self.path)
    #---------------------------------------------------------------------------
    # virtual_path
    #---------------------------------------------------------------------------
    def virtual_path(self):
        LGR.debug('Container.virtual_path()')
        path = []
        parent = self.__parent
        while parent is not None:
            path.insert(0, parent.realname)
            parent = parent.__parent
        return os.path.join(*path)
    #---------------------------------------------------------------------------
    # add_child
    #---------------------------------------------------------------------------
    def add_child(self, container):
        LGR.debug('Container.add_child()')
        container.__parent = self
        self.__children.append(container)
    #---------------------------------------------------------------------------
    # ifileptr
    #---------------------------------------------------------------------------
    def ifileptr(self):
        return open(self.path, 'rb')
    #---------------------------------------------------------------------------
    # ofileptr
    #---------------------------------------------------------------------------
    def ofileptr(self, suffix='ds'):
        oname = '{}.{}'.format(os.urandom(4).hex(), suffix)
        opath = os.path.join(self.tmpd, oname)
        return open(opath, 'wb')
#-------------------------------------------------------------------------------
# ContainerActionGroup
#-------------------------------------------------------------------------------
class ContainerActionGroup(ActionGroup):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(ContainerActionGroup, self).__init__('container', {
            'hash': ActionGroup.action(ContainerActionGroup.hash, "gives container's hash value."),
            'mimes': ActionGroup.action(ContainerActionGroup.mimes, "gives container's mime type and text.")
        })
    #---------------------------------------------------------------------------
    # hash
    #---------------------------------------------------------------------------
    @staticmethod
    def hash(keywords, args):
        if len(args.files) > 0:
            for f in args.files:
                if os.path.isfile(f):
                    LGR.info('{}: {}'.format(f, Container.hash(f)))
                else:
                    LGR.error('{}: invalid path.'.format(f))
        else:
            LGR.error('this action expects at least one input file.')
    #---------------------------------------------------------------------------
    # mimes
    #---------------------------------------------------------------------------
    @staticmethod
    def mimes(keywords, args):
        if len(args.files) > 0:
            for f in args.files:
                if os.path.isfile(f):
                    mimes = Container.mimes(config('magic_file'), f)
                    LGR.info('{}:\n'
                             '\tmime: {}\n'
                             '\ttext: {}'.format(f, mimes[1], mimes[0]))
                else:
                    LGR.error('{}: invalid path.'.format(f))
        else:
            LGR.error('this action expects at least one input file.')