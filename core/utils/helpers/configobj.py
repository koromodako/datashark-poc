#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: configobj.py
#    date: 2017-11-28
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
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# ConfigObj
#-------------------------------------------------------------------------------
class ConfigObj(object):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, dic):
        for option, value in dic.items():
            if isinstance(value, list):
                setattr(self, option, self.__process_list(value))
            elif isinstance(value, dict):
                setattr(self, option, ConfigObj(value))
            else:
                setattr(self, option, value)
    #---------------------------------------------------------------------------
    # __process_list
    #---------------------------------------------------------------------------
    def __process_list(self, l):
        nl = []
        for v in l:
            if isinstance(v, list):
                nl.append(self.__process_list(v))
            elif isinstance(v, dict):
                nl.append(ConfigObj(v))
            else:
                nl.append(v)
        return nl
    #---------------------------------------------------------------------------
    # has
    #---------------------------------------------------------------------------
    def has(self, member):
        return hasattr(self, member)
    #---------------------------------------------------------------------------
    # get
    #---------------------------------------------------------------------------
    def get(self, member, default=None):
        if self.has(member):
            return getattr(self, member)
        return default