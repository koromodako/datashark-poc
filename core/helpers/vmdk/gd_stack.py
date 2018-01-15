# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: gd_stack.py
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
from utils.wrapper import trace
from utils.logging import get_logger
from utils.binary_file import BinaryFile
from helpers.vmdk.gd import GrainDirectory
from helpers.vmdk.vmdk_disk import VmdkDisk
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      List of grain directories.
##
class GrainDirectoryStack(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      wdir  The wdir
    ## @param      vmdk  The vmdk
    ##
    def __init__(self, wdir, vmdk):
        super(GrainDirectoryStack, self).__init__()
        self.wdir = wdir
        self.base_gd = self.__build_gd(vmdk)
    ##
    ## @brief      Builds a gd.
    ##
    ## @param      vmdk  The vmdk
    ##
    ## @return     The gd.
    ##
    @trace()
    def __build_gd(self, vmdk):
        df = vmdk.descriptor_file()

        parent_filename = df.parent_filename()

        if parent_filename is not None:
            parent_path = os.path.join(self.wdir, parent_filename)

            if BinaryFile.exists(parent_path):
                parent_bf = BinaryFile(parent_path)
                parent_bf.open()
                parent_vmdk = VmdkDisk(parent_bf)
                parent_gd = self.__build_gd(parent_vmdk)

            else:
                LGR.warn("could not find parent disk. Disk image will be "
                            "incomplete.")
        else:
            parent_gd = None

        return GrainDirectory(vmdk, parent_gd)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def base(self):
        return self.base_gd
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def term(self):
        self.base_gd.term()
