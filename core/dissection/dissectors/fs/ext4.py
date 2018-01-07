# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4.py
#     date: 2018-01-07
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
# IMPORTS
# =============================================================================
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from container.container import Container
from dissection.helpers.ext4.ext4 import Ext4FS
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
    if 'Linux rev 1.0 ext4 filesystem data' not in container.mime_text:
        return False

    ibf = container.ibf()
    fs = Ext4FS(ibf)
    valid = fs.is_valid()
    ibf.close()

    return valid
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

    #obf = container.obf('vdi.raw')
    #ibf = container.ibf()

    todo(LGR, "implement ext4.dissect()", no_raise=True)

    #obf.close()
    #ibf.close()

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
    def __action_superblock(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            sb = None
            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                sb = fs.sb

            if sb is None:
                continue

            LGR.info(sb._sb.to_str())

        return True

    return ActionGroup('ext4', {
        'superblock': ActionGroup.action(__action_superblock,
                                         "display ext4 fs superblock.")
    })
