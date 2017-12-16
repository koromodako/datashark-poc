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
from utils.logging import get_logger
from utils.wrapper import trace_func
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
BLANK_LINE = ' ' * 120
# =============================================================================
# FUNCTIONS
# =============================================================================


def __printable(byte):
    # -------------------------------------------------------------------------
    # __printable
    # -------------------------------------------------------------------------
    if byte < 0x20 or byte > 0x7e:
        return '.'

    return chr(byte)


@trace_func(__name__)
def hexdump(data, col_sz=2, col_num=4, human=True, max_lines=10):
    # -------------------------------------------------------------------------
    # hexdump
    # -------------------------------------------------------------------------
    lines = []
    row_sz = col_sz * col_num
    r = len(data) % row_sz

    for k in range(0, (len(data) // row_sz) + 1):
        lhex = '%#08x: ' % (k * row_sz)
        lhum = ' |'
        d = data[k * row_sz:(k + 1) * row_sz]

        for i in range(0, col_num):
            lhex += ' '

            for j in range(0, col_sz):
                idx = i * col_sz + j
                if idx < len(d):
                    c = d[idx]
                    lhex += '%02x' % c
                    lhum += __printable(c)
                else:
                    lhex += '  '

        if human:
            lhex += lhum + '|'
        lines.append(lhex)

    if max_lines > 1:
        if len(lines) > max_lines:
            ml = max_lines // 2
            text = '\n'.join(lines[0:ml])
            text += '\n[snip]\n'
            text += '\n'.join(lines[-ml:])
            return text

    return '\n'.join(lines)
