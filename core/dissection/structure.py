# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: structure.py
#    date: 2017-11-18
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
# Additional information from python documentation:
#
#   | Character | Byte order             | Size     | Alignment |
#   |:---------:|:----------------------:|:--------:|:---------:|
#   | @         | native                 | native   | native    |
#   | =         | native                 | standard | none      |
#   | <         | little-endian          | standard | none      |
#   | >         | big-endian             | standard | none      |
#   | !         | network (= big-endian) | standard | none      |
#
#   | Format | C Type             | Python type       | Standard size |
#   |:------:|:-------------------|:------------------|:-------------:|
#   | x      | pad byte           | no value          |               |
#   | c      | char               | bytes of length 1 | 1             |
#   | b      | signed char        | integer           | 1             |
#   | B      | unsigned char      | integer           | 1             |
#   | ?      | _Bool              | bool              | 1             |
#   | h      | short              | integer           | 2             |
#   | H      | unsigned short     | integer           | 2             |
#   | i      | int                | integer           | 4             |
#   | I      | unsigned int       | integer           | 4             |
#   | l      | long               | integer           | 4             |
#   | L      | unsigned long      | integer           | 4             |
#   | q      | long long          | integer           | 8             |
#   | Q      | unsigned long long | integer           | 8             |
#   | n      | ssize_t            | integer           |               |
#   | N      | size_t             | integer           |               |
#   | f      | float              | float             | 4             |
#   | d      | double             | float             | 8             |
#   | s      | char[]             | bytes             |               |
#   | p      | char[]             | bytes             |               |
#   | P      | void *             | integer           |               |
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import re
import struct
from utils.logging import get_logger
from utils.converting import str_to_int
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class Struct(object):
    # -------------------------------------------------------------------------
    # Struct class
    # -------------------------------------------------------------------------
    K_OBJ_TYPE = 'obj_type'
    K_OBJ_SIZE = 'obj_size'
    RESERVED = [
        K_OBJ_TYPE,
        K_OBJ_SIZE
    ]

    def __init__(self, obj_type, obj_size):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Struct, self).__init__()
        setattr(self, Struct.K_OBJ_TYPE, obj_type)
        setattr(self, Struct.K_OBJ_SIZE, obj_size)

    def to_str(self):
        # ---------------------------------------------------------------------
        # to_str
        # ---------------------------------------------------------------------
        LGR.debug('Struct.to_str()')

        members = vars(self)
        obj_type = members.pop(Struct.K_OBJ_TYPE)
        obj_size = members.pop(Struct.K_OBJ_SIZE)
        s = '\n{}(size={}):'.format(obj_type, obj_size)

        for key, value in members.items():

            if isinstance(value, Struct):
                s += value.to_str().replace('\n', '\n\t')
            else:
                s += '\n\t+ {}: {}'.format(key, value)

        return s


class StructSpecif(object):
    # -------------------------------------------------------------------------
    # StructSpecif
    # -------------------------------------------------------------------------
    RE_NAME = re.compile(r'^\w+$')
    K_FMT = 'fmt'
    K_NAME = 'name'
    K_IS_STRUCT = 'is_struct'
    K_LOAD = 'load'
    EXPECTED_KEYS = set([
        K_FMT,
        K_NAME,
        K_IS_STRUCT,
        K_LOAD
    ])

    def __init__(self, name, members):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(StructSpecif, self).__init__()
        self.name = name
        self.members = members
        self.valid = self.__validate()

    def __validate(self):
        # ---------------------------------------------------------------------
        # __validate
        # ---------------------------------------------------------------------
        LGR.debug('StructSpecif.__validate()')

        if not isinstance(self.name, str):
            LGR.error("struct's specs name must be a string!")
            return False

        if not isinstance(self.members, list):
            LGR.error("struct's specs members must be a dict!")
            return False

        for member in self.members:

            having = set(member.keys()).intersection(
                StructSpecif.EXPECTED_KEYS)
            if len(having) != len(StructSpecif.EXPECTED_KEYS):
                LGR.error("struct member's specs must have these keys: "
                          "{}".format(StructSpecif.EXPECTED_KEYS))
                return False

            name = member[StructSpecif.K_NAME]
            is_str = isinstance(name, str)
            if not is_str or StructSpecif.RE_NAME.match(name) is None:
                LGR.error("struct member's name must be a string matching "
                          "regexp: {}".format(StructSpecif.RE_NAME.pattern))
                return False

            if name in Struct.RESERVED:
                LGR.error("struct member's name <{}> is reserved.".format(
                    name))
                return False

            if not isinstance(member[StructSpecif.K_FMT], str):
                LGR.error("struct member's format must be a string.")
                return False

            if not isinstance(member[StructSpecif.K_IS_STRUCT], bool):
                LGR.error("struct member's is_struct must be a bool.")
                return False

        return True

    @staticmethod
    def member(name, fmt, is_struct=False, load=True):
        # ---------------------------------------------------------------------
        # member
        # ---------------------------------------------------------------------
        LGR.debug('StructSpecif.member()')
        return {
            StructSpecif.K_NAME: name,
            StructSpecif.K_FMT: fmt,
            StructSpecif.K_IS_STRUCT: is_struct,
            StructSpecif.K_LOAD: load
        }


