# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: backspace_printer.py
#     date: 2017-12-19
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 koromodako
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
#  CLASSES
# =============================================================================
##
## @brief      Class for backspace printer.
##
class BackspacePrinter(object):
    ##
    ## { item_description }
    ##
    CR = '\r'
    ##
    ## { item_description }
    ##
    BLANK = ' '
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(BackspacePrinter, self).__init__()
        self.__prev_sz = 0
    ##
    ## @brief      { function_description }
    ##
    def __erase(self):
        print(self.__prev_sz * self.BLANK, end=self.CR)
    ##
    ## { item_description }
    ##
    def print(self, line):
        self.__erase()
        self.__prev_sz = len(line)
        print(line, end=self.CR)
    ##
    ## @brief      { function_description }
    ##
    ## @param      text  The text
    ##
    ## @return     { description_of_the_return_value }
    ##
    def finish(self, text=''):
        self.__prev_sz = 0
        print(text)
