# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: sparse_extent_extractor.py
#     date: 2017-12-04
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
import os.path
from utils.logging import todo
from utils.wrapper import trace
from utils.logging import get_logger
from utils.constants import SECTOR_SZ
from utils.binary_file import BinaryFile
from helpers.vmdk.gd_stack import GrainDirectoryStack
from helpers.vmdk.vmdk_disk import VmdkDisk
from helpers.vmdk.vmdk_disk import S_SPARSE_EXTENT_HDR
# =============================================================================
#  GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for sparse extent extractor.
##
class SparseExtentExtractor(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      wdir  The wdir
    ## @param      vmdk  The vmdk
    ## @param      obf   The obf
    ##
    def __init__(self, wdir, vmdk, obf):
        super(SparseExtentExtractor, self).__init__()
        self.wdir = wdir
        self.vmdk = vmdk
        self.obf = obf
        self.df = vmdk.descriptor_file()
    ##
    ## @brief      { function_description }
    ##
    ## @param      extent  The extent
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __extract_sparse_extent(self, extent):
        extent_path = os.path.join(self.wdir, extent.filename)
        if not BinaryFile.exists(extent_path):
            LGR.error("cannot find extent: {}".format(extent_path))
            return False

        LGR.info("processing extent: {}".format(extent_path))
        with BinaryFile(extent_path, 'r') as ebf:
            evmdk = VmdkDisk(ebf)

            hdr = evmdk.header()
            if hdr is None or hdr.st_type != S_SPARSE_EXTENT_HDR:
                return False

            gds = GrainDirectoryStack(self.wdir, evmdk)

            num_grains = hdr.capacity // hdr.grainSize

            LGR.info("extracting {} grains from extent...".format(num_grains))
            for gidx in range(num_grains):

                grain = gds.base().read_grain(gidx*hdr.grainSize)
                self.obf.write(grain) # output grain


                if (gidx+1) % 100 == 0:
                    LGR.info("{}/{} grains extracted.".format(gidx+1, num_grains))

            LGR.info("extent processed.")
            gds.term() # close grain directory stack internal binary files
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __extract_monolithic_sparse(self):
        total_sectors = sum([extent.size for extent in self.df.extents])
        total_sectors = total_sectors // SECTOR_SZ

        LGR.info("extracting raw disk...")
        for extent in self.df.extents:
            extent_sectors = extent.size // SECTOR_SZ
            LGR.info("extracting {} of {} sectors.".format(extent_sectors,
                                                           total_sectors))
            if not self.__extract_sparse_extent(extent):
                LGR.error("sparse extent extraction failed!")
                return False

            LGR.info("extraction of {} of {} sectors completed.".format(
                extent_sectors,
                total_sectors))

        LGR.info("extraction completed.")
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def extract(self):
        if self.df.is_monolithic():
            return self.__extract_monolithic_sparse()

        elif self.df.is_2gb_splitted():
            todo(LGR, 'implement sparse 2GB splitted disk extraction.')

        elif self.df.is_esx_disk():
            todo(LGR, 'implement sparse ESX disk extraction.')

        return False
