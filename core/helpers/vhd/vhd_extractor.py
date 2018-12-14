# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vhd_extractor.py
#     date: 2017-12-09
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
#  IMPORTS
# =============================================================================
from utils.wrapper import trace
from utils.logging import get_logger
from helpers.vhd.vhd_disk import VhdDiskType
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for vhd extractor.
##
class VhdExtractor(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      wdir  The wdir
    ## @param      vhd   The vhd
    ## @param      obf   The obf
    ##
    def __init__(self, wdir, vhd, obf):
        super(VhdExtractor, self).__init__()
        self.wdir = wdir
        self.vhd = vhd
        self.obf = obf
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def extract(self):
        blk_cnt = self.vhd.block_count()

        LGR.info("extracting {} blocks...".format(blk_cnt))

        for n in range(blk_cnt):
            data = self.vhd.read_block(n)

            if data is None:
                LGR.error("an error occured while extracting data.")
                return False

            self.obf.write(data)

            if (n+1) % 50 == 0:
                LGR.info("{}/{} blocks extracted.".format(n+1, blk_cnt))

        LGR.info("extraction completed.")
        return True
