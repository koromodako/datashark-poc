# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: fs.py
#     date: 2017-12-16
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
import os
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  FUNCTIONS
# =============================================================================


@trace_func(__name__)
def enumerate_files(dirs, dir_filter, file_filter, recursive):
    # -------------------------------------------------------------------------
    # enumerate_files
    # -------------------------------------------------------------------------
    fpaths = []

    for dpath in dirs:
        adpath = os.path.abspath(dpath)

        if recursive:
            # recursive listing from given directory
            for root, dirs, files in os.walk(adpath):
                dirs[:] = [d for d in dirs if dir_filter.keep(d)]
                for f in files:
                    if file_filter.keep(f):
                        fpaths.append(os.path.join(root, f))
        else:
            # listing only inside given directory
            for entry in os.listdir(adpath):
                fpath = os.path.join(adpath, entry)
                if BinaryFile.exists(fpath):
                    if file_filter.keep(entry):
                        fpaths.append(fpath)

    return fpaths
