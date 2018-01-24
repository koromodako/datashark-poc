# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: vhd.py
#    date: 2017-11-18
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
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from container.container import Container
from helpers.vhd.vhd_disk import VhdDisk
from helpers.vhd.vhd_extractor import VhdExtractor
# =============================================================================
# GLOBAL
# =============================================================================
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================
##
## @brief      returns a list of mime types that this dissector can handle
## @warning    public mandatory function that the module must define
##
## @return     a list of mime types
##
@trace_func(__name__)
def mimes():
    return [
        'application/octet-stream'
    ]
##
## @brief      configures the dissector internal parameters
## @warning    public mandatory function that the module must define
##
## @param      config  The configuration
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def configure(config):
    return True
##
## @brief      Determines ability to dissect given container.
## @warning    public mandatory function that the module must define
##
## @param      container  The container
##
## @return     True if able to dissect, False otherwise.
##
@trace_func(__name__)
def can_dissect(container):
    if 'Microsoft Disk Image' not in container.mime_text:
        return False

    ibf = container.ibf()
    vhd = VhdDisk(ibf)

    if vhd.footer() is None:
        ibf.close()
        return False

    ibf.close()
    return True
##
## @brief      performs the dissection of the container and returns a list of
##             containers found in the dissected container
## @warning    public mandatory function that the module must define
##
## @param      container  The container
##
## @return     a list of containers
##
@trace_func(__name__)
def dissect(container):
    containers = []

    obf = container.obf('vhd.raw')
    ibf = container.ibf()

    extractor = VhdExtractor(container.wdir(), VhdDisk(ibf), obf)
    if extractor.extract():
        containers.append(Container(obf.abspath, 'vhd.raw'))
    else:
        LGR.error("failed to extract data from VDI.")

    obf.close()
    ibf.close()
    return containers
##
## @brief      { function_description }
## @warning    public mandatory function that the module must define
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def action_group():
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_header(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                vhd = VhdDisk(bf)
                hdr = vhd.header()

            if hdr is None:
                LGR.warn("fail to read VHD header.")
                continue

            print(hdr.to_str())

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_footer(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                vhd = VhdDisk(bf)
                ftr = vhd.footer()

            if ftr is None:
                LGR.warn("fail to read VHD footer.")
                continue

            print(ftr.to_str())

        return True

    return ActionGroup('vhd', {
        'header': ActionGroup.action(__action_header, "display vhd header."),
        'footer': ActionGroup.action(__action_footer, "display vhd footer.")
    })
