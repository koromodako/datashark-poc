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
from utils.logging import get_logger
from helpers.vmdk.vmdk_disk import VmdkDisk
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)

SECTOR_SZ = VmdkDisk.SECTOR_SZ
# =============================================================================
# CLASSES
# =============================================================================


class GrainDirectory(object):
    # -------------------------------------------------------------------------
    # GrainDirectory
    # -------------------------------------------------------------------------
    def __init__(self, vmdk, parent_gd=None):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(GrainDirectory, self).__init__()

        self.bf = vmdk.bf
        self.hdr = vmdk.header()
        self.parent_gd = parent_gd

        self.metadata = vmdk.metadata()
        if self.metadata is None:
            LGR.error("failed to load metadata.")

        self.gt_coverage = self.hdr.numGTEsPerGT * self.hdr.grainSize

    def __read_metadata(self, offset, skip=0):
        # ---------------------------------------------------------------------
        # read_metadata
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.__read_metadata()')
        fmt = '<I'
        sz = struct.calcsize(fmt)
        start = skip+offset*sz
        data = self.metadata[start:start+sz]
        return struct.unpack(fmt, data)[0]

    def __read_file_grain(self, gte):
        # ---------------------------------------------------------------------
        # __read_file_grain
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.__read_file_grain()')
        self.bf.seek(gte * SECTOR_SZ)
        return self.bf.read(self.hdr.grainSize * SECTOR_SZ)

    def read_grain(self, sector):
        # ---------------------------------------------------------------------
        # read_grain
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.read_grain()')

        gde_idx = math.floor(sector / self.gt_coverage)

        gt_offset = self.__read_metadata(gde_idx)
        gt_offset -= self.hdr.rgdOffset  # offset relative to r.g.d. start

        gte_idx = math.floor((sector % self.gt_coverage) / self.hdr.grainSize)

        gte = self.__read_metadata(gte_idx, skip=gt_offset*SECTOR_SZ)

        if gte == 0:
            if self.parent_gd is None:
                data = b'\x00' * (self.hdr.grainSize * SECTOR_SZ)
            else:
                data = self.parent_gd.read_grain(sector)
        else:
            data = self.__read_file_grain(gte)

        return data

    def read_sector(self, n):
        # ---------------------------------------------------------------------
        # read_sector
        # ---------------------------------------------------------------------
        LGR.debug('GrainDirectory.read_sector()')

        grain = self.read_grain(n)
        start = n*SECTOR_SZ

        return grain[start:start+SECTOR_SZ]
