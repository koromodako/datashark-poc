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
from struct import calcsize
from utils.wrapper import trace
from utils.logging import get_logger
from utils.constants import SECTOR_SZ
from utils.converting import unpack_one
from helpers.vmdk.vmdk_disk import VmdkDisk
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for grain directory.
##
class GrainDirectory(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      vmdk       The vmdk
    ## @param      parent_gd  The parent gd
    ##
    def __init__(self, vmdk, parent_gd=None):
        super(GrainDirectory, self).__init__()

        self.bf = vmdk.bf
        self.hdr = vmdk.header()
        self.parent_gd = parent_gd

        self.metadata = vmdk.metadata()
        if self.metadata is None:
            LGR.error("failed to load metadata.")

        self.gt_coverage = self.hdr.numGTEsPerGT * self.hdr.grainSize
    ##
    ## @brief      Reads a metadata.
    ##
    ## @param      offset  The offset
    ## @param      skip    The skip
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __read_metadata(self, offset, skip=0):
        fmt = '<I'
        sz = calcsize(fmt)
        start = skip+offset*sz
        data = self.metadata[start:start+sz]
        return unpack_one(fmt, data)
    ##
    ## @brief      Reads a grain.
    ##
    ## @param      sector  The sector
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def read_grain(self, sector):
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
            data = self.bf.read(SECTOR_SZ * self.hdr.grainSize,
                                SECTOR_SZ * gte)

        return data
    ##
    ## @brief      Reads a sector.
    ##
    ## @param      n     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def read_sector(self, n):
        grain = self.read_grain(n)
        start = n*SECTOR_SZ

        return grain[start:start+SECTOR_SZ]
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def term(self):
        if self.parent_gd is not None:
            self.parent_gd.term()
        self.bf.close()
