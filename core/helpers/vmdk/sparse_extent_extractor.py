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
from utils.logging import get_logger
from utils.binary_file import BinaryFile
from helpers.vmdk.gd_stack import GrainDirectoryStack
from helpers.vmdk.vmdk_disk import VmdkDisk
# =============================================================================
#  GLOBALS
# =============================================================================
LGR = get_logger(__name__)
SECTOR_SZ = VmdkDisk.SECTOR_SZ
# =============================================================================
#  CLASSES
# =============================================================================


class SparseExtentExtractor(object):
    # -------------------------------------------------------------------------
    # SparseExtentExtractor
    # -------------------------------------------------------------------------

    def __init__(self, wdir, vmdk, obf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(SparseExtentExtractor, self).__init__()
        self.wdir = wdir
        self.vmdk = vmdk
        self.obf = obf
        self.df = vmdk.descriptor_file()

    def __extract_sparse_extent(self, extent):
        # ---------------------------------------------------------------------
        # __extract_sparse_extent
        # ---------------------------------------------------------------------
        LGR.debug('SparseExtentExtractor.__extract_sparse_extent()')

        extent_path = os.path.join(self.wdir, extent.filename)
        if not BinaryFile.exists(extent_path):
            LGR.error('cannot find extent: {}'.format(extent_path))
            return False

        LGR.info('processing extent: {}'.format(extent_path))
        ebf = BinaryFile(extent_path, 'r')
        evmdk = VmdkDisk(ebf)

        hdr = evmdk.header()
        if hdr is None or hdr.obj_type != 'SparseExtentHeader':
            ebf.close()
            return False

        gds = GrainDirectoryStack(self.wdir, evmdk)

        num_grains = hdr.capacity // hdr.grainSize

        LGR.info('extracting {} grains from extent...'.format(num_grains))
        for gidx in range(num_grains):

            if (gidx+1) % 100 == 0:
                LGR.info('{}/{} grains extracted.'.format(gidx+1, num_grains))

            grain = gds.base().read_grain(gidx*hdr.grainSize)
            self.obf.write(grain) # output grain

        ebf.close()
        return True

    def __extract_monolithic_sparse(self):
        # ---------------------------------------------------------------------
        # __extract_monolithic_sparse
        # ---------------------------------------------------------------------
        LGR.debug('SparseExtentExtractor.__extract_monolithic_sparse()')

        total_sectors = sum([extent.size for extent in self.df.extents])
        total_sectors = total_sectors // SECTOR_SZ

        for extent in self.df.extents:
            extent_sectors = extent.size // SECTOR_SZ
            LGR.info('extracting {} of {} sectors.'.format(extent_sectors,
                                                           total_sectors))
            if not self.__extract_sparse_extent(extent):
                LGR.error('sparse extent extraction failed!')
                return False

        return True

    def extract(self):
        # ---------------------------------------------------------------------
        # extract
        # ---------------------------------------------------------------------
        LGR.debug('SparseExtentExtractor.extract()')

        if self.df.is_monolithic():
            return self.__extract_monolithic_sparse()

        elif self.df.is_2gb_splitted():
            todo(LGR, 'implement flat 2GB splitted disk extraction.')

        elif self.df.is_esx_disk():
            todo(LGR, 'implement flat ESX disk extraction.')

        return False
