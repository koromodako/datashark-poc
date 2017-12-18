# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import os
import enum
import utils.config as config
from magic import Magic
from workspace.workspace import workspace
from utils.crypto import randstr
from utils.crypto import hashbuf
from utils.crypto import hashfile
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_static
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================
# =============================================================================
# CLASSES
# =============================================================================


class Container(object):
    # -------------------------------------------------------------------------
    # Container
    # -------------------------------------------------------------------------
    class Flag(enum.Flag):
        # ---------------------------------------------------------------------
        # Flag
        # ---------------------------------------------------------------------
        NONE = 0x00
        CARVED = 0x01
        FLAGGED = 0x02
        DISSECTED = 0x04
        WHITELISTED = 0x08
        BLACKLISTED = 0x10 | FLAGGED  # blacklisted => flagged
        CARVING_REQUIRED = 0x20

    @staticmethod
    @trace_static('Container')
    def hash(path):
        # ---------------------------------------------------------------------
        # hash
        # ---------------------------------------------------------------------
        if BinaryFile.exists(path):
            hash_func = config.value('hash_func', 'sha256')
            LGR.info("computing <{}> {}... please wait...".format(path,
                                                                  hash_func))
            return hashfile(hash_func, path).hex()
        return None

    @staticmethod
    @trace_static('Container')
    def mimes(magic_file, path):
        # ---------------------------------------------------------------------
        # mimes
        # ---------------------------------------------------------------------
        return (Magic(magic_file=magic_file).from_file(path),
                Magic(magic_file=magic_file, mime=True).from_file(path))

    def __init__(self, path, realname, magic_file=None):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Container, self).__init__()
        # container file path
        self.path = path
        self.realname = realname
        # file information
        self.hashed = ''
        if not config.value('skip_hash', False):
            self.hashed = Container.hash(path)
        (self.mime_text, self.mime_type) = Container.mimes(magic_file, path)
        # properties
        self.flags = Container.Flag.NONE
        # container hierarchy
        self.parent = None
        # unexpected dissection results will fill this list of errors
        self.__errors = []

    @trace()
    def to_dict(self):
        # ---------------------------------------------------------------------
        # to_dict
        # ---------------------------------------------------------------------
        return {
            'parent': self.parent,
            'path': self.path,
            'realname': self.realname,
            'hashed': self.hashed,
            'mime': {
                'type': self.mime_type,
                'text': self.mime_text
            },
            'flagged': self.has_flag(Container.Flag.FLAGGED),
            'whitelisted': self.has_flag(Container.Flag.WHITELISTED),
            'blacklisted': self.has_flag(Container.Flag.BLACKLISTED)
        }

    @trace()
    def set_parent(self, container):
        # ---------------------------------------------------------------------
        # set_parent
        # ---------------------------------------------------------------------
        self.parent = container.realname

    @trace()
    def set_flag(self, flag):
        # ---------------------------------------------------------------------
        # set_flag
        # ---------------------------------------------------------------------
        self.flags |= flag

    @trace()
    def unset_flag(self, flag):
        # ---------------------------------------------------------------------
        # unset_flag
        # ---------------------------------------------------------------------
        self.flags &= ~flag

    @trace()
    def has_flag(self, flag):
        # ---------------------------------------------------------------------
        # has_flag
        # ---------------------------------------------------------------------
        return (self.flags & flag) == flag

    @trace()
    def wdir(self):
        # ---------------------------------------------------------------------
        # wdir
        # ---------------------------------------------------------------------
        return os.path.dirname(self.path)

    @trace()
    def virtual_path(self):
        # ---------------------------------------------------------------------
        # virtual_path
        # ---------------------------------------------------------------------
        path = []
        parent = self.__parent
        while parent is not None:
            path.insert(0, parent.realname)
            parent = parent.__parent
        return os.path.join(*path)

    @trace()
    def ibf(self):
        # ---------------------------------------------------------------------
        # ibf
        # ---------------------------------------------------------------------
        return BinaryFile(self.path, 'r')

    @trace()
    def obf(self, suffix='ds'):
        # ---------------------------------------------------------------------
        # obf
        # ---------------------------------------------------------------------
        return workspace().tmpfile(suffix=suffix)



class ContainerActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # ContainerActionGroup
    # -------------------------------------------------------------------------
    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(ContainerActionGroup, self).__init__('container', {
            'hash': ActionGroup.action(ContainerActionGroup.hash,
                                       "container's hash value."),
            'mimes': ActionGroup.action(ContainerActionGroup.mimes,
                                        "container's mime type and text.")
        })

    @staticmethod
    @trace_static('ContainerActionGroup')
    def hash(keywords, args):
        # ---------------------------------------------------------------------
        # hash
        # ---------------------------------------------------------------------
        if len(args.files) == 0:
            LGR.error("this action expects at least one input file.")
            return False

        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("{}: invalid path => skipped.".format(f))
                continue

            LGR.info('{}: {}'.format(f, Container.hash(f)))

        return True


    @staticmethod
    @trace_static('ContainerActionGroup')
    def mimes(keywords, args):
        # ---------------------------------------------------------------------
        # mimes
        # ---------------------------------------------------------------------
        if len(args.files) == 0:
            LGR.error("this action expects at least one input file.")
            return False

        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("{}: invalid path => skipped.".format(f))
                continue

            mimes = Container.mimes(config.value('magic_file'), f)
            LGR.info('{}:\n'
                     '\tmime: {}\n'
                     '\ttext: {}'.format(f, mimes[1], mimes[0]))

        return True
