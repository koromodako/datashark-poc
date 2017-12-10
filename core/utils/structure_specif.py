# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: structure_specif.py
#     date: 2017-12-05
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
# =============================================================================
#  IMPORTS
# =============================================================================
import re
from struct import calcsize
from utils.wrapper import trace
from utils.wrapper import lazy_getter
from utils.logging import get_logger
from utils.structure import Struct
from utils.converting import unpack_one
from utils.structure_factory import StructFactory
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class Member(object):
    RE_TYPE = re.compile(r'([a-zA-Z_]\w*)')
    RE_FMT = re.compile(r'([@=<>!]?[0-9xcbB?hHiIlLqQnNfdspP]+)')
    # -------------------------------------------------------------------------
    # Member
    # -------------------------------------------------------------------------
    def __init__(self, name, load=True, valid=False):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Member, self).__init__()
        self.name = name
        self.load = load
        self.valid = valid
        if not valid:
            self.valid = (self._validate() and self.__validate())

    def __validate(self):
        # ---------------------------------------------------------------------
        # __validate
        # ---------------------------------------------------------------------
        if not isinstance(self.name, str):
            LGR.error("Member's name must be a string.")
            return False

        if self.RE_TYPE.match(self.name) is None:
            LGR.error("Member's name must validate this regexp: "
                      "{} <{}>".format(self.RE_TYPE.pattern, self.name))
            return False

        if not isinstance(self.load, bool):
            LGR.error("Member's load property must be a boolean value: "
                      "{} <{}>".format(self.name, self.load))
            return False

        return True

    @lazy_getter('__size')
    def size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        return self._size()

    def read(self, data):
        # ---------------------------------------------------------------------
        # read
        # ---------------------------------------------------------------------
        if not self.load:
            return None

        return self._read(data)

    def _validate(self):
        raise NotImplementedError

    def _size(self):
        raise NotImplementedError

    def _read(self, data):
        raise NotImplementedError


class SimpleMember(Member):
    # -------------------------------------------------------------------------
    # SimpleMember
    # -------------------------------------------------------------------------
    def __init__(self, name, fmt, load=True, valid=False):
        self.fmt = fmt
        super(SimpleMember, self).__init__(name, load, valid)

    def _validate(self):
        # ---------------------------------------------------------------------
        # _validate
        # ---------------------------------------------------------------------
        if not isinstance(self.fmt, str):
            LGR.error("SimpleMember's fmt must be a string.")
            return False

        if StructMember.RE_FMT.match(self.fmt) is None:
            LGR.error("SimpleMember's fmt must validate this regexp: "
                      "{} <{}>".format(StructMember.RE_FMT.pattern, self.fmt))
            return False

        return True

    def _size(self):
        # ---------------------------------------------------------------------
        # _size
        # ---------------------------------------------------------------------
        return calcsize(self.fmt)

    def _read(self, data):
        # ---------------------------------------------------------------------
        # _read
        # ---------------------------------------------------------------------
        return unpack_one(self.fmt, data)


class ArrayMember(Member):
    # -------------------------------------------------------------------------
    # ArrayMember
    # -------------------------------------------------------------------------
    def __init__(self, name, member, length, load=True, valid=False):
        self.member = member
        self.length = int(length)
        super(ArrayMember, self).__init__(name, load, valid)

    def _validate(self):
        # ---------------------------------------------------------------------
        # _validate
        # ---------------------------------------------------------------------
        if not isinstance(self.member, Member):
            LGR.error("ArrayMember's member must a subclass of Member.")
            return False

        if not self.member.valid:
            LGR.error("ArrayMember's member is invalid.")
            return False

        if self.length <= 0:
            LGR.error("ArrayMember's length must be in [1,+inf[.")
            return False

        return True

    def _size(self):
        # ---------------------------------------------------------------------
        # _size
        # ---------------------------------------------------------------------
        return self.member.size() * self.length

    def _read(self, data):
        # ---------------------------------------------------------------------
        # _read
        # ---------------------------------------------------------------------
        array = []
        msz = self.member.size()

        for i in range(self.length):
            array.append(self.member.read(data[i*msz:(i+1)*msz]))

        return array


