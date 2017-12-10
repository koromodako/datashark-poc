# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: flat_extent_extractor.py
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
from utils.logging import todo
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
#  GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class FlatExtentExtractor(object):
    # -------------------------------------------------------------------------
    # FlatExtentExtractor
    # -------------------------------------------------------------------------

    def __init__(self, wdir, vmdk, obf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(FlatExtentExtractor, self).__init__()
        self.wdir = wdir
        self.vmdk = vmdk
        self.obf = obf

    @trace(LGR)
    def extract(self):
        # ---------------------------------------------------------------------
        # extract
        # ---------------------------------------------------------------------
        if self.df.is_monolithic():
            todo(LGR, 'implement flat monolithic disk extraction.')

        elif self.df.is_2gb_splitted():
            todo(LGR, 'implement flat 2GB splitted disk extraction.')

        return False
