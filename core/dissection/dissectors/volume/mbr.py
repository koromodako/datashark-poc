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
from helpers.mbr.mbr import MBR
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================
def _extract_memory_maps(container, mem_maps, prefix):
    containers = []

    n = 1
    for mm in mem_maps:
        name = '{}.{}'.format(prefix, n)
        obf = container.obf(name)

        LGR.info("extracting {} sectors...".format(mm.size))
        for i in range(0, mm.size):
            obf.write(mm.read_one(i))

            if (i+1) % 20480 == 0:
                LGR.info("{}/{} sectors extracted.".format(i+1, mm.size))

        containers.append(Container(obf.abspath, name))
        obf.close()
        n += 1

    return containers
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

    ibf = container.ibf()
    mbr = MBR(ibf)

    LGR.info("extracting partitions...")
    containers += _extract_memory_maps(container,
                                       mbr.partitions(),
                                       'partition')

    LGR.info("extracting unallocated space...")
    containers += _extract_memory_maps(container,
                                       mbr.unallocated(),
                                       'unallocated')

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

            LGR.info(mbr.to_str())

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
    def __action_partitions(keywords, args):
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
            text = "partitions:"
            for part in mbr.partitions():
                text += "\n\t{}. {}".format(n, part)
                n += 1

            LGR.info(text)

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
            text = "allocated:"
            for mm in mbr.allocated():
                text += "\n\t{}. {}".format(n, mm)
                n += 1

            n = 1
            text += "\nunallocated:"
            for mm in mbr.unallocated():
                text += "\n\t{}. {}".format(n, mm)
                n += 1

            LGR.info(text)

        return True

    return ActionGroup('mbr', {
        'display': ActionGroup.action(__action_display,
                                      "display MBR/EBR structure(s)."),
        'mapping': ActionGroup.action(__action_mapping,
                                      "display full drive mapping."),
        'partitions': ActionGroup.action(__action_partitions,
                                      "display partitions.")
    })
