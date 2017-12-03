# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: gd.py
#    date: 2017-12-01
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
# IMPORTS
# =============================================================================
import math
import struct
from utils.helpers.logging import get_logger
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
SECTOR_SZ = 512  # bytes
# =============================================================================
# CLASSES
# =============================================================================


class GrainDirectory(object):
    # -------------------------------------------------------------------------
    # GrainDirectory
    # -------------------------------------------------------------------------
    def __init__(self, hdr, fp):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(GrainDirectory, self).__init__()
        self.fp = fp
        self.hdr = hdr
        self.metadata = self.__load_metadata()
        self.gtCoverage = hdr.numGTEsPerGT * hdr.grainSize

    def __load_metadata(self):
        # ---------------------------------------------------------------------
        # __load_metadata
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.__cache_data()')
        fp.seek(hdr.rgdOffset * SECTOR_SZ)
        return fp.read(hdr.overHead * SECTOR_SZ)

    def read_sector(self, n):
        # ---------------------------------------------------------------------
        # read_sector
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.read_sector()')
        gde_idx = math.floor(n / self.gtCoverage)
        # gt_offset = ...
