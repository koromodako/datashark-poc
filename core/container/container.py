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
from magic import Magic
from utils.config import config
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
    @staticmethod
    @trace_static(LGR, 'Container')
    def hash(path):
        # ---------------------------------------------------------------------
        # hash
        # ---------------------------------------------------------------------
        if BinaryFile.exists(path):
            hash_func = config('hash_func', 'sha256')
            LGR.info("computing <{}> {}... please wait...".format(path,
                                                                  hash_func))
            return hashfile(hash_func, path).hex()
        return None

    @staticmethod
    @trace_static(LGR, 'Container')
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

    @trace(LGR)
    def set_parent(self, container):
        # ---------------------------------------------------------------------
        # set_parent
        # ---------------------------------------------------------------------
        self.parent = container.realname

    @trace(LGR)
    def wdir(self):
        # ---------------------------------------------------------------------
        # wdir
        # ---------------------------------------------------------------------
        return os.path.dirname(self.path)

    @trace(LGR)
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

    @trace(LGR)
    def ibf(self):
        # ---------------------------------------------------------------------
        # ibf
        # ---------------------------------------------------------------------
        return BinaryFile(self.path, 'r')

    @trace(LGR)
    def obf(self, suffix='ds'):
        # ---------------------------------------------------------------------
        # obf
        # ---------------------------------------------------------------------
        return workspace().tmpfile(suffix=suffix)

    @trace(LGR)
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
            'flagged': self.flagged,
            'whitelisted': self.whitelisted,
            'blacklisted': self.blacklisted
        }


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
    @trace_static(LGR, 'ContainerActionGroup')
    def hash(keywords, args):
        # ---------------------------------------------------------------------
        # hash
        # ---------------------------------------------------------------------
        if len(args.files) > 0:
            for f in args.files:
                if BinaryFile.exists(f):
                    LGR.info('{}: {}'.format(f, Container.hash(f)))
                else:
                    LGR.error("{}: invalid path.".format(f))
        else:
            LGR.error("this action expects at least one input file.")

    @staticmethod
    @trace_static(LGR, 'ContainerActionGroup')
    def mimes(keywords, args):
        # ---------------------------------------------------------------------
        # mimes
        # ---------------------------------------------------------------------
        if len(args.files) == 0:
            LGR.error("this action expects at least one input file.")
            return

        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.error("{}: invalid path.".format(f))
                return

            mimes = Container.mimes(config('magic_file'), f)
            LGR.info('{}:\n'
                     '\tmime: {}\n'
                     '\ttext: {}'.format(f, mimes[1], mimes[0]))
