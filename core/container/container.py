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
#
import os
import enum
import utils.config as config
from uuid import uuid4
from magic import Magic
#
from utils.crypto import randstr
from utils.crypto import hashbuf
from utils.crypto import hashfile
from utils.logging import get_logger
from utils.wrapper import trace
from utils.wrapper import trace_static
from utils.formatting import hexdump
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from workspace.workspace import workspace
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
##
## @brief      Class for container.
##
class Container(object):
    ##
    ## @brief      Class for flag.
    ##
    class Flag(enum.Flag):
        NONE = 0x00
        CARVED = 0x01
        FLAGGED = 0x02
        DISSECTED = 0x04
        WHITELISTED = 0x08
        BLACKLISTED = 0x10 | FLAGGED  # blacklisted => flagged
        CARVING_REQUIRED = 0x20
    ##
    ## @brief      { function_description }
    ##
    ## @param      path  The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('Container')
    def hash(path):
        if BinaryFile.exists(path):
            hash_func = config.value('hash_func', 'sha256')
            LGR.info("computing <{}> {}... please wait...".format(path,
                                                                  hash_func))
            return hashfile(hash_func, path).hex()
        return None
    ##
    ## @brief      { function_description }
    ##
    ## @param      magic_file  The magic file
    ## @param      path        The path
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('Container')
    def mimes(magic_file, path):
        return (Magic(magic_file=magic_file).from_file(path),
                Magic(magic_file=magic_file, mime=True).from_file(path))
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      path        The path
    ## @param      realname    The realname
    ## @param      magic_file  The magic file
    ##
    def __init__(self, path, realname, magic_file=None):
        super(Container, self).__init__()
        ## @brief Container's unique id
        self.uuid = uuid4()
        ## @brief Parent container's unique id for hierarchy
        self.parent_uuid = None
        ## @brief Container's data file path
        self.path = path
        ## @brief Container's real name
        self.realname = realname
        ## @brief Container's data hash value
        self.hashed = ''
        if not config.value('skip_hash', False):
            self.hashed = Container.hash(path)
        #
        (mime_text, mime_type) = Container.mimes(magic_file, path)
        ## @brief Container's data MIME text
        self.mime_text = mime_text
        ## @brief Container's data MIME type
        self.mime_type = mime_type
        ## @brief Container's properties stored as a flag
        self.flags = Container.Flag.NONE
        # unexpected dissection results will fill this list of errors
        self.__errors = []
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def to_dict(self):
        parent_uuid = self.parent_uuid
        if parent_uuid is not None:
            parent_uuid = str(parent_uuid)

        return {
            'uuid': str(self.uuid),
            'parent_uuid': parent_uuid,
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
    ##
    ## @brief      Sets the parent.
    ##
    ## @param      container  The container
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def set_parent(self, container):
        self.parent = container.uuid
    ##
    ## @brief      Sets the flag.
    ##
    ## @param      flag  The flag
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def set_flag(self, flag):
        self.flags |= flag
    ##
    ## @brief      { function_description }
    ##
    ## @param      flag  The flag
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def unset_flag(self, flag):
        self.flags &= ~flag
    ##
    ## @brief      Determines if it has flag.
    ##
    ## @param      flag  The flag
    ##
    ## @return     True if has flag, False otherwise.
    ##
    @trace()
    def has_flag(self, flag):
        return (self.flags & flag) == flag
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def wdir(self):
        return os.path.dirname(self.path)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def virtual_path(self):
        path = []
        parent = self.__parent
        while parent is not None:
            path.insert(0, parent.realname)
            parent = parent.__parent
        return os.path.join(*path)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def ibf(self):
        bf = BinaryFile(self.path, 'r')
        bf.open()
        return bf
    ##
    ## @brief      { function_description }
    ##
    ## @param      suffix  The suffix
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def obf(self, prefix=''):
        return workspace().tmpfile(prefix=prefix, suffix='ds')
##
## @brief      Class for container action group.
##
class ContainerActionGroup(ActionGroup):
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('ContainerActionGroup')
    def hash(keywords, args):
        if len(args.files) == 0:
            LGR.error("this action expects at least one input file.")
            return False

        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("{}: invalid path => skipped.".format(f))
                continue

            print("{}: {}".format(f, Container.hash(f)))

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('ContainerActionGroup')
    def mimes(keywords, args):
        if len(args.files) == 0:
            LGR.error("this action expects at least one input file.")
            return False

        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("{}: invalid path => skipped.".format(f))
                continue

            mimes = Container.mimes(config.value('magic_file'), f)

            print("{}:\n\tmime: {}\n\ttext: {}".format(f,
                                                       mimes[1],
                                                       mimes[0]))

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('ContainerActionGroup')
    def read(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("file not found (<{}>) => skipping.".format(f))
                continue

            if args.offset is None:
                args.offset = 0

            if args.size is None:
                args.size = -1

            with BinaryFile(f, 'r') as bf:

                if args.offset > 0:
                    bf.seek(args.offset)

                data = bf.read(args.size)

            text = "\n"
            text += "{} offset={} size={}\n".format(f, args.offset, args.size)
            text += hexdump(data, col_num=8, max_lines=-1)
            print(text)
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(ContainerActionGroup, self).__init__('container', {
            'hash': ActionGroup.action(ContainerActionGroup.hash,
                                       "container's hash value."),
            'mimes': ActionGroup.action(ContainerActionGroup.mimes,
                                        "container's mime type and text."),
            'read': ActionGroup.action(ContainerActionGroup.read,
                                       "reads a portion of a file.")
        })
