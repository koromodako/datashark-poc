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
from magic                      import Magic
from utils.config               import config
from utils.helpers.crypto       import randstr
from utils.helpers.crypto       import hashbuf
from utils.helpers.crypto       import hashfile
from utils.helpers.logging      import get_logger
from utils.helpers.workspace    import workspace
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
            hash_func = config('hash_func', 'sha256')
            LGR.info('computing <{}> {}... please wait...'.format(path, hash_func))
            return hashfile(hash_func, path).hex()
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
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, path, realname, magic_file=None):
        super(Container, self).__init__()
        # container file path
        self.path = path
        self.realname = realname
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
        self.parent = None
        # unexpected dissection results will fill this list of errors
        self.__errors = []
    #---------------------------------------------------------------------------
    # add_child
    #---------------------------------------------------------------------------
    def set_parent(self, container):
        LGR.debug('Container.add_child()')
        self.parent = container.realname
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
    # ifileptr
    #---------------------------------------------------------------------------
    def ifileptr(self):
        return open(self.path, 'rb')
    #---------------------------------------------------------------------------
    # ofileptr
    #---------------------------------------------------------------------------
    def ofileptr(self, suffix='ds'):
        return workspace().tmpfile(suffix=suffix)
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_dict(self):
        return {
            "parent": self.parent,
            "path": self.path,
            "realname": self.realname,
            "hashed": self.hashed,
            "mime": {
                "type": self.mime_type,
                "text": self.mime_text
            },
            "flagged": self.flagged,
            "whitelisted": self.whitelisted,
            "blacklisted": self.blacklisted
        }
#-------------------------------------------------------------------------------
# ContainerActionGroup
#-------------------------------------------------------------------------------
class ContainerActionGroup(ActionGroup):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        super(ContainerActionGroup, self).__init__('container', {
            'hash': ActionGroup.action(ContainerActionGroup.hash, 
                "gives container's hash value."),
            'mimes': ActionGroup.action(ContainerActionGroup.mimes, 
                "gives container's mime type and text.")
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