class StructFactory:
    # -------------------------------------------------------------------------
    # StructFactory
    # -------------------------------------------------------------------------
    STRUCTS = {}
    RE_BA = re.compile(r'ba:(0x[0-9a-fA-F]+|0o[0-7]+|0b[0-1]+|[0-9]+)')
    K_SIZE = 'size'
    K_MEMBERS = 'members'

    @staticmethod
    def obj_exists(obj_type, log=False):
        # ---------------------------------------------------------------------
        # obj_exists
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.obj_exists()')

        s = StructFactory.STRUCTS.get(obj_type, None)
        if log and s is None:
            LGR.error('object <{}> has not been registered!'.format(obj_type))

        return (s is not None)

    @staticmethod
    def obj_size(obj_type):
        # ---------------------------------------------------------------------
        # obj_size
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.obj_size()')

        if not StructFactory.obj_exists(obj_type, log=True):
            return None

        return StructFactory.STRUCTS[obj_type][StructFactory.K_SIZE]

    @staticmethod
    def __member_size(member):
        # ---------------------------------------------------------------------
        # __member_size
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.__member_size()')

        fmt = member[StructSpecif.K_FMT]
        if member[StructSpecif.K_IS_STRUCT]:

            if not StructFactory.obj_exists(fmt):
                LGR.error("struct's member refers to another structure not "
                          "registered yet.")
                return None

            return StructFactory.obj_size(fmt)

        if StructFactory.RE_BA.match(fmt) is not None:
            return str_to_int(fmt.split(':')[-1])

        return struct.calcsize(fmt)

    @staticmethod
    def __compute_size(s):
        # ---------------------------------------------------------------------
        # __compute_size
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.__compute_size()')
        s_sz = 0
        for member in s.members:
            sz = StructFactory.__member_size(member)

            if sz is None:
                LGR.error('invalid member size.')
                return None

            s_sz += sz

        return s_sz

    @staticmethod
    def register_structure(s):
        # ---------------------------------------------------------------------
        # register_structure
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.register_structure()')

        if s.valid:
            s_sz = StructFactory.__compute_size(s)
            if s_sz is None:
                LGR.error('size computation error.')
                return False

            if s.name in list(StructFactory.STRUCTS.keys()):
                LGR.error("structure with the same name (<{}>) already "
                          "registered.".format(s.name))
                return False

            StructFactory.STRUCTS[s.name] = {
                StructFactory.K_SIZE: s_sz,
                StructFactory.K_MEMBERS: s.members
            }
            return True

        LGR.error('invalid structure.')
        return False

    @staticmethod
    def obj_from_bytes(obj_type, dat, oft=0):
        # ---------------------------------------------------------------------
        # obj_from_bytes
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.obj_from_bytes()')

        if not StructFactory.obj_exists(obj_type, log=True):
            return None

        if len(dat) != StructFactory.obj_size(obj_type):
            LGR.error('given bytearray size does not match object size!')
            return None

        sz = 0
        s = StructFactory.STRUCTS[obj_type]
        obj = Struct(obj_type, -1)

        for member in s[StructFactory.K_MEMBERS]:
            fmt = member[StructSpecif.K_FMT]

            rsz = StructFactory.__member_size(member)
            if rsz is None:
                LGR.error('invalid member size.')
                return None

            if member[StructSpecif.K_LOAD]:
                if member[StructSpecif.K_IS_STRUCT]:
                    value = StructFactory.obj_from_bytes(fmt, dat[sz:sz+rsz])
                elif StructFactory.RE_BA.match(fmt) is not None:
                    value = dat[sz:sz+rsz]
                else:
                    value = struct.unpack(fmt, dat[sz:sz+rsz])[0]
            else:
                value = None

            sz += rsz
            setattr(obj, member[StructSpecif.K_NAME], value)

        setattr(obj, Struct.K_OBJ_SIZE, sz)
        return obj

    @staticmethod
    def obj_from_file(obj_type, fp, oft=0):
        # ---------------------------------------------------------------------
        # obj_from_file
        # ---------------------------------------------------------------------
        LGR.debug('StructFactory.obj_from_file()')

        if not StructFactory.obj_exists(obj_type, log=True):
            return None

        fp.seek(oft)
        dat = fp.read(StructFactory.obj_size(obj_type))
        obj = StructFactory.obj_from_bytes(obj_type, dat)

        return obj
