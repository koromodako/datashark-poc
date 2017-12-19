# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: union_member.py
#     date: 2017-12-19
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
from utils.logging import get_logger
from utils.struct.struct import Struct
from utils.struct.member import Member
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief
##
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