class ByteArrayMember(Member):
    # -------------------------------------------------------------------------
    # ByteArrayMember
    # -------------------------------------------------------------------------
    def __init__(self, name, length, load=True, valid=False):
        self.length = int(length)
        super(ByteArrayMember, self).__init__(name, load, valid)

    def _validate(self):
        # ---------------------------------------------------------------------
        # _validate
        # ---------------------------------------------------------------------
        if self.length <= 0:
            LGR.error("ByteArrayMember's length must be in [1,+inf[.")
            return False

        return True

    def _size(self):
        # ---------------------------------------------------------------------
        # _size
        # ---------------------------------------------------------------------
        return self.length

    def _read(self, data):
        # ---------------------------------------------------------------------
        # _read
        # ---------------------------------------------------------------------
        return data[0:self.size()]


class StructMember(Member):
    # -------------------------------------------------------------------------
    # StructMember
    # -------------------------------------------------------------------------
    def __init__(self, name, st_type, load=True, valid=False):
        self.st_type = st_type
        super(StructMember, self).__init__(name, load, valid)

    def _validate(self):
        # ---------------------------------------------------------------------
        # _validate
        # ---------------------------------------------------------------------
        if not StructFactory.st_exists(self.st_type):
            LGR.error("StructMember's struct_name must refer to an existant "
                      "structure registered in the StructFactory.")
            return False

        return True

    def _size(self):
        # ---------------------------------------------------------------------
        # _size
        # ---------------------------------------------------------------------
        return StructFactory.st_size(self.st_type)

    def _read(self, data):
        # ---------------------------------------------------------------------
        # _read
        # ---------------------------------------------------------------------
        return StructFactory.st_from_bytes(self.st_type, data)


class UnionMember(Member):
    # -------------------------------------------------------------------------
    # UnionMember
    # -------------------------------------------------------------------------
    def __init__(self, name, members, load=True, valid=False):
        self.members = members
        super(UnionMember, self).__init__(name, load, valid)

    def _validate(self):
        # ---------------------------------------------------------------------
        # _validate
        # ---------------------------------------------------------------------
        if not isinstance(self.members, list):
            LGR.error("UnionMember's members must be a non-empty dict.")
            return False

        names = []
        for member in self.members:
            names.append(member.name)

            if not isinstance(member, Member):
                LGR.error("all members of UnionMember must be subclasses of "
                          "Member.")
                return False

            if not member.valid:
                LGR.error("at least one of UnionMember's members is invalid.")
                return False

        if len(names) != len(set(names)):
            LGR.error("at least two members of UnionMember share the same "
                      "name.")
            return False

        return True

    def _size(self):
        # ---------------------------------------------------------------------
        # _size
        #   This is a union we return size its biggest member
        # ---------------------------------------------------------------------
        return max([member.size() for member in self.members])

    def _read(self, data):
        # ---------------------------------------------------------------------
        # _read
        # ---------------------------------------------------------------------
        st = Struct('union')

        for member in self.members:
            if not st.set_member(member.name, member.read(data)):
                return None

        st.set_size(self.size())
        return st


class StructSpecif(object):
    # -------------------------------------------------------------------------
    # StructSpecif
    # -------------------------------------------------------------------------
    RE_TYPE = re.compile(r'(\w+)')

    def __init__(self, st_type, members):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(StructSpecif, self).__init__()
        self.st_type = st_type
        self.members = members
        self.valid = self.__validate()

    @trace(LGR)
    def __validate(self):
        # ---------------------------------------------------------------------
        # __validate
        # ---------------------------------------------------------------------
        if not isinstance(self.st_type, str):
            LGR.error("StructSpecif's st_type must be a string!")
            return False

        if self.RE_TYPE.match(self.st_type) is None:
            LGR.error("StructSpecif's st_type must validate regexp: "
                      "{}".format(self.RE_TYPE.pattern))
            return False

        if not isinstance(self.members, list) or len(self.members) == 0:
            LGR.error("StructSpecif's members must be a non-empty list!")
            return False

        names = []
        for member in self.members:
            if not isinstance(member, Member):
                LGR.error("at least one member of StructSpecif's members "
                          "is not a subclass of Member.")

            if not member.valid:
                LGR.error("at least one of StructSpecif's members is invalid.")
                return False

            names.append(member.name)

        if len(names) != len(set(names)):
            LGR.error("at least two members of StructSpecif share the same "
                      "name.")
            return False

        return True

    def size(self):
        # ---------------------------------------------------------------------
        # size
        # ---------------------------------------------------------------------
        if not hasattr(self, '__size'):
            self.__size = sum([m.size() for m in self.members])

        return self.__size
