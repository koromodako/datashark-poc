# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vdi_extractor.py
#     date: 2017-12-08
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
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class VdiExtractor(object):
    # -------------------------------------------------------------------------
    # VdiExtractor
    # -------------------------------------------------------------------------
    def __init__(self, wdir, vdi, obf):
        self.wdir = wdir
        self.vdi = vdi
        self.obf = obf

    @trace(LGR)
    def extract(self):
        # ---------------------------------------------------------------------
        # extract
        # ---------------------------------------------------------------------
        vdi_blk_cnt = self.vdi.header().numBlkInHdd

        LGR.info("extracting {} 1MB blocks...".format(vdi_blk_cnt))
        for n in range(vdi_blk_cnt):

            data = self.vdi.read_block(n)
            if data is None:
                LGR.error("failed to read block.")
                return False

            self.obf.write(data)

            if (n+1) % 100 == 0:
                LGR.info("{}/{} blocks extracted.".format(n+1, vdi_blk_cnt))

        LGR.info("extraction completed.")
        return True
