#!/usr/bin/env <PROG>
# -!- encoding:utf8 -!-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: structure_factory.py
#     date: 2017-12-06
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundataion, either version 3 of the License, or
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
import re
import struct
from utils.logging import get_logger
from utils.wrapper import trace_static
from utils.struct.struct import Struct
from utils.struct.struct_specif import StructSpecif
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Front-end to create structure objects.
##
class StructFactory:
    STRUCTS = {}
    K_SIZE = 'size'
    K_MEMBERS = 'members'
    K_FORMATTERS = 'formatters'
    ##
    ## @brief      { function_description }
    ##
    ## @param      st_type  The st type
    ## @param      log      The log
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('StructFactory')
    def st_exists(st_type, log=False):
        st = StructFactory.STRUCTS.get(st_type, None)
        if log and st is None:
            LGR.error("object <{}> has not been registered!".format(st_type))

        return (st is not None)
    ##
    ## @brief      { function_description }
    ##
    ## @param      st_type  The st type
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('StructFactory')
    def st_size(st_type):
        if not StructFactory.st_exists(st_type, log=True):
            return None

        return StructFactory.STRUCTS[st_type][StructFactory.K_SIZE]
    ##
    ## @brief      { function_description }
    ##
    ## @param      st_specif  The st specif
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('StructFactory')
    def st_register(st_name, st_members):
        st_specif = StructSpecif(st_name, st_members)

        if st_specif.valid:

            if st_specif.size() == 0:
                LGR.error("structure must have a strictly positive size: "
                          "<{}>".format(st_specif.st_size))
                return False

            if st_specif.st_type in list(StructFactory.STRUCTS.keys()):
                LGR.error("structure with the same name (<{}>) already "
                          "registered.".format(st_specif.st_type))
                return False

            StructFactory.STRUCTS[st_specif.st_type] = {
                StructFactory.K_SIZE: st_specif.size(),
                StructFactory.K_MEMBERS: st_specif.members,
                StructFactory.K_FORMATTERS: st_specif.formatters
            }
            return True

        LGR.error("invalid structure: <{}>".format(st_specif.st_type))
        return False
    ##
    ## @brief      { function_description }
    ##
    ## @param      st_type  The st type
    ## @param      data     The data
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('StructFactory')
    def st_from_bytes(st_type, data):
        if not StructFactory.st_exists(st_type, log=True):
            return None

        if len(data) != StructFactory.st_size(st_type):
            LGR.warn("given bytearray size does not match <{}> "
                        "size!".format(st_type))
            return None

        sz = 0
        st_specif = StructFactory.STRUCTS[st_type]
        st = Struct(st_type,
                    st_specif[StructFactory.K_SIZE],
                    st_specif[StructFactory.K_FORMATTERS])

        for member in st_specif[StructFactory.K_MEMBERS]:
            rsz = member.size()

            if not st.set_member(member.name, member.read(data[sz:sz+rsz])):
                LGR.error("failed to set member <{}>".format(member.name))
                return None

            sz += rsz

        st.set_size(sz)
        return st
    ##
    ## @brief      { function_description }
    ##
    ## @param      st_type  The st type
    ## @param      bf       The binary file to read from
    ## @param      oft      The oft
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('StructFactory')
    def st_from_file(st_type, bf, oft=0):
        if not StructFactory.st_exists(st_type, log=True):
            return None

        bf.seek(oft)
        data = bf.read(StructFactory.st_size(st_type))
        st = StructFactory.st_from_bytes(st_type, data)

        return st
