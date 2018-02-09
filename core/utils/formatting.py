# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: formatting.py
#    date: 2017-07-23
#  author: paul.dautry
# purpose:
#    Utils formated printing functions
# license:
#    Utils
#    Copyright (C) 2017  Paul Dautry
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# =============================================================================
from enum import Enum
from termcolor import colored
#
from utils.logging import get_logger
from utils.wrapper import trace_func
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
BS = ' '
BLANK_LINE = BS * 120
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      Returns a character if it's part of ASCII printable caracters
##
## @param      byte  Byte to interpret as a char
##
## @return     char matching byte or '.'
##
def __printable(byte):
    if byte < 0x20 or byte > 0x7e:
        return '.'

    return chr(byte)
##
## @brief      { function_description }
##
## @param      size    The size
## @param      suffix  The suffix
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def format_size(size, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:

        if abs(size) < 1024.0:
            return "{:3.1f}{}{}".format(size, unit, suffix)

        size /= 1024.0

    return "{:.1f}{}{}".format(size, 'Y', suffix)
##
## @brief      { function_description }
##
## @param      data       The data
## @param      col_sz     The col size
## @param      col_num    The col number
## @param      human      The human
## @param      max_lines  The maximum lines
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def hexdump_lines(data, col_sz=2, col_num=4, human=True, max_lines=10):
    lines = []
    row_sz = col_sz * col_num
    r = len(data) % row_sz

    for k in range(0, (len(data) // row_sz) + 1):
        lhex = "{:#08x}: ".format(k * row_sz)
        lhum = " |"
        d = data[k * row_sz:(k + 1) * row_sz]

        for i in range(0, col_num):
            lhex += BS

            for j in range(0, col_sz):
                idx = i * col_sz + j
                if idx < len(d): # len(d) might be smaller than row_sz
                    c = d[idx]
                    lhex += "{:02x}".format(c)
                    lhum += __printable(c)
                else:
                    lhex += BS * 2
                    lhum += BS

        if human:
            lhex += lhum + '|'
        lines.append(lhex)

    if max_lines > 1:
        if len(lines) > max_lines:
            ml = max_lines // 2
            lines = lines[0:ml] + ["[snip]"] + lines[-ml:]

    return lines
##
## @brief      { function_description }
##
## @param      data       The data
## @param      col_sz     The col size
## @param      col_num    The col number
## @param      human      The human
## @param      max_lines  The maximum lines
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def hexdump(data, col_sz=2, col_num=4, human=True, max_lines=10):
    return '\n'.join(hexdump_lines(data, col_sz, col_num, human, max_lines))
##
## @brief      { function_description }
##
## @param      d1         The d 1
## @param      d2         The d 2
## @param      col_sz     The col size
## @param      col_num    The col number
## @param      human      The human
## @param      max_lines  The maximum lines
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def hexdiff_lines(d1, d2, col_sz=2, col_num=4, human=True):
    lines = []

    if len(d1) != len(d2):
        LGR.error("d1 and d2 sizes differs => no diff returned.")
        return lines

    row_sz = col_sz * col_num
    r = len(d1) % row_sz

    for k in range(0, (len(d1) // row_sz) + 1):
        lhead = "{:#08x}: ".format(k * row_sz)
        l1hex = ""
        l2hex = ""
        l1hum = " |"
        l2hum = " |"

        sd1 = d1[k * row_sz:(k + 1) * row_sz]
        sd2 = d2[k * row_sz:(k + 1) * row_sz]

        for i in range(0, col_num):
            l1hex += BS
            l2hex += BS

            for j in range(0, col_sz):
                idx = i * col_sz + j
                if idx < len(sd1):  # len(sd1) might be smaller than row_sz
                    c1 = sd1[idx]
                    c2 = sd2[idx]

                    color = 'green' if c1 == c2 else 'red'

                    l1hex += colored("{:02x}".format(c1), color)
                    l1hum += colored(__printable(c1), color)
                    l2hex += colored("{:02x}".format(c2), color)
                    l2hum += colored(__printable(c2), color)
                else:
                    l1hex += BS * 2
                    l1hum += BS
                    l2hex += BS * 2
                    l2hum += BS

        if human:
            l1hex += l1hum + '|'
            l2hex += l2hum + '|'

        sep = '\\' if (k+1) % 2 == 0 else '/'
        line = lhead + l1hex + sep + l2hex
        lines.append(line)

    return lines
##
## @brief      { function_description }
##
## @param      d1       The d 1
## @param      d2       The d 2
## @param      col_sz   The col size
## @param      col_num  The col number
## @param      human    The human
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def hexdiff(d1, d2, col_sz=2, col_num=4, human=True):
    return '\n'.join(hexdiff_lines(d1, d2, col_sz, col_num, human))
##
## @brief      Class for column.
##
class Column(object):
    ##
    ## @brief      Class for alignment.
    ##
    class Alignment(Enum):
        LEFT = 0
        RIGHT = 1
        CENTERED = 2
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      name   The name
    ## @param      align  The align
    ##
    def __init__(self, name=None, alignment=Alignment.LEFT, fmtr=None):
        self.name = name
        if not isinstance(alignment, Column.Alignment):
            LGR.error("programmatical error: align argument must be an "
                      "instance of Column.Alignment.")
        self.alignment = alignment
        self.fmtr = fmtr
    ##
    ## @brief      Returns value formatted using given fmtr or "stringified"
    ##
    ## @param      value  The value
    ##
    def format(self, value):
        if self.fmtr is not None:
            value = self.fmtr(value)

        if not isinstance(value, str):
            value = str(value)

        return value
    ##
    ## @brief      { function_description }
    ##
    ## @param      value      The value
    ## @param      max_width  The maximum width
    ##
    def align(self, value, max_width):
        vlen = len(value)
        miss = (max_width - vlen + 2)

        if self.alignment == Column.Alignment.LEFT:
            value += miss * BS

        elif self.alignment == Column.Alignment.RIGHT:
            value = miss * BS + value

        elif self.alignment == Column.Alignment.CENTERED:
            value = (miss // 2) * BS + value + (miss // 2) * BS
            value += BS if (miss % 2) == 1 else ''

        else:
            LGR.error("invalid alignment value => defaulting to "
                      "Column.Alignment.NONE.")

        return value
##
## @brief      Class for table.
##
class Table(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      rows  The rows
    ## @param      cols  The cols
    ##
    def __init__(self, cols=[]):
        self.cols = cols
        self.clen = len(cols)
        self.rows = []
        self.max_width_per_col = [0 for i in range(self.clen)]
    ##
    ## @brief      Adds a row.
    ##
    ## @param      row   The row
    ##
    def add_row(self, row):
        if len(row) != self.clen:
            LGR.error("incomplete row (row element count and col count "
                      "mismatch) => row ignored.")
            return False
        # process row elements
        for i in range(self.clen):
            # format element using Column formatter
            row[i] = self.cols[i].format(row[i])
            # update max width array if needed
            elen = len(row[i])
            if elen > self.max_width_per_col[i]:
                self.max_width_per_col[i] = elen
        # append row
        self.rows.append(row)
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      print_header  Prints header
    ##
    def print(self, print_header=True):
        rows = self.rows

        if print_header:
            row = []
            for i in range(self.clen):
                name = self.cols[i].name
                nlen = len(name)

                row.append(name)

                if nlen > self.max_width_per_col[i]:
                    self.max_width_per_col[i] = nlen

            rows = [row] + rows

        for row in rows:
            line = ""
            for i in range(self.clen):
                line += self.cols[i].align(row[i], self.max_width_per_col[i])
            print(line)
