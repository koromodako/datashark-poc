# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: mbr.py
#     date: 2018-01-04
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 paul.dautry
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
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from container.container import Container
from dissection.helpers.mbr.mbr import MBR
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# PUBLIC FUNCTIONS
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
    if 'DOS/MBR boot sector' not in container.mime_text:
        return False

    ibf = container.ibf()
    mbr = MBR(ibf)
    ibf.close()

    if not mbr.is_valid():
        return False

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

    obf = container.obf()
    ibf = container.ibf()

    #extractor = VdiExtractor(container.wdir(), VdiDisk(ibf), obf)
    #if extractor.extract():
    #    containers.append(Container(obf.abspath, 'disk.raw'))
    #else:
    #    LGR.error("failed to extract data from VDI.")

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
    def __action_display(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                mbr = MBR(bf)

            if not mbr.is_valid():
                LGR.warn("failed to read header, see previous logs for "
                         "error details.")
                continue

            LGR.info(mbr.mbr.to_str())

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
    def __action_mapping(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                mbr = MBR(bf)

            if not mbr.is_valid():
                LGR.warn("failed to read header, see previous logs for "
                         "error details.")
                continue

            n = 1
            text = "drive mapping:"
            for mm in mbr.drive_mapping():
                text += "\n\t{}. {} ({})".format(n, mm, mm.type)
                n += 1

            LGR.info(text)

        return True

    return ActionGroup('mbr', {
        'display': ActionGroup.action(__action_display,
                                      "display MBR structure."),
        'mapping': ActionGroup.action(__action_mapping,
                                      "display full drive mapping."),
    })
