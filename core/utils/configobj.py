# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for configuration object.
##
class ConfigObj(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      dic   The dic
    ##
    def __init__(self, dic):
        for option, value in dic.items():
            if isinstance(value, list):
                setattr(self, option, self.__process_list(value))
            elif isinstance(value, dict):
                setattr(self, option, ConfigObj(value))
            else:
                setattr(self, option, value)
    ##
    ## @brief      { function_description }
    ##
    ## @param      l     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
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
    ##
    ## @brief      { function_description }
    ##
    ## @param      member  The member
    ##
    ## @return     { description_of_the_return_value }
    ##
    def has(self, member):
        return hasattr(self, member)
    ##
    ## @brief      { function_description }
    ##
    ## @param      member   The member
    ## @param      default  The default
    ##
    ## @return     { description_of_the_return_value }
    ##
    def get(self, member, default=None):
        if self.has(member):
            return getattr(self, member)
        return default
    ##
    ## @brief      { function_description }
    ##
    ## @param      v     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __v_to_dict(self, v):
        if isinstance(v, ConfigObj):
            return v.to_dict()

        elif isinstance(v, dict):
            d = {}
            for key, val in v.items():
                d[key] = self.__v_to_dict(val)
            return d

        elif isinstance(v, list):
            nl = []
            for e in v:
                nl.append(self.__v_to_dict(e))
            return nl

        return v
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def to_dict(self):
        return self.__v_to_dict(vars(self))
