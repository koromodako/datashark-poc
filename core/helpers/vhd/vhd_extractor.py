# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vhd_extractor.py
#     date: 2017-12-09
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
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class VhdExtractor(object):
    # -------------------------------------------------------------------------
    # VhdExtractor
    # -------------------------------------------------------------------------
    def __init__(self, wdir, vhd, obf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(VhdExtractor, self).__init__()
        self.wdir = wdir
        self.vhd = vhd
        self.obf = obf

    def extract(self):
        # ---------------------------------------------------------------------
        # extract
        # ---------------------------------------------------------------------
        LGR.debug("VhdExtractor.extract()")

        // TODO
